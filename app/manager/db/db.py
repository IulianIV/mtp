# from mtp import database, app
# from flask.cli import with_appcontext
# import click
#
#
# def init_app():
#     app.cli.add_command(init_db_command)
#
#
# def get_db():
#
#     db = database
#
#     return db
#
#
# @with_appcontext
# @click.command('init-db')
# def init_db_command():
#     """Clear the existing data and create new tables."""
#     init_db()
#     click.echo('Initialized the database.')
#
#
# def init_db():
#     db_init = get_db()
#     db_init.create_all()
#
#     return db_init
#
