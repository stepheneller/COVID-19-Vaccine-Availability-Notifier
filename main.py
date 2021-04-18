from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR SECRET KEY'
Bootstrap(app)

# Connect to DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'YOUR DATABASE LOCATION'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Configure Table
class SearchParameters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    moderna = db.Column(db.Boolean, nullable=False)
    pfizer = db.Column(db.Boolean, nullable=False)
    johnson_and_johnson = db.Column(db.Boolean, nullable=False)
    zip_code = db.Column(db.String(5), nullable=False)
    radius = db.Column(db.String(2), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)


# Line below required only once when creating DB
# db.create_all()

# WTF Form
class CreateNewNotification(FlaskForm):
    moderna = BooleanField("Moderna COVID Vaccine")
    pfizer = BooleanField("Pfizer-BioNTech COVID Vaccine")
    johnson_and_johnson = BooleanField("Johnson & Johnson's Janssen COVID Vaccine")
    zip_code = StringField("Type a 5-Digit Zip Code",
                           validators=[DataRequired(), Length(min=5, max=5, message='Must be 5 digits')])
    radius = SelectField(u"Search Radius", choices=['1 mile', '5 miles', '10 miles', '25 miles', '50 miles'])
    email = StringField("Enter your email address", validators=[DataRequired(), Email()])
    submit = SubmitField("Sign Up")


@app.route('/', methods=["GET", "POST"])
def show_form():
    message = None
    error = None
    form = CreateNewNotification()
    if request.method == "GET":
        return render_template("index.html", form=form, message=message, error=error)

    if request.method == "POST" and form.validate_on_submit() and \
            request.form.get("moderna") is None and request.form.get("pfizer") is None and \
            request.form.get("johnson_and_johnson") is None:
        error = "Please select at least one vaccine."
        return render_template("index.html", form=form, message=message, error=error)

    if request.method == "POST" and form.validate_on_submit():

        moderna_bool = True if request.form.get("moderna") == 'y' else False
        pfizer_bool = True if request.form.get("pfizer") == 'y' else False
        j_and_j_bool = True if request.form.get("johnson_and_johnson") == 'y' else False

        existing_notification = SearchParameters.query.filter_by(email=request.form.get("email")).first()

        if existing_notification is not None:
            notification_to_update = SearchParameters.query.filter_by(email=request.form.get("email")).first()
            notification_to_update.moderna = moderna_bool
            notification_to_update.pfizer = pfizer_bool
            notification_to_update.johnson_and_johnson = j_and_j_bool
            notification_to_update.zip_code = request.form.get("zip_code")
            notification_to_update.radius = request.form.get("radius").split(" ")[0]

            db.session.commit()

            message = "Your preferences have been updated."

            return render_template("index.html", form=form, message=message, error=error)

        new_notification = SearchParameters(
            moderna=moderna_bool,
            pfizer=pfizer_bool,
            johnson_and_johnson=j_and_j_bool,
            zip_code=request.form.get("zip_code"),
            radius=request.form.get("radius").split(" ")[0],
            email=request.form.get("email")
        )
        db.session.add(new_notification)
        db.session.commit()

        message = "Your preferences have been recorded."

        return render_template("index.html", form=form, message=message, error=error)

    return render_template("index.html", form=form, message=message, error=error)


@app.route('/<email>/', methods=['POST'])
def delete_notification(email):
    existing_notification = SearchParameters.query.filter_by(email=email.first())
    db.session.delete(existing_notification)
    db.session.commit()

    return render_template("unsubscribed.html")


if __name__ == '__main__':
    app.run(debug=True)
