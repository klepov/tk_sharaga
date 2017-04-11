from tkinter import *

from model import MaskEqualsPassword
from presenter import Presenter


class Gui():
    def __init__(self, root):
        self.presenter = Presenter()
        self.root = root
        self.__set_view_center(self.root)
        self.root.resizable(False, False)

    def login(self):
        self.__login_form()

    def __login_form(self):
        self.errors_count = 0
        self.root.withdraw()
        self.login_frame = self.__create_modal_view()
        Label(self.login_frame, text='логин:').grid(column=1, row=1)
        self.login = Entry(self.login_frame)
        self.login.grid(column=2, row=1)
        Label(self.login_frame, text='пароль:').grid(column=1, row=2)
        self.passwd = Entry(self.login_frame, show="*")
        self.passwd.grid(column=2, row=2)
        self.passwd_btn = Button(self.login_frame, text="войти", command=self.__make_login)
        self.passwd_btn.grid(column=2, row=3)

    def make_menu_admin(self):
        main_menu = Menu(self.root)
        # ------------------------------------------------------------------
        head_menu = Menu(main_menu, tearoff=0)
        head_menu.add_command(label="Новый пользователь", command=self.__reg_user_view)
        head_menu.add_command(label="Выйти", command=self.root.destroy)
        main_menu.add_cascade(label="Главное", menu=head_menu)
        # ------------------------------------------------------------------
        change_menu = Menu(main_menu, tearoff=0)
        change_menu.add_command(label="Свой пароль", command=self.__change_password_view)
        main_menu.add_cascade(label="Изменить", menu=change_menu)
        # ------------------------------------------------------------------

        self.root.config(menu=main_menu)

    def __inflate_list_box(self):
        self.user_list_box = Listbox(selectmode=SINGLE)
        self.user_list_box.pack(side='top', fill='x')
        for user in self.presenter.get_users():
            self.user_list_box.insert(END, user)

    # region view
    def __load_main_view(self):
        self.__inflate_list_box()
        Button(text="Редактировать", command=self.__edit_user).pack(side='right')
        Button(text="Удалить", command=self.__delete_user).pack(side='left')

    def __create_new_password_view(self):
        self.password_form = self.__create_modal_view()
        Label(self.password_form, text="Новый пароль").grid(row=2, column=1)
        self.new_pass = Entry(self.password_form, show="*")
        self.new_pass.grid(row=2, column=2)
        Button(self.password_form, command=self.__change_password, text="Сменить").grid(row=3, column=2)

    def __change_password_view(self):
        self.password_form = self.__create_modal_view()
        Label(self.password_form, text="Старый пароль").grid(row=1, column=1)
        self.old_pass = Entry(self.password_form, show="*")
        self.old_pass.grid(row=1, column=2)
        Label(self.password_form, text="Новый пароль").grid(row=2, column=1)
        self.new_pass = Entry(self.password_form, show="*")
        self.new_pass.grid(row=2, column=2)
        Button(self.password_form, command=self.__change_password, text="Сменить").grid(row=3, column=2)

    def __reg_user_view(self):
        self.create_user = self.__create_modal_view()
        Label(self.create_user, text="Логин:").grid(row=1, column=1)
        self.login = Entry(self.create_user)
        self.login.grid(row=1, column=2)
        Button(self.create_user, command=self.__reg_user, text="Зарегистрировать").grid(row=2, column=2)

    #     region listener
    def __reg_user(self):
        login = self.login.get()
        if login == '':
            self.dialog_fragment("Пустой логин")
            return
        if self.presenter.reg_user(self.login.get()):
            self.create_user.destroy()
            self.user_list_box.insert(END, login)
        else:
            self.dialog_fragment("Пользователь уже существует")

    def __edit_user(self):
        selected_items = self.user_list_box.curselection()
        if selected_items and len(selected_items) > 0:
            selected = selected_items[0]
        else:
            return
        self.__edit_admin(self.user_list_box.get(selected))

    def __delete_user(self):
        selected_items = self.user_list_box.curselection()
        if selected_items and len(selected_items) > 0:
            selected = selected_items[0]
        else:
            return
        if self.presenter.delete_user(self.user_list_box.get(selected)):
            self.user_list_box.delete(selected)

    def __edit_admin(self, param):
        self.selected_user = param
        self.is_blocked_user_admin = IntVar()
        self.is_blocked_user_admin.set(0)
        self.edit_frame = self.__create_modal_view()
        Label(self.edit_frame, text="Блокировка:").grid(row=1, column=1)
        self.block_checkbox = Checkbutton(self.edit_frame, variable=self.is_blocked_user_admin, onvalue=1, offvalue=0)
        self.block_checkbox.grid(row=1, column=2)
        Label(self.edit_frame, text="Паттерн пароля:").grid(row=2, column=1)
        self.pattern_passwd = Entry(self.edit_frame)
        self.pattern_passwd.grid(row=2, column=2)
        Button(self.edit_frame, text="Применить", command=self.__save_result).grid(row=3, column=2)

    def __save_result(self):
        if self.presenter.set_state(self.selected_user,
                                    self.pattern_passwd.get(),
                                    self.is_blocked_user_admin.get()):
            self.edit_frame.destroy()
        else:
            self.dialog_fragment('Ошибка')

    def __make_login(self):
        user = self.presenter.login(self.login.get(), self.passwd.get())
        type_user = type(user)
        if self.errors_count >= 3:
            self.dialog_fragment("заблокирован")
            return
        if type_user is str:
            if user == "Вводи пароль":
                self.name_user = self.login.get()
                self.__create_new_password_view()
                return
            self.dialog_fragment(user)
            self.errors_count += 1
        else:
            errors_count = 0
            self.login_frame.destroy()
            self.root.update()
            self.root.deiconify()
            self.__load_main_view()
            self.user = user

    def __change_password(self):
        try:
            result = self.presenter.change_pass(self.user, self.old_pass.get(), self.new_pass.get())
            if result:
                self.password_form.destroy()
            else:
                self.dialog_fragment('Пароль не совпадает с прошлым')

        except AttributeError:
            try:
                result = self.presenter.create_password(self.name_user, self.new_pass.get())
                if result:
                    self.password_form.destroy()
                else:
                    self.dialog_fragment('Пароль не совпадает с прошлым')
            except MaskEqualsPassword:
                self.dialog_fragment('Пароль совпадает маской. Придумай новый пароль')
        except MaskEqualsPassword:
            self.dialog_fragment('Пароль совпадает маской. Придумай новый пароль')

    # region custom view
    def dialog_fragment(self, message):
        self.dialog_form = self.__create_modal_view()
        w = self.dialog_form.winfo_screenwidth()
        h = self.dialog_form.winfo_screenheight()
        size = tuple(int(_) for _ in self.dialog_form.geometry().split('+')[0].split('x'))
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        self.dialog_form.geometry("+{}+{}".format(int(x), int(y)))
        Label(self.dialog_form, text=message).grid(column=1, row=1)
        Button(self.dialog_form, text='ok', command=self.dialog_form.destroy).grid(column=1, row=2)

    def __create_modal_view(self):
        dialog_form = Toplevel()
        self.__set_view_center(dialog_form)
        return dialog_form

    def __set_view_center(self, toplevel):
        w = toplevel.winfo_screenwidth()
        h = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        toplevel.geometry("+{}+{}".format(int(x), int(y)))


root = Tk()
g = Gui(root)
g.login()
g.make_menu_admin()

root.mainloop()
