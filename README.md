# ELCM (Experiment Life-Cycle Manager)

## Requirements

[Python 3.7.x](https://www.python.org)

## Installing (development)
> It is recommended, but not required, to run the Portal in a [Python virtual environment](https://virtualenv.pypa.io/en/stable/).
> If you are not using virtual environments, skip steps 3 and 4.

1. Clone the repository to a known folder, e.g. in `c:\ELCM` 
2. Enter the folder
```bash
cd c:/ELCM
```
3. Create a new Python virtualenv:
```bash
pip install virtualenv
virtualenv venv
```
4. Activate the virtual environment:
- For Windows:
```powershell
venv\Scripts\Activate.bat
```
- For Linux:
```bash
source venv/bin/activate
```
5. Install Python dependencies:
```bash
pip install -r requirements.txt
```

6. Start the development server:
```bash
flask run
```
The app will generate a default configuration file (`config.yml`) and start listening for requests on port 5001.
Refer to the Configuration section for information about customizing the default values.
Press `Control+C` to stop the development server.

## Deployment (production)

Since the ELCM should not be exposed to the Internet (the administration interface should only be accessed on the host 
machine or from inside a trusted network), and it will not receive a large number of concurrent requests it is possible 
to run the ELCM using the included development server. 

It is, however, also possible to run the ELCM using a production WSGI server such as [Waitress](https://github.com/Pylons/waitress) 
following these instructions:

1. Install Waitress on the ELCM Python environment:
```bash
pip install waitress
```
2. Start the server:
```bash
waitress-serve --listen=*:5001 app:app
```

## Configuration

The ELCM instance can be configured by setting environment variables and by editing the `config.yml` file. The ELCM uses
`python-dotenv`, so it's possible to save the environment variables in the `.flaskenv` file.

The environment variables that can be set are:
* FLASK_RUN_PORT: Port where the portal will listen (5001 by default)

The values that can be configured on `config.yml` are:
* TempFolder: Root folder where the temporal files for the Executors can be created.
* Logging:
    * Folder: Root folder where the different log files will be saved.
    * AppLevel: Minimum log level that will be displayed in the console.
    * LogLevel: Minimum log level that will be recorded in the log files.
* Dispatcher:
    * Host: Location of the machine where the Dispatcher is running (localhost by default).
    * Port: Port where the Dispatcher is listening for connections (5000 by default).
> The Dispatcher does not currently exist as a separate entity, so this information refers to the Portal during Release A.
* Flask:
    * SECRET_KEY: A random string.
> Since the ELCM should not be exposed to the Internet it is not so important to set a random SECRET_KEY. However, the 
value is still needed and it's recommended to follow the same approach as in the 5Genesis Portal.

## Authors

* **Bruno Garcia Garcia**

## License

TBD