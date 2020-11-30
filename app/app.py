from os import TMP_MAX
from flask import Flask, render_template, request, redirect, url_for, session,flash
from database import *
from datetime import timedelta
import logging as logger
from database import db, app, bcrypt
import os
from flask import send_from_directory, abort
from random import randint 


logger.basicConfig(level='DEBUG')
app.permanent_session_lifetime = timedelta(minutes=30)
app.jinja_env.globals.update(zip=zip)
# List of keys set during session
SESSION_USER_DATA = ['isAdmin', 'isDoctor', 'isInsurance', 'user_id']


USER_QUERY = ['_id', 'name', 'surname', 'email']
HEALT_PROBLEM_QUERY = ['_id', 'name', 'state']
PAID_ACTION_QUERY = ['_id', 'name', 'price', 'type']

def get_query(query, TABLE_QUERY, values):
    kwargs = { key: values.get(key) for key in TABLE_QUERY if values.get(key) }
    if kwargs.get('_id'):
        kwargs['_id'] = int(kwargs['_id'])
    return query.filter_by(**kwargs).all()


@app.route('/', methods=['GET', 'POST'])
def index():
    '''Show health problems according to user permissions'''
    if session.get('isDoctor'):
        problems = HealthProblem.query.filter_by(doctor_id=session['user_id'])
    elif session.get('user_id'):
        problems = HealthProblem.query.filter_by(
            patient_id=session['user_id']
        )
    else:
        problems = HealthProblem.query.filter_by(_id=-1)
    if request.method == 'POST':
        data=request.form
        return render_template('index.html', problems=problems, data=data)
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
        session['bad_password'] = True
        return render_template('index.html', data=data)
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
                    if User.query.filter_by(email=request.form['replacement_name']).first() == None:
                        flash("Doktor nenalezen")
                        return render_template('user.html', user=user, my_user=False)
                    user_replacement_id = User.query.filter_by(email=request.form['replacement_name']).first()._id
                    user.delete(sub_doc_id=user_replacement_id)
                else:
                    user.delete()
                if(session.get('user_id') == user._id):
                    return redirect(url_for('logout'))
                return redirect(url_for('manage_users'))
            elif request.form['submit_button'] == 'update_user':
                user.update(**request.form.to_dict())
        return render_template('user.html', user=user, my_user=False)
    else:
        abort(404)


@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    '''Manage users (admin only)'''
    if session.get('isAdmin'):
        if request.method == 'POST' and request.form.get('filter'):
            users = get_query(User.query, USER_QUERY, request.form)
        else:
            users = User.query.all()
        return render_template(
            'admin_only/manage_users.html',
            users=users
        )
    abort(404)


@app.route('/paid_action_db', methods=['GET', 'POST'])
def paid_action():
    if session.get('isAdmin') or session.get('isInsurance'):
        query = PaymentTemplate.query
        if request.method == 'POST':
            templates = get_query(query, PAID_ACTION_QUERY, request.form)
        else:
            templates = query.all()
        return render_template(
            'insurance_worker/paid_action_db.html',
            p_templates=templates
        )
    abort(404)


@app.route('/paid_action_new', methods=['GET', 'POST'])
def paid_action_new():
    if session.get('isAdmin') or session.get('isInsurance'):
        if request.method == "POST":
            add_row(PaymentTemplate, **request.form.to_dict())
            flash("Šablona vytvořena")
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


@app.route('/manage_paid_actions',  methods=['GET', 'POST'])
def manage_paid_actions():
    if session.get('isAdmin') or session.get('isInsurance'):
        p_requests = PaymentRequest.query
        p_templates = PaymentTemplate.query
        p_doctor = {}
        templates=[]
        for req in p_requests:
            templates.append(PaymentTemplate.query.filter_by(_id=req.template).first())
            p_doctor[req._id]=User.query.filter_by(_id=req.creator).first().name
        if request.method == "POST":
            data=request.form
            return render_template('insurance_worker/manage_paid_actions.html', p_requests=p_requests,
                                   templates=templates, p_doctor=p_doctor, data=data)
        return render_template('insurance_worker/manage_paid_actions.html', p_requests = p_requests, templates = templates, p_doctor=p_doctor)
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
                flash("Žádost o vyšetření podána")
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
                    problem=problem, doctor=doctor.surname, reports=reports, examinations=examinations
                )
        abort(404)
    abort(404)


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

