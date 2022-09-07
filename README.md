# Loan Calculator & Record
#### Video Demo:  <https://youtu.be/mzibejqsZOo>
#### Description:

My final project "Loan Calculator & Record" is a web-based application using JavaScript, Python, and SQL.
The web-based application is designed for registered users to keep a record of home loans and auto loans
and visualize data indicating monthly payment, repayment, monthly interests, remaining balance, etc. in
the format of tables and plot charts.

Inside the static folder, there are pictures used for website decoration, styles.css, and png files temporarily
saved using Pandas as the visualization of user's data. These pgn files were named as balance_per_year.png,
interest_paid.png, and principal_paid.png. They were called in the history.html file.

Inside the templates folder, there are 10 html files:
1. apology.html: Used as the template for the error message.
2. auto_loan.html: A template of forms for user input on auto loan information. All input information are
collected in the sql file loans.db in the auto_loan table.
3. history.html: Presents plots and tables of logged-in user's mortgage payment history and amoritization
schedule.
4. home_loan.html: A template of forms for user input on home loan information. All input information are
collected in the sql file loans.db in the mortgage table.
5. index.html: The home page for a signed in user. If the user had lent money and used the website to log
the information, the index page would present tables of the basic information on the most recent home loan
and auto loan. The logged-in user can also use links at the top of the page to "Lend" auto loan or home loan
and keep a record, to check mortgage history in "History", to change the password in "Profile", and to "Log
out".
6. layout.html: The template and skeleton of the website layout.
7. lend.html: A template of forms with buttons and pictures for user to select a type of loan to be recorded.
User's input leads to either auto loan page with auto_loan.html or home loan page with home_loan.html.
8. login.html: A template of forms that collect user's username an password for the registered user to log in.
9. profile.html: A template of forms that collect user's new password. The new password are hashed and updated
in the user table in loans.db.
10. register.html: A template of forms that collect user's username, password, and confirmation of password.
The information are stored in the user table in loans.db.

In the project folder, there are application.py, helpers.py, loans.db, this README.md, and requirement.txt.
The application.py include all functions for the application. The helpers.py include functions for error
messages, login record, usd symbol, and other helper functions. The loans.db is the sql file including three
tables users, mortgage, and auto_laon which store information from the user input.# CS50LoanCalculator-RecordProject
