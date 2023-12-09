# senditark-backend
A Flack API backend for senditark.


## Setup
### Python environment
 - Create venv (e.g., `python3.11 -m venv <venv_name>`)
 - Install reqs with `make install`
### Postgres Database (Manjaro/Arch install commands)
 - update / upgrade system `sudo pacman -Syu`
 - install postgresql `sudo pacman -S postgresql`
   - Postgres 15 at time of install
 - Verify version `postgres --version`
 - Go into postgres `sudo -iu postgres`
 - Initialize data directory
   ```bash
   initdb --locale $LANG -E UTF8 -D '/var/lib/postgres/data/'
   ```
 - `exit` after done
 - Start postgresql server `sudo systemctl start postgresql`
 - Check status `sudo systemctl status postgresql`
 - Enable it to run on boot `sudo systemctl enable postgresql`
 - Log in to psql as default user `sudo -u postgres psql`
 - Create new user
   ```postgresql
   CREATE USER <username> WITH ENCRYPTED PASSWORD '<password>';
   ```
 - Create database
   ```postgresql
   CREATE DATABASE <db>;
   ```
 - Grant all permissions to user on new db
   ```postgresql
   GRANT ALL PRIVILEGES ON DATABASE <db> TO <user>;
   ```
 - Make user owner of new db
   ```postgresql
   ALTER DATABASE <db> OWNER TO <user>;
   ```

## Running
For this instance, we'll try dockerizing, as locally I'm using a nginx proxy manager instance.

### Example docker file
[Source](https://github.com/wemake-services/wemake-django-template/blob/master/%7B%7Bcookiecutter.project_name%7D%7D/docker/django/Dockerfile)
```dockerfile
FROM python:3.11-alpine

ENV PYTHONBUFFERED=1 \
    POETRY_VERSION=1.7.0

# System deps
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project utilization
RUN poetry config virtualenvs.create false \
    && poetry install --no-interation --no-ansi

# Creating folders and files for project
COPY . /code
```