# pisi-farm
Next generation pisi farm system


- [Abstract] (#Abstract)
- [Requirements] (#Requierements)
- [Installation] (#Installation)
    * [Virtualenv] (#Virtualenv)
    * [Flask] (#Flask)
    * [SqlAlchemy] (#SqlAlchemy)
    * [Database] (#Database)
    * [lxml] (#lxml)
  
## Abstract ##
Current farm system that builds the packages for the PisiLinux distribution 
have some shortcomings. This new approach will provide us more functionality,
like allowing volunteers to compile individual packages on their own systems
in a chrooted environment, or in a docker container. 

Whole system will triggered by a github web hook. The details of the commit 
will be parsed, and modified packages will be added to the compile queue. 
An application running on the volunteers' computers will take the package
name and the docker image name associated with that github repository and 
branch. That docker image will be pulled, and the package will be compiled
inside that docker image. Results of this operations (log files and if 
successful, binary package files) will be uploaded to the web server.

## Requirements ##
* virtualenv
* Flask 
* SqlAlchemy
* Database ( Sqlite, mysql or postgresql)
* lxml 

## Installation ##
Installation requires the installation of some python modules. These 
python modules are not in pisi repository, so the first step is the  
installation of python-setuptools

    $ sudo pisi it  python-setuptools

### Virtualenv ###
Virtualenv enables side-by-side installations of Python, for each project.

    $ sudo easy_install virtualenv

Then we can create our environment inside a directory:

    $ mkdir pisifarm
    $ cd pisifarm
    $ virtualenv venv
    $ virtualenv venv
    New python executable in venv/bin/python
    Installing setuptools, pip...done.

To activate this virtual environment:

    $ source venv/bin/activate
    (venv)ilker@pisi pisifarm $ 

Notice the change in the prompt. This shows that we are now in the
virtual environment.

### Flask ###
Inside the virtual environment, we can continue installing the other required 
modules:

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

We also need more packages related with flask:

    (venv)ilker@pisi pisifarm $ pip install flask-login
    (venv)ilker@pisi pisifarm $ pip install flask-mail
    (venv)ilker@pisi pisifarm $ pip install flask-whooshalchemy
    (venv)ilker@pisi pisifarm $ pip install flask-wtf
    (venv)ilker@pisi pisifarm $ pip install flask-babel

### SQLAlchemy ###
SQLAlchemy 

    (venv)ilker@pisi pisifarm $ pip install flask-sqlalchemy
    
    
### Database ###
We will use sqlite for simplicity, real system is using postgresql. 

    (venv)ilker@pisi pisifarm $ pip install pysqlite
    
For postgresql:
    
    (venv)ilker@pisi pisifarm $ pip install psycopg2

For mysql:

    (venv)ilker@pisi pisifarm $ pip install MySQL-python 


### lxml ###
lxml python package requires libxml2-devel package:

    (venv)ilker@pisi pisifarm $ sudo pisi it libxml2-devel libxslt-devel
    (venv)ilker@pisi pisifarm $ pip install lxml 
    
lxml was used for parsing the pisi-index.xml files.

