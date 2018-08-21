from core import ftp_manage
from lib import common


def login():
    while True:
        # 判断用户名是否重复2:用户名不存在，1：登录成功，0：登录失败
        name = input('请输入您的账号(退出:Q):').strip()
        if name.upper() == 'Q':
            break

        passwd = input('请输入您的密码:')
        passwd = common.my_md5(name, passwd)
        info_dic = {'cmd': 'login', 'info': {"name": name, 'passwd': passwd}}

        # 调用member的登录功能
        ret = ftp_manage.FTPManage().request_and_response(info_dic)

        info_list = ['\033[1;31;0m登录失败！\n\033[0m', '\033[1;31;0m登录成功！\n\033[0m',
                     '\033[1;31;0m该账号不存在！\n\033[0m', '\033[1;31;0m该用户已经登录！\n\033[0m']

        if ret['state'] == 1:
            #保存 更新 断点续传的数据
            common.update_br_info('download',name,ret['br_download_info'])
            common.update_br_info('upload', name, ret['br_upload_info'])
            print('\033[1;31;0m登录成功！\n\033[0m')
            return ret
        else:
            print(info_list[ret['state']])
            return {'state':0}
