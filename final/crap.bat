cmd.exe /k retail.bat
celery worker --app=retailserver.tasks --loglevel=info
cmd.exe /k retail.bat
celery beat --app=retailserver.tasks --loglevel=info