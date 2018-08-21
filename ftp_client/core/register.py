import re

from core import ftp_manage
from lib import common


def register():
    # 正则表达式 name:数字字母下划线 age:数字 phone:字符串
    name_re = re.compile(r'^[0-9a-zA-Z]\w*$')
    age_re = re.compile(r'^[0-9]{1,2}$')
    sex_re = re.compile(r'[男女]')
    phone_re = re.compile(r'1[3458]\d{9}')
    passwd_re = re.compile(r'.{6}')

    while True:
        flag = 0
        while True:
            name = input("请输入您的姓名(退出:Q):").strip()
            if name.upper() == 'Q':
                flag = 1
                print("\033[1;31;0m欢迎使用！\n\033[0m")
                break
            if not name_re.match(name):
                print("\033[1;31;0m您输入的用户名不合法(用户名:由字母数字下划线组成，不能以下划线开头)，请重新输入！\033[0m")
                continue
            else:
                break

        if flag:break

        while True:
            age = input("请输入您的年龄(退出:Q):").strip()
            if age.upper() == 'Q':
                print("\033[1;31;0m欢迎使用！\n\033[0m")
                flag = 1
                break
            if not age_re.match(age) or int(age) <= 0 or int(age) >= 100:
                print("\033[1;31;0m您输入的用户名不合法(年龄:在0-100之间)，请重新输入！\033[0m")
                continue
            else:
                break

        if flag: break

        while True:
            sex = input("请输入您的性别(退出:Q):").strip()
            if sex.upper() == 'Q':
                print("\033[1;31;0m欢迎使用！\n\033[0m")
                flag = 1
                break
            if not sex_re.match(sex):
                print("\033[1;31;0m您输入的性别不合法(性别:只有男或女)，请重新输入！\033[0m")
                continue
            else:
                break

        if flag: break

        while True:
            phone = input("请输入您的电话(退出:Q):").strip()
            if phone.upper() == 'Q':
                print("\033[1;31;0m欢迎使用！\n\033[0m")
                flag = 1
                break
            if not phone_re.match(phone):
                print("\033[1;31;0m您输入的电话号码不合法(电话号码:支持13\\14\\15\\18开头的:11位电话)，请重新输入！\033[0m")
                continue
            else:
                break

        if flag: break

        while True:
            passwd = input('请输入您的密码(退出:Q):')
            if passwd.upper() == 'Q':
                flag = 1
                print("\033[1;31;0m欢迎使用！\n\033[0m")
                break
            if not passwd_re.match(passwd) or len(passwd) != 6:
                print("\033[1;31;0m密码格式错误:密码由6位任意字符构成！\033[0m")
                continue
            else:
                break

        if flag: break

        while True:
            passwd_check = input("请确认您的密码(退出:Q):")
            if passwd_check.upper() == 'Q':
                print("\033[1;31;0m欢迎使用！\n\033[0m")
                flag = 1
                break
            if not passwd_re.match(passwd_check) or len(passwd_check) != 6:
                print("\033[1;31;0m密码格式错误:密码由6位任意字符构成！\033[0m")
                continue
            else:
                break

        if flag: break

        if passwd == passwd_check:
            passwd = common.my_md5(name, passwd)
            info_dic = {'cmd': 'register',
                        'info': {"name": name, "age": age, "sex": sex, "phone": phone, 'passwd': passwd}}
            # 调用member的注册功能
            ret = ftp_manage.FTPManage().request_and_response(info_dic)

            # 接收服务器返回的信息,True注册成功,False 注册失败
            if ret['state'] == 1:
                print("\033[1;31;0m注册成功，请登录！\n\033[0m")
                return ret
            elif ret['state'] == 2:
                msg = input("该用户已经存在，是否继续(Y/N):").strip().upper()
                if msg == 'Y':
                    continue
                else:
                    break
            elif ret['state'] == 0:
                msg = input("用户注册失败，是否继续(Y/N):").strip().upper()
                if msg == 'Y':
                    continue
                else:
                    break
        else:
            print("\033[1;31;0m对不起，您的密码不一致！\n\033[0m")
