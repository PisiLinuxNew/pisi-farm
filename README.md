# pisi-farm

Next generation pisi farm system

- [Abstract](#abstract)
- [Requirements](#requirements)
- [Installation](#installation)
- [Virtualenv](#virtualenv)
- [Flask](#flask)
- [Database](#database)
- [lxml](#lxml)

---

- [Özet](#Özet)
- [Gereksinimler](#gereksinimler)
- [Kurulum](#kurulum)
- [Virtualenv Sanal ortamı](#virtualenv-sanal-ortamı)
- [Flask Kurulumu](#flask-kurulumu)
- [Veritabanı](#veritabanı)
- [lxml](#lxml)

## Abstract

Current farm system that builds the packages for the PisiLinux distribution
have some shortcomings.This new approach will provide us more functionality,
like allowing volunteers to compile individual packages on their own systems
in a chrooted environment, or in a docker container.

Whole system will triggered by a github web hook. The details of the commit
will be parsed, and modified packages will be added to the compile queue.
An application running on the volunteers' computers will take the package
name and the docker image name associated with that github repository and
branch. That docker image will be pulled, and the package will be compiled
inside that docker image. Results of this operations (log files and if
successful, binary package files) will be uploaded to the web server.

## Requirements

- virtualenv
- Flask
- SQLAlchemy
- Database ( SQLite, MySQL or PostgreSQL)
- lxml

## Installation

Installation requires the installation of some python modules.These
python modules are not in pisi repository, so the first step is the installation of python-setuptools

`$ sudo pisi it python-setuptools`

### Virtualenv

Virtualenv enables side-by-side installations of Python, for each project.

`$ sudo easy_install virtualenv`

Then we can create our environment inside a directory:

```
$ mkdir pisifarm
$ cd pisifarm
$ virtualenv venv
New python executable in venv/bin/python
Installing setuptools, pip...done.
```

To activate this virtual environment:

```
$ source venv/bin/activate
(venv)ilker@pisi pisifarm $
```

Notice the change in the prompt. This shows that we are now in the
virtual environment.

### Flask

Inside the virtual environment, we can continue installing the other required
modules:

```
(venv)ilker@pisi pisifarm $ pip install flask
You are using pip version 6.1.1, however version 7.0.1 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
Collecting flask
Using cached Flask-0.10.1.tar.gz
lask-sqlalchemy
Collecting Werkzeug>=0.7 (from flask)
Using cached Werkzeug-0.10.4-py2.py3-none-any.whl
Collecting Jinja2>=2.4 (from flask)
Using cached Jinja2-2.7.3.tar.gz
Collecting itsdangerous>=0.21 (from flask)
Using cached itsdangerous-0.24.tar.gz
Collecting markupsafe (from Jinja2>=2.4->flask)
Using cached MarkupSafe-0.23.tar.gz
Installing collected packages: Werkzeug, markupsafe, Jinja2, itsdangerous, flask
Running setup.py install for markupsafe
Running setup.py install for Jinja2
Running setup.py install for itsdangerous
Running setup.py install for flask
Successfully installed Jinja2-2.7.3 Werkzeug-0.10.4 flask-0.10.1 itsdangerous-0.24 markupsafe-0.23
(venv)ilker@pisi pisifarm $
```

We also need more packages related with flask:

```
(venv)ilker@pisi pisifarm $ pip install flask-login
(venv)ilker@pisi pisifarm $ pip install flask-mail
(venv)ilker@pisi pisifarm $ pip install flask-whooshalchemy
(venv)ilker@pisi pisifarm $ pip install flask-wtf
(venv)ilker@pisi pisifarm $ pip install flask-babel
```

### SQLAlchemy

SQLAlchemy

`(venv)ilker@pisi pisifarm $ pip install flask-sqlalchemy`

### Database

We will use SQLite for simplicity, real system is using PostgreSQL.

`(venv)ilker@pisi pisifarm $ pip install pysqlite`

For PostgreSQL:

`(venv)ilker@pisi pisifarm $ pip install psycopg2`

For MySQL:

`(venv)ilker@pisi pisifarm $ pip install MySQL-python`

### lxml

lxml was used for parsing the pisi-index.xml files.
lxml python package requires libxml2-devel package:

```
(venv)ilker@pisi pisifarm $ sudo pisi it libxml2-devel libxslt-devel
(venv)ilker@pisi pisifarm $ pip install lxml
```

---

## Özet

Halihazırda kullanılan pisi paketlerini derleme sisteminin bazı eksiklikleri
bulunmaktadır. Tasarlanan yeni yaklaşım, bize daha fazla esneklik sağlayacak,
ve halen kullanılan sistemin eksikliklerini de kapatacaktır. Örneğin, yeni
sistemde, gönüllü kullanıcılar derlenmek üzere bekleyen paketleri kendi
sistemlerinde bir docker imajı içinde derleyebileceklerdir.

Tüm sistem, github commit işlemi ile tetiklenecektir. Commit işlemi bilgileri
parse edilecek, o commit işlemi ile değişikliğe uğramış paketler tespit
edilerek, derleme kuyruğuna alınacaklardır. Son kullanıcılarda çalışan bir
uygulama, derleme kuyruğunu sürekli olarak kontrol ederek, kuyruğa eklenmiş olan
paketlerin derlenmesi işlemini o repository ve branch icin belirlenmiş olan docker
imajı içinde başlatacaktır. Derleme işlemi sonucunda ortaya çıkacak olan log ve
pisi dosyaları merkezde bulunan sunucuya dosya upload işlemi ile gonderilecektir.

## Gereksinimler

- virtualenv
- Flask
- SQLAlchemy
- Database ( SQLite, MySQL veya PostgreSQL)
- lxml

## Kurulum

Kurulum için bazı python modüllerinin kurulması gerekmektedir. Bu modüller pisi
deposunda da bulunmadıkları için, önce python-setuptools paketi kurulacaktır:

`$ sudo pisi it python-setuptools`

### Virtualenv Sanal ortamı

Virtualenv ile, her bir proje için gerekli olacak python modülleri, gerçek sisteme
kurulmasına gerek kalmadan, bir dizin altına kurulup kullanılabilmektedir:

`$ sudo easy_install virtualenv`

Virtualenv uygulaması kurulduktan sonra, kendi uygulamamızın bulunacağı dizini
hazırlarız:

```
$ mkdir pisifarm
$ cd pisifarm
$ virtualenv venv
New python executable in venv/bin/python
Installing setuptools, pip...done.
```

Sanal ortama geçiş yapmak için:

```
$ source venv/bin/activate
(venv)ilker@pisi pisifarm $
```

Burada promptun nasıl değiştiğine dikkat edin. Böylece sanal ortamın içinde olduğunuzu
anlayabilirsiniz. Bu aşamada, python, easy_install, pip gibi komutları kullandığınzda,
gerçek sisteme değil, venv dizini altına modüller kurulacaktır.

### Flask Kurulumu

Sanal ortam içinde uygulamamız için gerekli olan diğer modülleri de yükleriz.

```
(venv)ilker@pisi pisifarm $ pip install flask
You are using pip version 6.1.1, however version 7.0.1 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
Collecting flask
Using cached Flask-0.10.1.tar.gz
Collecting Werkzeug>=0.7 (from flask)
Using cached Werkzeug-0.10.4-py2.py3-none-any.whl
Collecting Jinja2>=2.4 (from flask)
Using cached Jinja2-2.7.3.tar.gz
Collecting itsdangerous>=0.21 (from flask)
Using cached itsdangerous-0.24.tar.gz
Collecting markupsafe (from Jinja2>=2.4->flask)
Using cached MarkupSafe-0.23.tar.gz
Installing collected packages: Werkzeug, markupsafe, Jinja2, itsdangerous, flask
Running setup.py install for markupsafe
Running setup.py install for Jinja2
Running setup.py install for itsdangerous
Running setup.py install for flask
Successfully installed Jinja2-2.7.3 Werkzeug-0.10.4 flask-0.10.1 itsdangerous-0.24 markupsafe-0.23
(venv)ilker@pisi pisifarm $
```

Flask kullanabilmek için aşağıdaki paketler de gerekecektir:

```
(venv)ilker@pisi pisifarm $ pip install flask-login
(venv)ilker@pisi pisifarm $ pip install flask-mail
(venv)ilker@pisi pisifarm $ pip install flask-whooshalchemy
(venv)ilker@pisi pisifarm $ pip install flask-wtf
(venv)ilker@pisi pisifarm $ pip install flask-babel
(venv)ilker@pisi pisifarm $ pip install flask-sqlalchemy
```

### Veritabanı

Test ortamında kolaylık olması için SQLite kullanacağız, ancak gerçek sistemde PostgreSQL kullanılacaktır.

`(venv)ilker@pisi pisifarm $ pip install pysqlite`

PostgreSQL için:

`(venv)ilker@pisi pisifarm $ pip install psycopg2`

MySQL için:

`(venv)ilker@pisi pisifarm $ pip install MySQL-python`

### lxml Kurulumu

lxml paketi, pisi-index.xml dosyasını okumak için kullanılmıştır. Bu paketin
kurulumu için, libxml2-devel ve libxslt-devel paketlerinin de sistemde kurulu olması
gerekmektedir:

```
(venv)ilker@pisi pisifarm $ sudo pisi it libxml2-devel libxslt-devel
(venv)ilker@pisi pisifarm $ pip install lxml
```
