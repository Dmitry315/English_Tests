from forms import SignInForm, LoginForm
from models import *


# init data bases from models
db.create_all()

# return user's login if session is not empty
def check_session():
    try:
        if not(UserModel.query.filter_by(username=session['username']).first()):
            session['username'] = None
        return session['username']
    except KeyError as err:
        return False

# home page with nav bar
# if session is empty redirect to log in
@app.route('/')
def home():
    is_loged = check_session()
    if not is_loged:
        return redirect('/log_in')
    return render_template('home.html', user=UserModel.query.filter_by(username=is_loged).first())

@app.route('/profile/<int:id>')
def profile(id):
    is_loged = check_session()
    if not is_loged:
        return redirect('/log_in')
    return render_template('profile.html', user=UserModel.query.filter_by(id=id).first())

# remove user from session
# and redirect to log in
@app.route('/log_out')
def log_out():
    session['username'] = None
    return redirect('/log_in')

# insert user in session
# and redirect to home page
@app.route('/log_in', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = request.form['login']
        password = request.form['password']
        form.login.errors = ['Wrong login']
        form.password.errors = []
        user = UserModel.query.filter_by(username = login).first()
        if bool(user):
            form.login.errors = []
            if password != user.get_password():
                form.password.errors = ['Wrong password']
        if not form.login.errors and not form.password.errors:
            session['username'] = login
            return redirect('/')
    return render_template('login.html', form=form)

# sign user in system
# and redirect to authorisation
@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = SignInForm()
    if form.validate_on_submit():
        form.login.errors = []
        form.password.errors = []
        form.re_password.errors = []
        login = request.form['login']
        password = request.form['password']
        re_password = request.form['re_password']
        # try to pull user from date
        # to check login
        user = UserModel.query.filter_by(username = login).first()
        # check input information
        if bool(user):
            form.login.errors = ['User with this login already exsist.']
            return render_template('sign_in.html', form=form)
        if password != re_password:
            form.re_password.errors = ['Your passwords differ.']
            return render_template('sign_in.html', form=form)
        # add user to date base and commit changes
        db.session.add(UserModel(
            username=login,
            password=password,
            about='',
            links='',
        ))
        db.session.commit()
        return redirect('/log_in')
    return render_template('sign_in.html', form=form)

if __name__ == '__main__':
    app.run(port='8000', host='127.0.0.1')
