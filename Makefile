ifneq (,$(wildcard ./.env))
    include .env
    export
endif

run:
	flask run

init_db:
	flask create-db
	flask db init
	 
routes:
	flask routes

list_users:
	flask list-users