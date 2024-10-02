#!/bin/sh

cd /app/unidbg-fetch-qsign
nohup  bash bin/unidbg-fetch-qsign --library=txlib/8.9.63  --port=8080 --count=1 --android_id=005106571c6572b1 --host=0.0.0.0 > /app/qsign.log &
sleep 30

cd /app/go-cqhttp/
nohup  ./go-cqhttp > /app/go-cqhttp.log &
sleep 30

cd /app
python cqie_bot.py

