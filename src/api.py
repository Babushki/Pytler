import cherrypy
import random
import string
from base64 import b64encode

import cherrypy
import psycopg2
from enum import Enum, auto

import smtplib
from email.message import EmailMessage
import configparser
from typing import Dict

class ResultSet(Enum):
    NONE = None
    ONE = auto()
    ALL = auto()

class Database:
    def __init__(self, dbname, user, host, port):
        self.connection_string = f'dbname={dbname} user={user} host={host} port={port}'
        self.connection = None

    def __enter__(self):
        self.connection = psycopg2.connect(self.connection_string)
        return self

    def __exit__(self, *args):
        self.connection.close()

    def execute(self, sql: str, parameters: tuple, result_set: ResultSet):
        with self.connection:
            with self.connection.cursor() as curs:
                curs.execute(sql, parameters)
                if result_set is not ResultSet.NONE:
                    rows = curs.fetchone() if result_set == ResultSet.ONE else curs.fetchall()
                else:
                    rows = None
        return rows

DBNAME_MAIN = 'pytler'
DBUSER = 'postgres'
DBHOST = '127.0.0.1'
DBPORT = '5432'
TOKEN_LENGTH = 30

PYTLER_DB = Database(DBNAME_MAIN, DBUSER, DBHOST, DBPORT)

def validate_password(realm, username, password):
    query = """SELECT EXISTS (SELECT * FROM users WHERE login = %s AND password ILIKE %s);"""
    with PYTLER_DB as db:
        result = db.execute(query, (username, password), ResultSet.ONE)
        if result is None or not result[0]:
            return False
        else:
            return True

#----

@cherrypy.expose
class AuthService:

    @cherrypy.tools.json_out()
    def GET(self, login, password):
        query = """SELECT EXISTS (SELECT * FROM users WHERE login = %s AND password ILIKE %s);"""
        with PYTLER_DB as db:
            user_exists = db.execute(query, (login, password), ResultSet.ONE)[0]
            if user_exists:
                auth_token = b64encode(bytes(f'{login}:{password}', 'utf-8')).decode('utf-8')
                return {'auth_token': auth_token}
            else:
                raise cherrypy.HTTPError(404, 'User not found')

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        query1 = """INSERT INTO users (login, password, email, created_at)
                    VALUES (%s, %s, %s, extract(epoch from now())) RETURNING id;"""
        query2 = """INSERT INTO keys (key_type_id, user_id, value, expiration_date)
                    VALUES (%s, %s, %s, extract(epoch from now() + interval '1 week'));"""
        activation_key_type_id = 1
        request = cherrypy.request.json
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=TOKEN_LENGTH))
        with PYTLER_DB as db:
            user_id = db.execute(query1, (request['login'], request['password'], request['email']), ResultSet.ONE)[0]
            db.execute(query2, (activation_key_type_id, user_id, token), ResultSet.NONE)

        self._send_activation_email(request['email'], token, request['login'])

    def _send_activation_email(self, email: str, token: str, login: str) -> None:
        CONFIG_FILE = 'email.config'
        config = self._read_email_config(CONFIG_FILE)

        message_content = f"""Email aktywacyjny dla konta o loginie {login} w aplikacji Pytler\n
        \n
        Jeśli nie zakładałeś konta w serwisie możesz zignorować ten email. \n
        \n
        Aby aktywować konto wklej poniższy token w odpowiednie miejsce w aplikacji. \n
        Token aktywacyjny: {token}

        """
        msg = EmailMessage()
        msg.set_content(message_content)
        msg['Subject'] = 'Aktywacja konta w w aplikacji Pytler'
        msg['From'] = config['Email']['Address']
        msg['To'] = email

        server = smtplib.SMTP(config['Server']['Host'], config['Server']['Port'])
        server.ehlo()
        server.starttls()
        server.login(config['Email']['Address'], config['Email']['Password'])
        server.send_message(msg)

    def _read_email_config(self, file_name: str) -> Dict[str, str]:
        config = configparser.ConfigParser()
        config.read(file_name)
        return config

    def PATCH(self, token):
        query1 = """UPDATE keys SET expiration_date = extract(epoch from now()) WHERE expiration_date > extract(epoch from now()) AND value = %s RETURNING user_id;"""
        query2 = """UPDATE users SET activated = TRUE WHERE id = %s;"""

        with PYTLER_DB as db:
            user_id = db.execute(query1, (token,), ResultSet.ONE)[0]
            db.execute(query2, (user_id,), ResultSet.NONE)

