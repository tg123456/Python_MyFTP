import socket
import os
import sys
import time
import json
import struct
import hashlib

BASE_DIR = os.path.dirname(os.getcwd())
sys.path.append(BASE_DIR)

from lib import common
from conf import settings


class FTPClient:
    coding = settings.configuration.get('coding')
    FILE_PATH = settings.FILE_PATH
    max_packet_size = settings.configuration.get('block_size')
    br_download_info = None
    br_upload_info = None

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, server_address, connect=True):
        self.server_address = server_address
        # 初始化时：创建客户端链接句柄
        self.sk = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

        if connect:
            try:
                self.client_connect()
                print("服务器连接成功！")
            except:
                self.client_close()
                raise Exception('服务器连接失败！')

    # 连接功能
    def client_connect(self):
        self.sk.connect(self.server_address)

    # 关闭功能
    def client_close(self):
        self.sk.close()

    def run(self, args):
        cmd = args['cmd']
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func(args['info'])
        else:
            raise Exception('客户端没有 %s 功能模块！' % cmd)

    # 安全连接验证
    def secure_connect(self, salt):
        head_dic = common.recv_info(self.sk, self.coding)['clear']
        # 加密 Secure connection verification
        scv = common.my_md5(salt, head_dic)
        head_dic = {'scv': scv}
        head_json_bytes, head_struct = common.struct_pack(head_dic)
        common.send_info(head_json_bytes, head_struct, self.sk)
        head_dic = common.recv_info(self.sk, self.coding)['state']

        return head_dic

    # 文件上传功能
    def upload_files(self, args):
        br_flag = 0
        args_info = args['info']
        name = args_info['name']
        ret = {'state': True}

        # 本地化判断是不是断点续传文件
        br_file_path = os.path.join(args_info['current_file'], args_info['filename'])

        if br_file_path in self.br_upload_info.keys():
            br_file_info = self.br_upload_info[br_file_path]
            # 是断点续传的文件，发送服务器端确认 如果信息不一致更新客户端信息
            br_file_md5 = str(common.br_file_md5(args_info['file_path'], br_file_info['seek'], self.max_packet_size))
            head_dic = {'cmd': 'upload_files', 'info':
                {'name': name, 'is_br_file': True, 'current_file': args_info['current_file'],
                 'filename': args_info['filename'], 'br_file_md5': br_file_md5}}
            head_json_bytes, head_struct = common.struct_pack(head_dic)
            common.send_info(head_json_bytes, head_struct, self.sk)
            head_dic = common.recv_info(self.sk, self.coding)
            # 判断信息是否一致 state:1 完全一致，state:2 不是br文件 state:3 MD5不一致
            state = head_dic['state']

            if state == 1:  # 发送数据
                file_seek = br_file_info['seek']
                br_flag = 1
            elif state == 2:  # 信息不一致，更新客户端数据，从新发送数据
                # 信息不一致，更新客户端数据
                self.br_upload_info = head_dic['br_upload_info']
                common.update_br_info('upload', name, self.br_upload_info)
                file_seek = 0
                if args_info['filename'] in args_info['file_list']:
                    flag = input("该文件已经存在，是否继续(Y/N):").strip()
                    if flag.upper() != 'Y':
                        ret = {'state': 'N'}
            elif state == 3:  # MD5不一致，从新发送数据
                # print("1234567890")
                flag = input("客户端和服务器端文件内容不一致，是否继续(Y/N):").strip()
                if flag.upper() != 'Y':
                    ret = {'state': 'N'}
                file_seek = 0
                br_flag = 1
        else:
            head_dic = {'cmd': 'upload_files', 'info':
                {'name': name, 'is_br_file': False, 'current_file': args_info['current_file'],
                 'filename': args_info['filename'], 'br_file_md5': ''}}
            head_json_bytes, head_struct = common.struct_pack(head_dic)
            common.send_info(head_json_bytes, head_struct, self.sk)
            head_dic = common.recv_info(self.sk, self.coding)
            state = head_dic['state']

            if state == 2:  # 信息不一致，更新客户端数据，从新发送数据
                # 信息不一致，更新客户端数据
                self.br_upload_info = head_dic['br_upload_info']
                common.update_br_info('upload', name, self.br_upload_info)

                br_file_md5 = str(common.br_file_md5(args_info['file_path'], head_dic['seek']))
                if br_file_md5 == head_dic['br_file_md5']:
                    file_seek = head_dic['seek']
                    br_flag = 1
            else:
                file_seek = 0
                if args_info['filename'] in args_info['file_list']:
                    flag = input("该文件已经存在，是否继续(Y/N):").strip()
                    if flag.upper() != 'Y':
                        ret = {'state': 'N'}

        if ret['state'] == True:
            head_json_bytes, head_struct = common.struct_pack(args)
            common.send_info(head_json_bytes, head_struct, self.sk)
            # file_path, filesize, file_seek, socket, size=1024
            common.send_file_info(args_info['file_path'], args_info['filesize'], file_seek, self.sk,
                                  self.max_packet_size)
            recv_info = common.recv_info(self.sk, self.coding)

            if recv_info['state'] and br_flag:
                self.br_upload_info.pop(br_file_path)
                common.update_br_info('upload', recv_info['name'], self.br_upload_info)
            else:
                return recv_info
        else:
            head_dic = {'cmd': 'download_files', 'info': {'name': name, 'is_recv': False}}
            head_json_bytes, head_struct = common.struct_pack(head_dic)
            common.send_info(head_json_bytes, head_struct, self.sk)

        return ret

    # 文件下载功能
    def download_files(self, args):
        args_info = args['info']
        # 本地化判断是不是断点续传文件
        br_file_path = os.path.join(settings.FILE_PATH, args_info['current_file'], args_info['filename'])
        br_flag = 0
        ret = {'state': True}

        if br_file_path in self.br_download_info.keys():
            # 是断点续传的文件，发送服务器端确认 如果信息不一致更新客户端信息
            br_file_info = self.br_download_info[br_file_path]
            br_file_md5 = str(common.br_file_md5(args_info['file_path'], br_file_info['seek'], 0))
            head_dic = {'cmd': 'download_files', 'info':
                {'name': args_info['name'], 'is_br_file': True, 'current_file': args_info['current_file'],
                 'filename': args_info['filename'], 'br_file_md5': br_file_md5}}
            head_json_bytes, head_struct = common.struct_pack(head_dic)
            common.send_info(head_json_bytes, head_struct, self.sk)
            head_dic = common.recv_info(self.sk, self.coding)
            # 判断信息是否一致 state:1 完全一致，state:2 不是br文件 state:3 MD5不一致
            state = head_dic['state']

            if state == 1:  # 接收数据
                br_flag = 1
            elif state == 2:  # 信息不一致，更新客户端数据，从新发送数据
                # 信息不一致，更新客户端数据
                self.br_download_info = head_dic['br_download_info']
                common.update_br_info('download', args_info['name'], self.br_download_info)
                if args_info['filename'] in args_info['file_list']:
                    flag = input("该文件已经存在，是否继续(Y/N):").strip()
                    if flag.upper() != 'Y':
                        ret = {'state': 'N'}
            elif state == 3:  # MD5不一致，从新发送数据
                flag = input("客户端和服务器端文件内容不一致，是否继续(Y/N):").strip()
                if flag.upper() != 'Y':
                    ret = {'state': 'N'}
                br_flag = 1
        else:
            head_dic = {'cmd': 'download_files', 'info':
                {'name': args_info['name'], 'is_br_file': False, 'current_file': args_info['current_file'],
                 'filename': args_info['filename'], 'br_file_md5': ''}}
            head_json_bytes, head_struct = common.struct_pack(head_dic)
            common.send_info(head_json_bytes, head_struct, self.sk)
            head_dic = common.recv_info(self.sk, self.coding)
            state = head_dic['state']

            if state == 2:  # 信息不一致，更新客户端数据，从新发送数据
                # 信息不一致，更新客户端数据
                self.br_download_info = head_dic['br_download_info']
                common.update_br_info('download_files', args_info['name'], self.br_download_info)

                br_file_md5 = str(common.br_file_md5(args_info['file_path'], head_dic['file_seek']))
                if br_file_md5 == head_dic['br_file_md5']:
                    br_flag = 1
            else:
                if args_info['filename'] in args_info['file_list']:
                    flag = input("该文件已经存在，是否继续(Y/N):").strip()
                    if flag.upper() != 'Y':
                        ret = {'state': 'N'}

        if ret['state'] == True:
            head_dic = {'name': args_info['name'], 'is_recv': True}
            head_json_bytes, head_struct = common.struct_pack(head_dic)
            common.send_info(head_json_bytes, head_struct, self.sk)
            head_dic = common.recv_info(self.sk, self.coding)
            file_path = os.path.join(settings.FILE_PATH, head_dic['filename'])

            # file_path, filesize, file_seek, socket, size=1024
            if head_dic['seek'] == 0: mode = 'wb'
            else: mode = 'ab'

            recv_seek, rev_file_md5 = common.recv_file_info(file_path, head_dic['filesize'], head_dic['seek'], self.sk,
                                                            self.max_packet_size,mode)
            name = head_dic['name']
            file_mad5 = str(common.file_md5(file_path))
            if rev_file_md5 == file_mad5:
                print('download success!')
            else:
                print('download fail!')

        else:
            head_dic = {'name': args['name'], 'is_recv': False}
            head_json_bytes, head_struct = common.struct_pack(head_dic)
            common.send_info(head_json_bytes, head_struct, self.sk)

        return ret

    # 统一的服务器消息请求
    def request_and_response(self, args):

        head_json_bytes, head_struct = common.struct_pack(args)
        common.send_info(head_json_bytes, head_struct, self.sk)
        head_dic = common.recv_info(self.sk, self.coding)

        # 登录之后获取 断点续传文件，避免每次上传下载 去 读取上传下载文件，减少对os的访问
        if args['cmd'] == 'login' and head_dic['state'] == 1:
            self.br_download_info = head_dic['br_download_info']
            self.br_upload_info = head_dic['br_upload_info']
        return head_dic

# client = FTPClient(('127.0.0.1', 8080))
# client.run()
