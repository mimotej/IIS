
DROP TABLE if exists request_for_payment  ;
DROP TABLE if exists type_of_medical_intervention  ;
DROP TABLE if exists medical_report  ;
DROP TABLE if exists medical_examination_request  ;
DROP TABLE if exists health_problem  ;
DROP TABLE if exists health_insurance_worker  ;
DROP TABLE if exists doctor  ;
DROP TABLE if exists patient  ;
DROP TABLE if exists person  ;

CREATE TABLE person (
	id_person INT AUTO_INCREMENT  ,
	person_name VARCHAR(50) NOT NULL,
    person_password VARCHAR(255) ,
	surname VARCHAR(50) NOT NULL,
	email VARCHAR(50) ,
	phone_number VARCHAR(50) ,
    address VARCHAR(100) ,
    PRIMARY KEY(id_person),
	CONSTRAINT valid_email CHECK(email LIKE '%___@___%.__%'),
    UNIQUE(email)
);

CREATE TABLE patient (
	id_person INT NOT NULL ,
    date_of_birth DATE ,
    personal_identification_number VARCHAR(20),
    PRIMARY KEY(id_person),
    FOREIGN KEY (id_person) REFERENCES person (id_person)
);

CREATE TABLE doctor (
	id_person INT NOT NULL ,
    ward VARCHAR(100) ,
    PRIMARY KEY(id_person),
    FOREIGN KEY (id_person) REFERENCES person (id_person)
);

CREATE TABLE health_insurance_worker (
	id_person INT NOT NULL ,
	PRIMARY KEY(id_person),
    FOREIGN KEY (id_person) REFERENCES person (id_person)
);

CREATE TABLE health_problem (
	id_health_problem INT NOT NULL AUTO_INCREMENT ,
    problem_name VARCHAR(100) ,
    problem_description TEXT(1027) , 
    problem_state VARCHAR(100) ,
    problem_patient INT NOT NULL,
    problem_doctor INT NOT NULL,
    PRIMARY KEY(id_health_problem),
    FOREIGN KEY (problem_patient) REFERENCES patient (id_person),
    FOREIGN KEY (problem_doctor) REFERENCES doctor (id_person)
);



CREATE TABLE medical_examination_request (
	id_examination_request INT NOT NULL AUTO_INCREMENT ,
    request_name VARCHAR(100) , 
    request_text TEXT(1027) , 
    request_state VARCHAR(100) ,
    id_health_problem INT NOT NULL,
    
    id_doctor_who_created_it INT NOT NULL,
    id_doctor_who_work_on_it INT NOT NULL,
    PRIMARY KEY(id_examination_request),
    FOREIGN KEY (id_health_problem) REFERENCES health_problem (id_health_problem),
    
    FOREIGN KEY (id_doctor_who_created_it) REFERENCES doctor (id_person),
    FOREIGN KEY (id_doctor_who_work_on_it) REFERENCES doctor (id_person)
);

CREATE TABLE medical_report (
	id_medical_report INT NOT NULL AUTO_INCREMENT ,
    report_text TEXT(1027) , 
    report_attachement TEXT(1027) ,
    id_health_problem INT NOT NULL,
    id_doctor_who_wrote_it INT NOT NULL,
    id_examination_request INT,
    PRIMARY KEY(id_medical_report),
    FOREIGN KEY (id_examination_request) REFERENCES medical_examination_request (id_examination_request),
    FOREIGN KEY (id_health_problem) REFERENCES health_problem (id_health_problem),
    FOREIGN KEY (id_doctor_who_wrote_it) REFERENCES doctor (id_person)
);

CREATE TABLE type_of_medical_intervention (
	id_intervention INT  NOT NULL AUTO_INCREMENT ,
    intervention_name VARCHAR(100), 
    worker_who_made_it INT,
    intervention_price FLOAT(22) CHECK(intervention_price >= 0.0 OR intervention_price is NULL),
    PRIMARY KEY(id_intervention),
    FOREIGN KEY (worker_who_made_it) REFERENCES health_insurance_worker (id_person)
);