#----
@cherrypy.expose
class UserService:

    @cherrypy.tools.json_out()
    def GET(self):
        query = """SELECT id, login, email, activated, profile_image, description, created_at FROM users WHERE login = %s;"""
        with PYTLER_DB as db:
            info = db.execute(query, (cherrypy.request.login,), ResultSet.ONE)
        return {'id': info[0], 'login': info[1], 'email': info[2], 'activated': info[3], 'profile_image': info[4], 'description': info[5], 'created_at': info[6]}

    @cherrypy.tools.json_in()
    def PUT(self):
        request = cherrypy.request.json
        login = cherrypy.request.login

        password = request.get('password')
        if password:
            self._update_password(password, login)

        email = request.get('email')
        if email:
            self._update_email(email, login)

        description = request.get('description')
        if description:
            self._update_description(description, login)

        profile_image = request.get('profile_image')
        if profile_image:
            self._update_profile_image(profile_image, login)

    def _update_password(self, new_password: str, login: str):
        query = 'UPDATE users set password = %s WHERE login = %s'
        if len(new_password) != 64:
            raise cherrypy.HTTPError(400, "Bad request")
        with PYTLER_DB as db:
            db.execute(query, (new_password, login), ResultSet.NONE)

    def _update_email(self, new_email: str, login: str):
        query = 'UPDATE users set email = %s WHERE login = %s'
        with PYTLER_DB as db:
            db.execute(query, (new_email, login), ResultSet.NONE)

    def _update_description(self, new_description: str, login: str):
        query = 'UPDATE users set description = %s WHERE login = %s'
        with PYTLER_DB as db:
            db.execute(query, (new_description, login), ResultSet.NONE)

    def _update_profile_image(self, new_profile_image: str, login: str):
        query = 'UPDATE users set profile_image = %s WHERE login = %s'
        with PYTLER_DB as db:
            db.execute(query, (new_profile_image, login), ResultSet.NONE)

    def DELETE(self):
        query = """DELETE FROM users WHERE login = %s;"""
        with PYTLER_DB as db:
            db.execute(query, (cherrypy.request.login,), ResultSet.NONE)

#----
@cherrypy.expose
class ContactsService:

    @cherrypy.tools.json_out()
    def GET(self):
        query1 = """SELECT u.login, profile_image, u.id, description, ringtone FROM contacts JOIN users u ON contacts.contact_id = u.id WHERE contacts.user_id = %s;"""
        query2 = """SELECT id FROM users WHERE login = %s;"""

        with PYTLER_DB as db:
            user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
            contacts = db.execute(query1, (user_id,), ResultSet.ALL)
        result = []

        for c in contacts:
            result.append({'login': c[0], 'profile_image': c[1], 'id': c[2], 'description': c[3], 'ringtone': c[4]})

        return result

    def POST(self, contact_login):
        pending_status_id = 1
        query1 = """INSERT INTO invitations (inviting_user_id, invited_user_id, invitation_status_id, created_at, last_modified)
                    VALUES (%s, %s, %s, extract(epoch from now()), extract(epoch from now()));"""
        query2 = """SELECT id FROM users WHERE login = %s;"""

        with PYTLER_DB as db:
            user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
            contact_id = db.execute(query2, (contact_login,), ResultSet.ONE)[0]
            db.execute(query1, (user_id, contact_id, pending_status_id), ResultSet.NONE)

    def DELETE(self, contact_login):
        query1 = """DELETE FROM contacts WHERE user_id = %s AND contact_id = %s;"""
        query2 = """SELECT id FROM users WHERE login = %s;"""

        with PYTLER_DB as db:
            user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
            contact_id = db.execute(query2, (contact_login,), ResultSet.ONE)[0]
            db.execute(query1, (user_id, contact_id), ResultSet.NONE)
            db.execute(query1, (contact_id, user_id), ResultSet.NONE)

