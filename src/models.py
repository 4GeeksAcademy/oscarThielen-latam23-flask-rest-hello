from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    color_eyes = db.Column(db.String, unique=False,nullable=False)
    height = db.Column(db.String, unique= False, nullable=False)

    """def __repr__(self):
        return '<Character %r>' % self"""

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "color_eyes": self.color_eyes,
            "height": self.height
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    terrain= db.Column(db.String, unique=False,nullable=False)
    surface= db.Column(db.String, unique= False, nullable=False)
    
    """def __repr__(self):
        return '<Planets %r>' % self"""

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "terrain": self.terrain,
            "surface": self.surface
        }

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    user = db.relationship("User")
    character= db.relationship("Character") 
    planets= db.relationship("Planets")

    def serialize(self):
        return{
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id
        }