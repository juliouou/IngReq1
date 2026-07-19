from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # crea samr.db con todas las tablas si no existe
    app.run(debug=True, port=5000)
