# -*- coding: utf-8 -*-
# @Author: wsljc
# @Date:   2016-11-18 11:17:42
# @Last Modified by:   wsljc
# @Last Modified time: 2016-11-20 22:36:57
import os
from app import create_app, db
from app.models import User, Vote, Option
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
	return dict(app=app, db=db, User=User, Vote=Vote, Option=Option)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	#manager.run()
	app.run(host='0.0.0.0', debug=True)