from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, g
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
db = SQLAlchemy(app)
app.secret_key='daffjsdfyi76487pa'

# executive uname=admin password = 12345
# cashier uname=cashier password = 12345


class LoginExec(db.Model):
    exec_name = db.Column(db.String(30), primary_key=True, nullable=False)
    exec_pass = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return 'Executive: ' + self.exec_name

class LoginCashier(db.Model):
    cash_name = db.Column(db.String(30), primary_key=True, nullable=False)
    cash_pass = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return 'Cashier: ' + self.cash_name

@app.before_request
def before_request():
    g.username=None
    if 'username' in session:
        g.username = session['username']
    

@app.route("/", methods=['GET','POST'])
def home():
    if(g.username != None):
        return redirect('/execpage')
    name=''
    passwd=''
    ppp =''
    if request.method=='POST' and 'uname' in request.form and 'pass' in request.form:
        session.pop('username', None)
        name = request.form['uname']
        passwd = request.form['pass']
        actual_exec_name = LoginExec.query.all()[0].exec_name
        actual_exec_pass = LoginExec.query.all()[0].exec_pass
        actual_cash_name = LoginCashier.query.all()[0].cash_name
        actual_cash_pass = LoginCashier.query.all()[0].cash_pass
        if name==actual_exec_name and passwd==actual_exec_pass:
            session['username'] = request.form['uname']
            return redirect('/execpage')
        elif name==actual_cash_name and passwd==actual_cash_pass:
            session['username'] = request.form['uname']
            return redirect('/cashierpage')
        else:
            flash('Invalid credentials. Please try again!')
    return render_template('index.html')

@app.route('/execpage', methods=['GET','POST'])
def home1():
    
    if not g.username:
        abort(403)
    return render_template('home_executive.html', temp=session['username'])

@app.route('/cashierpage', methods=['GET','POST'])
def home2():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'
    return render_template('home_cashier.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__=='__main__':
    app.run()