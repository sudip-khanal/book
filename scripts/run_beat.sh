#!/bin/bash -x
celery -A config beat --loglevel=info
