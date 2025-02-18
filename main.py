from flask import Flask, render_template, request, redirect, url_for, Response
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
# from flask_login import current_user
from functools import wraps
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
# import my_secrets

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "baf3e1c5f9a7e8d3f2b4c5d1a2e9f8c7")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books-collection.db"
ADMIN_USERNAME = my_secrets.ADMIN_USERNAME
ADMIN_PASSWORD = my_secrets.ADMIN_PASSWORD 


def check_auth(username, password):
  return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def authenticate():
    """Sends a 401 response prompting for authentication."""
    return Response(
        "You need to login with proper credentials", 401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated




# Define base class for ORM
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class NewBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    submit = SubmitField('Add')

class EditBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    submit = SubmitField('Update')

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

# Home Route
@app.route('/', methods=['GET'])
def home():
    books = Book.query.all()  # Fix: Fetch books from database
    return render_template('index.html', books=books)

# Add Book Route
@app.route("/add", methods=['GET', 'POST'])
@requires_auth
def add():
    form = NewBookForm()
    
    if form.validate_on_submit():
        new_book = Book(title=form.title.data, author=form.author.data)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("home"))  # Redirect to home page
    return render_template("add.html", form=form)


# Update Book Route
@app.route("/edit/<int:book_id>", methods=['GET', 'POST'])
@requires_auth
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = EditBookForm(obj=book)

    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        db.session.commit()
        return redirect(url_for("home"))  # Redirect to home page

    return render_template('edit.html', form=form, book_id=book.id)

# Delete Book Route
@app.route("/delete/<int:book_id>", methods=['GET', 'POST'])
@requires_auth
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("home"))  # Redirect back to homepage

if __name__ == "__main__":
    app.run(debug=True)


""" Use http://127.0.0.1:5000/edit/<id number> to edit  """
""" Use http://127.0.0.1:5000/delete/<id number> to edit  """
""" If you want to add the buttons in index.html : 

  <!-- <td>
    <!-- Edit Button -->
  <a href="{{ url_for('update_book', book_id=book.id) }}">
    <button>Edit</button>
  </a>

  <!-- Delete Button -->
  <form
    action="{{ url_for('delete_book', book_id=book.id) }}"
    method="post"
    style="display: inline"
  >
    <button
      type="submit"
      onclick="return confirm('Are you sure you want to delete this book?')"
    >
      Delete
    </button>
  </form>
</td>
-->

"""