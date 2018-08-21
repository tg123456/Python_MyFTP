import os
import sys
import json
import struct
import socketserver
import hashlib
import time

BASE_DIR = os.path.dirname(os.getcwd())
sys.path.append(BASE_DIR)

from core import modes, data_handle
from lib import common
from conf import settings


class FtpServer(socketserver.BaseRequestHandler):
    """
    文件的上传 下载
    """
    coding = settings.configuration.get('coding')
    USER_DIR = ''
    USERS_LIST = ''
    max_packet_size = settings.configuration.get('block_size')
    FILE_PATH = settings.FILE_PATH
    data_handle = data_handle.Data_handle()
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def handle(self):
        print(self.request)
        if self.secure_connect()['state']:
            while True:
                head_dic = common.recv_info(self.request, self.coding)
                cmd = head_dic['cmd']

                if hasattr(self, cmd):
                    func = getattr(self, cmd)
                    func(head_dic['info'])
                else:
                    info_dic = {'state': 9}
                    head_json_bytes, head_struct = common.struct_pack(info_dic)
                    common.send_info(head_json_bytes, head_struct, self.request)
                    print('%s is not exists!' % cmd)
                    return
        else:
            pass

    # 安全连接验证
    def secure_connect(self):
        salt = settings.configuration.get('salt')
        random_clear = str(os.urandom(32))

        # 封装明文
        head_dic = {'clear': random_clear}
        head_json_bytes, head_struct = common.struct_pack(head_dic)
        common.send_info(head_json_bytes, head_struct, self.request)

        # 接收校验密文,自加密
        scv = common.my_md5(salt, random_clear)
        head_json = common.recv_info(self.request, self.coding)['scv']

        if head_json == scv:
            head_dic = {'state': True}
            print("安全连接！")
        else:
            head_dic = {'state': False}
            print("非安全连接！")

        head_json_bytes, head_struct = common.struct_pack(head_dic)
        common.send_info(head_json_bytes, head_struct, self.request)

        return head_dic

    # 判断是不是断点续传
    def is_br_file(self):
        # 判断信息是否一致，不一致更新客户端信息
        pass

    # 断点续传
    def breakpoint_resume(self):
        pass

    # 文件下载功能
    def download_files(self, args):
        # 接收文件上传，获取上传过来的文件名，将文件接收保存到本地
        file_path = os.path.normpath(os.path.join(
            self.FILE_PATH,
            args['current_file'],
            args['filename']
        ))

        name = args['name']
        is_br_file = args['is_br_file']
        head_dic = {'name': name}
        # 判断该文件是否是断点续传的文件
        br_file_path = os.path.join(args['current_file'], args['filename'])
        data = common.is_br_file('download', br_file_path, name)
        br_flag = 0

        if len(data) and is_br_file:  # 是一致的 下一不判断MD5是否一致
            if data['br_file_md5'] == args['br_file_md5']:
                head_dic['state'] = 1  # 发送一个信息包，之后再发送数据
                seek = data['seek']
            else:  # MD5不一致
                head_dic['state'] = 3
                seek = 0
            br_flag = 1
        elif len(data) or is_br_file:
            seek = 0
            head_dic['state'] = 2
            head_dic['br_download_info'] = data
        else:  # 全新上传的文件
            head_dic['state'] = 1
            seek = 0

        head_json_bytes, head_struct = common.struct_pack(head_dic)
        common.send_info(head_json_bytes, head_struct, self.request)

        head_dic = common.recv_info(self.request, self.coding)
        # print("======is_recv========",head_dic)
        # 断点之前的数据是可以的 file_path, recv_size, filesize, max_packet_size, file_seek, socket
        if head_dic['is_recv']:  # 继续下载文件
            filesize = os.path.getsize(file_path)
            head_dic = {'name':args['name'],'current_file':args['current_file'],'filename':args['filename'],
                        'filesize':filesize,'seek':seek}
            head_json_bytes, head_struct = common.struct_pack(head_dic)
            common.send_info(head_json_bytes, head_struct, self.request)

            # file_path, filesize, file_seek, socket, size=1024
            common.send_file_info(file_path, filesize, seek, self.request, self.max_packet_size)

    # 文件上传功能
    def upload_files(self, args):
        # 接收文件上传，获取上传过来的文件名，将文件接收保存到本地
        file_path = os.path.normpath(os.path.join(
            self.FILE_PATH,
            args['current_file'],
            args['filename']
        ))

        name = args['name']
        is_br_file = args['is_br_file']
        head_dic = {'name': name}
        # 判断该文件是否是断点续传的文件
        br_file_path = os.path.join(args['current_file'], args['filename'])
        data = common.is_br_file('upload', br_file_path, name)
        br_flag = 0

        if len(data) and is_br_file:  # 是一致的 下一不判断MD5是否一致
            # br_file_md5(file_path, file_seek, size=1024)
            print("data['seek'] ==",data['seek'])
            print("br_file_path === ", br_file_path)
            print("file_path === ", file_path)
            br_file_md5 = str(common.br_file_md5(file_path,data['seek'],self.max_packet_size))
            print('data[br_file_md5] == args[br_file_md5] = ', br_file_md5, args['br_file_md5'])
            if br_file_md5 == args['br_file_md5']:
                head_dic['state'] = 1  # 发送一个信息包，之后再发送数据
                seek = data['seek']
            else:  # MD5不一致
                head_dic['state'] = 3
                seek = 0
            br_flag = 1
        elif len(data) or is_br_file:
            seek = 0
            head_dic['state'] = 2
            head_dic['br_upload_info'] = data
        else:  # 全新上传的文件
            head_dic['state'] = 1
            seek = 0

        head_json_bytes, head_struct = common.struct_pack(head_dic)
        common.send_info(head_json_bytes, head_struct, self.request)
        head_dic = common.recv_info(self.request, self.coding)['info']

        if head_dic['is_recv']:
            # 断点之前的数据是可以的
            # file_path, filesize, file_seek, socket, size=1024
            filesize = head_dic['filesize']
            file_md5 = head_dic['file_md5']

            if seek == 0: mode = 'wb'
            else: mode = 'ab'

            recv_seek, rev_file_md5 = common.recv_file_info(file_path, filesize, seek,
                                                            self.request, self.max_packet_size,mode)

            if br_flag:
                rev_file_md5 = str(common.file_md5(file_path))
            else: rev_file_md5 = str(rev_file_md5)

            print("rev_file_md5 == file_md5 =", rev_file_md5, file_md5)
            if rev_file_md5 == file_md5:
                head_dic = {'state': True, 'recv_size': recv_seek, 'name': name}
                print('upload success!')
                if br_flag:
                    data = common.get_br_file('upload', name)
                    print("data === ",data)
                    data.pop(br_file_path)
                    common.update_br_file(name, 'upload', data)
            else:
                head_dic = {'state': False, 'recv_size': recv_seek, 'name': name}
                # 保存没有成功上传的文件  type, file_path, time, num, seek, size, name
                data = common.is_br_file('upload', br_file_path, name)
                num = 0
                if len(data):
                    num = data['num'] + 1
                    # type, file_path, br_file_md5, time, num, seek, size, name
                common.save_br_file('upload', br_file_path, rev_file_md5, time.strftime(self.TIME_FORMAT),
                                    num, recv_seek, recv_seek, name)
                print('upload fail!')

            head_json_bytes, head_struct = common.struct_pack(head_dic)
            common.send_info(head_json_bytes, head_struct, self.request)

    # 登录认证功能 返回完整的数据
    def login(self, args):
        name = args['name']
        passwd = common.my_md5('20180610'+name, args['passwd'])
        person_info_dic = self.data_handle.select_data('person_info')
        person_login_info = self.data_handle.select_data('person_login_info')
        person_login_info = {}
        # print("person_info_dic = ", person_info_dic)
        info_dic = {}
        if name in person_login_info.keys():
            info_dic['state'] = 3
            print("该用户已经登录！")
        else:
            if name in person_info_dic.keys():
                if person_info_dic[name]['passwd'] == passwd:
                    # 登录人员的文件目录
                    self.USER_DIR = name
                    info_dic['state'] = 1
                    info_dic['name'] = name
                    person_info_dic[name].pop('passwd')  # 去除密码
                    info_dic['person_info'] = person_info_dic[name]
                    # 获取该用户当前目录下的文件信息
                    file_path = os.path.join(self.FILE_PATH, name)
                    info_dic['file_list'] = os.listdir(file_path)
                    info_dic['current_file'] = name
                    # 获取断点续传文件
                    br_download_info = common.get_br_file('download', name)
                    br_upload_info = common.get_br_file('upload', name)
                    print('br_download_info br_upload_info = ', br_download_info, br_upload_info)
                    info_dic['br_download_info'] = br_download_info
                    info_dic['br_upload_info'] = br_upload_info
                    print('br_download_info br_upload_info = ', info_dic['br_download_info'],
                          info_dic['br_upload_info'])
                    # 保存登录信息
                    login_info = {name: 1}
                    self.data_handle.save_data(login_info, 'person_login_info')
                    self.USERS_LIST = os.listdir(os.path.join(self.FILE_PATH, name))
                    print("登录成功！")
                else:
                    info_dic['state'] = 0
                    print("用户名或密码错误！")
            else:
                info_dic['state'] = 2
                print('该用户名不存在！')

        head_json_bytes, head_struct = common.struct_pack(info_dic)
        common.send_info(head_json_bytes, head_struct, self.request)

    # 注册认证功能 完整的数据
    def register(self, args):
        name = args['name']
        passwd = common.my_md5('20180610'+name,args['passwd'])
        person_info_dic = self.data_handle.select_data('person_info')
        info_dic = {}
        if name in person_info_dic.keys():
            info_dic['state'] = 0
            print('该用户已经存在')
        else:
            info_dic['state'] = 1
            # 实例化一个用户
            person = modes.Member('1', name, passwd, args['age'], args['sex'], args['phone'])
            person_info_dic[name] = person.get_info()

            # 创建用户对应文件目录
            flag = common.create_dir(name)
            if flag:
                info_dic['info'] = {'create_dir': 1}
                # 保存已经注册的用户的数据
                self.data_handle.save_data(person_info_dic, 'person_info')
                print('注册成功！')
            else:
                info_dic['info'] = {'create_dir': 0}
                print('注册失败！')

        head_json_bytes, head_struct = common.struct_pack(info_dic)
        common.send_info(head_json_bytes, head_struct, self.request)

    # 操作自己的目录或当前文件下下面的文件
    def file_operate(self, args):
        # cmd 文件路径 放回该路径下的文件信息 dir cd info {'cmd':'listdir','file_path':'xxx'}
        # info {'cmd':'mkdir','file_path':'xxx'}
        cmd = args['cmd']
        current_file = args['current_file']
        name = args['name']
        file_name = args['file_path']
        head_dic = {'name': name}

        print("cmd,file_name, current_file = ", cmd, file_name, current_file)

        if cmd == 'mkdir':
            try:
                os.mkdir(os.path.join(self.FILE_PATH, current_file, file_name))
                head_dic['info'] = '\033[1;31;0m文件创建成功！\033[0m'
            except Exception as e:
                print(e)
                head_dic['info'] = '\033[1;31;0m文件创建失败！\033[0m'
        elif cmd == 'cd':
            # 判断文件目录是否存在，并且判断是否越界
            file_path = os.path.join(self.FILE_PATH, file_name)
            if (file_name not in self.USERS_LIST) and os.path.exists(file_path) and os.path.isdir(file_path):
                current_file = file_name
                head_dic['info'] = '\033[1;31;0m文件目录切换成功！\033[0m'
            else:
                head_dic['info'] = '\033[1;31;0m %s:不合理，操作失败！\033[0m' % file_name

        elif cmd == 'rename':
            old_file_name = os.path.join(self.FILE_PATH, current_file, args['old_file_name'])
            new_file_name = os.path.join(self.FILE_PATH, current_file, args['new_file_name'])
            try:
                os.rename(old_file_name, new_file_name)
                head_dic['info'] = '\033[1;31;0m文件修改成功！\033[0m'
            except Exception as e:
                head_dic['info'] = '\033[1;31;0m文件修改失败！\033[0m'
        else:
            head_dic['info'] = '\033[1;31;0m操作成功！\033[0m'

        file_list = common.get_files(os.path.join(self.FILE_PATH, current_file))
        head_dic['file_list'] = file_list
        head_dic['current_file'] = current_file
        print("file_list = ", file_list)

        head_json_bytes, head_struct = common.struct_pack(head_dic)
        common.send_info(head_json_bytes, head_struct, self.request)
