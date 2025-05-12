from models.ModelUser import db, User

def create_default_user():
    default_user = [
        {"username": "Gerente", "password": "gerente123"},
        {"username": "Cajero", "password": "cajero123"},
        {"username": "Mantenimiento", "password": "mantenimiento123"}
    ]

    for user_data in default_user:
        existing_user = User.query.filter_by(username=user_data["username"]).first()
        if not existing_user:
            user = User(username=user_data["username"], password=user_data["password"])
            db.session.add(user) 

    db.session.commit()