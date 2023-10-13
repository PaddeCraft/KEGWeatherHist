FROM alpine:latest

RUN mkdir /server

COPY run_prod.sh /server

COPY assets/ /server/assets/
COPY static/ /server/static/
COPY templates/ /server/templates/

COPY *.py /server
COPY requirements.txt /server

WORKDIR /server

RUN apk add python3 bash && \
    python3 -m ensurepip && \
    python3 -m pip install -r requirements.txt && \
    python3 -m pip install gunicorn && \
    rm requirements.txt && \
    chmod +x run_prod.sh && \
    mkdir /data

ENV HISTORY_FILE="/data/history.pickle"

ENTRYPOINT [ "/bin/bash", "/server/run_prod.sh"]