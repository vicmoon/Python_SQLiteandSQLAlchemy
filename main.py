from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import my_secrets

app = Flask(__name__)

app.config['SECRET_KEY'] = my_secrets.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books-collection.db"

# Define base class for ORM
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Define a model
class Book(db.Model):
    id = Column(Integer, primary_key=True)  # Fix: Add Primary Key
    title = Column(String(250), nullable=False, unique=True)
    author = Column(String(250), nullable=False)

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"

# Create tables
with app.app_context():
    db.create_all()

# WTForms form for adding books
class NewBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    submit = SubmitField('Add')

# Home Route
@app.route('/', methods=['GET'])
def home():
    books = Book.query.all()  # Fix: Fetch books from database
    return render_template('index.html', books=books)

# Add Book Route
@app.route("/add", methods=['GET', 'POST'])
def add():
    form = NewBookForm()
    if form.validate_on_submit():
        new_book = Book(title=form.title.data, author=form.author.data)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=form)

# Update Book Route
@app.route("/update/<int:book_id>", methods=['POST', 'PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    if book:
        book.author = "J.K. Rowling (Updated)"
        db.session.commit()
        return redirect(url_for("home"))
    return "Book not found", 404

# Delete Book Route
@app.route("/delete/<int:book_id>", methods=['POST', 'DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for("home"))
    return "Book not found", 404

if __name__ == "__main__":
    app.run(debug=True)
