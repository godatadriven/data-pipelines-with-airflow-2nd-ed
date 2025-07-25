# Chapter 15

Code accompanying Chapter 15 (Securing Airflow) of the book [Data Pipelines with Apache Airflow](https://www.manning.com/books/data-pipelines-with-apache-airflow).

## Contents

This folder holds three example Docker Compose examples:

- `01-rbac`: Example explaining the RBAC interface
- `02-webserver-theme`: Explaining the UI configuration
- `03-ldap`: Example configuration fetching user credentials from OpenLDAP
- `04-ssl`: Example configuring a secure connection between Airflow components
- `05-secretsbackend`: Example fetching secrets from HashiCorp Vault

Each folder holds a Docker Compose file which can be started with `docker compose up -d`.

## Usage

Read the `README.md` file in the respective directory.
