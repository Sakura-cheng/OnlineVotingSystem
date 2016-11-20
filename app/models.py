# -*- coding: utf-8 -*-
# @Author: wsljc
# @Date:   2016-11-18 11:17:01
# @Last Modified by:   wsljc
# @Last Modified time: 2016-11-20 17:07:07
from . import db
from flask_login import UserMixin
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	#password = db.Column(db.String(64), nullable=False)
	password_hash = db.Column(db.String(128))
	votes = db.relationship('Vote', backref='user')

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

class Vote(db.Model):
	__tablename__ = 'votes'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True, index=True, nullable=False)
	description = db.Column(db.String(100))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	options = db.relationship('Option', backref='vote')

class Option(db.Model):
	__tablename__ = 'options'
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(64), nullable=False)
	number = db.Column(db.Integer, default=0)
	vote_id = db.Column(db.Integer, db.ForeignKey('votes.id'))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))