from config import *

# add User model
class UserModel(db.Model):
    __tablename__ = 'user_model'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), unique=False, nullable=False)
    about = db.Column(db.String(256), unique=False, nullable=True)
    links = db.Column(db.String(64), unique=False, nullable=True)
    is_teacher = db.Column(db.Boolean, nullable=False)

    def get_all(self):
        return {'id': self.id, 'username': self.username, 'about': self.about, 'links': self.links}

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

# model for themes of tasks
class Theme(db.Model):
    __tablename__ = 'theme'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def get_all(self):
        return {'id': self.id, 'name':self.name}

# model for tasks
class TestModel(db.Model):
    __tablename__ = 'test_model'
    id = db.Column(db.Integer, primary_key=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'), nullable=False)
    question = db.Column(db.String(512), unique=False, nullable=False)
    right_answer = db.Column(db.String(64), unique=False, nullable=True) # use || if more than one questions
    explanation = db.Column(db.String(256), unique=False, nullable=True)
    author_id = db.Column(db.Integer, unique=False, nullable=False)
    theme = db.relationship('Theme',backref=db.backref('TestModel',lazy=True))

    def __repr__(self):
        return '<br>'.join([str(self.id), str(self.theme_id), self.question,
                            self.right_answer, self.explanation, str(self.author_id)])

    def get_all(self):
        return {'id': self.id, 'theme id': self.theme_id,
                'question': self.question, 'right answer': self.right_answer,
                'explanation': self.explanation, 'author id': self.author_id}

