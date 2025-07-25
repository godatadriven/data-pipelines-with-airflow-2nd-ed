# LDAP

Demonstrate RBAC UI + LDAP authentication using OpenLDAP.

## Usage

```
docker compose up -d
```

Login in Airflow with username `bsmith` and password `test`.

## Details

OpenLDAP is bootstrapped with:

- An admin user (DN=`cn=admin,dc=apacheairflow,dc=com`, password=`admin`)
- A readonly user (DN=`cn=readonly,dc=apacheairflow,dc=com`, password=`readonly`)
- A group named "engineers" (DN=`cn=engineers,dc=apacheairflow,dc=com`)
- A user in this group (DN=`cn=bob smith,dc=apacheairflow,dc=com`, password=`test`)

Exposed ports on host:
- 5432: PostgreSQL (user=airflow, pass=airflow)
- 8080: Airflow UI
- 8081: phpLDAPadmin (OpenLDAP UI)
