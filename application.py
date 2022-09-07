import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

from datetime import datetime
import pytz

import pandas as pd
import matplotlib.pyplot as plt


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///loans.db")

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

MONTH_NUM = 12


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username was submitted
        if username == "" or len(rows) > 0:
            return apology("must provide username/username already exists", 400)

        # Ensure password was submitted
        elif password == "" or password != request.form.get("confirmation"):
            return apology("must provide password/passwords do not match", 400)

        # Ensure password contains at least 8 characters with uppercase letter, lowercase letter, and digit
        elif len(password) < 8:
            return apology("password must contain at least 8 characters", 400)
        else:
            counter_l = 0
            counter_u = 0
            counter_d = 0
            for char in password:
                if char.islower():
                    counter_l += 1
                if char.isupper():
                    counter_u += 1
                if char.isdigit():
                    counter_d += 1
            if counter_l < 1 or counter_u < 1 or counter_d < 1:
                return apology("password must contain at least 1 uppercase, 1 lowercase, and 1 number", 400)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hashed_password)

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Check/change user info"""
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    hashed_old_password = str(db.execute("SELECT hash FROM users WHERE username = ?", username)[0]["hash"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        new_password = request.form.get("new_password")
        # Ensure password was submitted

        if new_password == "" and request.form.get("confirmation") == "" and new_password == request.form.get("confirmation"):
             return apology("must provide password/passwords do not match", 400)
        # Ensure password contains at least 8 characters with uppercase letter, lowercase letter, and digit
        elif len(new_password) < 8:
             return apology("password must contain at least 8 characters", 400)
        else:
            counter_l = 0
            counter_u = 0
            counter_d = 0
            for char in new_password:
                if char.islower():
                    counter_l += 1
                if char.isupper():
                    counter_u += 1
                if char.isdigit():
                    counter_d += 1
            if counter_l < 1 or counter_u < 1 or counter_d < 1:
                return apology("password must contain at least 1 uppercase, 1 lowercase, and 1 number", 400)

            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)

            db.execute("UPDATE users SET hash = %s WHERE username = %s", hashed_password, username)
            # Redirect user to profile page
            return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("profile.html", username=username)


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():
    """Show portfolio of loans"""

    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    home_loans = db.execute("SELECT * FROM mortgage WHERE username = ?", username)
    auto_loans = db.execute("SELECT * FROM auto_loan WHERE username = ?", username)

    return render_template("index.html", home_loans=home_loans, auto_loans=auto_loans)


@app.route("/lend", methods=["GET", "POST"])
@login_required
def lend():
    """Lend money main page"""

    return render_template("lend.html")


@app.route("/home_loan", methods=["GET", "POST"])
@login_required
def home_loan():
    """Lend money on home mortgage"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]

        home_value = request.form.get("home_value")
        down_payment = request.form.get("down_payment")
        annual_interest_rate = request.form.get("interest_rate")
        term = request.form.get("term")
        month = request.form.get("month")
        year = request.form.get("year")
        annual_tax = request.form.get("tax")
        annual_insurance = request.form.get("insurance")
        hoa = request.form.get("hoa")


        if not home_value or not down_payment or not annual_interest_rate or not term or not month or not year or not annual_insurance or not hoa:
            return apology("must fill in all blanks")
        elif not home_value.isdigit() or not down_payment.isdigit() or not year.isdigit() or not annual_insurance.isdigit() or not hoa.isdigit():
            return apology("input is not a valid number")

        home_value = float(home_value)
        down_payment = float(down_payment)
        annual_interest_rate = float(annual_interest_rate)
        term = int(term)
        year = int(year)
        annual_tax = float(annual_tax)
        annual_insurance = float(annual_insurance)
        hoa = float(hoa)

        if home_value < 0 or down_payment < 0 or down_payment > home_value or annual_interest_rate < 0 or annual_interest_rate > 100 or year < 2021 or annual_insurance < 0 \
        or annual_insurance > home_value or hoa < 0 or hoa > home_value:
            return apology("invalid number", 400)
        else:
            loan_amount = home_value - down_payment
            down_payment_rate = down_payment / home_value
            start_date = month + " " + str(year)
            monthly_interest_rate = (annual_interest_rate / 100) / MONTH_NUM
            payment_num = MONTH_NUM * term
            monthly_mortgage_payment = (loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** payment_num) / ((1 + monthly_interest_rate)
            ** payment_num - 1))
            monthly_tax = annual_tax / MONTH_NUM
            monthly_insurance = annual_insurance / MONTH_NUM
            monthly_payment = monthly_mortgage_payment + monthly_tax + monthly_insurance + hoa

            # calculate payoff date
            index_month = MONTHS.index(month)
            if index_month == 0:
                payoff_month = MONTHS[len(MONTHS) - 1]
            else:
                payoff_month = MONTHS[index_month - 1]
            payoff_year = year + term
            payoff_date = str(payoff_month) + " " + str(payoff_year)

            # insert data into mortgage table
            db.execute("INSERT INTO mortgage (home_value, down_payment, loan_amount, interest_rate, loan_term, start_date, monthly_tax, monthly_insurance, \
            monthly_HOA, monthly_payment, payoff_date, username) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", home_value, down_payment, loan_amount, \
            annual_interest_rate, term, start_date, monthly_tax, monthly_insurance, hoa, monthly_payment, payoff_date, username)

            # update users table
            db.execute("UPDATE users SET home_loan = %s WHERE username = %s", loan_amount, username)

            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("home_loan.html", months=MONTHS)


