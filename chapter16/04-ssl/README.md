# SSL config

## Generate SSL certificate

```bash
openssl req \
-x509 \
-newkey rsa:4096 \
-sha256 \
-nodes \
-days 365 \
-keyout privatekey.pem \
-out certificate.pem \
-extensions san \
-config \
 <(echo "[req]";
   echo distinguished_name=req;
   echo "[san]";
   echo subjectAltName=DNS:localhost,IP:127.0.0.1
   ) \
-subj "/CN=localhost"
```

## Usage

```
docker compose up -d
```

Log in to the secure website https://localhost:8080
