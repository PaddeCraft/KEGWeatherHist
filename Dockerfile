FROM alpine:latest

RUN mkdir /server

COPY run.sh /server

COPY *.py /server
COPY static /server
COPY templates /server

COPY requirements.txt /server

WORKDIR /server

RUN apk add python3 bash && \
    python3 -m ensurepip && \
    python3 -m pip install -r requirements.txt && \
    rm requirements.txt && \
    chmod +x run.sh && \
    mkdir /data

ENV HISTORY_FILE="/data/history.pickle"

ENTRYPOINT [ "/bin/bash", "/server/run.sh"]