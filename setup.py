from setuptools import find_packages, setup
import os

setup(
    name='mtp',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'wtforms',
        'click',
        'pandas',
        'flask-dropzone',
        'flask_sqlalchemy',
        'werkzeug',
        'flask-migrate'
    ],
)
