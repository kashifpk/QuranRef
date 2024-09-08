# Quran Reference

Online easily accessible searchable reference of the Holy Quran and it's translations.

## Dev Documentation

Create `.env` file with required parameters. See `env_example` for things that need to be present in `.env` file.

### First Time Setup


```shell
# First time
docker compose -f docker-compose-dev.yml build

# Bring up arangodb
docker compose -f docker-compose-dev.yml up --detach arangodb
```

Open arango web interface at: `http://127.0.0.1:8530` and create databases and users according to your `.env` file.


### Normal startup

```shell
docker compose -f docker-compose-dev.yml up --detach
```

Shell into app container

```shell
docker compose -f docker-compose-dev.yml exec app sh
```

Run commands against dockerized arangodb from local system (not the app container).

```
DB_HOSTS=http://127.0.0.1:8530 poetry run quranref-cli db --help
```