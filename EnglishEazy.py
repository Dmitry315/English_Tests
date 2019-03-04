from forms import *
from models import *


# init data bases from models
db.create_all()

def abort_if_user_not_found(id):
    if not UserModel.query.filter_by(id = id):
        abort(404, message="User {} not found".format(id))

def abort_if_test_not_found(id):
    if not TestModel.query.filter_by(id=id):
        abort(404, message="Test {} not found".format(id))

# API classes
class User(Resource):
    def get(self, id):
        abort_if_user_not_found(id)
        user = UserModel.query.filter_by(id=id).first()
        return jsonify({'user': user})

class UserList(Resource):
    def get(self):
        users = UserModel.query.all()
        return jsonify({'users': users})

class Tests(Resource):
    def get(self, id):
        abort_if_test_not_found(id)
        test = TestModel.query.filter_by(id=id)
        return jsonify({'test': test})

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

# show categories of tests
@app.route('/tests')
def show_themes():
    is_loged = check_session()
    if not is_loged and is_loged == admin['login']:
        return redirect('/log_in')
    themes = Theme.query.all()
    user = UserModel.query.filter_by(username=is_loged).first()
    return render_template('themes.html', themes=themes, user=user)

# show all tests in thic category
@app.route('/test/all/<int:id>')
def show_all_tests(id):
    is_loged = check_session()
    if not is_loged and is_loged == admin['login']:
        return redirect('/log_in')
    tests = TestModel.query.filter_by(id=id).all()
    user = UserModel.query.filter_by(username=is_loged).first()
    if not tests:
        abort(404)
    return render_template('all_tests.html', tests=tests, user=user)

# make quiz from random tasks
@app.route('/test/random/<int:id>', methods=['GET', 'POST'])
def show_tests_random(id):
    is_loged = check_session()
    if not is_loged and is_loged == admin['login']:
        return redirect('/log_in')
    user = UserModel.query.filter_by(username=is_loged).first()
    form = AnswerQuestions()
    form.answer.errors = []
    tests = TestModel.query.filter_by(id=id).all()
    if not tests:
        abort(404)
    if form.validate_on_submit() and form.submit.data:
        answer = request.form['answer']
        test = TestModel.query.filter_by(id=session['test_id']).first()
        right_answers = [i.strip() for i in test.right_answer.split('||')]
        if answer not in right_answers:
            form.answer.errors = ['No, right answer is']
        return render_template('test.html', test=test, form=form, next=True,
                               right_answers='or'.join(right_answers), user=user)

    test = choice(list(TestModel.query.filter_by(theme_id=id)))
    session['test_id'] = test.id
    return render_template('test.html', test=test, form=form, next=False, right_answers=[], user=user)

###########
# TEACHER #
###########
@app.route('/test/<int:id>')
def show_test(id):
    is_loged = check_session()
    if not is_loged or is_loged == admin['login']:
        return redirect('/log_in')
    user = UserModel.query.filter_by(username=is_loged).first()
    if not user.is_teacher or is_loged == admin['login']:
        abort(403)  # only teachers can edit tests
    test = str(TestModel.query.filter_by(id=id).first())
    return test

@app.route('/test/delete/<int:id>')
def test_delete(id):
    is_loged = check_session()
    if not is_loged or is_loged == admin['login']:
        return redirect('/log_in')
    user = UserModel.query.filter_by(username=is_loged).first()
    if not user.is_teacher:
        abort(403)  # only teachers can edit tests
    db.session.delete(TestModel.query.filter_by(id=id))
    db.session.commit()
    return redirect('/test_editor')

# delete themes is very dangerous
# it might cause database error
# because theme connected with tests
@app.route('/theme/edit/<int:id>', methods=['GET', 'POST'])
def theme_edit(id):
    is_loged = check_session()
    if not is_loged or is_loged == admin['login']:
        return redirect('/log_in')
    user = UserModel.query.filter_by(username=is_loged).first()
    if not user.is_teacher :
        abort(403)  # only teachers can edit tests
    theme = Theme.query.filter_by(id=id)
    form = AddTheme()
    if form.validate_on_submit() or form.cancel.data:
        if form.cancel.data:
            return redirect('/test_editor')
        name = request.form['name']
        theme.name = name
        db.session.commit()
        return redirect('/test_editor')
    return render_template('theme_edit.html', form=form)

