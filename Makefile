.PHONY: install dev collectstatic migrate build render-start makemessages compilemessages

install:
	uv sync

dev:
	uv run python manage.py runserver

collectstatic:
	uv run python manage.py collectstatic --noinput

migrate:
	uv run python manage.py migrate

makemessages:
	uv run python manage.py makemessages -l ru

compilemessages:
	uv run python manage.py compilemessages

build:
	./build.sh

render-start:
	uv run gunicorn task_manager.wsgi:application --bind 0.0.0.0:$$PORT