@app.route('/medical_examinations',  methods=['GET', 'POST'])
def medical_examinations():
    if session.get('isAdmin') or session.get('isDoctor'):
        health_problem_names={}
        for request_exam in ExaminationRequest.query:
            health_problem_names[request_exam._id]= HealthProblem.query.filter_by(_id=request_exam.health_problem_id).first().name

        doctor_received_by_names={}
        for request_exam in ExaminationRequest.query:
            if request_exam.received_by:
                doctor_received_by_names[request_exam._id]= User.query.filter_by(_id=request_exam.received_by).first().surname
        doctor_created_by_names={}
        for request_exam in ExaminationRequest.query:
            doctor_created_by_names[request_exam._id]= User.query.filter_by(_id=request_exam.created_by).first().surname

        if request.method == "POST":
            data=request.form
            return render_template('doctor_only/medical_examinations.html',
                                   requests=ExaminationRequest.query, health_problem_names=health_problem_names,
                                   doctor_received_by_names=doctor_received_by_names,
                                   doctor_created_by_names=doctor_created_by_names, data=data)

        return render_template('doctor_only/medical_examinations.html',
                               requests=ExaminationRequest.query, health_problem_names=health_problem_names,doctor_received_by_names=doctor_received_by_names,doctor_created_by_names=doctor_created_by_names)
    abort(404)

@app.route('/payment_request',  methods=['GET', 'POST'])
def payment_request():
    if session.get('isAdmin') or session.get('isInsurance') or session.get('isDoctor'):
        templates=PaymentTemplate.query.all()
        if request.method == 'POST':
            data = request.form.to_dict()
            template=PaymentTemplate.query.filter_by(name=data['template']).first()
            if template == None:
                flash("Neznámý typ zákroku")
                return render_template('doctor_only/payment_request.html', data=data, templates=templates)
            data['template']=template._id
            insurance=User.query.filter_by(isInsurance=1).first()._id
            add_row(PaymentRequest, **data, creator=session.get('user_id'), examination_request=session.get('examination_request'), validator=insurance)
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


@event.listens_for(User.__table__, 'after_create')
def create_users(*args, **kwargs):
    add_row(User, name="Jan", surname="Novák", password=bcrypt.generate_password_hash("password"),
            email="novak@seznam.cz", phone="735443223", address="Na Příkopech 450", city="Brno",
            birthnumber="9008125447", isAdmin="True", isDoctor="True", isInsurance="True")
    add_row(User, name="Petr", surname="Pavel", password=bcrypt.generate_password_hash("password"),
            email="pavel@seznam.cz", phone="735111223", address="U Hradu 111", city="Brno",
            birthnumber="9801145447", isAdmin="True")
    add_row(User, name="Josef", surname="Dvořák", password=bcrypt.generate_password_hash("password"),
            email="dvorak@gmail.com", phone="700144213", address="Nábřeží 112", city="Brno",
            birthnumber="7001185557", isDoctor="True")
    add_row(User, name="Daniel", surname="Korn", password=bcrypt.generate_password_hash("password"),
            email="korn@mail.com", phone="065222423", address="Pražská 555", city="Čáslav",
            birthnumber="5501140447", isDoctor="True")
    add_row(User, name="Petra", surname="Domovská", password=bcrypt.generate_password_hash("password"),
            email="domovska@mail.com", phone="135485223", address="Stará 112", city="Brno",
            birthnumber="4501145447", isDoctor="True")
    add_row(User, name="Vladislav", surname="Jiný", password=bcrypt.generate_password_hash("password"),
            email="jiny@seznam.cz", phone="222111243", address="Centrální", city="Brno",
            birthnumber="9801445447")
    add_row(User, name="Alžbeta", surname="Filipová", password=bcrypt.generate_password_hash("filip01"),
            email="filipova@gmail.com", phone="700111223", address="Palackého 113", city="Vyškov",
            birthnumber="7001145887", isInsurance="True")
    add_row(User, name="Jan", surname="Nový", password=bcrypt.generate_password_hash("password"),
            email="novy@gmail.com", phone="735121223", address="U Hradu 111", city="Brno",
            birthnumber="9801145447", isInsurance="True")
    add_row(User, name="Karel", surname="Veselý", password=bcrypt.generate_password_hash("password"),
            email="vesely@centrum.cz", phone="744000223", address="Brněnská 745", city="Brumlov",
            birthnumber="9801145447")
    add_row(User, name="Richard", surname="Starý", password=bcrypt.generate_password_hash("password"),
            email="stary@gmail.com", phone="735121223", address="Kolejení 2422", city="Jihlava",
            birthnumber="9002145447")
    add_row(User, name="Libuše", surname="Mladá", password=bcrypt.generate_password_hash("password"),
            email="mlada@gmail.com", phone="735004423", address="Pumpa 8851", city="Brno",
            birthnumber="9801425447")

