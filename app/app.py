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
    return render_template('manage_users.html')

@app.route('/paid_action')
def paid_action():
    return render_template('paid_action.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
