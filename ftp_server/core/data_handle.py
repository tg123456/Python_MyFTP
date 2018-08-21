
import os
import pickle

class Data_handle:

    #清空文件内容
    def clear_file_content(self,filename):
        data_path = os.path.join(os.path.dirname(os.getcwd()), 'db', filename)
        with open(data_path,'wb') as f:
            f.write(b'')

    #查询信息
    def select_data(self,filename):
        data_path = os.path.join(os.path.dirname(os.getcwd()), 'db', filename)
        if os.path.getsize(data_path):
            f = open(data_path, 'rb')
            try:
                data_info = pickle.load(f)
                return data_info
            except Exception as e:
                print(e)
            finally:
                f.close()
        else:
            return {}

    #保存信息
    def save_data(self,person_info_dic,filename):
        person_info_file = os.path.join(os.path.dirname(os.getcwd()), 'db', filename)
        f = open(person_info_file, 'wb')
        try:
            pickle.dump(person_info_dic, f)
        except Exception as e:
            print(e)
        finally:
            f.close()

# t = Data_handle()
# t.clear_file_content('person_login_info')



