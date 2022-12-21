from . import create_app

# run server using gunicorn = gunicorn src.runner:application on terminal
application = create_app()