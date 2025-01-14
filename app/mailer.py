from flask_mail import Mail, Message


class Mailer:
    _mailer = None

    def __new__(cls, app):
        if not cls._mailer:
            cls._mailer = super(Mailer, cls).__new__(cls)
        return cls._mailer

    def __init__(self, app):
        self.mail = Mail(app)

    def get_mailer():
        if not Mailer._mailer:
            raise Exception("Mailer not initialized")
        return Mailer._mailer

    def send_mail(self, recipients, subject, body):
        msg = Message(subject=subject, recipients=recipients, body=body)

        self.mail.send(msg)
