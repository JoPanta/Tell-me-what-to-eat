from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash


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


@app.route("/", methods=["GET", 'POST'])
def home():
    example_food = ExampleFood.query.all()

    return render_template("base.html", example_food=example_food)


if __name__ == '__main__':
    app.run(debug=True)