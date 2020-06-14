from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
db = SQLAlchemy(app)
# app.secret_key='daffjsdfyi76487'

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


@app.route("/", methods=['GET','POST'])
def home():
    name=''
    passwd=''
    ppp =''
    if request.method=='POST' and 'uname' in request.form and 'pass' in request.form:
        name = request.form['uname']
        passwd = request.form['pass']
        actual_exec_name = LoginExec.query.all()[0].exec_name
        actual_exec_pass = LoginExec.query.all()[0].exec_pass
        actual_cash_name = LoginCashier.query.all()[0].cash_name
        actual_cash_pass = LoginCashier.query.all()[0].cash_pass
        if name==actual_exec_name and passwd==actual_exec_pass:
            return redirect('/execpage')
        elif name==actual_cash_name and passwd==actual_cash_pass:
            return redirect('/cashierpage')

    return render_template('index.html')

@app.route('/execpage', methods=['GET','POST'])
def home1():
    return render_template('home_executive.html')

@app.route('/cashierpage', methods=['GET','POST'])
def home2():
    return render_template('home_cashier.html')




if __name__=='__main__':
    app.run()