# Dockerfile
FROM python:3.8-buster

RUN apt-get update && apt-get install nginx -y --no-install-recommends
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

RUN mkdir -p /opt/app/static
RUN mkdir -p /opt/app/backend
WORKDIR /opt/app/backend
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./backend .
COPY ./deployment/backend/nginx.conf /etc/nginx/sites-available/default
COPY ./deployment/backend/start_server.sh /opt/app/backend/buildfiles/start_server.sh
#RUN python manage.py collectstatic
#RUN chown -R www-data:www-data /opt/app/

EXPOSE 8002
STOPSIGNAL SIGTERM
RUN chmod 777 /opt/app/backend/buildfiles/start_server.sh
CMD ["/opt/app/backend/buildfiles/start_server.sh"]
