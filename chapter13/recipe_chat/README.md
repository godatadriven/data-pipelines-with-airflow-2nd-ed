docker build -t local_dev .  

dcker run --env-file ../.env  -p 8084:8084 local_dev
``` 