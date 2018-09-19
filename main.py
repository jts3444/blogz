from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy # Python ORM
from sqlalchemy import create_engine, inspect

app = Flask(__name__)
app.config["DEBUG"] = True  # set to True for Flask report on web server activity
app.config["SQLALCHEMY_ECHO"] = False   # set True for MySQL report on database activity

# put in your database credentials here
username = "build-a-blog"
password = "buildablog"
host = "localhost"
port = "8889"
database = "build-a-blog"

connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

app.config["SQLALCHEMY_DATABASE_URI"] = connection_string
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app) # uses the SQLAlchemy Database URI (connection string) to connect to the db
db_session = db.session # used for interaction with the database

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(360))
    completed = db.Column(db.Boolean)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

    
@app.route('/blog')
def b_display():
    
    blogs = Blog.query.filter_by().all()
    completed_blogs = Blog.query.filter_by(completed=False).all()
    return render_template('blog.html',title="New Blog Post", 
        blogs=blogs, completed_blogs=completed_blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title_name = request.form['title']
        body_text = request.form['body']
        new_post = Blog(title_name, body_text)
        db.session.add(new_post)
        db.session.commit()

    return render_template('newpost.html', title="New Blog Entries")

def main():
    ENGINE = create_engine(connection_string)
    INSPECTOR = inspect(ENGINE)  # used for checking if tables exist on startup

    tables = INSPECTOR.get_table_names()
    if not tables:
        db.create_all()

    app.run()
      
if __name__ == '__main__':
    main()