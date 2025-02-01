#!/bin/bash -x

celery -A config worker --loglevel=info --max-tasks-per-child=20
