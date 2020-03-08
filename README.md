# Movie Application

 > A Movie app built with Flask.

## Requirements
 - Docker
 - Python3
 - Postgres
 - Flask
 - Redis

## Development setup

 > Clone this repo and navigate into the project's directory
 
 > create an `instance` directory in the root folder. 
 Copy the config_sample into the instance directory and rename it to `config.py`.


#### Start up the server

```bash
$ docker-compose up --build
```

 >  The app should now be available from your browser at `http://127.0.0.1:8000`

#### Run Tests

> Before running the test, ensure the test database is created. Do this with the following command:

```bash
$ docker exec -it sennder_db_1 sh -c "psql -U postgres"

Inside the psql terminal, run the following commands:

# \l  -- To see all database available, if test_sennder is missing, create it with:

# CREATE DATATBASE test_sennder;

# ALTER ROLE postgres WITH PASSWORD 'postres';

# ALTER ROLE postgres WITH SUPERUSER CREATEDB;

# \q -- to quit the psql terminal 
```

> Run test locally with the following command:

```bash
$ docker-compose -f docker-compose.test.yml up
$ docker-compose -f docker-compose.test.yml run --rm  app sh -c "pytest -s --disable-warnings"
```


##### Visit Movie Page

 > The movie page is available on `http://127.0.0.1:8000/movies`

  