FROM alpine:3.8

USER root

WORKDIR /home/app

COPY . /home/app

ENV ALPINE_MIRROR "http://dl-cdn.alpinelinux.org/alpine"
RUN echo "${ALPINE_MIRROR}/edge/main" >> /etc/apk/repositories
RUN apk add --no-cache nodejs-current  --repository="http://dl-cdn.alpinelinux.org/alpine/edge/community"
RUN apk add --update nodejs-npm

RUN node --version

RUN apk add nano

EXPOSE 3000

# docker run -d   -it   --name bimtransfer   --mount type=bind,source="$(pwd)",target=/home/app   bim-transfer-image:BT-alpine /bin/sh