import os

#文件保存地址
FILE_PATH = os.path.join(os.path.dirname(os.getcwd()),'download')

#断点续传的文件目录
BR_PATH = os.path.join(os.path.dirname(os.getcwd()),'breakpoint_resume')

#配置信息
configuration = {
    'server_ip':'127.0.0.1',
    'server_port':8080,
    'coding':'utf-8',
    'block_size':1024,
    'salt':'secure_connect',
}



