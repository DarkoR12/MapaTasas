FROM ubuntu:16.10

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8

ENV HOME /root
ENV SECRET_KEY no-secret-key #Set a secure Django secret key for production!

## ENVRIOMENT DEPENDENCIES
RUN apt-get update && \
    apt-get install -y -q libtiff5-dev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk python3-pip python3-dev nodejs-legacy npm git && \
    pip3 install --upgrade pip  && \
    npm install -g topojson ogr2ogr

RUN npm install -g bower@1.7.8


WORKDIR $HOME
COPY . $HOME
    
## PROJECT DEPENDENCIES
RUN pip3 install -r requirements.txt
RUN bower install --allow-root

## DEPLOY

RUN python3 manage.py migrate # Creación de la base de datos y definición de tablas
RUN python3 manage.py collectstatic --noinput # Copia los ficheros estáticos de todas las aplicaciones a un directorio común
RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'password')" | python3 manage.py shell # Crea un superusuario
RUN python3 manage.py check --deploy # Comprueba que los ajustes definidos son apropiados para una configuración de despliegue
RUN python3 manage.py importar mapa/data/uni/unis.json mapa/img/uni
RUN python3 manage.py rendervariations 'tasas.universidad.logo'


EXPOSE 8000

#CMD ["python3", "manage.py runserver 0.0.0.0:8000"]
