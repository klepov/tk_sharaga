import re
from peewee import DoesNotExist, IntegrityError

from encrypt import crypt
from model import User, MaskEqualsPassword


class Presenter():
    def __init__(self):
        admin = User.select().where(User.name == 'admin').count()
        if admin == 0:
            User.create(is_granted=True,
                        is_blocked=False,
                        mask_password="",
                        name='admin',
                        password=crypt('admin')).save()

    def login(self, login, password):
        user = self.__get_by_name(login)
        if user:
            if not user.password:
                return "Вводи пароль"
            if user.password == crypt(password):
                if user.is_blocked:
                    return "заблокирован"
                return user
            else:
                return "не найден"
        return "не найден"

    def __get_by_name(self, name):
        try:
            return User.select().where(User.name == name).get()
        except DoesNotExist:
            return None

    def change_pass(self, user, old_pass, new_pass):
        var_reg = r'[a-z]|[,.!?;:()]'
        var_reg_k = r'[a-z]|[,.!?;:()]|[0-9]'
        if user.password == crypt(old_pass):
            if user.mask_password:
                var_reg = user.mask_password
            if re.search(var_reg, new_pass):
                raise MaskEqualsPassword(Exception)
            user.password = crypt(new_pass)
            user.save()
            return True
        else:
            return False

    def create_password(self, user, new_pass):
        var_reg = r'[a-z]|[,.!?;:()]'
        user = self.__get_by_name(user)
        if user.mask_password:
            var_reg = user.mask_password
        if re.search(var_reg, new_pass):
            raise MaskEqualsPassword(Exception)
        user.password = crypt(new_pass)
        user.save()
        return True

    def set_state(self, selected_user, pattern, block):
        user = self.__get_by_name(selected_user)
        if user:
            user.is_blocked = block
            user.mask_password = pattern
            user.save()
            return True
        else:
            return False

    def get_users(self):
        users = []
        for user in User.select():
            if user.name == 'admin':
                continue
            users.append(user.name)
        return users

    def delete_user(self, param):
        user = self.__get_by_name(param)
        if user:
            user.delete_instance()
            return True

    def reg_user(self, param):
        try:
            user = User.create(name=param,
                               is_granted=0,
                               is_blocked=0,
                               mask_password="",
                               password="")
            user.save()
            return True
        except IntegrityError:
            return False
