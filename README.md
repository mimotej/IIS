# PROJEKT IIS
Pro spuštěni je vyžadován docker

RHEL/CentOS - sudo yum install docker
Debian - sudo apt install docker (asi)
Zkontrolujte, zda=li je sližba docker aktivní: systemctl status docker Pokud služba aktivní není, aktivujte ji: systemctl start docker

Spuštění serveru:

sudo docker build -t iis-project .
sudo docker run -it -v $PWD:/app:Z -p 5000:5000 iis-project
Web je na http://0.0.0.0/5000

## Skupinový projekt vytvoření v Pythonu za využití Flask frameworku

## Finální hodnocení 

### 30/40
