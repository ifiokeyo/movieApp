import sqlalchemy as sa
from sqlalchemy.orm import validates
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ModelOpsMixin(object):
    """
    Contains the serialize method to convert objects to a dictionary
    """

    def serialize(self):
        return {column.name: getattr(self, column.name)
                for column in self.__table__.columns if column.name not in ['created_at', 'updated_at']}

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


movie_cast = db.Table('movie_cast',
                      db.Column('movie_id', db.String(), db.ForeignKey('movie.id'), primary_key=True),
                      db.Column('actor_id', db.String(), db.ForeignKey('person.id'), primary_key=True)
                      )

CONVERSATION_TYPE_ENUM = ('Personal', 'Group')


class Person(db.Model, ModelOpsMixin):
    __tablename__ = "person"

    id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String(1000), nullable=False)
    age = db.Column(db.String(1000), nullable=True)
    gender = db.Column(db.String(), nullable=True)
    eyeColor = db.Column(db.String(1000), nullable=True)
    hairColor = db.Column(db.String(1000), nullable=True)

    movies = db.relationship('Movie', secondary=movie_cast, lazy=True, backref=db.backref('cast', lazy=True))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        sa.CheckConstraint('char_length(name) > 0',
                           name='name column is required'),
    )

    @validates('name')
    def validate_name_is_supplied(self, key, name) -> str:
        if not name or name is None:
            raise ValueError('name is required')
        return name

    def __repr__(self):
        return f'Person: {self.name}'


class Movie(db.Model, ModelOpsMixin):
    __tablename__ = "movie"

    id = db.Column(db.String(), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    director = db.Column(db.String(), nullable=False)
    producer = db.Column(db.String(), nullable=False)
    releaseDate = db.Column(db.String(), nullable=False)
    rating = db.Column(db.String(), nullable=True)
    people = db.relationship('Person', secondary=movie_cast, lazy='joined')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'Movie: {self.title}'

