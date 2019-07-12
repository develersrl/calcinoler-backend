# Calcinoler

Calcinoler is a software for management of calcino matches in Develer


## Configuration

A file named `config.py` is the default for project configuration. If you want to change it, you can specify your custom configuration filename as a parameter of Flask app factory function. 
Following, the required parameters you must add in configuration file:

- `SQLALCHEMY_DATABASE_URI` database connection string
- `SLACK_TOKEN` auth token for Slack Api

You can add all Flask supported parameters. [Flask Configuration Docs](http://flask.pocoo.org/docs/1.0/config/).

## Scripts Usage

`script/bootstrap` will install all project's dependencies.

`script/setup` will create all database schema.

`script/update` will run `bootstrap` and `setup` scripts.

`script/server` will run app.

`script/test` will run test suite.
