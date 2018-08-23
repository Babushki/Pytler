from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from pytler import Pytler
import time
import re
import cv2
from base64 import b64encode, b64decode


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
        self.logged = False
        self.update_session()
        self.settings = None
        self.calling_id = None
        self.calling = False
        self.in_call = False
        self.check_incoming_calls()
        self.call_session = False
        self.profile_image = None
        self.image_raw = None

    def update_session(self):
        if self.logged:
            self.pytler.update_session()

        self.root.after(10000, func=self.update_session)

    def reset_back(self):
        self.back.destroy()
        self.back = Frame(master=self.root, bg='black')
        self.back.pack_propagate(0)
        self.back.pack(fill=BOTH, expand=1)
        self.check_incoming_calls()


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

        if len(login)>32:
            messagebox.showerror('Błąd', 'Maksymalna długość loginu to 32 znaki')
            return
        if not self.check_password(password):
            messagebox.showwarning('Błąd', 'Hasło powinno mieć co najmniej 8 znaków długości oraz zawierać minimum jedną cyfrę, jedną małą literę oraz jedną wielką literę')
            return
        if not self.check_email(email):
            messagebox.showwarning('Błąd', 'Niepoprawny adres e-mail')
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

    def check_email(self, email):
        return bool(re.match('[^@]+@[^@]+\.[^@]+', email))

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
                    self.logged=True
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
                self.logged=True
                self.main_view()

    def logout(self):
        self.logged = False
        if self.in_call:
            self.pytler.stop_comm()
            self.in_call = False
        self.pytler.logout()
        self.view_login_or_register()


    def main_view(self):
        #self.reset_back()
        self.delete_children(self.back)
        self.root.geometry('1000x500')
        self.pytler.delete_pending_call()

        self.in_call = False
        self.calling = False
        self.calling_id = None

        contact_frame = Frame(master=self.back, bg='black', height=500, width=200)
        contact_frame.pack_propagate(0)
        contact_frame.pack(side=LEFT)

        main_frame = Frame(master=self.back, bg='green', height=500, width=800)
        main_frame.pack_propagate(0)
        main_frame.pack(side=LEFT)

        menu_frame = Frame(master=main_frame, bg='black', width=800, height=70)
        menu_frame.pack_propagate(0)
        menu_frame.pack()

        content_frame = Frame(master=main_frame, bg='white', width=800, height=350)
        content_frame.pack_propagate(0)
        content_frame.pack()

        action_bar = Frame(master=main_frame, bg='black', width=800, height=80)
        action_bar.pack_propagate(0)
        action_bar.pack()

        self.generate_topbar_content(menu_frame, content_frame, action_bar)
        self.generate_contacts(contact_frame, content_frame, action_bar)
        self.popup_invitations()

    def popup_invitations(self):
        r = self.pytler.get_invitations()

        for i in r['my_invitations']:
            result = messagebox.askquestion(f'Masz zaproszenie od {i["login"]}', f'Czy chcesz dodać {i["login"]} do znajomych?')
            if result=='yes':
                r1 = self.pytler.accept_invitation(i['invitation_id'])
                if r1:
                    messagebox.showinfo('Gratulacje', f'Poprawnie dodano {i["login"]} do znajomych')
                    self.main_view()
                else:
                    messagebox.showerror('Błąd', f'Nie udało się dodać {i["login"]} do znajomych')
            elif result=='no':
                r1 = self.pytler.decline_invitation(i['invitation_id'])

        for i in r['rejected_invitations']:
            messagebox.showinfo('Ojej', f'{i["login"]} odrzucił twoje zaproszenie')

    def generate_contacts(self, contact_frame, content_frame, action_bar):
        r = self.pytler.get_contacts()
        if not r:
            messagebox.showwarning('Błąd', 'Błąd podczas wczytywania kontaktów')
        self.delete_children(contact_frame)
        frame = Frame(master=contact_frame, bg='black')
        frame.pack()
        label = self.create_label('Kontakty', frame, width = 200, pady=(20,0), fg='white', bg='black')
        label.pack(fill=BOTH, expand=1, side=TOP)

        frame2 = Frame(master=contact_frame, bg='black', height=350, width=200)
        frame2.pack(pady=10)
        frame2.pack_propagate(0)
        scrollbar = Scrollbar(frame2)
        scrollbar.pack(fill=BOTH, expand=1, side=RIGHT)
        contact_list = Listbox(frame2, yscrollcommand = scrollbar.set, width= 180, bg='black', font=self.font, fg='white')
        self.update_contacts(contact_list)
        contact_list.pack(side = LEFT, fill = BOTH)

        contact_list.bind('<<ListboxSelect>>', lambda evt: self.onselect(evt, content_frame, action_bar))

        frame1 = Frame(master=contact_frame, bg='black')
        frame1.pack()
        add_button = self.create_button('Dodaj kontakt +', frame1, width = 150, height=60, fg='black', bg='white', action=lambda: self.popup('Wyślij zaproszenie', 'Login', 'Wyślij', self.popup_add_contact))
        add_button.pack(fill=BOTH, expand=1, side=TOP)

    def update_contacts(self, contact_list):
        contact_list.delete(0,END)
        if self.pytler.contacts:
            for i, contact in enumerate(self.pytler.contacts):
                contact_list.insert(END, contact['login'])
                status = self.pytler.get_user_status(contact['id'])
                if status == 'active':
                    contact_list.itemconfig(i, foreground='green')
                elif status == 'inactive':
                    contact_list.itemconfig(i, foreground='red')
        contact_list.after(5000, lambda: self.update_contacts(contact_list))

    def popup_add_contact(self, popup, entry_value):
        if not entry_value:
            messagebox.showerror('Błąd', 'Nie wypełniono pola z nazwą użytkownika')
            return
        if entry_value == self.pytler.nick:
            messagebox.showerror('Błąd', 'Nie możesz zaprosić siebie do znajomych')
            return
        r = self.pytler.invite_to_contacts(entry_value)
        if not r:
            messagebox.showerror('Błąd', 'Użytkownik o takim loginie nie istnieje')
            return
        else:
            messagebox.showinfo('Gratulacje', f'Wysłano zaproszenie do użytkownika {entry_value}')
            popup.destroy()

    def generate_topbar_content(self, topbar, content_frame, action_bar):

        nickname = self.create_label(self.pytler.nick, topbar, height=50, padx=(180,20), fg='white', bg='black')
        nickname.pack(fill=BOTH, expand=1, side=RIGHT)

        home = self.create_button('Strona główna', topbar, padx=(20,20), height=50, action=self.main_view)
        home.pack(fill=BOTH, expand=1, side=RIGHT)

        self.settings = self.create_button('Ustawienia', topbar, padx=(20,20), height=50, action=lambda: self.show_settings(content_frame, action_bar))
        self.settings.pack(fill=BOTH, expand=1, side=RIGHT)

        logout = self.create_button('Wyloguj', topbar, padx=(20,20), height=50, action=self.logout)
        logout.pack(fill=BOTH, expand=1, side=RIGHT)


    def onselect(self, evt, content_frame, action_bar):
        #TODO wyświetlanie info
        w = evt.widget
        index = int(w.curselection()[0])

        self.delete_children(content_frame)
        self.delete_children(action_bar)

        self.generate_contact_info(index, content_frame)
        self.generate_action_bar_for_contact(index, action_bar)

    def show_settings(self, content_frame, action_bar):
        self.delete_children(content_frame)
        self.delete_children(action_bar)

        self.generate_content_for_settings(content_frame)
        self.generate_action_bar_for_settings(action_bar)

    def generate_content_for_settings(self, content_frame):
        frame = Frame(master=content_frame, bg='white', pady=20)
        frame.pack()

        img_label = self.create_label(f'Zdjęcie profilowe:', frame, width= 150)
        img_label.pack(fill=BOTH, expand=1, side=LEFT)

        frame_img = Frame(master=frame, bg='red', width=150, height=150)
        frame_img.pack_propagate(0)
        frame_img.pack(fill=BOTH, expand=1, side=LEFT)

        if self.pytler.profile_image:
            self.image_raw = self.pytler.profile_image
            self.profile_image = PhotoImage(format='png', data=self.image_raw)
            contact_image = Label(frame_img, image=self.profile_image, width=150, height=150)
            #contact_image.pack_propagate(0)
            contact_image.pack(fill=BOTH, expand=1, side=LEFT)

        frame1 = Frame(master=content_frame, bg='black')
        frame1.pack()

        email_label = self.create_label(f'Email: {self.pytler.email}', frame1, width=800)
        email_label.pack(fill=BOTH, expand=1, side=TOP)
        frame2 = Frame(master=content_frame, bg='black')
        frame2.pack()

        created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.pytler.created_at))

        date_label = self.create_label(f'Konto utworzone: {created_at}', frame2, width=800)
        date_label.pack(fill=BOTH, expand=1, side=TOP)

        frame3 = Frame(master=content_frame, bg='black')
        frame3.pack()
        if self.pytler.description:
            desc_label = self.create_label(f'Opis: {self.pytler.description}', frame3, width=800, height=100)
            desc_label.pack(fill=BOTH, expand=1, side=TOP)
        else:
            desc_label = self.create_label(f'Opis: Brak', frame3, width=800, height=100)
            desc_label.pack(fill=BOTH, expand=1, side=TOP)


    def generate_action_bar_for_settings(self, action_bar):
        change_desc_button = self.create_button('Zmień opis', action_bar, padx=(150,20), height=50, action=lambda: self.popup('Zmiana opisu', 'Nowy opis', 'Zmień', self.popup_change_desc))
        change_desc_button.pack(fill=BOTH, expand=1, side=RIGHT)

        change_password_button = self.create_button('Zmień hasło', action_bar, padx=(20,20), height=50, action=self.popup_password)
        change_password_button.pack(fill=BOTH, expand=1, side=RIGHT)

        change_email_button = self.create_button('Zmień email', action_bar, padx=(20,20), height=50, action=lambda: self.popup('Zmiana adresu email', 'Nowy adres', 'Zmień', self.popup_change_email))
        change_email_button.pack(fill=BOTH, expand=1, side=RIGHT)

        change_img_button = self.create_button('Zmień zdjęcie', action_bar, padx=(20,20), height=50, action=self.change_img)
        change_img_button.pack(fill=BOTH, expand=1, side=RIGHT)

    def change_img(self):
        path = askopenfilename(initialdir="C:/",
                           filetypes =(("PNG", "*.png"),("All Files","*.*")),
                           title = "Choose a file.")
        print(path)
        if len(path)>0:
            img_cv = cv2.imread(path)
            if img_cv is not None:
                height, width, _ = img_cv.shape
                if height > 150 or width > 150:
                    messagebox.showerror('Błąd', 'Maksymalny rozmiar obrazka to 150x150px')
                else:
                    _, buffer = cv2.imencode('.png', img_cv)
                    encoded_img = str(b64encode(buffer))[2:-1]
                    self.pytler.change_profile_image(encoded_img)
                    messagebox.showinfo('Gratulacje', f'Poprawnie zmieniono zdjęcie')
                    self.settings.invoke()
            else:
                messagebox.showerror('Błąd', 'Wybrano plik o niepoprawnym formacie')
        else:
            return

    def popup_password(self):
        popup = Toplevel()
        popup.title('Zmiana hasła')
        popup.config(bg='white')

        frame = Frame(popup)
        frame.pack()
        label = self.create_label('Nowe hasło', frame, fg='white', bg='black')
        entry = self.create_entry(frame)
        entry.config(show='*')
        label.pack(fill=BOTH, expand=1)
        entry.pack(fill=BOTH, expand=1)
        entry.config(font=self.font)

        frame1 = Frame(popup)
        frame1.pack()
        label1 = self.create_label('Powtórz hasło', frame1, fg='white', bg='black')
        entry1 = self.create_entry(frame1)
        entry1.config(show='*')
        label1.pack(fill=BOTH, expand=1)
        entry1.pack(fill=BOTH, expand=1)
        entry1.config(font=self.font)

        button = self.create_button('Zmień', popup, height=40, fg='white', bg='black', width=250, action=lambda: self.change_pass(entry.get(), entry1.get()))
        button.pack(fill=BOTH, expand=1)

    def change_pass(self, password, confirm):
        if not password or not confirm:
            messagebox.showwarning('Błąd', 'Nie wszystkie pola zostały wypełnione')
            return

        if not self.check_password(password):
            messagebox.showwarning('Błąd', 'Hasło powinno mieć co najmniej 8 znaków długości oraz zawierać minimum jedną cyfrę, jedną małą literę oraz jedną wielką literę')
            return

        if password!=confirm:
            messagebox.showwarning('Błąd', 'Hasło oraz potwierdzone hasło muszą być identyczne')
            return

        r = self.pytler.change_password(password)
        if not r:
            messagebox.showwarning('Błąd', 'Nie udało się zmienić hasła')
            return
        else:
            messagebox.showinfo('Gratulacje', f'Poprawnie zmieniono hasło')
            self.settings.invoke()

    def popup_change_desc(self, popup, entry_value):
        if not entry_value:
            messagebox.showerror('Błąd', 'Nie wypełniono pola z nowym opisem')
            return
        if len(entry_value) > 100:
            messagebox.showerror('Błąd', 'Maksymalna długość opisu to 100 znaków')
            return
        r = self.pytler.change_description(entry_value)
        if not r:
            messagebox.showerror('Błąd', 'Nie udało się zmienić opisu')
            return
        else:
            messagebox.showinfo('Gratulacje', f'Poprawnie zmieniono opis')
            self.pytler.description = entry_value
            self.settings.invoke()
            popup.destroy()

    def popup_change_email(self, popup, entry_value):
        if not entry_value:
            messagebox.showerror('Błąd', 'Nie wypełniono pola z nowym adresem email')
            return
        if not self.check_email(entry_value):
            messagebox.showerror('Błąd', 'Niepoprawny adres e-mail')
            return
        r = self.pytler.change_email(entry_value)
        if not r:
            messagebox.showerror('Błąd', 'Nie udało się zmienić adresu email')
            return
        else:
            messagebox.showinfo('Gratulacje', f'Poprawnie zmieniono adres email')
            self.pytler.email = entry_value
            self.settings.invoke()
            popup.destroy()

    def popup(self, title, text, button_text, button_action, show=None):
        popup = Toplevel()
        popup.title(title)
        label = self.create_label(text, popup, fg='white', bg='black')
        entry = self.create_entry(popup)
        if show is not None:
            entry.config(show=show)
        label.pack(fill=BOTH, expand=1)
        entry.pack(fill=BOTH, expand=1)
        entry.config(font=self.font)
        button = self.create_button(button_text, popup, action=lambda: button_action(popup, entry.get()), height=40, fg='white', bg='black')
        button.pack(fill=BOTH, expand=1)


    def generate_contact_info(self, contact_number, content_frame):
        frame = Frame(master=content_frame, bg='white', pady=20)
        frame.pack()

        img_label = self.create_label(f'Zdjęcie profilowe:', frame, width= 150)
        img_label.pack(fill=BOTH, expand=1, side=LEFT)

        frame_img = Frame(master=frame, bg='red', width=150, height=150)
        frame_img.pack_propagate(0)
        frame_img.pack(fill=BOTH, expand=1, side=LEFT)

        if self.pytler.contacts[contact_number]["profile_image"]:
            self.image_raw = self.pytler.contacts[contact_number]["profile_image"]
            self.profile_image = PhotoImage(format='png', data=self.image_raw)
            contact_image = Label(frame_img, image=self.profile_image, width=150, height=150)
            #contact_image.pack_propagate(0)
            contact_image.pack(fill=BOTH, expand=1, side=LEFT)

        frame1 = Frame(master=content_frame, bg='black')
        frame1.pack()

        nick_label = self.create_label(f'Nick: {self.pytler.contacts[contact_number]["login"]}', frame1, width=800)
        nick_label.pack(fill=BOTH, expand=1, side=TOP)

        frame3 = Frame(master=content_frame, bg='black')
        frame3.pack()
        if self.pytler.contacts[contact_number]['description']:
            desc_label = self.create_label(f'Opis: {self.pytler.contacts[contact_number]["description"]}', frame3, width=800, height=100)
            desc_label.pack(fill=BOTH, expand=1, side=TOP)
        else:
            desc_label = self.create_label(f'Opis: Brak', frame3, width=800, height=100)
            desc_label.pack(fill=BOTH, expand=1, side=TOP)

    def generate_action_bar_for_contact(self, index, action_bar):
        remove = self.create_button('Usuń kontakt', action_bar, padx=(300,20), height=50, action=lambda: self.remove_contact(index))
        remove.pack(fill=BOTH, expand=1, side=RIGHT)

        call = self.create_button('Zadzwoń', action_bar, padx=(20,20), height=50, action=lambda: self.make_call(index))
        call.pack(fill=BOTH, expand=1, side=RIGHT)

    def remove_contact(self, index):
        try:
            r = self.pytler.delete_from_contacts(self.pytler.contacts[index]['login'])
            if r:
                messagebox.showinfo('Udało się!', 'Kontakt został poprawnie usunięty')
                self.main_view()
                return
        except IndexError:
            pass
        messagebox.showerror('Błąd!', 'Nie udało się usunać kontaktu')

    def delete_children(self, frame):
        for child in frame.winfo_children():
            child.destroy()

    def check_incoming_calls(self):
        if self.logged:
            if not self.calling and not self.in_call:
                pending_calls = self.pytler.get_pending_calls()
                for call in pending_calls:
                    result = messagebox.askquestion(f'Połączenie przychodzące od {call["login"]}', f'Czy chcesz odebrać od {call["login"]}?')
                    if result=='yes':
                        self.create_call_session(call['id'])
                        in_port, out_port = self.pytler.create_sockets()
                        host = self.pytler.host
                        self.pytler.create_new_pending_call(call['id'], host, in_port, out_port)
                        self.in_call = True
                        self.pytler.connect(call['host'], call['port'], call['port2'])
                        self.pytler.start_comm()
                        self.answer_call(call['login'], call['id'])
                    elif result=='no':
                       self.pytler.delete_pending_call(call['id'])
        self.back.after(100, self.check_incoming_calls)

    def create_call_session(self, id):
        self.pytler.create_new_callsession(id)
        self.call_session=True


    def answer_call(self, login, id):
        self.delete_children(self.back)
        self.root.geometry('400x100')
        self.pytler.delete_pending_call()

        label = self.create_label(f'Rozmowa z {login}...', self.back, width = 200, padx=(30,10))
        label.pack(fill=BOTH, expand=1, side=TOP)
        button = self.create_button('Rozłącz', self.back, action=self.end_call, padx=(10,20), height=40)
        button.pack(fill=BOTH, expand=1, side=TOP)

        self.back.after(1000, lambda: self.update_call_session(id))


    def update_call_session(self, id):
        if self.call_session == True:
            if self.pytler.get_user_callsession_status(id) == 'active':
                self.pytler.extend_callsession(id)
                self.back.after(1000, lambda: self.update_call_session(id))
            else:
                messagebox.showinfo('Koniec rozmowy', 'Rozmówca rozłączył się')
                self.call_session=False
                self.end_call()
        else:
            self.end_call()

    def end_call(self):
        self.in_call = False
        self.call_session = False
        self.pytler.stop_comm()
        self.main_view()


    def make_call(self, index):
        in_port, out_port = self.pytler.create_sockets()
        host = self.pytler.host
        print(in_port, out_port, host)
        self.pytler.create_new_pending_call(self.pytler.contacts[index]['id'], host, in_port, out_port)
        self.calling_id = self.pytler.contacts[index]['id']
        self.view_calling(index)

    def view_calling(self, index):
        self.calling = True
        self.reset_back()
        self.root.geometry('400x100')

        label = self.create_label(f'Dzwonię do {self.pytler.contacts[index]["login"]}...', self.back, width = 200, padx=(30,10))
        label.pack(fill=BOTH, expand=1, side=TOP)
        button = self.create_button('Anuluj', self.back, action=self.check_calling, padx=(10,20), height=40)
        button.pack(fill=BOTH, expand=1, side=TOP)

        self.root.after(15000, self.check_calling)
        self.check_if_call_answered()

    def check_if_call_answered(self):
        pending_calls = self.pytler.get_pending_calls()
        for call in pending_calls:
            if call['id'] == self.calling_id:
                self.create_call_session(call['id'])
                self.calling = False
                self.in_call = True
                self.pytler.delete_pending_call(call['id'])
                self.pytler.connect(call['host'], call['port'], call['port2'])
                self.pytler.start_comm()
                self.answer_call(call['login'], call['id'])

        if self.calling:
            self.root.after(100, self.check_if_call_answered)

    def check_calling(self):
        if self.calling == True:
            self.calling = False
            self.pytler.delete_pending_call()
            self.main_view()

    def main(self):
        self.view_login_or_register()

        self.root.mainloop()

GUI().main()

