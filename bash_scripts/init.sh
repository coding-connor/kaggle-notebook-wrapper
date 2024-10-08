#!/bin/bash

# Define the package name and GitHub repository details
PACKAGE_NAME="kaggle_notebook_wrapper"
REPO_NAME="kaggle-notebook-wrapper"
GITHUB_USERNAME="coding-connor"
GITHUB_REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Create the main project directory
mkdir $PACKAGE_NAME

# Navigate into the project directory
cd $PACKAGE_NAME

# Create the package directory and files
mkdir $PACKAGE_NAME
touch $PACKAGE_NAME/__init__.py
touch $PACKAGE_NAME/module.py

# Create the tests directory and test file
mkdir tests
touch tests/test_module.py

# Create the scripts directory
mkdir scripts

# Create the example notebooks directory
mkdir example_notebooks

# Create the README.md file
cat <<EOL > README.md
# Kaggle Notebook Wrapper

This package allows you to push your notebook to Kaggle, wait for the output to be available, and then parses the output so that the output is attached to the correct cell.
EOL

# Create the setup.py file
cat <<EOL > setup.py
from setuptools import setup, find_packages

setup(
    name='$PACKAGE_NAME',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            '$PACKAGE_NAME=$PACKAGE_NAME.module:main',
        ],
    },
)
EOL

# Create the pyproject.toml file
cat <<EOL > pyproject.toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
EOL

# Initialize a new git repository
git init
git add .
git commit -m "Initial commit"

# Create the GitHub repository (requires GitHub CLI)
gh repo create $GITHUB_USERNAME/$REPO_NAME --private

# Add the remote GitHub repository
git remote add origin $GITHUB_REPO_URL

# Push the initial commit to GitHub
git push -u origin main

echo "Project structure for $PACKAGE_NAME created and pushed to GitHub successfully."