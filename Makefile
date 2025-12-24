install:
	uv sync

dev:
	python manage.py runserver

collectstatic:
	python manage.py collectstatic --noinput

migrate:
	python manage.py migrate

build:
	./build.sh

render-start:
	gunicorn task_manager.wsgi:application --bind 0.0.0.0:$$PORT
