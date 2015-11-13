from flask import Flask, render_template

app = Flask(__name__)

# Temp code, for templates basic test
#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

def getRest(id):
    for rest in restaurants:
        if int(rest['id']) == id:
            return rest

def getMenuItem(id):
    for item in items:
        if int(item['id']) == id:
            return item
# END Temp code, for templates basic test

@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurants/new', methods=['GET', 'POST'])
def createRestaurant():
    return render_template('newrestaurant.html')

@app.route('/restaurants/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
    restaurant = getRest(restaurant_id)
    return render_template('editrestaurant.html', restaurant=restaurant)

@app.route('/restaurants/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    restaurant = getRest(restaurant_id)
    return render_template('deleterestaurant.html', restaurant=restaurant)

@app.route('/restaurants/<int:restaurant_id>/menu')
def showRestaurant(restaurant_id):
    restaurant = getRest(restaurant_id)
    return render_template('menu.html', restaurant=restaurant)

@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
    return render_template('newmenuitem.html')

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_item_id):
    menu_item = getMenuItem(menu_item_id)
    return render_template('editmenuitem.html', menu_item=menu_item)

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/delete', methods=["GET", "POST"])
def deleteMenuItem(restaurant_id, menu_item_id):
    menu_item = getMenuItem(menu_item_id)
    return render_template('deletemenuitem.html', menu_item=menu_item)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)