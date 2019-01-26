# Quantum 3d Printer UI - By Persia Printer
For full documentation on this, go to www.persia3dprinter.ir

## How to install:
### `pip install quantum3d`
### `pip install -r requirements.txt`
## How to run:  
### `python app.py`
Note: Environment variables usage:  
To be able to run the app, use `FLASK_APP=quantum3d`  
For setting the base directory of usb mount, use `BASE_PATH`, which for raspberry pi by default should be set to `/media/pi`  
For development, use `FLASK_ENV=development`   
To set the database name, use `DB_NAME=<name>` (default: `database`)  
To enable camera support, use `CAMERA=<name>` (e.g. `pi`)  
To set a directory for uploading files, use `UPLOAD_FOLDER=</path/to/folder>` (default: `uploads`)


To set database connection limit if failed, use `DB_CONNECTION_LIMIT=<number>` (default is `3`)

## How to test:  
### `python test.py`
Note: use `-q` and `-v` for quiet and verbose running, respectively  
Note: the only way you'd know that you're in test mode, if anywhere needed, is by `ENV_MODE=test` env var, which is set at the beginning of test execution  
Note: Environment variables usage:  
Also you need to set `DB_NAME_TEST=<name>` for the test database name

> Note on environment variables: You can use `set env_var=value` (windows) or `export env_var=value` (linux) to set environment variables. Alternatively, you can use a `.env` file in project root directory and add these variables.
