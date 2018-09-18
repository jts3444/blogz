from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(360))
    completed = db.Column(db.Boolean)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.completed = False


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        title_name = request.form['title']
        body_text = request.form['body']
        new_post = Blog(title_name, body_text)
        db.session.add(new_post)
        db.session.commit()

    blogs = Blog.query.filter_by(completed=False).all()
    completed_tasks = Blog.query.filter_by(completed=True).all()
    return render_template('blog.html',title="New Blog Post", 
        blogs=blogs, completed_tasks=completed_tasks)

@app.route('/newpost')
def newpost():
    title = request.args.get('title')
    body = request.args.get('body')
    return render_template('blog.html', title = title, body = body)

if __name__ == '__main__':
    app.run()