import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):

    __tablename__ = 'user'
    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String(80), nullable = False)
    picture = Column(String(200), nullable = True)
    email = Column(String(100), nullable = False)
    restaurants = relationship("Restaurant", backref='user', cascade='all, delete-orphan')
    menu_items = relationship("MenuItem", backref='user', cascade='all, delete-orphan')

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name' : self.name, 
            'id' : self.id,
            'picture' : self.picture,
            'email' : self.email
        }

class Restaurant(Base):

    __tablename__ = 'restaurant'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    menu_items = relationship("MenuItem", backref='restaurant', cascade='all, delete-orphan')

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name' : self.name, 
            'id' : self.id 
        }

class MenuItem(Base):

    __tablename__ = 'menu_item'

    id = Column(Integer, primary_key = True)
    name = Column(String(250))
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name' : self.name,
            'description' : self.description,
            'id' : self.id,
            'price' : self.price,
            'course' : self.course,
        }

engine = create_engine('sqlite:///restaurantmenuwithusers.db')

Base.metadata.create_all(engine)