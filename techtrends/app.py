import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys


# Function for logging to file and console
def custom_logger (name):

      logger = logging.getLogger()
      logFormatter = logging.Formatter(fmt=' %(name)s - %(levelname)s - %(asctime)s -%(message)s ',datefmt='%d-%m-%Y:%H:%M:%S')

# Set up the console handler
      consoleHandler = logging.StreamHandler(stream=sys.stdout)
      consoleHandler.setFormatter(logFormatter)
      logger.addHandler(consoleHandler)
# Set up the file handler 
      fileHandler = logging.FileHandler("app.log")
      fileHandler.setFormatter(logFormatter)
      logger.addHandler(fileHandler)  
# Set up logging levels
      consoleHandler.setLevel(logging.DEBUG)
      fileHandler.setLevel(logging.DEBUG)
      logger.setLevel(logging.DEBUG)
      return logger

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    app.config["Connection_Count"]= app.config["Connection_Count"]+1
    return connection
def check_db_connection():
    try:
     connection = sqlite3.connect('database.db')
     connection.row_factory = sqlite3.Row
     post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    except sqlite3.Error as er:
     app.logger.error('SQLite error: %s' % (' '.join(er.args)))
     return "Unhealthy"
    return "ok"
# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config["Connection_Count"]=0
app.config['DEBUG'] = True

def get_postcount():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    connection.close()
    app.logger.info("status request successful"+str(post_count[0]))
    return post_count[0]


# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info("A non-existing article is accessed and a 404 page is returned.")
      return render_template('404.html'), 404
    else:
      app.logger.info("An existing Article: \""+str(post["Title"])+"\" is retrieved")
      return render_template('post.html', post=post)
      

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("About Page is retrieved ")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info("A new Article: \""+title+"\" is created") 
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route("/healthz")
def status():
     
   if check_db_connection()=='ok':
      response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
      )
      app.logger.info("status request successful")
      return response
   else:
      response = app.response_class(
            response=json.dumps({"result":"Error - Unhealthy"}),
            status=500,
            mimetype='application/json'
      )
      app.logger.info("status unhealthy")
      return response
     #return Response("{'result':'OK-Healthy'}", status=200, mimetype='application/json')
@app.route("/metrics")
def metrics():
 # response=json.dumps({"data":{"post count":"{0}".format(app.config["Connection_Count"]),"number of connection":"{1}".format(get_PostCount())}})

    response = app.response_class(
            #response=json.dumps({"data":{"post count":'0',"number of connection":'1'}}),
            response=json.dumps({"data":{"post count":"{0}".format(get_postcount()),"connection count":"{0}".format(app.config["Connection_Count"])}}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info("status request successful")
    return response
    
#return Response("{'data':{'usercount':150,'usercountactive':130}}", status=200, mimetype='application/json')

# start the application on port 3111
if __name__ == "__main__":
      custom_logger('TechTrendApp')
      app.run(host='0.0.0.0', port='3111')
     
   
