from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

def showRestaurants():
    return session.query(Restaurant).all()

def newRestaurant(a_name):
    myRestaurant = Restaurant(name = a_name)
    session.add(myRestaurant)
    session.commit()

def editRestaurant(a_id, new_name):
    cur_restaurant = getRestaurant(a_id)
    if not new_name:
    	return
    cur_restaurant.name = new_name
    session.add(cur_restaurant)
    session.commit()

def deleteRestaurant(a_id):
    cur_restaurant = getRestaurant(a_id)
    session.delete(cur_restaurant)
    session.commit()

def newMenuItem(name, description, price, course, restaurant_id):
    myItem = MenuItem(name = name,
                      description = description,
                      price = price,
                      course = course,
                      restaurant_id = restaurant_id)
    session.add(myItem)
    session.commit()
    return myItem

def editMenuItem(menu_item_id, name, course=None, description=None, price=None):
    cur_item = getMenuItem(menu_item_id)
    # replace only if field is not empty
    if name:
        cur_item.name = name
    if course:
        cur_item.course = course
    if description:
        cur_item.description = description
    if price:
        cur_item.price = price
    session.add(cur_item)
    session.commit()
    return cur_item

def deleteMenuItem(a_id):
    cur_menu_item = getMenuItem(a_id)
    session.delete(cur_menu_item)
    session.commit()

def getRestaurantItems(rest_id):
    return session.query(MenuItem).filter_by(restaurant_id = rest_id)

def getMenuItem(menu_item_id):
    return session.query(MenuItem).filter_by(id = menu_item_id).one()

def getRestaurant(a_id):
    return session.query(Restaurant).filter_by(id = a_id).one()