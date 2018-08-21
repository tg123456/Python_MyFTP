import socketserver

from core import ftp_server,data_handle

def main():
    """
    程序的入口：登录认证+日志记录，这里使用反射相关的知识
    :return:
    """

    clear_login_data = data_handle.Data_handle()
    clear_login_data.clear_file_content('person_login_info')

    ftpserver = socketserver.ThreadingTCPServer(('127.0.0.1', 8080), ftp_server.FtpServer)
    ftpserver.serve_forever()












