from os import TMP_MAX
from flask import Flask, render_template, request, redirect, url_for, session,flash
from database import *
from datetime import timedelta
import logging as logger
from database import db, app
import os
from flask import send_from_directory, abort
from random import randint 


logger.basicConfig(level='DEBUG')
bcrypt = Bcrypt(app)
app.permanent_session_lifetime = timedelta(minutes=30)
app.jinja_env.globals.update(zip=zip)

# List of keys set during session
SESSION_USER_DATA = ['isAdmin', 'isDoctor', 'isInsurance', 'user_id']


@app.route('/')
def index():
    '''Show health problems according to user permissions'''
    if session.get('isDoctor'):
        problems = HealthProblem.query.filter_by(doctor_id=session['user_id'])
    elif session.get('user_id'):
        problems = HealthProblem.query.filter_by(
            patient_id=session['user_id']
        )
    else:
        problems = []
    return render_template('index.html', problems=problems)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    '''Log out user'''
    for item in SESSION_USER_DATA:
        session.pop(item)
    flash("Účet odhlášen")
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Process data for login'''
    if request.method == "POST":
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            if bcrypt.check_password_hash(user.password, request.form['password']):
                session.update(user.login_dict())
                logger.debug("User logged in")
                if 'bad_password' in session:
                    session.pop('bad_password')
                    session.pop('email_bad')
            else:
                logger.debug("Bad password")  
                flash("Špatné heslo")
                session['bad_password']=True
                session['email_bad']=request.form['email']
        else:
            logger.debug("User not found") 
            flash("Zadaný účet neexistuje")
            session['bad_password'] = True
            session['email_bad'] = request.form['email']
            '''return render_template("index.html")'''
    return redirect(url_for('index'))


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    '''Process data for sign up'''
    data = request.form.to_dict()
    if User.query.filter_by(email=data['email']).first():
        flash("Zadaný účet je již existující, zkuste zadat jiný e-mail")
    else:
        data['password'] = bcrypt.generate_password_hash(data['password'])
        add_row(User, **data)
        flash("Účet úspěšně registrován")
    return redirect(url_for('index'))

@app.route('/user', methods=['GET', 'POST'])
def user():
    '''Show user info'''
    user = User.query.filter_by(_id=session.get('user_id')).first()
    if request.method == 'POST':
        user.update(**request.form.to_dict())
        if request.form['submit_button'] == 'delete_user':
            user.delete()
            return redirect(url_for('logout'))
        elif request.form['submit_button'] == 'update_user':
            user.update(**request.form.to_dict())
    if not user:
        abort(404)
    return render_template('user.html', user=user, my_user=True)

@app.route('/manage_users/<int:id>', methods=['GET', 'POST'])   
def redirect_user(id):
    '''Redirect to edit user'''
    # code 307 preserves http method
    return redirect(url_for('update_user', id=id, code=307))


@app.route('/manage_users/user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    '''Show and update user info '''
    if session.get('isAdmin') or id == session.get('user_id'):
        logger.debug(id)
        user = User.query.filter_by(_id=id).first()
        if request.method == 'POST':
            if request.form['submit_button'] == 'delete_user':
                if user.isDoctor or user.isAdmin:
                    user_replacement_id = User.query.filter_by(email=request.form['replacement_name']).first()._id
                    user.delete(sub_doc_id=user_replacement_id)
                else:
                    user.delete()
                if(session.get('user_id') == user._id):
                    return redirect(url_for('logout'))
                return redirect(url_for('manage_users'))
            elif request.form['submit_button'] == 'update_user':
                user.update(**request.form.to_dict())
        # TODO user not logged in scenerio not coverd in user.html
        return render_template('user.html', user=user, my_user=False)
    else:
        abort(404)

@app.route('/manage_users')
def manage_users():
    '''Manage users (admin only)'''
    if session.get('isAdmin'):
        return render_template(
            'admin_only/manage_users.html',
            users=permitted_query(User, session.get('isAdmin'))
        )
    abort(404)


@app.route('/paid_action_db')
def paid_action():
    if session.get('isAdmin') or session.get('isInsurance'):
        return render_template(
            'insurance_worker/paid_action_db.html',
            p_templates=permitted_query(PaymentTemplate,
                                        session.get('isInsurance'))
        )
    abort(404)


@app.route('/paid_action_new', methods=['GET', 'POST'])
def paid_action_new():
    if session.get('isAdmin') or session.get('isInsurance'):
        if request.method == "POST":
            add_row(PaymentTemplate, **request.form.to_dict())
            flash("Událost vytvořena")
        return render_template('insurance_worker/manage_new_action.html')
    abort(404)

@app.route('/process_request_payment_approved/<int:payment_id>')
def process_request_approved_payment(payment_id):
    if session.get('isAdmin') or session.get('isInsurance'):
        request_pay = PaymentRequest.query.filter_by(_id=payment_id).first()
        request_pay.state = "Schváleno"
        db.session.commit()
        return redirect(url_for('manage_paid_actions'))
    abort(404)

@app.route('/process_request_payment_not_approved/<int:payment_id>')
def process_request_not_approved_payment(payment_id):
    if session.get('isAdmin') or session.get('isInsurance'):
        request_pay = PaymentRequest.query.filter_by(_id=payment_id).first()
        request_pay.state = "Neschváleno"
        db.session.commit()
        return redirect(url_for('manage_paid_actions'))
    abort(404)


@app.route('/health', methods=['GET', 'POST'])
def health_problem():
    if session.get('isAdmin') or session.get('isDoctor'):
        if request.method == "POST":
            data = request.form.to_dict()
            if(User.query.filter_by(email=data['email']).first()):
                flash("Uživatel již je registrován")
                return render_template('doctor_only/add_health_problem_new_user.html', data=data)
            else:
                data['password'] = bcrypt.generate_password_hash(data['password'])
                add_row(User, **data)
                logger.debug("New user registered")
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                add_row(HealthProblem, **data, patient_id=user._id,
                        doctor_id=session['user_id'])
            else:
                logger.debug("User not found")
            return redirect(url_for('health_problem'))
        return render_template('doctor_only/add_health_problem_new_user.html')
    abort(404)

### ???
@app.route('/health_old', methods=['GET', 'POST'])
def health_problem_old():
    if session.get('isAdmin') or session.get('isDoctor'):
        if request.method == "POST":
            data = request.form.to_dict()
            user = User.query.filter_by(email=request.form['user_email']).first()
            if user:
                add_row(HealthProblem, **data, patient_id=user._id,
                        doctor_id=session.get('user_id'))
            else:
                flash("Uživatel nenalezen")
                return render_template('doctor_only/add_health_problem_new_user.html', data=data)
            return redirect(url_for('health_problem'))
        return render_template('doctor_only/add_health_problem_registered_user.html')
    abort(404)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if session.get('isAdmin'):
        if request.method == "POST":
            data = request.form.to_dict()
            if(User.query.filter_by(email=data['email']).first()):
                flash("Zadaný účet je již existující, zkuste zadat jiný e-mail")
                return render_template('admin_only/add_user.html', data=data)
            else:
                data['password']=bcrypt.generate_password_hash(data['password'])
                add_row(User, **data)
                flash("Účet vytvořen")
        return render_template('admin_only/add_user.html')
    abort(404)


@app.route('/manage_paid_actions')
def manage_paid_actions():
    if session.get('isAdmin') or session.get('isInsurance'):
        p_requests = PaymentRequest.query
        p_templates = PaymentTemplate.query
        p_doctor = {}
        templates=[]
        for req in p_requests:
            templates.append(PaymentTemplate.query.filter_by(_id=req.template).first())
            p_doctor[req._id]=User.query.filter_by(_id=req.creator).first().name
        return render_template('insurance_worker/manage_paid_actions.html', p_requests = p_requests, p_templates = p_templates,templates = templates, p_doctor=p_doctor)
    abort(404)


@app.route('/ticket',  methods=['GET', 'POST'])
def tickets():
    if session.get('isAdmin') or session.get('isDoctor'):
        if request.method == 'POST':
            problem_id =  request.args.get('p_id')
            data = request.form.to_dict()
            doctor = User.query.filter_by(email=data.get('received_by')).first()
            if doctor == None:
                flash("Doktor nenalezen")
                return render_template('medical_examination_ticket.html', name=data['name'], received_by=data['received_by'], description=data['description'])
            if doctor.isDoctor:
                add_row(ExaminationRequest, created_by=session.get('user_id'), receiver=doctor._id, state="Nevyřízeno", health_problem=problem_id, **data)
            else:
                flash("Uživatel není doktor")
                return render_template('medical_examination_ticket.html', name=data['name'],
                                       received_by=data['received_by'], description=data['description'])

        return render_template('medical_examination_ticket.html')
    abort(404)


@app.route('/problem_report',  methods=['GET', 'POST'])
def medical_report():
    problem_id =  request.args.get('p_id')
    problem = HealthProblem.query.filter_by(_id=problem_id).first()
    reports = MedicalReport.query.filter_by(health_problem=problem_id)
    examinations= ExaminationRequest.query.filter_by(health_problem_id=problem_id)
    if problem:
        if(session.get('isAdmin') or problem.patient_id == session.get('user_id')
            or problem.doctor_id == session.get('user_id')):
            doctor = User.query.filter_by(_id=problem.doctor_id).first()
            if doctor:
                return render_template(
                    'not_menu_accessible/problem_report.html',
                    problem=problem, doctor=doctor.name, reports=reports, examinations=examinations
                )
        abort(404)
    ### TODO Maybe get to previous link?
    

@app.route('/404')
def not_found_404():
    return render_template('404_not_found.html')


@app.route('/delegate_problem',  methods=['GET', 'POST'])
def delegate():
    if session.get('isAdmin') or session.get('isDoctor'):
        if (request.method == 'POST'):
            problem_id =  request.args.get('p_id')
            problem = HealthProblem.query.filter_by(_id=problem_id).first()
            if problem:
                doctor = User.query.filter_by(email=request.form['id_doctor']).first()
                if doctor:
                    logger.debug(doctor._id)
                    problem.doctor_id = doctor._id
                    db.session.commit()
                else:
                    flash("Uživatel nenalezen nebo nemá dostatečná opravnění")
                    return render_template('doctor_only/delegate_problem.html', id_doctor=request.form['id_doctor'])

    return render_template('doctor_only/delegate_problem.html')


@app.route('/medical_report/<int:id>',  methods=['GET', 'POST'])
def medical_problem(id):
    report = MedicalReport.query.filter_by(_id=id).first()
    problem = HealthProblem.query.filter_by(_id=report.health_problem).first()
    if session['user_id'] != problem.patient_id and session['user_id'] != problem.doctor_id:
        abort(404)
    author = User.query.filter_by(_id=report.author).first()
    if(request.method=="POST"):
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=report.attachment_name, as_attachment=True)
    return render_template('not_menu_accessible/medical_report.html', report=report, author=author)


@app.route('/medical_report_creator/<int:health_problem_id>', methods=['GET', 'POST'])
def medical_report_creator(health_problem_id):
    if session.get('isAdmin') or session.get('isDoctor'):
        if request.method == 'POST':
            data = request.form.to_dict()
            file = request.files['attachment']
            filename=secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            add_row(MedicalReport, attachment=filename, author=session.get('user_id'), health_problem_id=health_problem_id, **data)
        return render_template('not_menu_accessible/medical_report_creator.html')
    abort(404)
#TODO: Fix buttons change doctor after delete (just design)

@app.route('/medical_examinations')
def medical_examinations():
    if session.get('isAdmin') or session.get('isDoctor'):
        health_problem_names={}
        for request in ExaminationRequest.query:
            health_problem_names[request.id]= HealthProblem.query.filter_by(_id=request.health_problem_id).first().name

        doctor_received_by_names={}
        for request in ExaminationRequest.query:
            if request.received_by:
                doctor_received_by_names[request.id]= User.query.filter_by(_id=request.received_by).first().surname
        doctor_created_by_names={}
        for request in ExaminationRequest.query:
            doctor_created_by_names[request.id]= User.query.filter_by(_id=request.created_by).first().surname

        return render_template('doctor_only/medical_examinations.html',
                               requests=ExaminationRequest.query, health_problem_names=health_problem_names,doctor_received_by_names=doctor_received_by_names,doctor_created_by_names=doctor_created_by_names)
    abort(404)

### TODO Refactor adding table row
@app.route('/payment_request',  methods=['GET', 'POST'])
def payment_request():
    if session.get('isAdmin') or session.get('isInsurance'):
        templates=PaymentTemplate.query.all()
        if request.method == 'POST':
            data = request.form.to_dict()
            template=PaymentTemplate.query.filter_by(name=data['template']).first()
            if template == None:
                flash("Neznámý typ zákroku")
                return render_template('doctor_only/payment_request.html', data=data, templates=templates)
            data['template']=template._id
            add_row(PaymentRequest, **data, creator=session.get('user_id'),
                    examination_request=session.get('examination_request'),
                    validator = 1 )  # je to vzdy 1 <- musi se to nejak upravit at je to korektne
            flash("Žádost podána")
        return render_template('doctor_only/payment_request.html',templates=templates)
    abort(404)

@app.route('/process_delete/<int:id>')
def process_delete(id):
    ExaminationRequest.query.filter_by(_id=id).delete()
    db.session.commit()
    return redirect(url_for('medical_examinations'))

@app.route('/medical_examination', methods=['GET', 'POST'])
def medical_examination():
    if session.get('isAdmin') or session.get('isDoctor'):
        request_id =  request.args.get('r_id')
        session['examination_request'] = request_id 
        e_request = ExaminationRequest.query.filter_by(_id=request_id).first()
        doctor_received_by= User.query.filter_by(_id=e_request.received_by).first()
        doctor_created_by= User.query.filter_by(_id=e_request.created_by).first()
        health_problem_name = HealthProblem.query.filter_by(_id=e_request.health_problem_id).first().name
        if request.method == 'POST':
            if e_request.received_by == None:
                email=request.form['replacement_name']
                user_id =User.query.filter_by(email=email).first()._id
                e_request.received_by=user_id
                doctor_received_by = User.query.filter_by(_id=e_request.received_by).first()
                db.session.commit()
                return render_template('doctor_only/medical_examination.html',
                                       e_request=e_request, health_problem_name=health_problem_name,
                                       doctor_received_by=doctor_received_by, doctor_created_by=doctor_created_by)
            e_request.state= "Vyřízeno"
            db.session.commit()
            return redirect(url_for('medical_examinations'))
        return render_template('doctor_only/medical_examination.html',
                               e_request=e_request, health_problem_name =health_problem_name ,doctor_received_by=doctor_received_by,doctor_created_by=doctor_created_by)
    else :
        flash("Nedostačující oprávnění")
        return render_template('doctor_only/medical_examination.html',e_request=None)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_not_found.html'), 404


def random_integer():
    min_ = 100000
    max_ = 999999
    rand = randint(min_, max_)
    return rand

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0')
