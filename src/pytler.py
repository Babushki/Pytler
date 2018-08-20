import requests
from typing import Dict, List, Union
import hashlib

ADDRESS = 'http://127.0.0.1:8080'


class Pytler:

    def __init__(self):
        self.nick = None
        self.password = None

    def register_user(self, login: str, password: str, email: str) -> bool:
        #TODO sprawdzanie jakości hasła i ew. mejla

        password = self._encode_password(password)
        r = requests.post(ADDRESS + '/api/auth', json={'login': login, 'password': password, 'email': email})
        return True if r.ok else False

    def _encode_password(self, password: str) -> str:
        return str(hashlib.sha256(password.encode()).hexdigest())

    def activate_account(self, token: str) -> bool:
        #TODO danie znać użytkownikowi że token jest złej długości
        r = requests.patch(ADDRESS + '/api/auth', params={'token':token})
        return True if r.ok else False

    def login(self, login: str, password: str) -> bool:
        #TODO co w przypadku braku gdy login lub password = None - załatwiamy to tutaj czy w gui?
        password = self._encode_password(password)
        r = requests.get(ADDRESS + '/api/auth', params = {'login': login, 'password': password})
        if r.ok:
            self.nick = login
            self.password = password
            return True
        else:
            return False

    def get_user_info(self) -> Dict[str, Union[int, str]]:
        r = requests.get(ADDRESS + '/api/user', auth=(self.nick,self.password))
        if r.ok:
            user_info = r.json()
            return user_info
        else:
            pass

    def change_password(self, new_password: str):
        pass

    def change_email(self, new_email: str):
        pass

    def change_description(self, new_description: str):
        pass

    def change_profile_image(self, new_image):
        pass

    def delete_account(self):
        pass

    def get_contacts(self):
        pass

    def invite_to_contacts(self, contact_login: str):
        pass

    def delete_from_contacts(self, contact_login: str):
        pass

    def get_invitations(self) -> Dict[str, List[Dict[str, Union[int, str]]]]:
        pass

    def accept_invitation(self, invitation_id: int):
        pass

    def decline_invitation(self, invitation_id: int):
        pass

    def get_user_status(self, user_id: int = None) -> bool:
        pass

    def update_session(self):
        pass

    def _create_new_session(self):
        pass

    def _extend_session(self):
        pass

    def logout(self):
        pass

    def get_user_callsession_status(self, user_id: int = None) -> bool:
        pass

    def update_callsession(self):
        pass

    def _create_new_callsession(self):
        pass

    def _extend_callsession(self):
        pass

    def end_callsession(self):
        pass

    def get_pending_calls(self):
        pass

    def create_new_pending_call(self):
        pass

    def delete_pending_call(self):
        pass



