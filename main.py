from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import random




app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
Bootstrap5(app)


# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
db = SQLAlchemy()
db.init_app(app)


# User database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    food = db.relationship("Food", backref='user', lazy=True)


# food database
class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    recipe = db.Column(db.String(2000), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)


class ExampleFood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    recipe = db.Column(db.String(2000), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)

#
# with app.app_context():
#     db.create_all()
#
# with app.app_context():
#     new_example_food = ExampleFood(name="One-pan cheat’s lamb meatball casserole", recipe="Using pre-seasoned lamb sausages and canned chickpeas makes this one-pan dish as easy as could be.",
#                                    img_url="https://img.taste.com.au/Zr8d3MEd/w643-h428-cfill-q90/taste/2021/05/one-pan-cheatys-lamb-meatball-chickpea-casserole-171436-2.jpg")
#     db.session.add(new_example_food)
#     db.session.commit()


class RegisterForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired()])
    name = StringField("Name:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])

    submit = SubmitField("Sign Me Up!")


class MealForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    recipe = StringField("Recipe:")
    img_url = StringField("Image Link:", validators=[DataRequired()])

    submit = SubmitField("Add!")


class LoginForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


@app.route("/", methods=["GET", 'POST'])
def home():
    example_food = ExampleFood.query.all()

    return render_template("index.html", example_food=example_food)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # check if the user is already in the database
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/add_meal/<int:user_id>', methods=["GET", "POST"])
def add_meal(user_id):
    form = MealForm()
    if form.validate_on_submit():

        name = form.name.data
        recipe = form.recipe.data
        img_url = form.img_url.data

        new_food = Food(user_id=user_id, name=name, recipe=recipe, img_url=img_url)
        db.session.add(new_food)
        db.session.commit()

        session['form_submitted'] = True

        return redirect(url_for('add_meal', user_id=user_id))

    form_submitted = session.pop('form_submitted', False)

    return render_template('add_food.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            print(user)
            print(current_user)
            return redirect(url_for('home'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/menu/<int:user_id>', methods=["GET", "POST"])
@login_required
def show_menu(user_id):
    menu = Food.query.filter_by(user_id=user_id).all()

    random.shuffle(menu)

    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    return render_template("menu.html", user_id=user_id, menu=menu, days_of_week=days_of_week)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)