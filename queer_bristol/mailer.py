
from flask import current_app, render_template
from mailersend.emails import NewEmail

from queer_bristol.models import EmailLogin


class Mailer():
    def mailer(self) -> NewEmail:
        return NewEmail(current_app.config["MAILERSEND_TOKEN"])
    
    def _set_default_mail_fields(self, mailer: NewEmail, mail_body: dict):
        from_email = {
            "name": current_app.config["MAIL_FROM_NAME"],
            "email": current_app.config["MAIL_FROM_EMAIL"],
        }
        mailer.set_mail_from(from_email, mail_body)
        mailer.set_reply_to(from_email, mail_body)

    def send_login_token(self, login: EmailLogin, verify_url: str):
        mailer = self.mailer()
        mail_body = {}
        self._set_default_mail_fields(mailer, mail_body)

        mailer.set_mail_to([{
            "name": login.user.name,
            "email": login.user.email
        }], mail_body)

        mailer.set_subject("Your login link", mail_body)
        mailer.set_plaintext_content(render_template(
            "email/login.txt",
            login=login,
            verify_url=verify_url
        ), mail_body)
        return mailer.send(mail_body)