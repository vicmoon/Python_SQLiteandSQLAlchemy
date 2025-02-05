from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
app = Flask(__name__)

all_books = []

app.config['SECRET_KEY'] = "230853496459jgirfngdf8"

class newBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    submit = SubmitField('Add')



@app.route('/')
def home():
    return render_template('index.html', books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = newBookForm()

    if form.validate_on_submit():
        title = form.title.data
        author = form.author.data

        all_books.append({"title": title, "author": author})
         
        return redirect(url_for("home"))

    return render_template("add.html", form=form)



    


if __name__ == "__main__":
    app.run(debug=True)