CREATE TABLE request_for_payment (
	id_payment_request INT  NOT NULL AUTO_INCREMENT ,
    payment_request_type VARCHAR(100) , 
    payment_request_state VARCHAR(100),
    id_examination_request INT NOT NULL,
    id_doctor_who_created_it INT NOT NULL,
    id_worker_who_validated_it INT ,
    id_intervention INT NOT NULL,
    PRIMARY KEY(id_payment_request),
    FOREIGN KEY (id_examination_request) REFERENCES medical_examination_request (id_examination_request),
    FOREIGN KEY (id_intervention) REFERENCES type_of_medical_intervention (id_intervention),
    FOREIGN KEY (id_doctor_who_created_it) REFERENCES doctor (id_person),
    FOREIGN KEY (id_worker_who_validated_it) REFERENCES health_insurance_worker (id_person)
);

-- Inserting to tables

INSERT INTO person (person_name, surname, email, phone_number) VALUES('Jozef', 'Mrkva', 'j.mrkva@gmail.com', '00000000');
INSERT INTO person (person_name, surname, email, phone_number) VALUES('Dusan', 'Hruska', 'd.hruska@gmail.com', '11111111');
INSERT INTO person (person_name, surname, email, phone_number) VALUES('Matej', 'Jablko', 'm.jablko@gmail.com', '22222222');
INSERT INTO person (person_name, surname, email, phone_number) VALUES('Peter', 'Chren', 'p.chren@gmail.com', '33333333');

INSERT INTO patient (id_person,date_of_birth) VALUES('2', STR_TO_DATE('12/31/2011', '%m/%d/%Y'));
INSERT INTO patient (id_person,date_of_birth) VALUES('3', STR_TO_DATE('01/02/2010', '%m/%d/%Y'));

INSERT INTO doctor (id_person,ward) VALUES('1', 'ORL');
INSERT INTO doctor (id_person,ward) VALUES('4', 'JIP');

INSERT INTO health_insurance_worker (id_person) VALUES('2');
INSERT INTO health_insurance_worker (id_person) VALUES('1');

INSERT INTO health_problem (problem_patient,problem_doctor,problem_name) VALUES('2','1','Bolest hlavy');
INSERT INTO health_problem (problem_patient,problem_doctor,problem_name) VALUES('2','4','Bolest zad');
INSERT INTO health_problem (problem_patient,problem_doctor,problem_name) VALUES('3','1','Zlomena ruka');
INSERT INTO health_problem (problem_patient,problem_doctor,problem_name) VALUES('3','4','Zlomena noha');

INSERT INTO medical_examination_request (id_health_problem,id_doctor_who_created_it,id_doctor_who_work_on_it,request_name) VALUES('1','4','1','Rentgen');
INSERT INTO medical_examination_request (id_health_problem,id_doctor_who_created_it,id_doctor_who_work_on_it,request_name) VALUES('2','4','1','Rehabilitace');
INSERT INTO medical_examination_request (id_health_problem,id_doctor_who_created_it,id_doctor_who_work_on_it,request_name) VALUES('3','1','4','Zafixovani sadrou');
INSERT INTO medical_examination_request (id_health_problem,id_doctor_who_created_it,id_doctor_who_work_on_it,request_name) VALUES('4','1','4','Sadrovani');

INSERT INTO medical_report (id_health_problem,id_doctor_who_wrote_it,id_examination_request,report_text) VALUES('1','1','1','Rentgen dopadl dobre');
INSERT INTO medical_report (id_health_problem,id_doctor_who_wrote_it,id_examination_request,report_text) VALUES('3','4','3','Zafixovani se nezdarilo');

INSERT INTO type_of_medical_intervention (intervention_name,worker_who_made_it, intervention_price) VALUES('Rentgen','2',150.0);
INSERT INTO type_of_medical_intervention (intervention_name,worker_who_made_it, intervention_price) VALUES('Sadra','1',200.0);

INSERT INTO request_for_payment (payment_request_type,id_examination_request,id_doctor_who_created_it,id_intervention) VALUES('Sadrovani','4','1','2');
INSERT INTO request_for_payment (payment_request_type,id_examination_request,id_doctor_who_created_it,id_intervention,id_worker_who_validated_it) VALUES('Rengenovani','1','4','1','2');



SELECT person.person_name , health_problem.problem_name , medical_examination_request.request_name
FROM patient  , person , health_problem ,medical_examination_request

WHERE person .id_person = patient.id_person AND patient.id_person = health_problem.problem_patient AND health_problem.id_health_problem = medical_examination_request.id_health_problem ; 




