'''
This is the python init file
'''
from flask import Flask
from celery import Celery
from celery.schedules import crontab
app = Flask(__name__)

def make_celery(app):
	celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
	celery.conf.update(app.config)
	TaskBase = celery.Task
	class ContextTask(TaskBase):
		abstract = True
		def __call__(self, *args, **kwargs):
			with app.app_context():
				return TaskBase.__call__(self, *args, **kwargs)
	celery.Task = ContextTask
	return celery

#celery config
app.config.update(
	CELERY_BROKER_URL='redis://localhost:6379',
	CELERY_RESULT_BACKEND='redis://localhost:6379',
	CELERY_TIMEZONE='Asia/Singapore',
	CELERYBEAT_SCHEDULE={
		'run-every-morning': {
			'task': 'retailserver.tasks.adjust_prices',
			'schedule': crontab(hour=6, minute=0),
		},
		'run-every-evening': {
			'task': 'retailserver.tasks.sync_transactions',
			'schedule': crontab(hour=22, minute=0),
		},
		'run-every-evening2': {
			'task': 'retailserver.tasks.restock',
			'schedule': crontab(hour=22, minute=30),
		},
	}
	)
celery = make_celery(app)