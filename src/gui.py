from tkinter import *
from tkinter import messagebox
import requests
import hashlib
import time
from base64 import b64decode, b64encode
from tkinter.filedialog import askopenfilename
import socket

from audio_management import AudioPlayer, AudioRecorder
from codecs_management import Coder, Decoder
import audio_communication

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
        self.email = None
        self.description = None
        self.contacts = None
        self.on = PhotoImage(file='on.png')
        self.off = PhotoImage(file='off.png')
        self.image = None
        self.contact_image = None
        self.profile_image = None
        self.image_raw = None
        self.calling = False
        self.calling_id = None
        self.root.protocol('WM_DELETE_WINDOW', func=self.close_window)
        self.s1 = None
        self.s2 = None
        self.in_call = False

    def close_window(self):
        r = requests.get(ADDRESS + '/api/sessions', auth = (self.login,self.password))
        if r.ok:
            my_status = r.json()['status']
            if my_status == 'active':
                r = requests.put(ADDRESS + '/api/sessions', params={'status': 'end'}, auth = (self.login,self.password))
        self.delete_pending()
        self.root.destroy()

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

    def update_my_status(self):
        r = requests.get(ADDRESS + '/api/sessions', auth = (self.login,self.password))
        if r.ok:
            my_status = r.json()['status']
            if my_status == 'active':
                r = requests.put(ADDRESS + '/api/sessions', params={'status': 'extend'}, auth = (self.login,self.password))
                if not r.ok:
                    messagebox.showinfo("Uwaga", "Błąd podczas odświeżania statusu")
            else:
                r = requests.post(ADDRESS + '/api/sessions', auth = (self.login,self.password))
                if not r.ok:
                    messagebox.showinfo("Uwaga", "Błąd podczas odświeżania statusu")
        else:
            messagebox.showinfo("Uwaga", "Błąd podczas ładowania statusów użytkowników")
        self.main_frame.after(10000, func = self.update_my_status)

    def reset_frame_main_view(self, frame):
        self.calling = False
        for widget in frame.winfo_children():
            widget.destroy()

    def show_contact_info(self, contact_info, frame):
        self.reset_frame_main_view(frame)

        if contact_info['profile_image']:
            self.contact_image = PhotoImage(format='png', data=contact_info['profile_image'])

            contact_image = Label(frame, image=self.contact_image, width=200, height=200, borderwidth=2, relief='groove')
            contact_image.grid(column=0, row=0, padx=20, pady=20)
            contact_image.grid_propagate(False)
            contact_image.pack_propagate(False)
        else:
            contact_image = Frame(frame, width=200, height=200, borderwidth=2, relief='groove')
            contact_image.grid(column=0, row=0, padx=20, pady=20)
            contact_image.grid_propagate(False)
            contact_image.pack_propagate(False)

        call_button = Button(frame, text='Zadzwoń', command=lambda: self.call(contact_info, frame))
        call_button.grid(column=1, row=0)
        if contact_info['description']:
            contact_description = Label(frame, text= 'Opis: ' + contact_info['description'])
        else:
            contact_description = Label(frame, text= 'Opis: brak')
        contact_description.grid(columnspan=2, row=1)

    CHUNK_SIZE = 4096
    def answer_call(self, host, port1, port2, frame):
        with AudioRecorder(chunk_= self.CHUNK_SIZE) as recorder, AudioPlayer(chunk_= self.CHUNK_SIZE) as player:
            audio_comm= audio_communication.AudioCommunication(audio_communication.Sockets(self.s1, self.s2),
                        audio_communication.Addresses((host, port1), (host, port2)), audio_communication.Audio(recorder, player))
            audio_comm.start()
            self.in_call = True
            frame.after(1000, lambda: self.in_call_(frame, audio_comm))


    def in_call_(self, frame, audio_comm):
        if not self.in_call:
            audio_comm.stop()
        frame.after(1000, lambda: self.in_call_(frame, audio_comm))


    def check_pending_call(self, frame):
        r = requests.get(ADDRESS + '/api/pendingcall', auth = (self.login,self.password))
        if r.ok:
            if r.json():
                info = r.json()
                if self.calling and info['id'] == self.calling_id:
                    self.answer_call(info['host'], info['port'], info['port2'], frame)
                    print('odebrał')
                elif not self.calling:
                    print('mam połączenie')
                    for c in self.contacts:
                        if c['id'] == info['id']:
                            name = info['login']
                    result = messagebox.askquestion('Połączenie', f'Czy chcesz odebrać połączenie od {name}?')
                    if result == 'yes':
                        self.s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.s1.connect(('10.255.255.255', 1))
                        address1 = self.s1.getsockname()
                        print(address1)
                        self.s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.s2.connect(('10.255.255.255', 1))
                        address2 = self.s2.getsockname()
                        print(address2)
                        r = requests.post(ADDRESS + '/api/pendingcall', auth = (self.login,self.password), json={'user_id':info['id'], 'host': address1[0], 'port':address1[1], 'encrypted':False, 'address_port2': address2[1]})
                        self.answer_call(info['host'], info['port'], info['port2'], frame)
                        print('odebralem')
            else:
                frame.after(1000, func = lambda: self.check_pending_call(frame))


    def stop_calling(self, frame):
        self.delete_pending()
        self.reset_frame_main_view(frame)
    def call(self, contact_info, frame):
        self.delete_pending()
        self.reset_frame_main_view(frame)
        self.calling = True
        label_calling = Label(frame, text='calling')
        label_calling.grid()
        self.s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s1.connect(('10.255.255.255', 1))
        address1 = self.s1.getsockname()
        print(address1)
        self.s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s2.connect(('10.255.255.255', 1))
        address2 = self.s2.getsockname()
        print(address2)
        r = requests.post(ADDRESS + '/api/pendingcall', auth = (self.login,self.password), json={'user_id':contact_info['id'], 'host': address1[0], 'port':address1[1], 'encrypted':False, 'address_port2': address2[1]})
        if r.ok:
            self.calling = True
            self.calling_id = contact_info['id']
        #frame.after(15000, func= lambda: self.stop_calling(frame))

    def delete_pending(self):
        r = requests.delete(ADDRESS + '/api/pendingcall', auth = (self.login,self.password))

    def popup_change_password(self):
        popup = Toplevel()
        popup.title('Zmień hasło')
        contact_label = Label(popup, text = 'Wpisz nowe hasło: ', )
        contact_label.grid(column=0, row=0)
        entry = Entry(popup,show='*')
        entry.grid(column=1, row=0)

        buttod_add_contact = Button(popup, text = 'Zmień hasło', command = lambda: self.change_password(popup, entry))
        buttod_add_contact.grid(columnspan=2, row=1)

    def change_password(self, popup, entry):
        password = entry.get()
        if not password:
            messagebox.showinfo("Uwaga", "Wypełnij pole")
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
        encrypted = self.encode_password(password)
        r = requests.put(ADDRESS + '/api/user', json={'email': self.email, 'password':encrypted, 'description': self.description, 'image': self.image_raw}, auth = (self.login,self.password))

        if r.ok:
            messagebox.showinfo("Ok", "Poprawnie zmieniono hasło")
            self.password = encrypted
            popup.destroy()
        else:
            messagebox.showinfo("Uwaga", "Nie udało się zmienić hasła")
            popup.destroy()

    def popup_change_email(self, frame):
        popup = Toplevel()
        popup.title('Zmień email')
        contact_label = Label(popup, text = 'Wpisz nowy email: ', )
        contact_label.grid(column=0, row=0)
        entry = Entry(popup)
        entry.grid(column=1, row=0)

        buttod_add_contact = Button(popup, text = 'Zmień email', command = lambda: self.change_email(popup, entry, frame))
        buttod_add_contact.grid(columnspan=2, row=1)

    def change_email(self, popup, entry, frame):
        email = entry.get()
        if not email:
            messagebox.showinfo("Uwaga", "Wypełnij pole")
            return

        r = requests.put(ADDRESS + '/api/user', json={'email': email, 'password':self.password, 'description': self.description, 'image': self.image_raw}, auth = (self.login,self.password))

        if r.ok:
            messagebox.showinfo("Ok", "Poprawnie zmieniono email")
            self.email = email
            popup.destroy()
            self.show_options(frame)
        else:
            messagebox.showinfo("Uwaga", "Nie udało się zmienić emaila")
            popup.destroy()

    def popup_change_desc(self, frame):
        popup = Toplevel()
        popup.title('Zmień opis')
        contact_label = Label(popup, text = 'Wpisz nowy opis: ', )
        contact_label.grid(column=0, row=0)
        entry = Entry(popup)
        entry.grid(column=1, row=0)

        buttod_add_contact = Button(popup, text = 'Zmień opis', command = lambda: self.change_desc(popup, entry, frame))
        buttod_add_contact.grid(columnspan=2, row=1)

    def change_desc(self, popup, entry, frame):
        desc = entry.get()
        if not desc:
            messagebox.showinfo("Uwaga", "Wypełnij pole")
            return

        r = requests.put(ADDRESS + '/api/user', json={'email': self.email, 'password':self.password, 'description': desc, 'image': self.image_raw}, auth = (self.login,self.password))

        if r.ok:
            messagebox.showinfo("Ok", "Poprawnie zmieniono opis")
            self.description = desc
            popup.destroy()
            self.show_options(frame)
        else:
            messagebox.showinfo("Uwaga", "Nie udało się zmienić opis")
            popup.destroy()

    def popup_change_img(self, frame):
        name = askopenfilename(initialdir="C:/",
                           filetypes =(("PNG", "*.png"),("All Files","*.*")),
                           title = "Choose a file.")
        if not name:
            return

        with open(name, 'rb') as img:
            encoded_img = str(b64encode(img.read()))[2:-1]
        r = requests.put(ADDRESS + '/api/user', json={'email': self.email, 'password':self.password, 'description': self.description, 'image': encoded_img}, auth = (self.login,self.password))
        if r.ok:
            messagebox.showinfo("Ok", "Poprawnie zmieniono obraz")
            self.image_raw = encoded_img
            self.show_options(frame)
        else:
            messagebox.showinfo("Uwaga", "Nie udało się zmienić opis")





    def show_options(self, frame):
        self.reset_frame_main_view(frame)
        r = requests.get(ADDRESS + '/api/user', auth = (self.login,self.password))
        if r.ok:
            info = r.json()
            self.email = info['email']
            label_email = Label(frame, text='Twój email: ' + info['email'])
            if info['description']:
                label_description = Label(frame, text='Twój opis: ' + info['description'])
                self.description = info['description']
            else:
                label_description = Label(frame, text='Twój opis: brak')

            if info['profile_image']:
                self.image_raw = info['profile_image']
                self.profile_image = PhotoImage(format='png', data=info['profile_image'])
                contact_image = Label(frame, image=self.profile_image, width=200, height=200, borderwidth=2, relief='groove')
                contact_image.grid(column=1, row=0, padx=20, pady=5)
                contact_image.grid_propagate(False)
                contact_image.pack_propagate(False)
            else:
                contact_image = Frame(frame, width=200, height=200, borderwidth=2, relief='groove')
                contact_image.grid(column=1, row=0, padx=20, pady=5)
                contact_image.grid_propagate(False)
                contact_image.pack_propagate(False)

            button_image = Button(frame, text='Zmień obraz', command=lambda: self.popup_change_img(frame))
            button_pass = Button(frame, text='Zmień hasło', command=self.popup_change_password)
            button_email = Button(frame, text='Zmień email', command=lambda: self.popup_change_email(frame))
            button_description = Button(frame, text='Zmień opis', command=lambda: self.popup_change_desc(frame))

            label_email.grid(column=1, row=1, pady=(50, 10), padx=60)
            label_description.grid(column=1, row=2, pady=10, padx=60)
            button_pass.grid(column=1, row=3, pady=10, padx=60)
            button_email.grid(column=2, row=1, pady=10)
            button_description.grid(column=2, row=2, pady=10)
            button_image.grid(column=2, row=0)


        else:
            messagebox.showinfo("Uwaga", "Błąd podczas ładowania opcji")


    def main_view(self):
        self.reset_frame()
        self.delete_pending()
        main_field = Frame(self.main_frame, width=400, height=400, borderwidth=2, relief='groove')
        main_field.grid(column=1, row=1, rowspan=10, pady=20, padx=(0,20))
        main_field.grid_propagate(False)
        main_field.pack_propagate(False)
        options_bar = Frame(self.main_frame)
        options_bar.grid(row=0, column=0, columnspan=2)
        options_button = Button(options_bar, text='Opcje', command = lambda: self.show_options(main_field))
        options_button.pack(side=RIGHT)
        refresh_button = Button(options_bar, text='Odśwież', command = self.main_view)
        refresh_button.pack(side=LEFT)
        w_contacts = Frame(self.main_frame, borderwidth=2, relief='groove')
        w_contacts.grid(row=1, column=0, padx=20, pady=20)
        contacts_label = Label(w_contacts, text='Kontakty', borderwidth=2, relief='groove')
        contacts_label.grid(row=0, column=0, padx=20, pady=10)
        contacts_frame = Frame(w_contacts)
        contacts_frame.grid(row=1, column=0, pady=(0,10))
        add_contact_button = Button(w_contacts, text='Dodaj kontakt', command = self.popup_add_contact)
        add_contact_button.grid(row=2, column=0, pady=(0,10))



        self.update_my_status()
        r = requests.get(ADDRESS + '/api/contacts', auth = (self.login,self.password))
        if r.ok:
            self.contacts = r.json()
        else:
            self.contacts = []

        for i, contact in enumerate(self.contacts):
            contact_button = Button(contacts_frame, text=contact['login'], command = lambda: self.show_contact_info(contact, main_field))
            contact_button.grid(row = i, column = 1, pady=10, padx=5)
            delete_button = Button(contacts_frame, text = 'x', fg='red', command=lambda: self.delete_contact(contact['login']))
            delete_button.grid(row = i, column = 2, padx=(0,10))
            status_label = Label(contacts_frame, image=self.off)
            status_label.grid(row=i, column=0)
            self.update_contact_status(contact['id'], status_label)

        self.check_invitations(main_field)
        self.check_pending_call(main_field)

    def check_invitations(self, field):
        r = requests.get(ADDRESS + '/api/invitations',  auth = (self.login,self.password))
        if r.ok:
            invitations = r.json()
        else:
            invitations = []
        for i in invitations['rejected_invitations']:
            messagebox.showinfo("Uwaga", f"Użytkownik {i['login']} odrzucił twoje zaproszenie")

        for i in invitations['my_invitations']:
            self.invitation_popup(i['login'], i['invitation_id'])

        field.after(5000, func= lambda: self.check_invitations(field))

    def update_contact_status(self, contact_id, status_label):
        r = requests.get(ADDRESS + '/api/sessions', params={'user_id': contact_id}, auth = (self.login,self.password))
        if r.ok:
            status = r.json()['status']
            if status == 'active':
                status_image = self.on
            else:
                status_image = self.off
        else:
            messagebox.showinfo("Uwaga", "Błąd podczas ładowania statusów użytkowników")

        status_label.configure(image = status_image)
        status_label.after(5000, func= lambda: self.update_contact_status(contact_id, status_label))

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