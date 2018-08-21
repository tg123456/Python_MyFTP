import os
import sys

BASE_DIR = os.path.dirname(os.getcwd())
sys.path.append(BASE_DIR)

from core import login, register, dispatch


def main():
    """
    验证连接
    程序的入口：登录认证+日志记录，这里使用反射相关的知识
    :return:
    """
    if dispatch.Dispatch().secure_verify() == False:
        print("\033[1;31;0m非安全连接，连接失败！\n\033[0m")
        return False
    print("\033[1;31;0m安全连接！\n\033[0m")

    while True:
        print("""注册:1 登录:2 退出:Q""")
        # 用户注册，用户名只能是英文+数字
        flag = input("请选择您的操作编码:").strip()
        if flag.upper() == 'Q':
            break
        elif flag == '1':
            # 登录认证，并接收相关的信息
            ret = register.register()
            # 日志记录

        elif flag == '2':
            # 登录认证，并接收相关的信息
            ret = login.login()
            # print("ret = ",ret)
            # 日志记录

            # 登录成功
            if ret['state'] == 1:
                func = ret['person_info']['type']
                if hasattr(dispatch.Dispatch(), func):
                    func = getattr(dispatch.Dispatch(), func)
                    func(ret)
                    break
                else:
                    print("\033[1;31;0m该用户类型不存在,请联系管理员！\n\033[0m")
                    break
        else:
            print('\033[1;31;0m请输入正确的操作编码！\n\033[0m')

    return
