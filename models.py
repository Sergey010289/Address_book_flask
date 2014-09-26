# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task2.db'

db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(255), nullable=True)
    enc_passwd = db.Column(db.String(255), nullable=False)
    addresses = db.relationship('Contacts', backref='user')

    def __init__(self, name, surname, salt, enc_passwd):
        self.name = name
        self.surname = surname
        self.salt = salt
        self.enc_passwd = enc_passwd

    def __repr__(self):
        return "{0}: {1}".format(self.name, self.surname,)


class Contacts(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    contact = db.Column(db.String(255), nullable=False)
    contact_type = db.Column(db.String(255), nullable=False)    # enum(tel, email, skype)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, contact, contact_type, users_id):
        self.contact = contact
        self.contact_type = contact_type
        self.users_id = users_id

    def __repr__(self):
        return "{0}: {1}".format(self.contact, self.contact_type,)


if __name__ == '__main__':
    # init DB
    db.create_all()
    print 'created'
    #app.run()
    #app.run(debug=True)
