from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, g
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

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

class Customer(db.Model):
    customerid = db.Column(db.Integer, primary_key=True, nullable=False)
    customerssn = db.Column(db.Integer, nullable=False)
    customeraccno = db.Column(db.Integer, nullable=False, default=0)
    customeracctype = db.Column(db.String(15), nullable=False, default='N/A')
    customerstatus = db.Column(db.String(15), nullable=False, default='Active')
    customermsg = db.Column(db.String(50), nullable=False, default='Customer created successfully')
    customerupd = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    customerage = db.Column(db.Integer, nullable=False)
    customername = db.Column(db.String(30), nullable=False)
    customeraddr = db.Column(db.String(100), nullable=False)
    customerstate = db.Column(db.String(20), nullable=False)
    customercity = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return 'Customer ' + str(self.customerid)


@app.before_request
def before_request():
    g.username=None
    if 'username' in session:
        g.username = session['username']
    

@app.route("/", methods=['GET','POST'])
def home():
    if(g.username == 'admin'):
        return redirect('/execpage')
    elif(g.username == 'cashier'):
        return redirect('/cashierpage')
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
        n = session['username']
        return render_template('home_cashier.html',n=n )
        # return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/execpage/create-customer', methods=['GET','POST'])
def custcreate():
    if request.method=='POST':
        new_ssn = request.form['ssnid']
        new_name = request.form['custname']
        new_age = request.form['age']
        new_address = request.form['address']
        new_state = request.form['state']
        new_city = request.form['city']
        new_record = Customer(customerid=random.randint(100,999),customerssn=new_ssn,customerage=new_age,customername=new_name,customeraddr=new_address,customerstate=new_state,customercity=new_city)
        db.session.add(new_record)
        db.session.commit()
        message = "User created successfully!"
        return render_template('createcustomer.html',message=message)
    return render_template('createcustomer.html')


@app.route('/execpage/customer-status', methods=['GET','POST'])
def show_customer_details():
    records = Customer.query.all()
    return render_template('customerstatus.html',records=records)

@app.route('/execpage/delete-customer', methods=['GET','POST'])
def delete_customer():
    if request.method=='POST':
        search_id=request.form['custid']
        result=Customer.query.filter(Customer.customerid == search_id).first()
        db.session.delete(result)
        db.session.commit()
        return render_template('deleted_record.html', result=result)
    return render_template('search_for_customer.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__=='__main__':
    app.run()