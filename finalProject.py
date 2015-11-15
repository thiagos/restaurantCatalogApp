from flask import Flask, render_template, url_for, redirect, request, flash
import rest_crud

app = Flask(__name__)

@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    restaurants = rest_crud.showRestaurants()
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurants/new', methods=['GET', 'POST'])
def createRestaurant():
    if request.method == 'GET':
        return render_template('newrestaurant.html')
    else:
        newRestaurant = rest_crud.newRestaurant(request.form['rest_name'])
        flash("new restaurant created!")
        return redirect(url_for('showRestaurants'))


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if request.method == 'GET':
        restaurant = rest_crud.getRestaurant(restaurant_id)
        menu_items = rest_crud.getRestaurantItems(restaurant_id)
        return render_template('editrestaurant.html', restaurant=restaurant, menu_items=menu_items)
    else:
        # edit on this level only for restaurant name
        # menu items edits are handled by editMenuItem function
        rest_crud.editRestaurant(restaurant_id, request.form['rest_name'])
        flash("Restaurant updated!")
        return redirect(url_for('editRestaurant', restaurant_id=restaurant_id))

@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = rest_crud.getRestaurant(restaurant_id)
    if request.method == 'GET':
        return render_template('deleterestaurant.html', restaurant=restaurant)
    else:
        rest_crud.deleteRestaurant(restaurant_id)
        flash('Restaurant ' + restaurant.name + ' deleted!')
        return redirect(url_for('showRestaurants'))

@app.route('/restaurants/<int:restaurant_id>/menu')
def showRestaurant(restaurant_id):
    restaurant = rest_crud.getRestaurant(restaurant_id)
    menu_items = rest_crud.getRestaurantItems(restaurant_id)
    return render_template('menu.html', restaurant=restaurant, menu_items=menu_items)

@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'GET':
        restaurant = rest_crud.getRestaurant(restaurant_id)
        return render_template('newmenuitem.html', restaurant=restaurant)
    else:
        menu_item = rest_crud.newMenuItem(request.form['menu_item_name'], restaurant_id)
        flash("New item " + menu_item.name + " created!")
        return redirect(url_for('editRestaurant', restaurant_id=restaurant_id))

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_item_id):
    menu_item = rest_crud.getMenuItem(menu_item_id)
    if request.method == 'GET':
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, item=menu_item)
    else:
        print "got here!"
        rest_crud.editMenuItem(menu_item_id=menu_item_id, 
                               name=request.form['name'],
                               description=request.form['description'],
                               course=request.form['course'],
                               price=request.form['price'])
        flash("Item " + request.form['name'] + " updated!")
        print "here too!"
        return redirect(url_for('editRestaurant', restaurant_id=restaurant_id))


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/delete', methods=["GET", "POST"])
def deleteMenuItem(restaurant_id, menu_item_id):
    menu_item = rest_crud.getMenuItem(menu_item_id)
    if request.method == 'GET':
        return render_template('deletemenuitem.html', menu_item=menu_item)
    else:
        rest_crud.deleteMenuItem(menu_item_id)
        flash("Item " + menu_item.name + " deleted!")
        return redirect(url_for('editRestaurant', restaurant_id=restaurant_id))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)