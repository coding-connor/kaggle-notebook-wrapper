from setuptools import setup, find_packages

setup(
    name='kaggle-notebook-wrapper',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'kaggle',
    ],
    entry_points={
        'console_scripts': [
            'kaggle-wrapper=kaggle_notebook_wrapper.cli:main',
        ],
    },
)