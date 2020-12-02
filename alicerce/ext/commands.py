import click

from alicerce.alicerce_api.models.user import User
from alicerce.alicerce_api.models.token_revokedlist import RevokedToken
from alicerce.ext.db import db


def create_db():
    """Cria as tabelas do banco"""
    db.create_all()


def drop_db():
    """Deleta todas as tabelas do banco"""
    db.drop_all()

def list_users():
    """Lista todos os usuários do banco de dados"""
    try:
        users = User.query.all()
        click.echo(f"lista de usuários: {users}")
    except Exception:
        click.echo("Não foi possível recuperar a lista de usuários.")



def clean_expired_tokens():
    """Remove os tokens expirados do banco de dados"""
    try:
        RevokedToken.prune_database()
        click.echo("Operação realizada com sucesso!")
    except Exception:
        click.echo("Não foi possível remover os tokens expirados.")



@click.option("--usr", "-u", "username")
@click.option("--pwd", "-p", "password")
@click.option("--admin", "-a", is_flag=True, default=False)
def add_user(username, password, admin=False):
    """Adiciona um novo usuário ao banco de dados.

    Args:
        username (str): nome do usuário, deve ser único.
        password (str): senha utilizada para logar no sistema
        admin (bool, optional): Flag que indica se o usuário é um admin. Defaults to False.
    """
    try:
        user = User(username=username, password=password, admin=admin)
        user.save_to_db()
    except Exception as e:
        click.echo(f'Não foi possivel criar o usuário {username}.')
        # raise
    else:
        click.echo(f"Usuário {username} criado com sucesso!")


@click.option("--usr", "-u", "username")
def del_user(username):
    """Deleta um usuário do banco de dados.

    Args:
        username (str): nome do usuário a ser deletado.
    """
    try:
        user = User.find_by_username(username)
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        click.echo(f'Não foi possivel remover o usuário {username}.')
        # raise
    else:
        click.echo(f"Usuário {username} removido com sucesso!")