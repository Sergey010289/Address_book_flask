# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_jwt import JWT, jwt_required
from models import Users, Contacts
from flask import request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import json


engine = create_engine('sqlite:///task2.db')
Session = sessionmaker(bind=engine)

app = Flask(__name__)

db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_EXPIRATION_DELTA'] = 3600   # time life token

jwt = JWT(app)


class User(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@jwt.authentication_handler
def authenticate(username, password):
    if username == 'joe' and password == 'pass':
        return User(id=1, username='joe')


@jwt.user_handler
def load_user(payload):
    if payload['user_id'] == 1:
        return User(id=1, username='joe')

#@app.route('/login', methods=['GET', 'POST'])
@app.route('/user/create', methods=['POST'])
@jwt_required()
def create_user():
    try:
        session = Session()
        user = Users(name=request.form.get('name'),
                     surname=request.form.get('surname'),
                     salt=request.form.get('salt'),
                     enc_passwd=request.form.get('enc_passwd'))
        session.add(user)
        session.commit()
        status = {'status': 'Success!', 'User_id': user.id}

    except IntegrityError:
        status = {'status': 'Error!', 'message': 'creating user'}

    return Response(response=json.dumps(status),
                    status=200,
                    mimetype="application/json")


@app.route('/user/update/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):

    session = Session()
    user = Users.query.filter_by(id=id).first()
    req = dict(request.form)

    for attr, value in req.iteritems():
        setattr(user, attr, value[0])

    session.merge(user)
    session.commit()

    status = {'status': 'Success!'}

    return Response(response=json.dumps(status),
                    status=200,
                    mimetype="application/json")

@app.route('/contact/create', methods=['POST'])
@jwt_required()
def create_contact():
    try:
        user = Users.query.filter_by(id=request.form.get('user_id', None)).first()
        user_id = user.id
        session = Session()
        if request.form.get('contact') and request.form.get('contact_type') and request.form.get('user_id'):
            obj = Contacts(contact=request.form.get('contact'),
                           contact_type=request.form.get('contact_type'),
                           users_id=user_id)
            session.add(obj)
            session.commit()
            status = {'status': 'Success!', 'Contact_id': obj.id}
        else:
            status = {'status': 'Error!', 'message': 'creating contact'}
    except AttributeError:
        status = {'status': 'Error!', 'message': 'user does not exist'}

    return Response(response=json.dumps(status),
                    status=200,
                    mimetype="application/json")

@app.route('/contact/update/<int:id>', methods=['PUT'])
@jwt_required()
def update_contact(id):

    session = Session()
    user = Contacts.query.filter_by(id=id).first()
    req = dict(request.form)

    for attr, value in req.iteritems():
        setattr(user, attr, value[0])

    session.merge(user)
    session.commit()

    status = {'status': 'Success!'}

    return Response(response=json.dumps(status),
                    status=200,
                    mimetype="application/json")


#@app.route('/user/search/<name>', methods=['GET'])
@app.route('/user/search', methods=['GET'])
@jwt_required()
def search_user():
    result = []
    if request.args.getlist('name') and request.args.getlist('surname'):
        name = request.args.getlist('name')[0]
        surname = request.args.getlist('surname')[0]

        user = Users.query.filter(func.lower(Users.name) == func.lower(name),
                                  func.lower(Users.surname) == func.lower(surname)).all()  # .first()#.all()
        cols = ['id', 'name', 'surname', 'salt', 'enc_passwd']
        result = [{col: getattr(d, col) for col in cols} for d in user]

    elif request.args.getlist('name'):
        name = request.args.getlist('name')[0]
        user = Users.query.filter(func.lower(Users.name) == func.lower(name)).all()  # .first()#.all()
        cols = ['id', 'name', 'surname', 'salt', 'enc_passwd']
        result = [{col: getattr(d, col) for col in cols} for d in user]

    elif request.args.getlist('surname'):
        surname = request.args.getlist('surname')[0]
        user = Users.query.filter(func.lower(Users.surname) == func.lower(surname)).all()  # .first()#.all()
        cols = ['id', 'name', 'surname', 'salt', 'enc_passwd']
        result = [{col: getattr(d, col) for col in cols} for d in user]

    else:
        print 'asdas'

    if result:
        for i in range(len(result)):
            contacts = Contacts.query.filter_by(users_id=result[i]['id']).all()
            cols = ['id', 'contact', 'contact_type']
            contacts = [{col: getattr(d, col) for col in cols} for d in contacts]
            result[i]['contacts'] = contacts

    else:
        result = {'status': 'Error!'}

    return Response(response=json.dumps(result),
                    status=200,
                    mimetype="application/json")


@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404


if __name__ == '__main__':
    # init DB
    #db.create_all()
    # print 'created'
    # app.run()
    print 'run'

    app.run(debug=True, port=5000)
