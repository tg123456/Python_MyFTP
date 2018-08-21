
class Person:
    def __init__(self,user_id,name,age,sex,phone,type):
        self.user_id = user_id
        self.name = name
        self,age = age
        self.sex = sex
        self.phone = phone
        self.type = type

class Manager(Person):
    def __init__(self,user_id,name,age,sex,phone,type='manager'):
        super().__init__(user_id,name,age,sex,phone,type)


class Member(Person):
    """
    会员：普通会员：normal 黄金会员：gold
    """
    def __init__(self,user_id,name,age,sex,phone,account=100,type='member',level='normal'):
        super().__init__(user_id,name,age,sex,phone,type)
        self.level = level
        self.account = account




