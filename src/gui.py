from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from pytler import Pytler

class GUI:
    def __init__(self):
        self.font = ('helvetica', 13, 'bold')

        self.root = Tk()
        self.root.title('Pytler')
        self.root.resizable(0, 0)
        self.root.pack_propagate(0)
        self.root.geometry("500x500")
        self.back = Frame(master=self.root, bg='black')
        self.back.pack_propagate(0)
        self.back.pack(fill=BOTH, expand=1)
        self.pytler = Pytler()

    def reset_back(self):
        self.back.destroy()
        self.back = Frame(master=self.root, bg='black')
        self.back.pack_propagate(0)
        self.back.pack(fill=BOTH, expand=1)

    def view_login_or_register(self):
        self.reset_back()
        self.root.geometry('340x200')
        login_button = self.create_button('Zaloguj', self.back, padx=(40,20), action=self.view_login)


        register_button = self.create_button('Zarejestruj', self.back, action=self.view_register)

        login_button.config()
        login_button.pack(fill=BOTH, expand=1, side=LEFT)
        register_button.pack(fill=BOTH, expand=1, side=LEFT)

    def create_button(self, text, master, action= None, height=80, width=120, side=LEFT, pady=(0,0), padx=(0,0)):
        f = Frame(master=master, height=height, width=width)
        f.pack_propagate(0)
        f.pack(side=side, padx=padx, pady=pady)
        return Button(master=f, text=text, command=action, bg='white', fg='black', font=self.font)

    def create_entry(self, master, height=40, width=120, side=LEFT, pady=(0,0), padx=(0,0)):
        f = Frame(master=master, height=height, width=width)
        f.pack_propagate(0)
        f.pack(side=side, padx=padx, pady=pady)
        return Entry(master=f, bg='white', fg='black')

    def create_label(self, text, master, height=40, width=130, side=LEFT, pady=(0,0), padx=(0,0)):
        f = Frame(master=master, height=height, width=width)
        f.pack_propagate(0)
        f.pack(side=side, padx=padx, pady=pady)
        return Label(master=f, text=text, bg='white', fg='black')

    def view_register(self):
        self.reset_back()
        self.root.geometry('340x460')

        login_entry = self.create_row_reg('Login')
        pass_entry = self.create_row_reg('Hasło')
        pass_entry.config(show='*')
        conf_entry = self.create_row_reg('Potwierdź hasło')
        conf_entry.config(show='*')
        email_entry = self.create_row_reg('Email')

        frame = Frame(master=self.back, bg='black', pady=20)
        frame.pack()
        accept_button = self.create_button('Zarejestruj', frame, action= lambda:self.register(login_entry.get(), pass_entry.get(), conf_entry.get(), email_entry.get()))
        accept_button.pack(fill=BOTH, expand=1)


    def register(self, login, password, confirm, email):
        if not login or not password or not confirm or not email:
            messagebox.showwarning('Błąd', 'Nie wszystkie pola zostały wypełnione')
            return

        if not self.check_password(password):
            messagebox.showwarning('Błąd', 'Hasło powinno mieć co najmniej 8 znaków długości oraz zawierać minimum jedną cyfrę, jedną małą literę oraz jedną wielką literę')
            return

        if password!=confirm:
            messagebox.showwarning('Błąd', 'Hasło oraz potwierdzone hasło muszą być identyczne')
            return

        r = self.pytler.register_user(login, password, email)
        if not r:
            messagebox.showwarning('Błąd', 'Login lub email są już w użyciu')
            return
        else:
            messagebox.showinfo('Gratulacje', f'Poprawnie zarejestrowano użytkownika {login}\nToken aktywacyjny został wysłany na email {email}')
            self.view_login_or_register()


    def check_password(self, password):
        upper = False
        lower = False
        digit = False
        long = False
        for letter in password:
            if letter.isupper():
                upper = True
            elif letter.islower():
                lower = True
            elif letter.isdigit():
                digit = True
            if upper and lower and digit:
                break
        if len(password) >= 8:
            long = True
        if not long or not digit or not lower or not upper:
            return False
        else:
            return True

    def create_row_reg(self, text):
        frame = Frame(master=self.back, bg='black', pady=20)
        frame.pack()
        label = self.create_label(text, frame, padx=(20,10))
        entry = self.create_entry(frame, padx=(10,20))
        label.config(font=self.font)
        entry.config(font=self.font)
        label.pack(fill=BOTH, expand=1)
        entry.pack(fill=BOTH, expand=1)

        return entry

    def view_login(self):
        self.reset_back()
        self.root.geometry('340x260')

        login_entry = self.create_row_reg('Login')
        pass_entry = self.create_row_reg('Hasło')
        pass_entry.config(show='*')
        frame = Frame(master=self.back, bg='black', pady=20)
        frame.pack()
        accept_button = self.create_button('Zaloguj', frame, action= lambda:self.login(login_entry.get(), pass_entry.get()))
        accept_button.pack(fill=BOTH, expand=1)

    def login(self, login, password):
        if not login or not password:
            messagebox.showwarning('Błąd', 'Nie wszystkie pola zostały wypełnione')
            return

        r = self.pytler.login(login, password)
        if r:
            r = self.pytler.get_user_info()
            if r:
                if self.pytler.activated:
                    self.main_view()
                else:
                    messagebox.showwarning('Uwaga', 'Konto nie zostało jeszcze aktywowane - prosimy o podanie tokenu aktywacyjnego z wiadomości email')
                    self.view_activation()
            else:
                messagebox.showwarning('Błąd', 'Błąd podczas pobierania danych użytkownika')
                return
        else:
            messagebox.showwarning('Błąd', 'Podano nieprawidłowy login lub hasło')
            return

    def view_activation(self):
        self.reset_back()
        self.root.geometry('340x160')

        token_entry = self.create_row_reg('Token')
        frame = Frame(master=self.back, bg='black', pady=20)
        frame.pack()
        accept_button = self.create_button('Aktywuj', frame, action= lambda:self.activate(token_entry.get()))
        accept_button.pack(fill=BOTH, expand=1)

    def activate(self, token):
        if not token:
            messagebox.showwarning('Błąd', 'Proszę uzupełnić pole tokenem aktywacyjnym z wiadomości email')
            return
        else:
            r = self.pytler.activate_account(token.strip())
            if not r:
                messagebox.showwarning('Błąd', 'Token aktywacyjny nie jest poprawny - spróbuj ponownie')
                return
            else:
                messagebox.showwarning('Gratulacje', 'Konto zostało pomyślnie aktywowane')
                self.main_view()

    def main_view(self):
        self.reset_back()
        self.root.geometry('340x160')


    def main(self):
        self.view_login_or_register()

        self.root.mainloop()

GUI().main()

