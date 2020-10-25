# A2 MOVIE APPLICATION

## Description

Mainly built off the covid web app, some minor visual changes were made, as well as changes to the memory_repository file to gather information to generate descriptions. Users cannot access any of the content without registering or logging in. Changes to the test files were made to work with the reworked code. Fulfills all points for the C grade.

## Installation

**Installation via requirements.txt**

```shell
$ cd A2
$ py -3 -m venv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

When using PyCharm, set the virtual environment using 'File'->'Settings' and select 'Project:COMPSCI-235' from the left menu. Select 'Project Interpreter', click on the gearwheel button and select 'Add'. Click the 'Existing environment' radio button to select the virtual environment. 

## Execution

**Running the application**

From the *A2* directory, and within the activated virtual environment (see *venv\Scripts\activate* above):

````shell
$ flask run
```` 


## Configuration

The *A2/.env* file contains variable settings. They are set with appropriate values.

* `FLASK_APP`: Entry point of the application (should always be `wsgi.py`).
* `FLASK_ENV`: The environment in which to run the application (either `development` or `production`).
* `SECRET_KEY`: Secret key used to encrypt session data.
* `TESTING`: Set to False for running the application. Overridden and set to True automatically when testing the application.
* `WTF_CSRF_SECRET_KEY`: Secret key used by the WTForm library.


## Testing

Testing requires that file *A2/tests/conftest.py* be edited to set the value of `TEST_DATA_PATH`. You should set this to the absolute path of the *A2/tests/data* directory. 

E.g. 

`TEST_DATA_PATH = os.path.join('C:', os.sep, 'Users', 'nicho', 'Documents', 'University 2020', 'Compsci 235',
                              'A2', 'tests', 'data')`
