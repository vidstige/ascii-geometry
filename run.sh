#!/bin/sh
FLASK_ENV=development FLASK_APP=server.py venv/bin/flask run $@
