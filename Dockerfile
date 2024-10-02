#FROM alpine:latest
#
#RUN apk update && apk upgrade \
#    && apk add --no-cache bash git openssh mysql mysql-client \
#    && apk add --no-cache python3 \
#    && apk add --no-cache openjdk8 \
#    # 设置 Python 环境变量
#    && ENV PATH="/usr/bin/python3:${PATH}" \
#    # 设置 Java 环境变量
#    && ENV JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk \
#    && ENV PATH="${JAVA_HOME}/bin:${PATH}"

#FROM alpine:latest
FROM python:3.10-alpine AS builder

WORKDIR /app

RUN apk add --no-cache build-base mysql-dev && \
    pip3 install --upgrade pip

COPY requirements.txt .

RUN pip3 wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.10-alpine

RUN apk add --no-cache bash vim && \
    apk add --no-cache openjdk8-jre

ENV JAVA_HOME=/usr/lib/jvm/default-jvm
ENV PATH=$PATH:$JAVA_HOME/bin

WORKDIR /app

COPY --from=builder /wheels /wheels

#RUN mkdir /app/go-cqhttp && cd /app/go-cqhttp && wget https://github.com/Mrs4s/go-cqhttp/releases/download/v1.1.0/go-cqhttp_linux_amd64.tar.gz && \
#    tar -zxvf go-cqhttp_linux_amd64.tar.gz && rm go-cqhttp_linux_amd64.tar.gz &&\
#    pip3 install --no-cache /wheels/* && \
#    rm -rf /wheels && \
#    rm -rf /root/.cache && \
#    rm -rf /var/cache/apk/* && \
#    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
#    echo "Asia/Shanghai" > /etc/timezone

RUN pip3 install --no-cache /wheels/* && \
    rm -rf /wheels && \
    rm -rf /root/.cache && \
    rm -rf /var/cache/apk/* && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

COPY . .

CMD sh /app/start.sh