#----
@cherrypy.expose
class InvitationsService:

    @cherrypy.tools.json_out()
    def GET(self):
        query1 = """SELECT inviting_user_id, id FROM invitations WHERE invited_user_id = %s AND invitation_status_id = 1;"""
        query2 = """SELECT invited_user_id, id FROM invitations WHERE inviting_user_id = %s AND invitation_status_id = 3;"""
        query3 = """SELECT id FROM users WHERE login = %s;"""
        query4 = """SELECT login FROM users WHERE id = %s;"""
        query5 = """UPDATE invitations SET invitation_status_id = 4, last_modified = extract(epoch from now()) WHERE inviting_user_id = %s AND invitation_status_id = 3;"""

        result = {'my_invitations': [], 'rejected_invitations': []}

        with PYTLER_DB as db:
            user_id = db.execute(query3, (cherrypy.request.login,), ResultSet.ONE)[0]
            my_invitations = db.execute(query1, (user_id,), ResultSet.ALL)
            rejected_invitations = db.execute(query2, (user_id,), ResultSet.ALL)
            db.execute(query5, (user_id,), ResultSet.NONE)

            for i in my_invitations:
                contact_login = db.execute(query4, (i[0],), ResultSet.ONE)[0]
                result['my_invitations'].append({'invitation_id': i[1], 'login': contact_login})

            for i in rejected_invitations:
                contact_login = db.execute(query4, (i[0],), ResultSet.ONE)[0]
                result['rejected_invitations'].append({'invitation_id': i[1], 'login': contact_login})

        return result

    def PUT(self, invitation_id, action):
        #accept:
        query1 = """UPDATE invitations SET invitation_status_id = 2, last_modified = extract(epoch from now()) WHERE id = %s AND invited_user_id = %s AND invitation_status_id = 1;"""
        #reject:
        query2 = """UPDATE invitations SET invitation_status_id = 3, last_modified = extract(epoch from now()) WHERE id = %s AND invited_user_id = %s AND invitation_status_id = 1;"""

        query3 = """SELECT id FROM users WHERE login = %s;"""

        query4 = """SELECT inviting_user_id FROM invitations WHERE id = %s;"""

        query5 = """INSERT INTO contacts (user_id, contact_id, invitation_id) VALUES (%s, %s, %s);"""

        with PYTLER_DB as db:
            user_id = db.execute(query3, (cherrypy.request.login,), ResultSet.ONE)[0]
            contact_id = db.execute(query4, (invitation_id,), ResultSet.ONE)[0]
            if action == 'reject':
                db.execute(query2, (invitation_id, user_id), ResultSet.NONE)
            elif action == 'accept':
                db.execute(query1, (invitation_id, user_id), ResultSet.NONE)
                db.execute(query5, (user_id, contact_id, invitation_id), ResultSet.NONE)
                db.execute(query5, (contact_id, user_id, invitation_id), ResultSet.NONE)
#----

@cherrypy.expose
class SessionsService:

    @cherrypy.tools.json_out()
    def GET(self, user_id = None):
        query1 = """SELECT id FROM sessions WHERE expiration_date > extract(epoch from now()) AND user_id = %s"""
        query2 = """SELECT id FROM users WHERE login = %s;"""

        with PYTLER_DB as db:
            if user_id is None:
                user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
            status = db.execute(query1, (user_id,), ResultSet.ONE)

        if status:
            return {'status': 'active'}
        else:
            return {'status': 'inactive'}

    def POST(self):
        query1 = """INSERT INTO sessions (user_id, created_at, expiration_date)
                    VALUES (%s, extract(epoch from now()), extract(epoch from now() + interval '20 seconds'))"""
        query2 = """SELECT id FROM users WHERE login = %s;"""

        with PYTLER_DB as db:
            user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
            db.execute(query1, (user_id,), ResultSet.NONE)

    def PUT(self, status):
        query2 = """SELECT id FROM users WHERE login = %s;"""
        if status == 'extend':
            query1 = """UPDATE sessions SET expiration_date = extract(epoch from now() + interval '20 seconds') WHERE user_id = %s AND expiration_date > extract(epoch from now())"""
            with PYTLER_DB as db:
                user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
                db.execute(query1, (user_id,), ResultSet.NONE)
        elif status == 'end':
            query1 = """UPDATE sessions SET expiration_date = extract(epoch from now()) WHERE user_id = %s AND expiration_date > extract(epoch from now())"""
            with PYTLER_DB as db:
                user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
                db.execute(query1, (user_id,), ResultSet.NONE)

#----

