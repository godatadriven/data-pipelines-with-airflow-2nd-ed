# RBAC demo

This docker compose file demonstrates the Airflow RBAC interface.

This is mainly based on the standard compose file.

## Usage

```
docker compose up -d
```

### Create first user

With this command you can add a user from the commandline

```
docker compose run airflow-cli bash
```

```
airflow users create \
  --role Admin \
  --username bobsmith \
  --password topsecret \
  --email bobsmith@company.com \
  --firstname Bob \
  --lastname Smith
```

Login in [Airflow UI](localhost:8080) username/password `bobsmith`/`topsecret`.
