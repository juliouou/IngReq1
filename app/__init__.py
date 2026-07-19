from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # --- Registro de blueprints por módulo (SAMR) ---
    from app.modules.m1_registro.routes import m1_bp
    from app.modules.m2_triaje.routes import m2_bp
    from app.modules.m3_monitoreo.routes import m3_bp
    from app.modules.m4_teleconsulta.routes import m4_bp
    from app.modules.m5_auditoria.routes import m5_bp

    app.register_blueprint(m1_bp, url_prefix="/api/m1")
    app.register_blueprint(m2_bp, url_prefix="/api/m2")
    app.register_blueprint(m3_bp, url_prefix="/api/m3")
    app.register_blueprint(m4_bp, url_prefix="/api/m4")
    app.register_blueprint(m5_bp, url_prefix="/api/m5")

    @app.route("/health")
    def health():
        return {"status": "ok", "proyecto": "SAMR"}

    @app.route("/registro")
    def pantalla_registro():
        return render_template("registro.html")

    return app
