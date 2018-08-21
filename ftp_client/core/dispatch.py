
from core import ftp_manage

class Dispatch:
    manage = ftp_manage.FTPManage()

    def secure_verify(self):
        ret = self.manage.secure_verify()
        return ret

    def manager(self):
        ftp_manage.FTPManage()

    def member(self,args):
        args.pop('person_info')
        args.pop('br_upload_info')
        args.pop('br_download_info')
        # print("args == ",args)
        while True:
            print("当前所在目录:",args['current_file'],'\n当前目录的列表:',end='')
            print(args['file_list'])
            print("\n文件上传:1  文件下载:2  文件夹管理:3  退出:0")
            operate_code = 'func' + input("请输入对应的操作编码:").strip()

            if hasattr(self.manage,operate_code):
                func = getattr(self.manage,operate_code)
                args = func(args)
                print(args['info']+'\n')
                if args.get('state') == 99:break
            else:
                print('\033[1;31;0m请输入正确的操作编码！\n\033[0m')





