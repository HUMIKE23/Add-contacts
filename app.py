from flask import Flask, render_template, request, redirect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'jiuyersxdreser234567yufryrd###4yu7u8ufiutfdet65432'
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
admin = Admin(app, name='myadmin')

# MODELS START
class client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(30), nullable=False)

admin.add_view(ModelView(client, db.session))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    First_name = db.Column(db.String(15), nullable=False)
    Last_name = db.Column(db.String(15), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Phone = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return f'{self.First_name} {self.Last_name} {self.Email}'

# creates tables
with app.app_context():
    db.create_all()

# Flask-Admin setup
admin.add_view(ModelView(Contact, db.session))

# FORMS
class ContactForm(FlaskForm):
    First_name = StringField('First_name')
    Last_name = StringField('lastname')
    Email = StringField('email')
    Phone = IntegerField('phone')
    Submit = SubmitField('submit')

class RegisterForm(FlaskForm):
    username = StringField('username')
    password = PasswordField('password')
    submit = SubmitField('submit')


# VIEWS
@app.route('/login/', methods=['POST', 'GET'])
def login():
     if request.method == 'POST':
        username = request.form.get('usernmame')
        password = request.form.get('password')

        user = client.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return redirect('home')
        else:
            return render_template('login.html', Error='Invalid Username or Password!')

     return render_template('login.html')



@app.route('/register/', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        newclient = client(username=username, password=hashed_password)
        db.session.add(newclient)
        db.session.commit()

        return redirect('/home/')
    return render_template ('register.html', csrf=csrf, form=form)


@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/contacts/')
def contacts():
    contacts = Contact.query.all()
    return render_template('contacts.html', contacts=contacts)

@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    form = ContactForm()

    if form.validate_on_submit():
        new_contact = Contact(
            First_name=form.First_name.data,
            Last_name=form.Last_name.data,
            Email=form.Email.data,
            Phone=form.Phone.data
        )
        db.session.add(new_contact)
        db.session.commit()
        return render_template('home.html')

    return render_template('add_contact.html', form=form)

@app.route('/update_contact/<int:pk>', methods=['GET', 'POST'])
def update_contact(pk):
    contact = Contact.query.get(pk)
    form = ContactForm(obj=contact)

    if form.validate_on_submit():
        contact.First_name = form.First_name.data
        contact.Last_name = form.Last_name.data
        contact.Email = form.Email.data
        contact.Phone = form.Phone.data

        db.session.commit()
        return redirect('/contacts/')

    return render_template('update_contact.html', contact=contact, form=form)

@app.route('/delete_contact/<int:pk>', methods=['GET', 'POST'])
def delete_contact(pk):
    contact = Contact.query.get(pk)

    if contact is None:
        abort(404)

    if request.method == 'POST':
        db.session.delete(contact)
        db.session.commit()
        return redirect('/contacts')

    csrf_token = generate_csrf()
    return render_template('delete.html', contact=contact, csrf_token=csrf_token)





if __name__ == '__main__':
    app.run(debug=True)
