#/bin/bash
./remove.sh
docker build --tag djangodocker .
docker run -v ~/:/home/$USER -p 8000:8000 -e USER=$USER --detach --name dockerDjango djangodocker