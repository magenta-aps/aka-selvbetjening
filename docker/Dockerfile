FROM python:3.6
RUN mkdir /backend && mkdir -p /var/log/aka
RUN apt-get update && apt-get install -y --no-install-recommends \
gettext \
wkhtmltopdf \
libxmlsec1-dev \
gpg
COPY backend/requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir -r /backend/requirements.txt
ENV PYTHONUNBUFFERED=1
COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./backend /backend
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
WORKDIR /backend
CMD ["gunicorn","-b","0.0.0.0:8000","project.wsgi:application","-w 4","--timeout 240", "--error-logfile", "-","--capture-output"]
