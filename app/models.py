from app import sql_db

db = sql_db


class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(45), index=True)
    last_name = db.Column(db.String(45), index=True)
    email = db.Column(db.String(100), index=True, unique=True)
    division = db.Column(db.Integer, index=True)
    admin = db.Column(db.Boolean, index=True, server_default='f')
    subscribed = db.Column(db.Boolean, index=True, server_default='t')

    def __repr__(self):
        return '<Player {} {}>'.format(self.first_name, self.last_name)