@cherrypy.expose
class CallSessionsService:

    @cherrypy.tools.json_out()
    def GET(self, user_id = None):
        query1 = """SELECT id, conversator_id FROM call_sessions WHERE expiration_date > extract(epoch from now()) AND user_id = %s"""
        query2 = """SELECT id FROM users WHERE login = %s;"""

        with PYTLER_DB as db:
            if user_id is None:
                user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
            status = db.execute(query1, (user_id,), ResultSet.ONE)

        if status:
            return {'status': 'active', 'conversator_id': status[1]}
        else:
            return {'status': 'inactive'}

    def POST(self, conversator_id):
        query1 = """INSERT INTO call_sessions (user_id, conversator_id, created_at, expiration_date)
                    VALUES (%s, %s, extract(epoch from now()), extract(epoch from now() + interval '15 seconds'))"""
        query2 = """SELECT id FROM users WHERE login = %s;"""

        with PYTLER_DB as db:
            user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
            db.execute(query1, (user_id, conversator_id), ResultSet.NONE)

    def PUT(self, conversator_id, status):
        if status == 'extend':
            query1 = """UPDATE call_sessions SET expiration_date = extract(epoch from now() + interval '10 seconds') WHERE user_id = %s AND expiration_date > extract(epoch from now()) AND conversator_id = %s"""
            query2 = """SELECT id FROM users WHERE login = %s;"""
            with PYTLER_DB as db:
                user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
                db.execute(query1, (user_id, conversator_id), ResultSet.NONE)
        elif status == 'end':
            query1 = """UPDATE call_sessions SET expiration_date = extract(epoch from now()) WHERE user_id = %s AND expiration_date > extract(epoch from now()) AND conversator_id = %s RETURNING created_at, expiration_date"""
            query3 = """INSERT INTO call_history (caller_id, receiver_id, datetime, duration) VALUES (%s, %s, %s, %s)"""

            with PYTLER_DB as db:
                user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
                info = db.execute(query1, (user_id, conversator_id), ResultSet.ONE)
                db.execute(query3, (user_id, conversator_id, info[0], info[1]-info[0]), ResultSet.NONE)

#----
@cherrypy.expose
class PendingCallsService:

    @cherrypy.tools.json_out()
    def GET(self):
        query1 = """SELECT calling_user_id, address_host, address_port, encrypted, public_key, address_port2 FROM pending_calls WHERE called_user_id = %s"""
        query2 = """SELECT id FROM users WHERE login = %s;"""
        query3 = """SELECT login FROM users WHERE id = %s;"""

        with PYTLER_DB as db:
            user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
            info = db.execute(query1, (user_id, ), ResultSet.ONE)
            if info:
                user_login = db.execute(query3, (info[0],), ResultSet.ONE)[0]
                result = {'login': user_login, 'host': info[1], 'id': info[0], 'port': info[2], 'encrypted': info[3], 'port2': info[5]}
                if info[3]:
                    result['public_key'] = info[4]
                return result
            else:
                return []

    @cherrypy.tools.json_in()
    def POST(self):
        query1 = """INSERT INTO pending_calls (calling_user_id, called_user_id, address_host, address_port, encrypted, public_key, address_port2)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        query2 = """SELECT id FROM users WHERE login = %s;"""
        request = cherrypy.request.json
        with PYTLER_DB as db:
            user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
            db.execute(query1, (user_id, request['user_id'], request['host'], request['port'], request['encrypted'], request.get('public_key', None), request['address_port2']), ResultSet.NONE)

    def DELETE(self):
        query1 = """DELETE FROM pending_calls WHERE calling_user_id = %s"""
        query2 = """SELECT id FROM users WHERE login = %s;"""
        with PYTLER_DB as db:
            user_id = db.execute(query2, (cherrypy.request.login,), ResultSet.ONE)[0]
            db.execute(query1, (user_id,), ResultSet.NONE)



if __name__ == '__main__':

    config = {
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
        'tools.auth_basic.on': True,
        'tools.auth_basic.realm': '127.0.0.1',
        'tools.auth_basic.checkpassword': validate_password,
    }
    without_authentication = {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher(), 'tools.auth_basic.on': False}}
    with_authentication = {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}

    cherrypy.config.update(config)
    cherrypy.tree.mount(AuthService(), '/api/auth', without_authentication)
    cherrypy.tree.mount(UserService(), '/api/user', with_authentication)
    cherrypy.tree.mount(ContactsService(), '/api/contacts', with_authentication)
    cherrypy.tree.mount(InvitationsService(), '/api/invitations', with_authentication)
    cherrypy.tree.mount(SessionsService(), '/api/sessions', with_authentication)
    cherrypy.tree.mount(CallSessionsService(), '/api/callsessions', with_authentication)
    cherrypy.tree.mount(PendingCallsService(), '/api/pendingcall', with_authentication)






    cherrypy.engine.start()
    cherrypy.engine.block()