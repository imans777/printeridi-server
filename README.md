# Quantum 3d Printer UI - By Persia Printer
For full documentation on this, go to www.persia3dprinter.ir

## How to run:  
### use `python app.py` to run the app  
Note: Environment variables usage:  
To be able to run the app, use `FLASK_APP=quantum3d`  
For development, use `FLASK_ENV=development`  
To test on windows, use `DEV_ENV=windows`  
To set the database name, use `DB_NAME=<name>` (default: `database`)  
To set database connection limit if failed, use `DB_CONNECTION_LIMIT=<number>` (default is `3`)

## How to test:  
### use `python test.py` to run the tests  
Note: use `-q` and `-v` for quiet and verbose running, respectively  
Note: Environment variables usage:  
Also you need to set `DB_NAME_TEST=<name>` for the test database name

> Note on environment variables: You can use `set env_var=value` (windows) or `export env_var=value` (linux) to set environment variables. Alternatively, you can use a `.env` file in project root directory and add these variables.
