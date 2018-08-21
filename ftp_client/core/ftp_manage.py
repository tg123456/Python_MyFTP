import re
import os

from core import ftp_client
from conf import settings
from lib import common


class FTPManage:
    client = ftp_client.FTPClient((settings.configuration.get('server_ip'), settings.configuration.get('server_port')))

    def secure_verify(self):
        return self.client.run({'cmd': 'secure_connect','info':settings.configuration.get('salt')})

    def request_and_response(self, args):
        info_dic = {'cmd': 'request_and_response', 'info': args}
        ret = self.client.run(info_dic)
        return ret

    # 文件上传功能
    def func1(self, args):
        file_path = input("请输入文件路径:").strip()
        if not os.path.isfile(file_path):
            print("file:\033[1;31;0m%s:文件不存在!\033[0m" % file_path)
            return args
        else:
            filesize = os.path.getsize(file_path)

        # 计算文件MD5的值
        file_md5 = str(common.file_md5(file_path))
        info_dic = {'cmd': 'upload_files', 'info':
            {'cmd': 'upload_files', 'info': {'name': args['name'], 'current_file': args['current_file'],
             'filename': os.path.basename(file_path), 'filesize': filesize, 'file_md5': file_md5,'is_recv':True,
            'file_path':file_path,'file_list':args['file_list']}}}

        ret = self.client.run(info_dic)

        if ret['state'] == True:
            print("\033[1;31;0m文件上传成功！\033[0m")
        elif ret['state'] == 'N':
            args['info'] = "\033[1;31;0m欢迎使用！\n\033[0m"
            return args
        else:
            args['info'] = "\033[1;31;0m文件上传失败！\n\033[0m"
            return args
        
        return self.func4(args)

    # 文件下载功能
    def func2(self, args):
        file_path = input("请输入文件名称:").strip()

        file_list = os.listdir(settings.FILE_PATH)

        info_dic = {'cmd': 'download_files', 'info':
            {'cmd': 'download_files', 'info': {'name': args['name'], 'current_file': args['current_file'],
                                             'filename': os.path.basename(file_path), 'filesize': '',
                                             'file_md5': '', 'is_recv': True,
                                             'file_path': file_path, 'file_list': file_list}}}

        ret = self.client.run(info_dic)

        if ret['state'] == True:
            print("\033[1;31;0m文件下载成功！\033[0m")
        elif ret['state'] == 'N':
            args['info'] = "\033[1;31;0m欢迎使用！\n\033[0m"
            return args
        else:
            args['info'] = "\033[1;31;0m文件下载失败！\n\033[0m"
            return args

        return self.func4(args)

    def func4(self, args):
        info_dic = {'cmd': 'request_and_response', 'info': {'cmd': 'file_operate', 'info':
            {'cmd': 'lsdir', 'name': args['name'], 'file_path': args['current_file'],
             'current_file': args['current_file']}}}
        return self.client.run(info_dic)

    # 文件目录的相关操作
    def func3(self, args):
        print("\n创建文件目录:mkdir filename  切换文件目录:cd filename 修改文件名:rename oldfilename newfilename")
        command = input("请输入文件目录的相关操作的命令(退出:Q):").strip()
        name = args['name']
        current_file = args['current_file']
        if command.upper() == 'Q':
            args['info'] = "\033[1;31;0m欢迎使用！\n\033[0m"
            return args
        elif command.startswith('rename'):
            info_list = command.split()

            if len(info_list) == 3:
                old_file_name = info_list[1].strip()
                new_file_name = info_list[2].strip()
                file_re = re.compile(r'\w+\.[a-zA-Z]+')
                dir_re = re.compile(r'\w+')

                if (len(file_re.findall(old_file_name)) == 1 and len(file_re.findall(new_file_name)) == 1) \
                        or (len(dir_re.findall(old_file_name)) == 1 and len(dir_re.findall(new_file_name)) == 1):
                    info_dic = {'cmd': 'request_and_response', 'info': {'cmd': 'file_operate', 'info':
                        {'cmd': info_list[0].strip(), 'current_file': current_file,
                         'old_file_name': old_file_name, 'new_file_name': new_file_name, 'file_path': current_file,
                         'name': name}}}
                    return self.client.run(info_dic)
                else:
                    args['info'] = "\033[1;31;0m语法错误！\n\033[0m"
            else: args['info'] = "\033[1;31;0m语法错误！\n\033[0m"
        elif command.startswith('mkdir') or command.startswith('cd'):
            info_list = command.split()
            filename = info_list[1].strip()
            if len(info_list) == 2:
                if command.startswith('mkdir') and filename.isalnum():
                    info_dic = {'cmd': 'request_and_response', 'info': {'cmd': 'file_operate', 'info':
                        {'cmd': info_list[0].strip(), 'current_file': current_file, 'file_path': filename,
                         'name': name}}}
                    return self.client.run(info_dic)
                elif command.startswith('cd') and len(re.findall(r'\w+(?:\\\w+)*', filename)) == 1:
                    info_dic = {'cmd': 'request_and_response', 'info': {'cmd': 'file_operate', 'info':
                        {'cmd': info_list[0].strip(), 'current_file': current_file, 'file_path': filename,
                         'name': name}}}
                    return self.client.run(info_dic)
                else:
                    args['info'] = "\033[1;31;0m语法错误！\n\033[0m"
            else:
                args['info'] = "\033[1;31;0m语法错误！\n\033[0m"
        else:
            args['info'] = "\033[1;31;0m语法错误！\n\033[0m"

        return args

    def func0(self, args):
        # print('args = ',args)
        args['state'] = 99
        args['info'] = "\033[1;31;0m欢迎使用！\n\033[0m"
        return args



