from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Inicializamos las extensiones sin asociarlas a una app todavía
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuraciones de la aplicación
    app.config["SECRET_KEY"] = "your_secret_key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tienda.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializamos la base de datos con la app
    db.init_app(app)

    # Importamos y registramos las rutas (o blueprints si los usas)
    with app.app_context():
        from app import models, main  # Importa los modelos y las rutas
        db.create_all()

    return app