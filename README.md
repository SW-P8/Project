# Project
The main code base for the project

# Install

1. Make a virtual environment
```bash 
python -m venv .venv/
```
2. Activate the virtual environment
```bash
source .venv/bin/activate
```
3. Install the required libraries
```bash
pip install -r requirements.txt
```

# Modify Requirements

If you install a new package in the virtual environment and you want it to be a permanent part of the repository then make sure to add it to the `requirements.txt`.
You can do this with the following command
```bash
pip freeze > requirements.txt
```

# Postgresql
Make sure you have a postgresql server running on localhost.
If you are getting authentication failure then check that password and user matches
[Check this stackoverflow post to debug](https://stackoverflow.com/questions/18664074/getting-error-peer-authentication-failed-for-user-postgres-when-trying-to-ge)