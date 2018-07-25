from tkinter import *
from tkinter import messagebox
import requests
class GUI:

    def __init__(self):
        self.root = Tk()
        self.main_frame = Frame(self.root)
        self.main_frame.grid()
    def choose_login_register(self):
        login_button = Button(self.main_frame, text = 'Zaloguj', command = self.login_frame)
        login_button.pack(side=LEFT, pady = 20, padx = 20)

        register_button = Button(self.main_frame, text = 'Zarejestruj', command = self.register_frame)
        register_button.pack(side=LEFT, pady = 20, padx = 20)

    #----
    def login_frame(self):
        self.reset_frame()
        login_label = Label(self.main_frame, text = 'Login')
        login_label.grid(row=0, column=0)
        login_entry = Entry(self.main_frame, bd=5)
        login_entry.grid(row=0, column=1)

        password_label = Label(self.main_frame, text = 'Hasło')
        password_label.grid(row=1, column=0)
        password_entry = Entry(self.main_frame, bd=5)
        password_entry.grid(row=1, column=1)

        login_button = Button(self.main_frame, text = 'Zaloguj')
        login_button.grid(row=2, columnspan=2)

    #----
    def register_frame(self):
        self.reset_frame()
        login_label = Label(self.main_frame, text = 'Login')
        login_label.grid(row=0, column=0)
        login_entry = Entry(self.main_frame, bd=5)
        login_entry.grid(row=0, column=1)

        password_label = Label(self.main_frame, text = 'Hasło')
        password_label.grid(row=1, column=0)
        password_entry = Entry(self.main_frame, bd=5)
        password_entry.grid(row=1, column=1)

        email_label = Label(self.main_frame, text = 'Email')
        email_label.grid(row=2, column=0)
        email_entry = Entry(self.main_frame, bd=5)
        email_entry.grid(row=2, column=1)

        login_button = Button(self.main_frame, text = 'Zarejestruj', command = lambda: self.register(login_entry, password_entry, email_entry))
        login_button.grid(row=3, columnspan=2)

    def register(self, login_entry, password_entry, email_entry):
        login = login_entry.get()
        password = password_entry.get()
        email = email_entry.get()
        if not login or not password or not email:
            messagebox.showinfo("Uwaga", "Co najmniej jedno z pól nie zostało wypełnione")
            return

        if len(password) < 8:
            messagebox.showinfo("Uwaga", "Hasło powinno mieć co najmniej 8 znaków")
            return

        upper = False
        lower = False
        digit = False

        for letter in password:
            if letter.isupper():
                upper = True
            elif letter.islower():
                lower = True
            elif letter.isdigit():
                digit = True

            if upper and lower and digit:
                break

        if not upper or not lower:
            messagebox.showinfo("Uwaga", "Hasło powinno mieć co najmniej jedną wielką literę oraz jedną małą literę")
            return
        if not digit:
            messagebox.showinfo("Uwaga", "Hasło powinno mieć co najmniej jedną cyfrę")
            return
    #----
    def reset_frame(self):
        self.main_frame.destroy()
        self.main_frame = Frame(self.root)
        self.main_frame.pack()

    def main(self):
        self.choose_login_register()
        self.root.mainloop()

if __name__ == '__main__':
    GUI().main()