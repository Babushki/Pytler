import requests
from typing import Dict, List, Union

ADDRESS = 'http://192.168.43.131:8080'


class Pytler:

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def register_user(self, login: str, password: str, email: str):
        pass

    def activate_account(self, token: str):
        pass

    def login(self, login: str, password: str):
        pass

    def get_user_info(self):
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



