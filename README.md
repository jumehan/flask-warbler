# 🪶 warbler
#### twitter clone
>  👩🏻‍💻 multi-day sprint, recreating a famous microblog
* users can register, sign in
* users can post and delete messages
* users like one another
* user can follow one another
* users can edit profile

#### ✨ accomplishments ✨:
* modeled relational database structures
* debug existing code bugs with pdb & debugger
* fixed routes, renderings
* extensive unit tests written for views and models
--------------------------------------------------------
## preview & demo:
![preview img](/warblerpreview.png)
* [demo](https://r27-warbler-jmh.herokuapp.com/)

## technologies:
* language: python
* framework: flask
* orm: SQLAlchemy
* brypt, WTFforms, unittests, jinja2

## issues & todos:

### future functionality:
* add ajax to popup modal for like/unlike
* dry up templates with {% macro/like/include %}
* dry up auth with decorators
* optimize queries
* add change password fn()
* allow private accounts
* add admin accounts
* add user blocking
* add direct messages


## setup:
in the project directory, you can run:
* CREATE VENV and install dependencies
```
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

* SETUP DATABASE
```
(venv) $ psql
=# CREATE DATABASE warbler;
=# (control-d)
(venv) $ python seed.py
```

* CREATE .env FILE FOR CONFIG
```
SECRET_KEY=*****
DATABASE_URL=postgresql:///warbler
```
* START SERVER
##### `flask run`
runs the app in the development mode.\
open [http://localhost:5000](http://localhost:5000) to view it in your browser.


