from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
from collections import OrderedDict
import rest_crud

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

# JSON API routes
@app.route('/restaurants/JSON')
def allRestaurantsJSON():
    all_rests = rest_crud.showRestaurants()
    return jsonify(Restaurants=[rest.serialize for rest in all_rests])


@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def getRestaurantJSON(restaurant_id):
    all_items = rest_crud.getRestaurantItems(restaurant_id)
    return jsonify(MenuItems=[item.serialize for item in all_items])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/JSON')
def getMenuItemJSON(restaurant_id, menu_item_id):
    menu_item = rest_crud.getMenuItem(menu_item_id)
    return jsonify(MenuItem=menu_item.serialize)

# TESTING PURPOSES ONLY, should not show users info openly :)
@app.route('/users/<int:user_id>/JSON')
def getUserJSON(user_id):
    user = rest_crud.getUserById(user_id)
    return jsonify(User=user.serialize)

# Login related routes
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=login_session['state'])

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    local_user = rest_crud.getUserByEmail(login_session['email'])
    if local_user:
        print "user already exists!"
        login_session['user_id'] = local_user.id
    else:
        print "new user being created!"
        new_user = rest_crud.newUser(login_session)
        login_session['user_id'] = new_user.id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/fbconnect', methods=["POST"])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.5/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.5/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    local_user = rest_crud.getUserByEmail(login_session['email'])
    if local_user:
        print "user already exists!"
        login_session['user_id'] = local_user.id
    else:
        print "new user being created!"
        new_user = rest_crud.newUser(login_session)
        login_session['user_id'] = new_user.id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['facebook_id']
    return "you have been logged out"

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['gplus_id']
        return 'Successfully disconnected.'
    else:
        return 'Failed to revoke token for given user.'

@app.route('/disconnect')
def disconnect():
    if 'access_token' not in login_session or login_session['access_token'] is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if login_session['provider'] == 'facebook':
        return_message = fbdisconnect()
    elif login_session['provider'] == 'google':
        return_message = gdisconnect()
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['access_token']
    flash(return_message)
    return redirect(url_for('showRestaurants'))

# navigation routes
@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    restaurants = rest_crud.showRestaurants()
    if 'username' not in login_session:
        return render_template('publicrestaurants.html', restaurants=restaurants)
    else:
        return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurants/new', methods=['GET', 'POST'])
def createRestaurant():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    if request.method == 'GET':
        return render_template('newrestaurant.html')
    else:
        newRestaurant = rest_crud.newRestaurant(request.form['rest_name'], login_session['user_id'])
        flash("New Restaurant Created")
        return redirect(url_for('showRestaurants'))


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    restaurant = rest_crud.getRestaurant(restaurant_id)
    if login_session['user_id'] != restaurant.user_id:
        return "you are not allowed to edit this restaurant!"
    if request.method == 'GET':
        menu_items = rest_crud.getRestaurantItems(restaurant_id)
        sections= OrderedDict()
        sections['Appetizers'] = [item for item in menu_items if item.course == "Appetizer"]
        sections['Entrees'] = [item for item in menu_items if item.course == "Entree"]
        sections['Desserts'] = [item for item in menu_items if item.course == "Dessert"]
        sections['Beverages'] = [item for item in menu_items if item.course == "Beverage"]
        return render_template('editrestaurant.html', restaurant=restaurant, 
                                                      sections=sections)
    else:
        # edit on this level only for restaurant name
        # menu items edits are handled by editMenuItem function
        rest_crud.editRestaurant(restaurant_id, request.form['rest_name'])
        flash("Restaurant " + restaurant.name + " Successfully Edited")
        return redirect(url_for('showRestaurants'))

@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    restaurant = rest_crud.getRestaurant(restaurant_id)
    if login_session['user_id'] != restaurant.user_id:
        return "you are not allowed to delete this restaurant!"
    if request.method == 'GET':
        return render_template('deleterestaurant.html', restaurant=restaurant)
    else:
        rest_crud.deleteRestaurant(restaurant_id)
        flash('Restaurant ' + restaurant.name + ' Successfully Deleted')
        return redirect(url_for('showRestaurants'))

@app.route('/restaurants/<int:restaurant_id>/menu')
def showRestaurant(restaurant_id):
    restaurant = rest_crud.getRestaurant(restaurant_id)
    creator = rest_crud.getUserById(restaurant.user_id)
    menu_items = rest_crud.getRestaurantItems(restaurant_id)
    sections= OrderedDict()
    sections['Appetizers'] = [item for item in menu_items if item.course == "Appetizer"]
    sections['Entrees'] = [item for item in menu_items if item.course == "Entree"]
    sections['Desserts'] = [item for item in menu_items if item.course == "Dessert"]
    sections['Beverages'] = [item for item in menu_items if item.course == "Beverage"]
    if 'username' not in login_session or login_session['user_id'] != restaurant.user_id:
        print "user not logged in"
        return render_template('menu.html', restaurant=restaurant,
                                            sections=sections,
                                            creator=creator)
    else:
        return render_template('editrestaurant.html', restaurant=restaurant,
                                                      sections=sections,
                                                      creator=creator)

@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    restaurant = rest_crud.getRestaurant(restaurant_id)
    if login_session['user_id'] != restaurant.user_id:
        return "you are not allowed to add an item to this restaurant!"
    if request.method == 'GET':
        return render_template('newmenuitem.html', restaurant=restaurant)
    else:
        menu_item = rest_crud.newMenuItem(name=request.form['name'],
                               description=request.form['description'],
                               course=request.form['course'],
                               price=request.form['price'],
                               restaurant_id=restaurant_id,
                               user_id=login_session['user_id'])
        flash("New Menu Item " + menu_item.name + " Created")
        return redirect(url_for('showRestaurant', restaurant_id=restaurant_id))

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/edit', 
               methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_item_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    restaurant = rest_crud.getRestaurant(restaurant_id)
    if login_session['user_id'] != restaurant.user_id:
        return "you are not allowed to edit an item from this restaurant!"
    menu_item = rest_crud.getMenuItem(menu_item_id)
    if request.method == 'GET':
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, item=menu_item)
    else:
        rest_crud.editMenuItem(menu_item_id=menu_item_id, 
                               name=request.form['name'],
                               description=request.form['description'],
                               course=request.form['course'],
                               price=request.form['price'])
        flash("Menu Item " + request.form['name'] + " Successfully Edited")
        return redirect(url_for('showRestaurant', restaurant_id=restaurant_id))


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/delete', methods=["GET", "POST"])
def deleteMenuItem(restaurant_id, menu_item_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    restaurant = rest_crud.getRestaurant(restaurant_id)
    if login_session['user_id'] != restaurant.user_id:
        return "you are not allowed to delete an item from this restaurant!"
    menu_item = rest_crud.getMenuItem(menu_item_id)
    if request.method == 'GET':
        return render_template('deletemenuitem.html', restaurant_id=restaurant_id, menu_item=menu_item)
    else:
        rest_crud.deleteMenuItem(menu_item_id)
        flash("Menu Item " + menu_item.name + " Successfully Deleted")
        return redirect(url_for('showRestaurant', restaurant_id=restaurant_id))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
