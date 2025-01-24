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

# TODO

- [] Push new version of arango-orm and update dependencies to use it. Required for building docker image for production.
- [] Graph traversal using the '/_api/traversal' endpoint is deprecated and removed from arangodb. Need to use PRUNE now. Will need to check if it's supported on older versions and also convert arango-orm and quranref code accordingly.

## Docker Swarm Deployment

On the swarm registry machine, build image and upload to registry

```shell
docker build -t localhost:5000/quranref:2.0.0 .
docker push localhost:5000/quranref:2.0.0
docker stack deploy --compose-file docker-compose.yml quranref
```

### Setup ArangoDB

```shell
docker exec -it <arango-container-id> arangosh

const users = require('@arangodb/users');
users.save('username', 'password');
db._createDatabase('quranref');
users.grantDatabase('quranref', 'quranref', 'rw');

```

### Create data folder in container

```shell
docker exec -it <arango-container-id> arangosh
mkdir /data
```

```shell
# on the docker host where data backup is present
docker cp quranref-db-dump/ <container-id>:/data
```

```shell
# Then on the container
arangorestore --server.endpoint tcp://127.0.0.1:8529 --server.username quranref --server.password password --server.database quranref --input-directory "quranref-db-dump"
```
