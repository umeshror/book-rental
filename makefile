.PHONY: all build push deploy run stop

all: build push deploy

build:
	docker build -t umeshvjti/book-rental:latest -f .

push:
	docker push umeshvjti/book-rental:latest

run:
	docker-compose up

stop:
	docker-compose down