release: python manage.py collectstatic --noinput
web: gunicorn config.wsgi --log-file -
web: python manage.py migrate && gunicorn config.wsgi