@app.route("/auto_loan", methods=["GET", "POST"])
@login_required
def auto_loan():
    """Lend money on home mortgage"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]

        car_price = request.form.get("car_price")
        down_payment = request.form.get("down_payment")
        annual_interest_rate = request.form.get("interest_rate")
        term = request.form.get("term")
        month = request.form.get("month")
        year = request.form.get("year")
        sales_tax = request.form.get("tax")

        if not car_price or not down_payment or not annual_interest_rate or not term or not month or not year:
            return apology("must fill in all blanks")
        elif (not car_price.isdigit() or not down_payment.isdigit() or not year.isdigit()):
            return apology("input is not a valid number")

        car_price = float(car_price)
        down_payment = float(down_payment)
        annual_interest_rate = float(annual_interest_rate)
        term = int(term)
        year = int(year)
        sales_tax = float(sales_tax)

        if car_price < 0 or down_payment < 0 or down_payment > car_price or annual_interest_rate < 0 or annual_interest_rate > 100:
            return apology("invalid number", 400)
        else:
            loan_amount = car_price * (1 + sales_tax * .01) - down_payment
            down_payment_rate = down_payment / car_price
            start_date = month + " " + str(year)
            monthly_interest_rate = (annual_interest_rate / 100) / MONTH_NUM
            payment_num = term
            monthly_mortgage_payment = (loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** payment_num) / ((1 + monthly_interest_rate)
            ** payment_num - 1))
            monthly_payment = monthly_mortgage_payment

            # calculate payoff date
            index_month = MONTHS.index(month)
            if index_month == 0:
                payoff_month = MONTHS[len(MONTHS) - 1]
            else:
                payoff_month = MONTHS[index_month - 1]
            payoff_year = year + term
            payoff_date = str(payoff_month) + " " + str(payoff_year)

            # insert data into mortgage table
            db.execute("INSERT INTO auto_loan (car_price, down_payment, loan_amount, interest_rate, loan_term, start_date, sales_tax, \
            monthly_payment, payoff_date, username) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", car_price, down_payment, loan_amount, \
            annual_interest_rate, term, start_date, sales_tax, monthly_payment, payoff_date, username)

            # update users table
            db.execute("UPDATE users SET auto_loan = %s WHERE username = %s", loan_amount, username)

            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("auto_loan.html", months=MONTHS)


@app.route("/history")
@login_required
def history():
    """Show history of loan payment"""

    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    if db.execute("SELECT home_loan FROM users WHERE username = ?", username)[0]["home_loan"] == 0:
        return apology("Congrats! No mortgage record", 400)
    else:
        home_loan_total = round(db.execute("SELECT loan_amount FROM mortgage WHERE username = ?", username)[0]["loan_amount"], 2)
        home_monthly_interest_rate = db.execute("SELECT interest_rate FROM mortgage WHERE username = ?", username)[0]["interest_rate"] / (MONTH_NUM * 100)
        home_loan_total_term = db.execute("SELECT loan_term FROM mortgage WHERE username = ?", username)[0]["loan_term"] * MONTH_NUM
        home_loan_start_date = db.execute("SELECT start_date FROM mortgage WHERE username = ?", username)[0]["start_date"]
        # monthly record
        home_initial_interest = round(home_monthly_interest_rate * home_loan_total, 2)

        # M = P [ i(1 + i)^n ] / [ (1 + i)^n – 1] this number does not change
        home_monthly_repayment = home_loan_total * (home_monthly_interest_rate * ((1 + home_monthly_interest_rate) ** home_loan_total_term)) / ((1 + home_monthly_interest_rate) ** home_loan_total_term - 1)
        home_monthly_repayment = round(home_monthly_repayment, 2)

        # create a list of dictionary including all monthly repayment record
        home_repay_history = []
        home_pre_balance = home_loan_total
        home_monthly_interest = home_initial_interest
        year = int(home_loan_start_date.split(" ")[1])
        for i in range(home_loan_total_term):
            home_repay_history.append({})
            month = MONTHS[(MONTHS.index(home_loan_start_date.split(" ")[0]) + i) % MONTH_NUM]
            home_repay_history[i]["Month"] = month
            home_repay_history[i]["Year"] = str(year)
            if month == "December":
                year += 1
            home_repay_history[i]["Repayment"] = home_monthly_repayment
            home_repay_history[i]["Interest Paid"] = round(home_monthly_interest, 2)
            home_paid_principal = round(home_monthly_repayment - home_monthly_interest, 2)
            home_repay_history[i]["Principal Paid"] = round(home_paid_principal, 2)
            home_repay_history[i]["Previous Balance"] = round(home_pre_balance, 2)
            # update the balance
            home_pre_balance = round(home_pre_balance - home_paid_principal, 2)
            home_repay_history[i]["New Balance"] = round(home_pre_balance, 2)
            # update the monthly interest
            home_monthly_interest = round(home_monthly_interest_rate * home_pre_balance, 2)

        df = pd.DataFrame(home_repay_history)

        year = []
        balance = []
        for j in range(0, len(home_repay_history), int(home_loan_total_term / MONTH_NUM)):
            year.append(home_repay_history[j]["Year"])
            balance.append(home_repay_history[j]["Previous Balance"])
        fig, ax = plt.subplots()
        ax.plot(year, balance)
        fig.savefig('static/balance_per_year.png')

        year = []
        interest_paid = []
        for j in range(0, len(home_repay_history), int(home_loan_total_term / MONTH_NUM)):
            year.append(home_repay_history[j]["Year"])
            interest_paid.append(home_repay_history[j]["Interest Paid"])
        fig, ax = plt.subplots()
        ax.plot(year, interest_paid)
        fig.savefig('static/interest_paid.png')

        year = []
        principal_paid = []
        for j in range(0, len(home_repay_history), int(home_loan_total_term / MONTH_NUM)):
            year.append(home_repay_history[j]["Year"])
            principal_paid.append(home_repay_history[j]["Principal Paid"])
        fig, ax = plt.subplots()
        ax.plot(year, principal_paid)
        fig.savefig('static/principal_paid.png')

        return render_template("history.html", data=df.to_html())


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
