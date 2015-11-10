from flask import Flask

app = Flask(__name__)

# Making an API Endpoint (GET Request)
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def showRestaurantJson(restaurant_id):
    restaurant = restaurant_crud.getRestaurant(restaurant_id)
    rest_items = restaurant_crud.getRestaurantItems(restaurant.id)
    return jsonify(MenuItems=[i.serialize for i in rest_items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/JSON')
def showRestaurantItemJson(restaurant_id, menu_item_id):
    rest_item = restaurant_crud.getMenuItem(menu_item_id)
    return jsonify(rest_item.serialize)

@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    return "page to show all restaurants!"

@app.route('/restaurants/new')
def createRestaurant():
    return "page to create a restaurant!"

@app.route('/restaurants/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
    return "page to edit a restaurant!"

@app.route('/restaurants/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    return "page to delete a restaurant!"

@app.route('/restaurants/<int:restaurant_id>/menu')
def showRestaurant(restaurant_id):
    return "page to show a restaurant!"

@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
    return "page to create a new menu item!"

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_item_id):
    return "page to edit a menu item!"

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/delete', methods=["GET", "POST"])
def deleteMenuItem(restaurant_id, menu_item_id):
    return "page to delete a menu item!"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)