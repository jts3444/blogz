from flask import Flask, request, redirect, render_template
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

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

    
@app.route('/blog')
def b_display():
    
    #handles blog display for one post
    blog_id = request.args.get('id')
    if (blog_id):
        post = Blog.query.get(blog_id)
        return render_template('blog_post.html', post = post)
    
    # handles display for all posts
    blogs = Blog.query.filter_by().all()
    return render_template('blog.html', 
        blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title_name = request.form['title']
        body_text = request.form['body']
        owner = User.query.filter_by(email=session['email']).first()

        title_error = ''
        text_error = ''
        
        # checks if there's no text entered in title or body
        if title_name == '':
            title_error = "Please enter a title"
        if body_text == '':
            text_error = "Please enter content for your blog post"
        
        # if there's an error, renders the template with error messages
        if title_error or text_error:
            return render_template('newpost.html', title_error=title_error, text_error=text_error)

        # with no errors, a new blog post is created and committed to the database
        new_post = Blog(title_name, body_text, owner)
        db.session.add(new_post)
        db.session.commit()

        # gets the new post's table id and assigns to variable
        post_id = str(new_post.id)
        
        # after user submits new post, redirects to blog post
        return redirect(f"/blog?id={post_id}") 
    
    # else, for get requests
    return render_template('newpost.html', title = "Add a Blog Entry")
    
def main():
    ENGINE = create_engine(connection_string)
    INSPECTOR = inspect(ENGINE)  # used for checking if tables exist on startup

    tables = INSPECTOR.get_table_names()
    if not tables:
        db.create_all()

    app.run()
      
if __name__ == '__main__':
    main()