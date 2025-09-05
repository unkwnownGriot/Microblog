from flask import Blueprint
import os
import click

bp = Blueprint('cli', __name__, cli_group=None)

@bp.cli.group()
def translate():
    """Translation and localizations commands"""
    pass

@translate.command()
def update():
    """Update all languages"""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('Update command failed')
    os.remove('messages.pot')

@translate.command()
def compile():
    """Compile all languages"""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')
    
@translate.command()
@click.argument('lang')
def init(lang):
    """initialize new language"""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extractit command failed')
    if os.system('pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')   