@app.route('/theme/add', methods=['GET', 'POST'])
def theme_add():
    is_loged = check_session()
    if not is_loged and is_loged != admin['login']:
        return redirect('/log_in')
    user = UserModel.query.filter_by(username=is_loged).first()
    if not user.is_teacher or is_loged == admin['login']:
        abort(403)  # only teachers can edit tests
    form = AddTheme()
    if form.validate_on_submit() or form.cancel.data:
        if form.cancel.data:
            return redirect('/test_editor')
        name = request.form['name']
        theme = Theme(name=name)
        db.session.add(theme)
        db.session.commit()
        return redirect('/test_editor')
    return render_template('theme_edit.html', form=form)

@app.route('/test/add', methods=['GET', 'POST'])
def test_add():
    is_loged = check_session()
    if not is_loged or is_loged == admin['login']:
        return redirect('/log_in')
    user = UserModel.query.filter_by(username=is_loged).first()
    if not user.is_teacher:
        abort(403)  # only teachers can edit tests
    # test = TestModel.query.filter_by(id=id)
    themes = Theme.query.all()
    form = AddTest()
    if form.validate_on_submit() or form.cancel.data:
        form.theme.errors = []
        if form.cancel.data:
            return redirect('/test_editor')
        theme = request.form['theme']
        question = request.form['question']
        answer = request.form['answer']
        explanation = request.form['explanation']
        theme_model = Theme.query.filter_by(name=theme).first()
        if theme_model:
            test = TestModel(question=question, right_answer=answer,
                             explanation=explanation, author_id=user.id)
            theme_model.TestModel.append(test)
            db.session.commit()
            return redirect('/test_editor')
    return render_template('test_edit.html', form=form, themes=themes)

@app.route('/test/edit/<int:id>', methods=['GET', 'POST'])
def test_edit(id):
    is_loged = check_session()
    if not is_loged or is_loged == admin['login']:
        return redirect('/log_in')
    user = UserModel.query.filter_by(username=is_loged).first()
    if not user.is_teacher:
        abort(403)  # only teachers can edit tests
    test = TestModel.query.filter_by(id=id)
    form = AddTest()
    themes = Theme.query.all()
    if form.validate_on_submit() or form.cancel.data:
        form.theme.errors = []
        if form.cancel.data:
            return redirect('/test_editor')
        theme = request.form['theme']
        question = request.form['question']
        answer = request.form['answer']
        explanation = request.form['explanation']
        theme_model = Theme.query.filter_by(name=theme).first()
        if theme_model:
            test2 = TestModel(question=question, right_answer=answer,
                             explanation=explanation, author_id=user.id)
            theme_model.TestModel.append(test2)
            db.session.delete(test)
            db.session.commit()
            return redirect('/test_editor')
    return render_template('test_edit.html', form=form, themes=themes)

@app.route('/test_editor')
def edit_tests():
    is_loged = check_session()
    if not is_loged or is_loged == admin['login']:
        return redirect('/log_in')
    user = UserModel.query.filter_by(username=is_loged).first()
    if not user.is_teacher:
        abort(403) # only teachers can edit tests
    tests = TestModel.query.all()
    themes = Theme.query.all()
    return render_template('test_editor.html', tests=tests, themes=themes)

# show user's profile (allowed for all users)
@app.route('/profile/<int:id>')
def profile(id):
    user = UserModel.query.filter_by(id=id).first()
    if not user:
        abort(404)
    return render_template('profile.html', user=user, is_user=(check_session() in [user.get_name(), admin['login']]))

# users can edit their profile (allowed for this user or admin)
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

###############
# ADMIN STUFF #
###############
# admin can delete account
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

# change student to teacher and teacher to student (default: student)
@app.route('/admin/switch_status/<int:id>')
def switch_status(id):
    is_loged = check_session()
    if is_loged == admin['login']:
        user = UserModel.query.filter_by(id=id).first()
        if not bool(user):
            return redirect('/admin/tool_bar')
        user.is_teacher = not user.is_teacher
        db.session.commit()
    return redirect('/admin/tool_bar')

# admin can add new user from tool bar
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
            form.login.errors = ['User with this login already exist.']
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

# render admin tool bar
# if user not loged as admin
# redirect to authorisation
@app.route('/admin/tool_bar')
def admin_tool_bar():
    is_loged = check_session()
    if is_loged != admin['login']:
        return redirect('/admin/log_in')
    model =  UserModel.query.all()
    return render_template('admin.html', model=model)

# authorisation of admin
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

###########################################
# USER  LOG IN - LOG OUT - SIGN IN  STUFF #
###########################################

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
            is_teacher=False
        ))
        db.session.commit()
        return redirect('/log_in')
    return render_template('sign_in.html', form=form)

if __name__ == '__main__':
    # run server on address: 127.0.0.1:8000
    app.run(port='8000', host='127.0.0.1')
