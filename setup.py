from setuptools import setup, find_packages

setup(
    name='kaggle-notebook-wrapper',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'kaggle-notebook-wrapper=kaggle-notebook-wrapper.module:main',
        ],
    },
)
