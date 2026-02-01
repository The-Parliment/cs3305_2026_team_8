#!/bin/bash
set -e

# make sure mkdocs.yml exists.
if [ ! -f "mkdocs.yml" ]; then
	echo "ERROR: mkdocks.yml not found."
	exit 1
fi 

echo "Going to the next step"

# make sure mkdocs-requirements exists.
if [ ! -f "mkdocs_requirements.txt" ]; then
	echo "ERROR: mkdocks_requirements.txt not found."
	exit 1
fi

# check if .venv-docs python enviornment exists.
# if it does, activate it; If it doesnt, create & activate it.
if [ ! -d ".venv-docs" ]; then
	echo ".venv-docs doesnt exist, creating now."
	python3 -m venv .venv-docs
	echo ".venv-docs created..."
	source .venv-docs/bin/activate
	echo "activated .venv enviornment"
	pip install -r mkdocs_requirements.txt
else
	echo "Using existing .venv-docs enviornment."
	source .venv-docs/bin/activate
	#pip install -r mkdocs_requirements.txt
fi

echo "WARNING: A new venv has been created and activated"
echo "If you were working in a development venv, you need to reactivate it after finishing here."

# now serve the documents via mkdocs.
mkdocs serve -a localhost:5000
