from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired

# form to sign user in
class SignInForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    re_password = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

# form to log user in
class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')

class AddUser(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Add')

class ProfileEdit(FlaskForm):
    about = TextAreaField('About you')
    links = TextAreaField('Your links in social networks')
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

class AnswerQuestions(FlaskForm):
    answer = StringField()
    submit = SubmitField('Answer')
    next = SubmitField('Next')

class AddTheme(FlaskForm):
    name = StringField('Theme')
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

class AddTest(FlaskForm):
    theme = IntegerField('Id of theme', validators=[DataRequired()])
    question = TextAreaField('Question', validators=[DataRequired()])
    answer = StringField('Right answer', validators=[DataRequired()])
    explanation = TextAreaField('Explanation', validators=[DataRequired()])
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')