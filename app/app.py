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

@app.route('/paid_action_db')
def paid_action():
    return render_template('insurance_worker/paid_action_db.html')
@app.route('/health')
def health_problem():
    return render_template('doctor_only/add_health_problem_new_user.html')
@app.route('/add_user')
def add_user():
    return render_template('admin_only/add_user.html')
@app.route('/manage_paid_actions')
def manage_paid_actions():
    return render_template('insurance_worker/manage_paid_actions.html')
@app.route('/health_problem')
def report():
    return render_template('not_menu_accessible/health_problem.html')
@app.route('/ticket')
def tickets():
    return render_template('medical_examination_ticket.html')
@app.route('/medical_report')
def medical_report():
    return render_template('not_menu_accessible/medical_report.html')
@app.route('/404')
def not_found_404():
    return render_template('404_not_found.html')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
