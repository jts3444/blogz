from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy # Python ORM
from sqlalchemy import create_engine, inspect

app = Flask(__name__)
app.config["DEBUG"] = True  # set to True for Flask report on web server activity
app.config["SQLALCHEMY_ECHO"] = False   # set True for MySQL report on database activity

# put in your database credentials here
username = "blogz"
password = "blogz"
host = "localhost"
port = "8889"
database = "blogz"

connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

app.config["SQLALCHEMY_DATABASE_URI"] = connection_string
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app) # uses the SQLAlchemy Database URI (connection string) to connect to the db
db_session = db.session # used for interaction with the database
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(360))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

#does the checking for the password and userinfo
#also works if userinfo is blank
def valid_content(userinfo):
    if len(userinfo) > 20 or len(userinfo) < 3:
        return False
    return True

# ensures user can't post a blog w/o logging in, only allows listed pages to be pulled up
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'b_display', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

# home page, displays all the blog authors
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', 
        users=users)
    
@app.route('/blog')
def b_display():
    
    #handles blog display for one post
    blog_id = request.args.get('id')
    if (blog_id):
        post = Blog.query.get(blog_id)
        return render_template('blog_post.html', post = post)

    # handles display of blogs by user
    user_id = request.args.get('userid')
    if (user_id):
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        user = User.query.filter_by(id = user_id).first()
        return render_template('user.html', user = user, blogs = blogs)
    
    # handles display for all posts
    blogs = Blog.query.filter_by().all()
    return render_template('blog.html', 
        blogs=blogs)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        # if there's a user and the password matches what's in the table, begins session and shows
        # that the user is logged in, else an error displays
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    # if post method, gets data from form and conducts checks to see if the data is valid
    # displays error messages if it's incorrect
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(email=email).first()

        if not valid_content(email) or not valid_content(password):
            flash("Invalid e-mail or password, must be between 3 and 20 characters", 'error')
        elif verify != password:
            flash("Password and verification do not match", 'error')
        elif valid_content(email) and valid_content(password) and verify == password and not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/newpost')
        else:
            flash("User already exists, please login", 'error')

    return render_template('signup.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title_name = request.form['title']
        body_text = request.form['body']
        owner = User.query.filter_by(email=session['email']).first()
        
        # checks if there's no text entered in title or body
        if title_name == '':
            flash("Please enter a title", 'error')
        if body_text == '':
            flash("Please enter content for your blog post", 'error')

        # with no errors, a new blog post is created and committed to the database
        if title_name != '' and body_text != '':
            new_post = Blog(title_name, body_text, owner)
            db.session.add(new_post)
            db.session.commit()

        # gets the new post's table id and assigns to variable
            post_id = str(new_post.id)
        
        # after user submits new post, redirects to blog post
            return redirect(f"/blog?id={post_id}") 
    
    # else, for get requests
    return render_template('newpost.html', title = "Add a Blog Entry")

@app.route('/logout')
def logout():
    del session['email']
    flash("Logged Out")
    return redirect('/')

def main():
    ENGINE = create_engine(connection_string)
    INSPECTOR = inspect(ENGINE)  # used for checking if tables exist on startup

    tables = INSPECTOR.get_table_names()
    if not tables:
        db.create_all()

    app.run()
      
if __name__ == '__main__':
    main()