FROM python:3.9
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.1.12/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=048b95b48b708983effb2e5c935a1ef8483d9e3e\
    PYTHONUNBUFFERED=1
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -fsSLO https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz && \
  tar xvf wkhtmltox*.tar.xz && \
  mv wkhtmltox/bin/wkhtmlto* /usr/bin
    
# hadolint ignore=DL3008
RUN mkdir /backend && mkdir -p /var/log/aka && mkdir -p /var/cache/aka \
 && apt-get update && apt-get install -y --no-install-recommends \
    gettext libxmlsec1-dev xmlsec1 gpg libmagic1 nano \
 && apt-get clean && rm -rf /var/lib/apt/lists/* \
 && curl -fsSLO "$SUPERCRONIC_URL" \
 && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
 && chmod +x "$SUPERCRONIC" \
 && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
 && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic \
 && groupadd -g 75080 -r aka  \
 && groupadd -g 75100 -r certificate_exporter \
 && useradd -m -u 75080 --no-log-init -r -g aka -G certificate_exporter aka \
 && chown aka:aka /var/log/aka \
 && chown aka:aka /var/cache/aka \
 && chmod a+w /var/cache/aka \
 && mkdir -p /ssl/sp \
 && mkdir -p /ssl/idp

COPY docker/crontab /crontab
COPY backend/requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir -r /backend/requirements.txt
COPY ./docker/entrypoint.sh /entrypoint.sh
COPY --chown=aka:aka ./backend /backend
# Include self-signed certificates for testing in pipeline
COPY dev-environment/cert/sp/selfsigned.* /ssl/sp/
COPY dev-environment/cert/idp/selfsigned.crt /ssl/idp/selfsigned.crt
USER aka
WORKDIR /backend
VOLUME  /var/cache/aka
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn","-b","0.0.0.0:8000","project.wsgi:application","-w 4","--timeout", "240", "--error-logfile", "-","--capture-output"]
