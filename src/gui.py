from tkinter import *
from tkinter import messagebox
import requests
import hashlib

ADDRESS = 'http://127.0.0.1:8080'

class GUI:

    def __init__(self):
        self.root = Tk()
        self.root.title('Pytler')
        self.main_frame = Frame(self.root)
        self.main_frame.grid()
        self.auth_token = None
        self.login = None
        self.password = None
        self.contacts = None
    def choose_login_register(self):
        self.reset_frame()
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
        password_entry = Entry(self.main_frame, bd=5, show='*')
        password_entry.grid(row=1, column=1)

        login_button = Button(self.main_frame, text = 'Zaloguj', command = lambda: self.login_(login_entry, password_entry))
        login_button.grid(row=2, columnspan=2)

    def login_(self, login_entry, password_entry):
        login = login_entry.get()
        password = password_entry.get()
        if not login or not password:
            messagebox.showinfo("Uwaga", "Co najmniej jedno z pól nie zostało wypełnione")
            return
        encoded_password = self.encode_password(password)
        r = requests.get(ADDRESS + '/api/auth', params={'login': login, 'password': encoded_password})
        if r.ok:
            self.auth_token = r.json()['auth_token']
            self.login = login
            self.password = encoded_password
            self.main_view()
        else:
            messagebox.showinfo("Uwaga", "Wpisano niepoprawny login i/lub hasło")

    #----
    def register_frame(self):
        self.reset_frame()
        login_label = Label(self.main_frame, text = 'Login')
        login_label.grid(row=0, column=0)
        login_entry = Entry(self.main_frame, bd=5)
        login_entry.grid(row=0, column=1)

        password_label = Label(self.main_frame, text = 'Hasło')
        password_label.grid(row=1, column=0)
        password_entry = Entry(self.main_frame, bd=5, show='*')
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
        encoded = self.encode_password(password)
        response = requests.post(ADDRESS + '/api/auth', json={'login': login, 'password': encoded, 'email': email})
        if not response.ok:
            messagebox.showinfo("Uwaga", "Login lub email już jest w użyciu")
            return
        else:
            self.choose_login_register()
    #----
    def popup_add_contact(self):
        popup = Toplevel()
        popup.title('Dodaj kontakt')
        contact_label = Label(popup, text = 'Wpisz nazwę kontaktu: ')
        contact_label.grid(column=0, row=0)
        contact_add_entry = Entry(popup)
        contact_add_entry.grid(column=1, row=0)

        buttod_add_contact = Button(popup, text = 'Wyślij zaproszenie', command = lambda: self.send_invitation(popup, contact_add_entry))
        buttod_add_contact.grid(columnspan=2, row=1)

    def send_invitation(self, popup_to_close, entry):
        contact_login = entry.get()
        if not contact_login:
            messagebox.showinfo("Uwaga", "Wpisz nazwę użytkownika!")
            return
        response = requests.post(ADDRESS + '/api/contacts', params={'contact_login': contact_login},  auth = (self.login,self.password))
        if response.ok:
            messagebox.showinfo("Ok", "Zaproszenie zostało wysłane")
            popup_to_close.destroy()
        else:
            messagebox.showinfo("Uwaga", "Użytkownik o podanym loginie nie istnieje")


    def main_view(self):
        self.reset_frame()
        contacts_label = Label(self.main_frame, text='Kontakty')
        contacts_label.grid(row=0, column=0)
        contacts_frame = Frame(self.main_frame)
        contacts_frame.grid(row=1, column=0)
        add_contact_button = Button(self.main_frame, text='Dodaj kontakt', command = self.popup_add_contact)
        add_contact_button.grid(row=2, column=0)
        r = requests.get(ADDRESS + '/api/contacts', auth = (self.login,self.password))
        if r.ok:
            self.contacts = r.json()
        else:
            self.contacts = []

        for i, contact in enumerate(self.contacts):
            contact_button = Button(contacts_frame, text=contact['login'])
            contact_button.grid(row = i, column = 0)
            delete_button = Button(contacts_frame, text = 'x', fg='red', command=lambda: self.delete_contact(contact['login']))
            delete_button.grid(row = i, column = 1)

        r = requests.get(ADDRESS + '/api/invitations',  auth = (self.login,self.password))
        if r.ok:
            invitations = r.json()
        else:
            invitations = []


        for i in invitations['rejected_invitations']:
            messagebox.showinfo("Uwaga", f"Użytkownik {i['login']} odrzucił twoje zaproszenie")

        for i in invitations['my_invitations']:
            self.invitation_popup(i['login'], i['invitation_id'])


    def invitation_popup(self, login, invitation_id):
        popup = Toplevel()
        popup.title('Zaproszenie')

        invitation_label = Label(popup, text=f'Masz zaproszenie do znajomych od użytkownika {login}')
        invitation_label.grid(column=0, row=0, columnspan=2)

        accept_button = Button(popup, text='Akceptuj', command = lambda: self.accept_contact(invitation_id, popup))
        accept_button.grid(column=0, row=1)

        reject_button = Button(popup, text='Odrzuć', command = lambda: self.reject_contact(invitation_id, popup))
        reject_button.grid(column=1, row=1)

    def accept_contact(self, invitation_id, popup):
        r = requests.put(ADDRESS + '/api/invitations', params={'invitation_id': invitation_id, 'action': 'accept'},  auth = (self.login,self.password))
        if r.ok:
            messagebox.showinfo("Ok", "Zaproszenie zostało zaakceptowane")
            popup.destroy()
            self.main_view()
        else:
            messagebox.showinfo("Ups", "Coś poszło nie tak")
            popup.destroy()
            self.main_view()

    def reject_contact(self, invitation_id, popup):
        r = requests.put(ADDRESS + '/api/invitations', params={'invitation_id': invitation_id, 'action': 'reject'},  auth = (self.login,self.password))
        if r.ok:
            messagebox.showinfo("Ok", "Zaproszenie zostało odrzucone")
            popup.destroy()
            self.main_view()
        else:
            messagebox.showinfo("Ups", "Coś poszło nie tak")
            popup.destroy()
            self.main_view()


    def delete_contact(self, contact_login):
        r = requests.delete(ADDRESS + '/api/contacts', auth = (self.login,self.password), params= {'contact_login': contact_login})
        if r.ok:
            messagebox.showinfo("Ok", "Kontakt został pomyślnie usunięty")
            self.main_view()
        else:
            messagebox.showinfo("Uwaga", "Nie udało się usunąć kontaktu")
            self.main_view()



    def encode_password(self, password):
        return str(hashlib.sha256(password.encode()).hexdigest())

    def reset_frame(self):
        self.main_frame.destroy()
        self.main_frame = Frame(self.root)
        self.main_frame.pack()

    def main(self):
        self.choose_login_register()
        self.root.mainloop()

if __name__ == '__main__':
    GUI().main()