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

class Transaction(db.Model):
    accountid = db.Column(db.Integer, primary_key=True, nullable=False)
    transactionid = db.Column(db.Integer, nullable=False, default = 0)
    balance = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(15), nullable=False, default='N/A')
    transdate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Integer, nullable=False, default = 0)

    def __repr__(self):
        return 'Transaction ' + str(self.transactionid)

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
    if not (g.username == 'admin'):
        abort(403)
    return render_template('home_executive.html', temp=session['username'])

@app.route('/cashierpage', methods=['GET','POST'])
def home2():
    if not (g.username == 'cashier'):
        abort(403)
    return render_template('home_cashier.html', temp=session['username']) 

@app.route('/cashierpage/deposit', methods=['GET','POST'])
def deposit():
    if request.method=='POST' and 'deposit_amount' in request.form:
        d = request.form['accid']
        r = Transaction.query.get(d)
        r.balance = r.balance + int(request.form['deposit_amount'])
        r.amount = request.form['deposit_amount']
        r.description = "Deposit"
        r.transdate = datetime.utcnow()
        r.transactionid=random.randint(100,999)
        db.session.commit()
        return render_template('depositmoney2.html',r=r)
    if request.method =='POST' and 'accid' in request.form:
        search_id = request.form['accid']
        record = Customer.query.filter(Customer.customeraccno == search_id).first()
        record2 = Transaction.query.filter(Transaction.accountid == search_id).first()
        if not record or not record2:
            return render_template('searchaccount.html')
        return render_template('depositmoney.html',record=record, record2=record2)
    return render_template('searchaccount.html')
    
@app.route('/cashierpage/withdraw', methods=['GET','POST'])
def withdraw():
    if request.method=='POST' and 'withdraw_amount' in request.form:
        d = request.form['accid']
        r = Transaction.query.get(d)
        if(r.balance<int(request.form['withdraw_amount'])):
            flash("Please enter a withdrawal amount less than the balance in the account")
            return redirect('/cashierpage/withdraw')
        r.balance = r.balance - int(request.form['withdraw_amount'])
        r.amount = request.form['withdraw_amount']
        r.description = "Deposit"
        r.transdate = datetime.utcnow()
        r.transactionid=random.randint(100,999)
        db.session.commit()
        return render_template('withdrawmoney2.html',r=r)
    if request.method =='POST' and 'accid' in request.form:
        search_id = request.form['accid']
        record = Customer.query.filter(Customer.customeraccno == search_id).first()
        record2 = Transaction.query.filter(Transaction.accountid == search_id).first()
        if not record or not record2:
            return render_template('searchaccountwithdraw.html')
        return render_template('withdrawmoney.html',record=record, record2=record2)
    return render_template('searchaccountwithdraw.html')

@app.route('/cashierpage/transfer', methods=['GET','POST'])
def transfer():
    if request.method == 'POST':
        temp1 = request.form['sourceid']
        temp2 = request.form['targetid']
        sid = Transaction.query.get(temp1)
        tid = Transaction.query.get(temp2)

        if(sid.balance < int(request.form['transfer_amount'])):
            flash("Source account should have more balance than the transfer amount")
            return redirect('/cashierpage/transfer')
        else:
            sid.balance -= int(request.form['transfer_amount'])
            tid.balance += int(request.form['transfer_amount'])
            db.session.commit()
            return render_template('transfermoney2.html', sid=sid, tid=tid)
    return render_template('transfermoney.html')

    
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
        if not result:
            return render_template('search_for_customer.html')
        db.session.delete(result)
        db.session.commit()
        return render_template('deleted_record.html', result=result)
    return render_template('search_for_customer.html')

@app.route('/execpage/update-customer', methods=['GET','POST'])
def update_customer_details():
    if request.method=='POST' and 'newcustname' in request.form:
        d = request.form['custid']
        r = Customer.query.get(d)
        r.customername = request.form['newcustname']
        r.customeraddr = request.form['newaddress']
        r.customerage = request.form['newage']
        r.customermsg = "Customer update complete"
        r.customerupd = datetime.utcnow()
        db.session.commit()
        return render_template('updatecustomer2.html',r=r)
    if request.method =='POST' and 'custid' in request.form:
        search_id = request.form['custid']
        record = Customer.query.filter(Customer.customerid == search_id).first()
        if not record:
            return render_template('search_for_customer.html')
        return render_template('updatecustomer.html',record=record)
    return render_template('search_for_customer.html')

@app.route('/execpage/create-account', methods=['GET','POST'])
def create_account():
    if request.method == 'POST' and 'depamt' in request.form:
        check_customer = request.form['custid']
        acc_type = request.form['acctype']
        dep_amt = request.form['depamt']
        r = Customer.query.get(check_customer)
        if not r:
            return render_template('createaccount.html', message="Create a Customer first!")
        if r.customeraccno!=0:
            return render_template('createaccount.html', message="Account already exists!")
        r.customeraccno = random.randint(10000,99999)
        r.customeracctype = acc_type
        # r.customermsg = 'Account created successfully'
        # r.customerupd = datetime.utcnow()
        new_record = Transaction(accountid=r.customeraccno, transactionid=random.randint(1000,9999), balance=dep_amt, description='Deposit', transdate=datetime.utcnow(), amount=dep_amt)
        db.session.add(new_record)
        db.session.commit()
        message = 'Account created successfully!'
        return render_template('createaccount.html', message=message)
    return render_template('createaccount.html')

@app.route('/execpage/delete-account', methods=['GET','POST'])
def delete_account():
    if request.method == 'POST' and 'accid' in request.form:
        check_account = request.form['accid']
        check_type = request.form['acctype']
        result = Customer.query.filter(Customer.customeraccno==check_account, Customer.customeracctype==check_type).first()
        if not result:
            return render_template('deleteaccount.html', message="Account doesn't exist!")
        result.customeraccno = 0
        result.customeracctype = 'N/A'
        # db.session.delete(result)
        db.session.commit()
        s = Transaction.query.filter(Transaction.accountid==check_account).first()
        if not s:
            return render_template('deleteaccount.html')
        db.session.delete(s)
        db.session.commit()
        return render_template('deleteaccount.html', message="Account Deleted Successfully!")
    return render_template('deleteaccount.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__=='__main__':
    app.run()