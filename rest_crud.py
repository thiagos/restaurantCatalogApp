from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

def showRestaurants():
    return session.query(Restaurant).all()

def newRestaurant(a_name, a_user_id):
    myRestaurant = Restaurant(name = a_name,
                              user_id = a_user_id)
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

def newMenuItem(name, description, price, course, restaurant_id, user_id):
    myItem = MenuItem(name = name,
                      description = description,
                      price = price,
                      course = course,
                      restaurant_id = restaurant_id,
                      user_id = user_id)
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

def newUser(login_session):
    my_user = User(name = login_session['username'],
                  email = login_session['email'],
                  picture = login_session['picture'])
    session.add(my_user)
    session.commit()
    # Get from DB again, so we have access to the user id
    retrieved_user = getUserByEmail(login_session['email'])
    return retrieved_user

def getUserByEmail(email):
    myUser = session.query(User).filter_by(email=email).first()
    return myUser

def getUserById(user_id):
    myUser = session.query(User).filter_by(id=user_id).first()
    return myUser

def deleteUser(user_id):
    my_user = session.query(User).filter_by(id=user_id).first()
    session.delete(my_user)
    session.commit()
