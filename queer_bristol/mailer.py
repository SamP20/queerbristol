from abc import ABC

class Mailer(ABC):
    def send_login_token(email: str, token_url: str):
        pass