from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/user')
def user():
    return render_template('user.html')
@app.route('/manage_users')
def manage_users():
    return render_template('admin_only/manage_users.html')

@app.route('/paid_action')
def paid_action():
    return render_template('not_menu_accessible/paid_action.html')

@app.route('/add_user')
def add_user():
    return render_template('admin_only/add_user.html')
@app.route('/manage_paid_actions')
def manage_paid_actions():
    return render_template('manage_paid_actions.html')
@app.route('/report')
def report():
    return render_template('not_menu_accessible/report.html')
@app.route('/ticket')
def tickets():
    return render_template('ticket.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
