class Person:
    def __init__(self, user_id, name, passwd, age, sex, phone, type):
        self.user_id = user_id
        self.name = name
        self.passwd = passwd
        self.age = age
        self.sex = sex
        self.phone = phone
        self.type = type


class Manager(Person):
    def __init__(self, user_id, name, passwd, age, sex, phone, type='manager'):
        super().__init__(user_id, name, passwd, age, sex, phone, type)

    def get_info(self):
        info_str = {"user_id": self.user_id, "name": self.name, "age": self.age, "sex": self.sex, "phone": self.phone, "type": self.type,
                    'passwd': self.passwd}
        return info_str


class Member(Person):
    """
    会员：普通会员：normal 黄金会员：gold
    """

    def __init__(self, user_id, name, passwd, age, sex, phone, account=100, type='member', level='normal',
                 storage_space=100):
        super().__init__(user_id, name, passwd, age, sex, phone, type)
        self.level = level
        self.account = account
        self.storage_space = storage_space

    def get_info(self):
        info_str = {"user_id": self.user_id, "name": self.name, "age": self.age, "sex": self.sex, "phone": self.phone,
                    "type": self.type, "account": self.account, "level": self.level, 'passwd': self.passwd,
                    'storage_space': self.storage_space}
        return info_str
