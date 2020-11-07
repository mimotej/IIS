#PROJEKT IIS
Pro spuštěni je vyžadován docker

RHEL/CentOS - sudo yum install docker
Debian - sudo apt install docker (asi)
Zkontrolujte, zda=li je sližba docker aktivní: systemctl status docker Pokud služba aktivní není, aktivujte ji: systemctl start docker

Spuštění serveru:

sudo docker build -t iis-project .
sudo docker run -it --network="host" -v $PWD:/app:Z -p 5000:5000 iis-project
Web je na http://0.0.0.0/5000

Odkaz na ER: https://drive.google.com/file/d/19_xYOqh3i3iQrzInmw7zHrXK5splNtJC/view?usp=sharing NUTNÉ přidat v drivu

###Spuštění appky s DB
Metoda funguje na ubuntu distribucích (mint, pop_os, lubuntu etc.)
Instalace mysql
```
sudo apt install mysql-server
```
Konfigurace mysql
```
sudo mysql_secure_installation
```
Nastavit heslo zbytek nezáleží extra moc kromě posledního který se musí potvrdit\
Přihlásíme se jako root
```
sudo mysql -u root
```
Vytvoříme DB
```
CREATE DATABASE IIS;
```
Vložíme data
```
USE IIS;
source abs/adresa/k/sql_souboru.sql
```
Vytvoříme uživatele flask
```
create user 'flask'@'localhost' identified by 'password';
grant usage on *.* to 'flask'@'localhost';
grant all privileges on IIS to 'flask'@'localhost';
ALTER USER 'flask'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';
```
v app.py nastavíme `app.config['SQLALCHEMY_DATABASE_URI'] =` na `'mysql://flask:password@127.0.0.1/IIS'`
pak spouštíme docker 
```
sudo docker run -it --network="host" -v $PWD:/app:Z -p 5000:5000 iis-project
```
####Debugovací tipy
Zkusit zda funguje mysql server
```
service mysql status
```
Případně zkusit nastartovat
```
service mysql start
```
Otestovaní zda funguje spojení s mysql
```
echo X | telnet -e X 127.0.0.1 3306
```
Výsledek by měl vypadat
```
Telnet escape character is 'X'.
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is 'X'.

telnet> Connection closed.
```
