from forms import SignInForm, LoginForm
from models import *

db.create_all()



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
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
            if password != str(user).split()[2]:
                form.password.errors = ['Wrong password']

        if not form.login.errors and not form.password.errors:
            return redirect('/')
    return render_template('login.html', form=form)

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
        user = UserModel.query.filter_by(username = login).first()
        if bool(user):
            form.login.errors = ['User with this login already exsist.']
            return render_template('sign_in.html', form=form)
        if password != re_password:
            form.re_password.errors = ['Your passwords differ.']
            return render_template('sign_in.html', form=form)
        db.session.add(UserModel(
            username=login,
            password=password,
        ))
        db.session.commit()
        return redirect('/login')
    return render_template('sign_in.html', form=form)

if __name__ == '__main__':
    app.run(port='8000', host='127.0.0.1')
