import cherrypy
import random
import string
from base64 import b64encode

import cherrypy
import psycopg2
from enum import Enum, auto

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

        return {'activation_token': token}

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
        query = """UPDATE users SET email = %s, password = %s, description = %s WHERE login = %s;"""
        request = cherrypy.request.json
        with PYTLER_DB as db:
            db.execute(query, (request['email'], request['password'], request['description'], cherrypy.request.login), ResultSet.NONE)

    def DELETE(self):
        query = """DELETE FROM users WHERE login = %s;"""
        with PYTLER_DB as db:
            db.execute(query, (cherrypy.request.login,), ResultSet.NONE)


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

    cherrypy.engine.start()
    cherrypy.engine.block()