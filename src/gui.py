from tkinter import *

class GUI:

    def __init__(self):
        self.root = Tk()
        self.main_frame = Frame(self.root)
        self.main_frame.grid()
    def choose_login_register(self):
        login_button = Button(self.main_frame, text = 'Zaloguj', command = self.login)
        login_button.pack(side=LEFT, pady = 20, padx = 20)

        register_button = Button(self.main_frame, text = 'Zarejestruj', command = self.register)
        register_button.pack(side=LEFT, pady = 20, padx = 20)

    #----
    def login(self):
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
    def register(self):
        self.reset_frame()
        login_label = Label(self.main_frame, text = 'Login')
        login_label.grid(row=0, column=0)
        login_entry = Entry(self.main_frame, bd=5)
        login_entry.grid(row=0, column=1)

        password_label = Label(self.main_frame, text = 'Hasło')
        password_label.grid(row=1, column=0)
        password_entry = Entry(self.main_frame, bd=5)
        password_entry.grid(row=1, column=1)

        password_label = Label(self.main_frame, text = 'Email')
        password_label.grid(row=2, column=0)
        password_entry = Entry(self.main_frame, bd=5)
        password_entry.grid(row=2, column=1)

        login_button = Button(self.main_frame, text = 'Zarejestruj')
        login_button.grid(row=3, columnspan=2)

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