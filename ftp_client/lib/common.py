import hashlib
import os
import time
import json
import struct
import pickle

from conf import settings


# 获取该目录下面的所有文件
# print(root)  # 当前目录路径  # print(dirs)  # 当前路径下所有子目录
#  print(files)  # 当前路径下所有非目录子文件   # print("dirs + files = ",(dirs + files))
def get_files(file_path):
    if os.path.exists(file_path):
        for root, dirs, files in os.walk(file_path):
            return dirs + files
    else:
        return None


# 统一的封装功能
def struct_pack(args, coding='utf-8'):
    head_json = json.dumps(args)
    head_json_bytes = bytes(head_json, encoding=coding)
    head_struct = struct.pack('i', len(head_json_bytes))

    return head_json_bytes, head_struct


# 用户加密认证
def my_md5(salt, clear):
    md5_obj = hashlib.md5(salt.encode('utf-8'))
    md5_obj.update(clear.encode('utf-8'))
    return md5_obj.hexdigest()

# 根据用户注册的账户，生产对的文件目录
def create_dir(file_dir):
    count = 0
    # 获取目录 settings.FILE_PATH
    user_dir = os.path.join(settings.FILE_PATH, file_dir)
    if os.path.exists(user_dir):
        print("user_dir = ",user_dir)
        print("该目录已经存在！")
        # 移除该目录，重新创建
        # os.removedirs(user_dir)

    os.mkdir(user_dir)
    # 创建目录尝试3次，如果3次都不成功则返回，创建失败的消息
    while count < 3:
        if os.path.exists(user_dir):
            print("文件目录创建成功！")
            return 1
        else:
            os.mkdir(user_dir)
        count += 1

    print("文件目录创建失败 ！")
    return 0


# 保存没有成功上传 下载 的文件 type:upload(上传) download(下载)
def save_br_file(type, file_path, br_file_md5, time, num, seek, size, name):
    br_file_path = os.path.join(settings.BR_PATH, type, name)
    if os.path.exists(br_file_path):
        f = open(br_file_path, 'rb')
        br_info = pickle.load(f)
        f.close()
        print('br_info = ',br_info)
        br_info[file_path] = {'file_path': file_path, 'br_file_md5': br_file_md5, 'time': time, 'num': num,
                                     'seek': seek, 'size': size}

        f = open(br_file_path, 'wb')
        pickle.dump(br_info, f)
        f.close()
    else:
        f = open(br_file_path, 'wb')
        br_info = {
            file_path: {'file_path': file_path, 'br_file_md5': br_file_md5, 'time': time, 'num': num, 'seek': seek,
                        'size': size}}
        pickle.dump(br_info, f)
        f.close()


# 保存没有成功上传 下载 的文件 type:upload(上传) download(下载)
def update_br_file(name, type, br_info):
    br_file_path = os.path.join(settings.BR_PATH, type, name)
    f = open(br_file_path, 'wb')
    pickle.dump(br_info, f)


def get_br_file(type, name):
    br_file_path = os.path.join(settings.BR_PATH, type, name)
    if os.path.exists(br_file_path):
        f = open(br_file_path, 'rb')
        data = pickle.load(f)
    else:
        data = {}
    return data


def is_br_file(type, file_path, name):
    data = get_br_file(type, name)
    if len(data) and file_path in data.keys():
        br_file = data[file_path]
    else:
        br_file = {}

    return br_file


#文件MD5计算
def file_md5(file_path,size=1024):
    file_size = os.path.getsize(file_path)
    read_size = 0
    md5_obj = hashlib.md5()
    with open(file_path,'rb') as f:
        while read_size < file_size:
            if file_size - read_size > size:
                data = f.read(size)
                read_size += size
            else:
                data = f.read(file_size-read_size)
                read_size = file_size
            md5_obj.update(data)
    return md5_obj.hexdigest()


# 断点文件MD5计算
def br_file_md5(file_path, file_seek, size=1024):
    md5_obj = hashlib.md5()
    read_size = 0
    with open(file_path, 'rb') as f:
        while read_size < file_seek:
            if file_seek - read_size > size:
                data = f.read(size)
                read_size += size
            else:
                data = f.read(file_seek - read_size)
                read_size = file_seek
            md5_obj.update(data)
    return md5_obj.hexdigest()


# 统一接收发送数据端口
def send_info(head_json_bytes, head_struct, socket):
    socket.send(head_struct)
    socket.send(head_json_bytes)

#在这里控制登录
def recv_info(socket, coding):
    try:
        head_struct = socket.recv(4)
    except Exception as e:
        print(e)
        return
    data_len = struct.unpack('i', head_struct)[0]
    head_dic = json.loads(socket.recv(data_len).decode(coding))
    return head_dic


# 发送文件数据
def send_file_info(file_path, filesize, file_seek, socket, size=1024):
    send_size = file_seek
    with open(file_path, 'rb') as f:
        f.seek(file_seek)
        while send_size < filesize:
            try:
                if filesize - send_size > size:
                    socket.send(f.read(size))
                    send_size += size
                else:
                    socket.send(f.read(filesize - send_size))
                    send_size = filesize
            except Exception as e:
                print(e)
                break
            percent = send_size * 100 / filesize
            print("\r%.f%% %s>" % (percent, '=' * int(percent // 10)), end='')


# 接收文件数据
def recv_file_info(file_path, filesize, file_seek, socket, size=1024,mode='wb'):
    recv_file_md5 = hashlib.md5()
    recv_size = file_seek
    with open(file_path, mode) as f:
        f.seek(file_seek)
        while recv_size < filesize:
            try:
                if filesize-recv_size > size:
                    recv_data = socket.recv(size)
                    recv_size += size
                else:
                    recv_data = socket.recv(filesize-recv_size)
                    recv_size = filesize
                if recv_data == b'':break

                f.write(recv_data)
                recv_file_md5.update(recv_data)
                recv_seek = f.tell()
            except Exception as e:
                break
                print(e)
            percent = recv_size * 100 / filesize
            print("\r%.f%% %s>" % (percent, '=' * int(percent // 10)), end='')
        f.close()
    return recv_seek, recv_file_md5.hexdigest()

#更新断点续传文件信息
def update_br_info(type,name,br_info):
    br_file_path = os.path.join(settings.BR_PATH, type, name)
    f = open(br_file_path, 'wb')
    pickle.dump(br_info, f)



