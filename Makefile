.PHONY: install dev collectstatic migrate build render-start

install:
	uv sync

dev:
	uv run python manage.py runserver

collectstatic:
	uv run python manage.py collectstatic --noinput

migrate:
	uv run python manage.py migrate

build:
	./build.sh

render-start:
	uv run gunicorn task_manager.wsgi:application --bind 0.0.0.0:$$PORT
