from setuptools import find_packages, setup

setup(
    name='mtp',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-WTF',
        'flask-dropzone',
        'flask_sqlalchemy',
        'flask-migrate',
        'flask-login',
        'alembic',
        'werkzeug',
        'wtforms',
        'click',
        'pandas'
    ],
)
