FROM python:alpine

MAINTAINER <github.com/plutobell>

RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apk del tzdata \
    && rm -rf /var/cache/apk/* \
    && pip3 install teelebot \
    && mkdir /config && mkdir /plugins \
    && history -c

ENTRYPOINT ["teelebot", "-c", "/config/config.cfg", "-p", "/plugins"]