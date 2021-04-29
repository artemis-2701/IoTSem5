import urllib.request,json
import requests
import sqlite3
import json
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__, template_folder='templates', static_folder='static')

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2527'
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in account table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into account table
            cursor.execute('INSERT INTO account VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route("/pythonlogin/home")
def home():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        conn  = urllib.request.urlopen("https://api.thingspeak.com/channels/1186703/feeds.json?results=1")
        response = conn.read()
        #print ("http status code=%s" % (conn.getcode()))
        data=json.loads(response)
        for d in data['feeds']:
            arr1="{}".format(int(float(d['field1'])))
            arr2="{0:.{1}f}".format(float(d['field2']),2)
            arr3="{0:.{1}f}".format(float(d['field3']),2)
            arr4="{0:.{1}f}".format(float(d['field4']),2)
            arr5="{0}".format(d['created_at'])

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE id = %s', (session['id'],))
        account = cursor.fetchone()

        conn.close()
        cur=mysql.connection.cursor()
        #cur.execute("UPDATE users SET  Temperature= %f ,HeartRate= %f,  BloodOxygen= %f , time= %s WHERE ID= %d",(arr2,arr3,arr4,arr5,arr1))
        #cur.execute(sql,val)
        cur.execute("INSERT INTO user_data(ID,Temperature,HeartRate,BloodOxygen,time) VALUES(%s,%s,%s,%s,%s)",(arr1,arr2,arr3,arr4,arr5))
        mysql.connection.commit()
        cur.close()
        
        return render_template("main.html", ID=arr1, Temperature=arr2, BloodOxygen=arr3,HeartRate=arr4, time=arr5, account=account)
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
@app.route('/pythonlogin/plots/graphs')
def graphs():
    return render_template("plots/graphs.html")
    

if __name__ == "__main__":
    app.run(debug=True)