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

    def get_user_info(self) -> Union[Dict[str, Union[int, str]], False]:
        r = requests.get(ADDRESS + '/api/user', auth=(self.nick,self.password))
        if r.ok:
            user_info = r.json()
            return user_info
        else:
            return False

    def change_password(self, new_password: str) -> bool:
        #TODO sprawdzanie jakości hasła
        password = self._encode_password(new_password)
        r = requests.put(ADDRESS + '/api/user', auth=(self.nick,self.password), json={'password':password})
        if r.ok:
            return True
        else:
            return False

    def change_email(self, new_email: str) -> bool:
        #TODO sprawdzanie poprawności mejla
        r = requests.put(ADDRESS + '/api/user', auth=(self.nick,self.password), json={'email':new_email})
        if r.ok:
            return True
        else:
            return False


    def change_description(self, new_description: str) -> bool:
        r = requests.put(ADDRESS + '/api/user', auth=(self.nick,self.password), json={'description':new_description})
        if r.ok:
            return True
        else:
            return False

    def change_profile_image(self, new_image: str) -> bool:
        r = requests.put(ADDRESS + '/api/user', auth=(self.nick,self.password), json={'profile_image':new_image})
        if r.ok:
            return True
        else:
            return False

    def delete_account(self) -> bool:
        r = requests.delete(ADDRESS + '/api/user', auth=(self.nick,self.password))
        if r.ok:
            return True
        else:
            return False

    def get_contacts(self) -> Union[List[Dict[str, Union[str, int]]], False]:
        r = requests.get(ADDRESS + '/api/contacts', auth=(self.nick,self.password))
        if r.ok:
            return r.json()
        else:
            return False

    def invite_to_contacts(self, contact_login: str) -> bool:
        r = requests.post(ADDRESS + '/api/contacts', auth=(self.nick,self.password), params={'contact_login': contact_login})
        if r.ok:
            return True
        else:
            return False

    def delete_from_contacts(self, contact_login: str) -> bool:
        r = requests.delete(ADDRESS + '/api/contacts', auth=(self.nick,self.password), params={'contact_login': contact_login})
        if r.ok:
            return True
        else:
            return False

    def get_invitations(self) -> Union[Dict[str, List[Dict[str, Union[int, str]]]], False]:
        r = requests.get(ADDRESS + '/api/invitations', auth=(self.nick,self.password))
        if r.ok:
            return r.json()
        else:
            return False

    def accept_invitation(self, invitation_id: int) -> bool:
        r = requests.put(ADDRESS + '/api/invitations', auth=(self.nick,self.password), params={'invitation_id': invitation_id, 'action':'accept'})
        if r.ok:
            return True
        else:
            return False

    def decline_invitation(self, invitation_id: int) -> bool:
        r = requests.put(ADDRESS + '/api/invitations', auth=(self.nick,self.password), params={'invitation_id': invitation_id, 'action':'reject'})
        if r.ok:
            return True
        else:
            return False

    def get_user_status(self, user_id: int = None) -> Union[str, False]:
        r = requests.get(ADDRESS + '/api/sessions', auth=(self.nick,self.password), params={'user_id': user_id})
        if r.ok:
            return r.json()['status']
        else:
            return False

    def update_session(self):
        if self.get_user_status() == 'active':
            self._extend_session()
        elif self.get_user_status() == 'inactive':
            self._create_new_session()

    def _create_new_session(self) -> bool:
        r = requests.post(ADDRESS + '/api/sessions', auth=(self.nick,self.password))
        if r.ok:
            return True
        else:
            return False

    def _extend_session(self):
        r = requests.put(ADDRESS + '/api/sessions', auth=(self.nick,self.password), params={'status': 'extend'})
        if r.ok:
            return True
        else:
            return False

    def logout(self):
        r = requests.put(ADDRESS + '/api/sessions', auth=(self.nick,self.password), params={'status': 'end'})
        if r.ok:
            return True
        else:
            return False

    def get_user_callsession_status(self, user_id: int = None) -> Dict[str, str]:
        r = requests.get(ADDRESS + '/api/callsessions', auth=(self.nick,self.password), params={'user_id':user_id})
        if r.ok:
            return r.json()

    def create_new_callsession(self, conversator_id: int) -> bool:
        r = requests.post(ADDRESS + '/api/callsessions', auth=(self.nick,self.password), params={'conversator_id': conversator_id})
        if r.ok:
            return True
        else:
            return False

    def extend_callsession(self, conversator_id: int) -> bool:
        r = requests.put(ADDRESS + '/api/callsessions', auth=(self.nick,self.password), params={'conversator_id': conversator_id, 'status':'extend'})
        if r.ok:
            return True
        else:
            return False

    def end_callsession(self, conversator_id: int) -> bool:
        r = requests.put(ADDRESS + '/api/callsessions', auth=(self.nick,self.password), params={'conversator_id': conversator_id, 'status':'end'})
        if r.ok:
            return True
        else:
            return False

    def get_pending_calls(self) -> List[Dict[str, Union[str, int, bool]]]:
        r = requests.get(ADDRESS + '/api/pendingcall', auth=(self.nick,self.password))
        if r.ok:
            return r.json()

    def create_new_pending_call(self, called_user_id: int, address_host: str, address_port1: int, address_port2: int, encrypted: bool = False, public_key: str = None):
        r = requests.post(ADDRESS + '/api/pendingcall', auth=(self.nick,self.password), json={'user_id': called_user_id, 'host': address_host, 'port': address_port1, 'encrypted': encrypted, 'public_key': public_key, 'port2': address_port2})
        if r.ok:
            return True
        else:
            return False

    def delete_pending_call(self):
        r = requests.delete(ADDRESS + '/api/pendingcall', auth=(self.nick,self.password))
        if r.ok:
            return True
        else:
            return False




