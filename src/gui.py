from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from pytler import Pytler

#TODO tworzenie i odświeżanie sesji

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

    def create_button(self, text, master, action= None, height=80, width=120, side=LEFT, pady=(0,0), padx=(0,0), bg='white', fg='black'):
        f = Frame(master=master, height=height, width=width)
        f.pack_propagate(0)
        f.pack(side=side, padx=padx, pady=pady)
        return Button(master=f, text=text, command=action, bg=bg, fg=fg, font=self.font)

    def create_entry(self, master, height=40, width=120, side=LEFT, pady=(0,0), padx=(0,0), bg='white', fg='black'):
        f = Frame(master=master, height=height, width=width)
        f.pack_propagate(0)
        f.pack(side=side, padx=padx, pady=pady)
        return Entry(master=f, bg=bg, fg=fg)

    def create_label(self, text, master, height=40, width=130, side=LEFT, pady=(0,0), padx=(0,0), bg='white', fg='black'):
        f = Frame(master=master, height=height, width=width)
        f.pack_propagate(0)
        f.pack(side=side, padx=padx, pady=pady)
        return Label(master=f, text=text, bg=bg, fg=fg, font=self.font)

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
        self.root.geometry('1000x500')


        contact_frame = Frame(master=self.back, bg='black', height=500, width=200)
        contact_frame.pack_propagate(0)
        contact_frame.pack(side=LEFT)

        main_frame = Frame(master=self.back, bg='green', height=500, width=800)
        main_frame.pack_propagate(0)
        main_frame.pack(side=LEFT)

        self.generate_contacts(contact_frame)

        menu_frame = Frame(master=main_frame, bg='black', width=800, height=70)
        menu_frame.pack_propagate(0)
        menu_frame.pack()

        self.generate_topbar_content(menu_frame)

        content_frame = Frame(master=main_frame, bg='blue', width=800, height=350)
        content_frame.pack_propagate(0)
        content_frame.pack()

        action_bar = Frame(master=main_frame, bg='green', width=800, height=80)
        action_bar.pack_propagate(0)
        action_bar.pack()

    def generate_contacts(self, root):
        r = self.pytler.get_contacts()
        if not r:
            messagebox.showwarning('Błąd', 'Błąd podczas wczytywania kontaktów')

        frame = Frame(master=root, bg='black')
        frame.pack()
        label = self.create_label('Kontakty', frame, width = 200, pady=(20,0), fg='white', bg='black')
        label.pack(fill=BOTH, expand=1, side=TOP)

        frame2 = Frame(master=root, bg='black', height=350, width=200)
        frame2.pack(pady=10)
        frame2.pack_propagate(0)
        scrollbar = Scrollbar(frame2)
        scrollbar.pack(fill=BOTH, expand=1, side=RIGHT)
        contact_list = Listbox(frame2, yscrollcommand = scrollbar.set, width= 180, bg='black', font=self.font, fg='white')
        contact_list.insert(END, 'login')
        if self.pytler.contacts:
            for contact in self.pytler.contacts:
                contact_list.insert(END, contact['login'])
        contact_list.pack( side = LEFT, fill = BOTH )

        contact_list.bind('<<ListboxSelect>>', lambda evt: self.onselect(evt, 1))

        frame1 = Frame(master=root, bg='black')
        frame1.pack()
        add_button = self.create_button('Dodaj kontakt +', frame1, width = 150, height=60, fg='black', bg='white')
        add_button.pack(fill=BOTH, expand=1, side=TOP)

    def generate_topbar_content(self, topbar):

        home = self.create_button('Strona główna', topbar, padx=(300,20), height=50)
        home.pack(fill=BOTH, expand=1, side=RIGHT)

        settings = self.create_button('Ustawienia', topbar, padx=(20,20), height=50)
        settings.pack(fill=BOTH, expand=1, side=RIGHT)

        logout = self.create_button('Wyloguj', topbar, padx=(20,20), height=50)
        logout.pack(fill=BOTH, expand=1, side=RIGHT)

    def onselect(self, evt, a):
        #TODO wyświetlanie info
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        print('You selected item %d: "%s"' % (index, value))




    def main(self):
        self.view_login_or_register()

        self.root.mainloop()

GUI().main()

