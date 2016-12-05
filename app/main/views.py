# -*- coding: utf-8 -*-
# @Author: wsljc
# @Date:   2016-11-18 11:07:10
# @Last Modified by:   wsljc
# @Last Modified time: 2016-12-05 22:23:28
from datetime import datetime
from flask import render_template, session, redirect, url_for, request, flash

from . import main
from .forms import LoginForm, RegisterForm, NewForm, AddForm
from .. import db
from ..models import Vote, User, Option, Classification
from flask_login import login_required, login_user, logout_user, current_user

@main.route('/', methods=['GET', 'POST'])
def index():
	classifications = Classification.query.all()
	votes = Vote.query.order_by(Vote.timestamp.desc()).all()
	options = Option.query.all()
	total = {}
	n = 0
	for vote in votes:
		for option in vote.options:
			n += option.number
		total[vote.id] = n
		n = 0
	return render_template('index.html', votes=votes, options=options, total=total, classifications=classifications)

@main.route('/<classification>', methods=['GET', 'POST'])
def index_(classification):
	classifications = Classification.query.all()
	i = Classification.query.filter_by(content=classification).first()
	votes = Vote.query.filter_by(classification_id=i.id).order_by(Vote.timestamp.desc()).all()
	options = Option.query.all()
	total = {}
	n = 0
	for vote in votes:
		for option in vote.options:
			n += option.number
		total[vote.id] = n
		n = 0
	return render_template('index.html', votes=votes, options=options, total=total, classifications=classifications)

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
	form.classification_id.choices = [(g.id, g.content) for g in Classification.query.order_by('id')]
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
			user=current_user._get_current_object(), 
			classification_id=form.classification_id.data
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

@main.route('/vote/<votename>', methods=['GET', 'POST'])
def vote(votename):
	vote=Vote.query.filter_by(name=votename).first()
	options = Option.query.filter_by(vote_id=vote.id).all()
	return render_template('vote.html', vote=vote, options=options)

@main.route('/success/option/<op>of<voteid>', methods=['GET', 'POST'])
def success(op, voteid):
	option=Option.query.filter_by(id=op).first()
	m = option.id
	db.session.execute('UPDATE options SET number = number+1 WHERE id = %d' % m)
	vote=Vote.query.filter_by(id=voteid).first()
	options = Option.query.filter_by(vote_id=vote.id).all()
	total = 0
	for option in vote.options:
		total += option.number
	return render_template('success.html', vote=vote, m=m, options=options, total=total)

@main.route('/usercenter', methods=['GET', 'POST'])
@login_required
def usercenter():
	votes = Vote.query.filter_by(user_id=current_user.id).order_by(Vote.timestamp.desc()).all()
	options = Option.query.all()
	total = {}
	n = 0
	for vote in votes:
		for option in vote.options:
			n += option.number
		total[vote.id] = n
		n = 0
	return render_template('usercenter.html', votes=votes, options=options, total=total)

@main.route('/usercenter/<v>', methods=['GET', 'POST'])
@login_required
def usercenter_(v):
	vote = Vote.query.filter_by(id=v).first()
	m = vote.id
	db.session.execute('DELETE FROM options WHERE vote_id = %d' % m)
	db.session.execute('DELETE FROM votes WHERE id = %d' % m)
	return redirect(url_for('.usercenter'))

@main.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
	return render_template('admin.html')

@main.route('/admin/votes', methods=['GET', 'POST'])
@login_required
def admin_votes():
	classifications = Classification.query.all()
	votes = Vote.query.order_by(Vote.timestamp.desc()).all()
	options = Option.query.all()
	total = {}
	n = 0
	for vote in votes:
		for option in vote.options:
			n += option.number
		total[vote.id] = n
		n = 0
	return render_template('admin_votes.html', votes=votes, options=options, total=total, classifications=classifications)

@main.route('/admin/votes/<v>', methods=['GET', 'POST'])
@login_required
def admin_votes_(v):
	vote = Vote.query.filter_by(id=v).first()
	m = vote.id
	db.session.execute('DELETE FROM options WHERE vote_id = %d' % m)
	db.session.execute('DELETE FROM votes WHERE id = %d' % m)
	return redirect(url_for('.admin_votes'))

@main.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
	users = User.query.filter(User.username!='admin').all()
	return render_template('admin_users.html', users=users)

@main.route('/admin/users/<v>', methods=['GET', 'POST'])
@login_required
def admin_users_(v):
	user = User.query.filter_by(id=v).first()
	m = user.id
	votes = Vote.query.filter_by(user_id=m).all()
	for vote in votes:
		n = vote.id
		db.session.execute('DELETE FROM options WHERE vote_id = %d' % n)
	db.session.execute('DELETE FROM votes WHERE user_id = %d' % m)
	db.session.execute('DELETE FROM users WHERE id = %d' % m)
	return redirect(url_for('.admin_users'))

@main.route('/admin/classifications', methods=['GET', 'POST'])
@login_required
def admin_classifications():
	classifications = Classification.query.all()
	return render_template('admin_classifications.html', classifications=classifications)

@main.route('/admin/classifications_add', methods=['GET', 'POST'])
@login_required
def admin_classifications_add():
	form = AddForm()
	if form.validate_on_submit():
		classification = Classification(
			content=form.name.data
			)
		db.session.add(classification)
		return redirect(url_for('.admin_classifications'))
	return render_template('admin_classifications_add.html', form=form)

@main.route('/admin/classifications/<v>', methods=['GET', 'POST'])
@login_required
def admin_classifications_(v):
	classification = Classification.query.filter_by(id=v).first()
	m = classification.id
	votes = Vote.query.filter_by(classification_id=m).all()
	for vote in votes:
		n = vote.id
		db.session.execute('DELETE FROM options WHERE vote_id = %d' % n)
	db.session.execute('DELETE FROM votes WHERE classification_id = %d' % m)
	db.session.execute('DELETE FROM classifications WHERE id = %d' % m)
	return redirect(url_for('.admin_classifications'))

@main.route('/logout')
@login_required
def logout():
	logout_user()
	flash('你已退出')
	return redirect(url_for('main.index'))