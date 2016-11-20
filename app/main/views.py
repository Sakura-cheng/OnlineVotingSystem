# -*- coding: utf-8 -*-
# @Author: wsljc
# @Date:   2016-11-18 11:07:10
# @Last Modified by:   wsljc
# @Last Modified time: 2016-11-20 12:01:19
from datetime import datetime
from flask import render_template, session, redirect, url_for, request, flash

from . import main
from .forms import LoginForm, RegisterForm, NewForm
from .. import db
from ..models import Vote, User, Option
from flask_login import login_required, login_user, logout_user, current_user

@main.route('/', methods=['GET'])
def index():
	votes = Vote.query.order_by(Vote.timestamp.desc()).all()
	options = Option.query.all()
	return render_template('index.html', votes=votes, options=options)

@main.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('无效的用户名或密码')
	return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(
			username=form.username.data, 
			password=form.password.data
			)
		db.session.add(user)
		#db.session.commit()
		flash('你现在可以登录了')
		return redirect(url_for('.login'))
	return render_template('register.html', form=form)

@main.route('/new', methods=['GET', 'POST'])
@login_required
def new():
	form = NewForm()
	i = 1
	m = 0
	for vote in Vote.query.all():
		m += 1
	m += 1
	options = {}
	if form.validate_on_submit():
		vote = Vote(
			name=form.name.data, 
			description=form.description.data, 
			user=current_user._get_current_object()
			)
		db.session.add(vote)
		while request.form.get('option' + str(i)) is not None:
			option = request.form.get('option' + str(i))
			if option != "":
				options['option' + str(i)] = option
			i += 1
		for j in options:
			o = Option(
				content=options[j], 
				vote=Vote.query.filter_by(id=str(m)).first()
				)
			db.session.add(o)
		return redirect(url_for('.index'))
	return render_template('new.html', form=form)

@main.route('/secret')
@login_required
def secret():
	return '请登录！'

@main.route('/logout')
@login_required
def logout():
	logout_user()
	flash('你已退出')
	return redirect(url_for('main.index'))