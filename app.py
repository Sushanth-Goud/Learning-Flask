import os
from flask import Flask,render_template,request,redirect,session
from flask_session import Session
import sqlite3
from waitress import serve

app=Flask(__name__)

app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
app.config["SESSION_FILE_DIR"] = "/tmp/flask_session"
Session(app)

SPORTS=['Football','Badminton','TT']

def get_db_connection(x):
	conn=sqlite3.connect(x)
	conn.row_factory=sqlite3.Row
	return conn

def init_db():
	conn=get_db_connection("registrants.db")
	conn.execute("create table if not exists registrants(name text not null, sport text not null)")
	conn.commit
	conn.close()

	conn=get_db_connection("books.db")
	conn.execute("Create table if not exists books(id integer primary key autoincrement, title text not null)")
	check=conn.execute('Select count(*) from books').fetchone()
	if check[0]==0:
		conn.execute("Insert into books(title) values (?,?,?)",('The Hobbit','1984','To Kill a Mockingbird'))
	conn.close()

init_db()

@app.route('/')
def index():
	return render_template('index.html',sports=SPORTS)

@app.route('/success',methods=['GET','POST'])
def success():
	name=request.form.get("name")
	sport=request.form.get("sport")
	
		
	if not name:
		return render_template('error.html',message='No name?')
	if sport not in SPORTS:
		return render_template('error.html',message='Sport?')

	conn=get_db_connection('registrations.db')
	conn.execute(
		'Insert into registrants (name,sport) values (?,?)',(name,sport)
		)
	conn.commit()
	conn.close()

	return render_template('success.html',name=name)
@app.route("/registrants")
def registrants():
	conn=get_db_connection('registrations.db')
	rows=conn.execute('Select name,sport from registrants').fetchall()
	conn.close()
	return render_template('registrants.html',registrants=rows)

@app.route("/shopping",methods=['GET','POST'])
def shopping():
	logid=session.get('name')
	if not logid:
		return redirect("/")
	if "cart" not in session:
		session["cart"]=[]
	book_id=request.form.get("title")
	if book_id:
		session['cart'].append(book_id)
	

	conn=get_db_connection('books.db')
	rows=conn.execute('Select id,title from books').fetchall()
	conn.close()
	

	return render_template("shopping.html",name=logid,data=rows)

@app.route("/login",methods=['GET','POST'])
def login():
	if request.method=='POST':
		name=request.form.get("login")
		session['name']=name
		return redirect("/shopping")

	return render_template("login.html")

@app.route("/cart",methods=["POST",'get'])
def cart():
	if 'cart' in session:
		data=session.get("cart")
	else:
		data=[]
	return render_template("cart.html",data=data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__=="__main__":
	port=int(os.environ.get('PORT',5000))
	serve(app,host="0.0.0.0",port=port)


