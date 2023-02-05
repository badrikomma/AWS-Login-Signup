import sqlite3

from flask import Flask, request, g, render_template, send_file

DATABASE = '/var/www/html/flaskapp/example.db'

app = Flask(__name__)
app.config.from_object(__name__)

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def query_db(query, args=()):
    cursor = get_db().execute(query, args)
    rows = cursor.fetchall()
    cursor.close()
    return rows

@app.route("/")
def initial():
    query_db("DROP TABLE IF EXISTS users")
    query_db("CREATE TABLE users (Username text, Password text, firstname text, lastname text, email text, count integer)")
    return render_template('index.html')

@app.route('/login', methods =['POST', 'GET'])
def login():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) != "":
        res = query_db("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (str(request.form['username']), str(request.form['password']) ))
        print(res)
        if res:
            for r in res:
                return responsePage(r[0], r[1], r[2], r[3])
        else:
            message = 'Invalid Credentials !'
    elif request.method == 'POST':
        message = 'Please enter Credentials'
    return render_template('index.html', message = message)


@app.route("/download")
def download():
    return send_file("Limerick.txt", as_attachment=True)

@app.route('/registration', methods =['GET', 'POST'])
def registration():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) !="" and str(request.form['firstname']) !="" and str(request.form['lastname']) !="" and str(request.form['email']) !="":
        un = str(request.form['username'])
        pw = str(request.form['password'])
        fn = str(request.form['firstname'])
        ln = str(request.form['lastname'])
        em = str(request.form['email'])
        uf = request.files['textfile']
        if not uf:
            filename = null
            wc = null
        else :
            filename = uf.filename
            wc = countOfWords(uf)
        result = query_db("""SELECT *  FROM users WHERE Username  = (?)""", (un, ))
        if result:
            message = 'User has already registered!'
        else:
            r1 = query_db("""INSERT INTO users (username, password, firstname, lastname, email, count) values (?, ?, ?, ?, ?, ? )""", (un, pw, fn, ln, em, wc, ))
            get_db().commit()
            r2 = query_db("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (un, pw ))
            if r2:
                for r in r2:
                    return responsePage(r[0], r[1], r[2], r[3])
    elif request.method == 'POST':
        message = 'Some of the fields are missing!'
    return render_template('registration.html', message = message)

def countOfWords(file):
    temp = file.read()
    length = temp.split()
    return str(len(length))

def responsePage(fn, ln, em, c):
    return """ First Name :  """ + str(fn) + """ <br> Last Name : """ + str(ln) + """ <br> Email : """ + str(em) + """ <br> Word Count : """ + str(c) + """ <br><br> <a href="/download" >Download</a> """

if __name__ == '__main__':
  app.run()

