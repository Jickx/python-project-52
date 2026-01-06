.PHONY: install dev collectstatic migrate build render-start makemessages compilemessages makemigrations test test-one

list:
	uv pip list

install:
	uv sync

dev:
	uv run python manage.py runserver

collectstatic:
	uv run python manage.py collectstatic --noinput

migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

makemessages:
	uv run python manage.py makemessages -l ru

compilemessages:
	uv run python manage.py compilemessages

build:
	./build.sh

render-start:
	uv run gunicorn task_manager.wsgi:application --bind 0.0.0.0:$$PORT

test:
	uv run python manage.py test users

test-verbose:
	uv run python manage.py test users -v 2

# Run a single test by dotted label:
# make test-one TEST=users.tests.UserCRUDTestCase.test_user_list_view
test-one:
	uv run python manage.py test $(TEST)

# Install coverage into the uv environment (one-time or CI)
coverage-install:
	uv pip install coverage

# Run tests with coverage and produce console, HTML, and XML reports
test-coverage:
	uv run coverage run --source='users' manage.py test users || true
	uv run coverage report
	uv run coverage html
	uv run coverage xml

coverage-view:
	uv run python -c "import webbrowser, os; webbrowser.open('file:///' + os.path.abspath('htmlcov/index.html').replace('\\', '/'))"


