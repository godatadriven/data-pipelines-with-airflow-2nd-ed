1) For Dockerfile.cli

docker build -t cli -f Dockerfile.cli .


Upload files to MinIO
```bash
docker run --env-file ~/.env --network=host cli upload "2024-10-01" 
```

Preprocess files
```bash
docker run --env-file ../.env --network=host cli preprocess "s3://data/2024-10-14" 
```

Save to vector database
```bash
docker run --env-file ../.env --network=host cli save  "recipes" "s3://data/2024-10-14" 
```


For Dockerfile.chat

```bash
docker build -t chat -f Dockerfile.chat .


docker run --env-file ~/.env -p 8084:8084 --network=chapter13_default chat
``` 