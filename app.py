from flask import Flask, request, render_template,session, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'   
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,name,email,password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
        
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign_up',methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        #handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('sign_up.html', error="Email already in use.")

        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    
    return render_template('sign_up.html')

@app.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
       email = request.form['email']
       password = request.form['password'] 

       # Query the database for the user
       user = User.query.filter_by(email=email).first()

       # Check if the user exists and verify the password
       if user and user.check_password(password):
        session['email'] = user.email
        session['name'] = user.name  # Store name in the session
        return redirect('/appointment')
       else:
           # Display an error if user not found or password doesn't match
           return render_template('login.html',error='user not found')
       
     # Render the login page for GET requests
    return render_template('login.html')

@app.route('/appointment')
def appointment():
    if 'email' in session:     # Check if user is logged in
        user = User.query.filter_by(email=session['email']).first()
        return render_template('appointment.html',user=user)
    return redirect('/login')     # If not logged in, redirect to login

@app.route('/logout')
def logout():
   session.pop('email',None)
   return redirect('/login')
   
@app.route("/about_us")
def about_us():
    return render_template('about_us.html')

@app.route('/our_doctors')
def our_doctors():
    return render_template('our_doctors.html')

if __name__ == "__main__":
    app.run(debug=True)