@event.listens_for(HealthProblem.__table__, 'after_create')
def create_health_problem(*args, **kwargs):
    user= User.query.filter_by(email="vesely@centrum.cz").first()._id
    doctor= User.query.filter_by(email="dvorak@gmail.com").first()._id
    add_row(HealthProblem, name="Problém č.1", description="Pacient se cítí být unaven a má nechutenství.", patient_id =user, doctor_id=doctor, state="Otevřeno")
    user= User.query.filter_by(email="vesely@centrum.cz").first()._id
    doctor= User.query.filter_by(email="korn@mail.com").first()._id
    add_row(HealthProblem, name="Problém č.2", description="Pacient trpí bolestmi zad a má problémy s chůzí.", patient_id =user, doctor_id=doctor, state="Otevřeno")
    user= User.query.filter_by(email="mlada@gmail.com").first()._id
    doctor= User.query.filter_by(email="domovska@mail.com").first()._id
    add_row(HealthProblem, name="Problém č.3", description="Pacient trpí bolestmi zad a má problémy s chůzí.", patient_id =user, doctor_id=doctor, state="Otevřeno")

@event.listens_for(ExaminationRequest.__table__, 'after_create')
def exam_request_create(*args, **kwargs):
    user= User.query.filter_by(email="dvorak@gmail.com").first()._id
    doctor= User.query.filter_by(email="korn@mail.com").first()._id
    health_prob= HealthProblem.query.filter_by(name="Problém č.1").first()._id
    add_row(ExaminationRequest, name="Žádost o vyšetření č.1", description="Žádám o vyšetření pacienta",created_by=user, receiver=doctor, health_problem=health_prob, state="Nevyřízeno")
    user= User.query.filter_by(email="domovska@mail.com").first()._id
    doctor= User.query.filter_by(email="korn@mail.com").first()._id
    health_prob= HealthProblem.query.filter_by(name="Problém č.3").first()._id
    add_row(ExaminationRequest, name="Žádost o vyšetření č.2", description="Žádám o vyšetření pacienta",created_by=user, receiver=doctor, health_problem=health_prob, state="Nevyřízeno")

@event.listens_for(PaymentTemplate.__table__, 'after_create')
def template_init(*args, **kwargs):
    add_row(PaymentTemplate, name="Kyčelní kloub", price="4500",type="Operace")
    add_row(PaymentTemplate, name="Korunka", price="1000",type="Zubní zákrok")
@event.listens_for(PaymentRequest.__table__, 'after_create')
def request_create(*args, **kwargs):
    template =PaymentTemplate.query.all()[0]._id
    doctor = User.query.filter_by(email="korn@mail.com").first()._id
    validator = User.query.filter_by(email="novy@gmail.com").first()._id
    exam = ExaminationRequest.query.all()[0]._id
    add_row(PaymentRequest, template=template, creator=doctor, validator=validator, examination_request=exam)
if __name__ == '__main__':
    #db.drop_all() # odstraní původní db a nahradí novou
    db.create_all()
    app.run(debug=True, host='0.0.0.0')
