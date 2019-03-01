from forms import *
from models import *


# init data bases from models
db.create_all()

# return user's login if session is not empty
def check_session():
    try:
        if not(UserModel.query.filter_by(username=session['username']).first()) and session['username'] != admin['login']:
            session['username'] = None
        return session['username']
    except KeyError as err:
        return False

# home page with nav bar
# if session is empty redirect to log in
@app.route('/')
def home():
    is_loged = check_session()
    if not is_loged or is_loged == admin['login']:
        return redirect('/log_in')
    return render_template('home.html', user=UserModel.query.filter_by(username=is_loged).first())

@app.route('/profile/<int:id>')
def profile(id):
    user = UserModel.query.filter_by(id=id).first()
    if not user:
        abort(404)
    return render_template('profile.html', user=user, is_user=(check_session() in [user.get_name(), admin['login']]))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    is_loged = check_session()
    if not is_loged:
        return redirect('/log_in')
    user = UserModel.query.filter_by(id=id).first()
    if is_loged != user.get_name() and is_loged != admin['login']:
        abort(403)
    form = ProfileEdit()
    is_success = False
    if form.validate_on_submit():
        if form.cancel.data:
            return redirect('/profile/'+str(id))
        is_success = True
        about = request.form['about']
        links = request.form['links']
        user.about = about
        user.links = links
        db.session.commit()
    return render_template('edit.html', user=user, form=form, is_success=is_success)

# remove user from session
# and redirect to log in
@app.route('/log_out')
def log_out():
    session['username'] = None
    return redirect('/log_in')

@app.route('/admin/delete_user/<int:id>')
def delete_user(id):
    is_loged = check_session()
    if is_loged == admin['login']:
        user = UserModel.query.filter_by(id = id).first()
        if not bool(user):
            return redirect('/admin/tool_bar')
        db.session.delete(user)
        db.session.commit()
    return redirect('/admin/tool_bar')

@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    is_loged = check_session()
    if is_loged != admin['login']:
        return redirect('/admin/log_in')
    form = AddUser()
    if form.validate_on_submit():
        login = request.form['login']
        password = request.form['password']
        form.login.errors = []
        form.password.errors = []
        user = UserModel.query.filter_by(username=login).first()
        if bool(user) or login == admin['login']:
            form.login.errors = ['User with this login already exsist.']
            return render_template('add_user.html', form=form)
        if not form.login.errors and not form.password.errors:
            db.session.add(UserModel(
                username=login,
                password=password,
                about='',
                links='',
            ))
            db.session.commit()
            return redirect('/admin/tool_bar')
    return render_template('add_user.html', form=form)


@app.route('/admin/tool_bar')
def admin_tool_bar():
    is_loged = check_session()
    if is_loged != admin['login']:
        return redirect('/admin/log_in')
    model =  UserModel.query.all()
    return render_template('admin.html', model=model)

@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/log_in', methods=['GET', 'POST'])
def admin_login():
    is_loged = check_session()
    if is_loged == admin['login']:
        return redirect('/admin/tool_bar')
    form = LoginForm()
    if form.validate_on_submit():
        login = request.form['login']
        password = request.form['password']
        form.login.errors = ['Wrong login']
        form.password.errors = []
        if login == admin['login']:
            form.login.errors = []
            if password != admin['password']:
                form.password.errors = ['Wrong password']
        if not form.login.errors and not form.password.errors:
            session['username'] = 'admin'
            return redirect('/admin/tool_bar')
    return render_template('login.html', form=form, is_admin=True)

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
    return render_template('login.html', form=form, is_admin=False)

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
        if bool(user) or login == admin['login']:
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
