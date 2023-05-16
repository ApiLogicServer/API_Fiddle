from safrs import SAFRSAPI
import logging as logging

app_logger = logging.getLogger("api_logic_server_app")

# use absolute path import for easier multi-{app,model,db} support
database = __import__('database')

def open_databases(flask_app, session, safrs_api, method_decorators):
    """ called by api_logic_server_run to open each additional database, and expose APIs """

    # Begin Bind URLs


    from api import authentication_expose_api_models
    from database import authentication_models

    # flask_app.config.update(SQLALCHEMY_BINDS = \
    #     {'authentication': flask_app.config['SQLALCHEMY_DATABASE_URI_AUTHENTICATION']})
    
    app_logger.debug(f"\nauthentication Config complete - database/authentication_models.py"
        + f'\n -- with bind: authentication'
        + f'\n -- len(database.authentication_models.authentication.metadata.tables) tables loaded')
    
    authentication_expose_api_models.expose_models(safrs_api, method_decorators= method_decorators)

        # End Bind URLs

    flask_app.config.update(SQLALCHEMY_BINDS = {
		'authentication': flask_app.config['SQLALCHEMY_DATABASE_URI_AUTHENTICATION']
    })  # make multiple databases available to SQLAlchemy
    return