
all:

up:
	docker compose -f ./docker-compose.yml up -d --build

log:
	docker compose -f ./docker-compose.yml up --build

down:
	docker compose -f ./docker-compose.yml down

collectstatic:
	docker exec -d backend python /var/django-site/manage.py collectstatic --noinput

migrate:
	docker exec -d backend python /var/django-site/manage.py migrate --noinput

cleandb:
	rm -rf ./srcs/pgdata

selfsigned-cert:
	openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout ./srcs/nginx/certs/selfsigned.key -out ./srcs/nginx/certs/selfsigned.crt  -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=localhost:8001"
	openssl dhparam -out ./srcs/nginx/certs/dhparam.pem 4096
