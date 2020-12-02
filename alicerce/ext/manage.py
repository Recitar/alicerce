import code
import click
from alicerce.ext.commands import (
    create_db,
    drop_db,
    add_user,
    del_user,
    list_users,
    clean_expired_tokens
)

def init_app(app):

    app.cli.add_command(app.cli.command()(create_db))
    app.cli.add_command(app.cli.command()(drop_db))
    app.cli.add_command(app.cli.command()(add_user))
    app.cli.add_command(app.cli.command()(del_user))
    app.cli.add_command(app.cli.command()(list_users))
    app.cli.add_command(app.cli.command()(clean_expired_tokens))
    
    @app.cli.command()
    def shell():
        """Abre um shell >>> com o `app` no contexto"""
        with app.app_context():
            code.interact(banner='SucupiraBot', local={'app': app})