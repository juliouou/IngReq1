.PHONY: install makemigrations migrate seed superuser run test docker-up docker-down clean

install:
	pip install -r requirements.txt

makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

seed:
	python manage.py seed

superuser:
	python manage.py createsuperuser

run:
	python manage.py runserver

test:
	python manage.py test

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
