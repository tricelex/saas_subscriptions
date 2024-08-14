bash:
	@docker compose -f docker-compose.local.yml run --rm django bash

build:
	@docker compose -f docker-compose.local.yml build

down:
	@docker compose down

format:
	@docker compose -f docker-compose.local.yml run --rm django ruff format .
	@docker compose -f docker-compose.local.yml run --rm django ruff check . --fix

lint:
	# mypy fails when Pydantic is present in codebase
	# haven't found a fix yet
	# @docker compose run --rm api poetry run mypy .
	@docker compose -f docker-compose.local.yml run --rm django ruff check .


migrate:
	@docker compose -f docker-compose.local.yml run --rm django python manage.py migrate

migrations:
	@docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations


resetdb:
	@docker compose run --rm api poetry run python src/manage.py reset_db --noinput

shell:
	@docker compose run --rm api poetry run python src/manage.py shell

stop:
	@docker compose stop

test:
	@docker compose -f docker-compose.local.yml run --rm django pytest -ra -vv tests/ -n 4 \
	--nomigrations -W error::RuntimeWarning --cov=saas_subscriptions --cov-report=html

testcase:
	@docker compose -f docker-compose.local.yml run --rm django py.test $(test) -vv

up:
	@docker compose -f docker-compose.local.yml up

es-index:
	@docker compose run --rm api poetry run python src/manage.py search_index -f --rebuild

superuser:
	@docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser

mypy:
	@docker compose -f docker-compose.local.yml run --rm django mypy saas_subscriptions

coverage:
	@docker compose -f docker-compose.local.yml run --rm django coverage run -m  pytest
