from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()
class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Person(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    skin_color: Mapped[str] = mapped_column(String(10), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(10), nullable=False)
    eye_color: Mapped[str] = mapped_column(String(10), nullable=False)
    height: Mapped[str] = mapped_column(String(3), nullable=False)
    mass: Mapped[str] = mapped_column(String(3), nullable=False)
    birth_year: Mapped[str] = mapped_column(String(6), nullable=False)
    homeworld: Mapped[str] = mapped_column(String(50), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "url": f'people/{self.id}',
            "name": self.name,
            "gender": self.gender,
            "skin_color": self.skin_color,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "height": self.height,
            "mass": self.mass,
            "birth_year": self.birth_year,
            "homeworld": self.homeworld
        }

    def serialize_simple(self):
        
        return {
            "id": self.id,
            "name": self.name,
            "url": f'people/{self.id}'
        }

class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    climate: Mapped[str] = mapped_column(String(50), nullable=False)
    diameter: Mapped[str] = mapped_column(String(6), nullable=False)
    rotation_period: Mapped[str] = mapped_column(String(6), nullable=False)
    terrain: Mapped[str] = mapped_column(String(120), nullable=False)
    gravity: Mapped[str] = mapped_column(String(20), nullable=False)
    orbital_period: Mapped[str] = mapped_column(String(6), nullable=False)
    population: Mapped[str] = mapped_column(String(6), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "url": f'planets/{self.id}',
            "name": self.name,
            "climate": self.climate,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "terrain": self.terrain,
            "gravity": self.gravity,
            "orbital_period": self.orbital_period,
            "population": self.population,
        }

    def serialize_simple(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": f'planets/{self.id}'
        }


class Favorite(db.Model):
    __table_args__ = (
        UniqueConstraint('user_id', 'item_type', 'item_id',
                         name='unique_user_favorite'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)

    user: Mapped["User"] = relationship("User", backref="favorites")

    def serialize(self):
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "item_type": self.item_type
        }
        
        # Add the actual item data based on type
        if self.item_type == "planet":
            planet = Planet.query.get(self.item_id)
            if planet:
                result["planet"] = planet.serialize_simple()
        elif self.item_type == "person":
            person = Person.query.get(self.item_id)
            if person:
                result["person"] = person.serialize_simple()
        
        return result
