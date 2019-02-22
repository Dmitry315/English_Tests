from config import *

# add User model
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), unique=False, nullable=False)
    about = db.Column(db.String(256), unique=False, nullable=True)
    links = db.Column(db.String(64), unique=False, nullable=True)

    def __repr__(self):
        return '<User {} {} {}>'.format(self.id, self.password, self.username)

    def get_description(self):
        return self.about

    def get_links(self):
        return self.links

    def get_id(self):
        return self.id

    def get_name(self):
        return self.username

    def get_password(self):
        return self.password
