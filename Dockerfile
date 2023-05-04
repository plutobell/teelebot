FROM python:alpine

LABEL maintainer="github.com/plutobell"
LABEL description="A Telegram Bot Framework written in Python"
LABEL source="https://github.com/plutobell/teelebot"

RUN apk add --no-cache --virtual .build-deps tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apk del .build-deps \
    && pip3 install --no-cache-dir teelebot \
    && mkdir /config && mkdir /plugins \
    && history -c

ENTRYPOINT ["teelebot", "-c", "/config/config.cfg", "-p", "/plugins"]