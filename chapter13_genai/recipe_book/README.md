1) 

docker build -t local_dev .

Upload files to MinIO
```bash
docker run --env-file ../.env --network=host local_dev upload "/app/sample_recipes/2024-10-14" "s3://data/2024-10-14/raw"   
```

Preprocess files
```bash
docker run --env-file ../.env --network=host local_dev preprocess "s3://data/2024-10-14" 
```

Split files in chunks
```bash
docker run --env-file ../.env --network=host local_dev split "s3://data/2024-10-14" 
```

Save to vector database
```bash
docker run --env-file ../.env --network=host local_dev save  "recipes" "s3://data/2024-10-14" 
```
