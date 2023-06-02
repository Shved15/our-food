# our-food

# To check the deployment result:
- https://www.ourfood-proj.es

## About project:
This is a project for online buying and selling of food products from post-Soviet countries in Spain. I currently reside in Spain 
and often miss "our" food. That's why I wanted to create a project where cafes or restaurants selling food from the former USSR 
countries could showcase and sell their products. Those who are interested in such food could visit the website, browse the assortment,
and choose a nearby organization.<br>

On this marketplace platform, users can register as buyers using their email and verify their email through a verification email.
They can also edit their profiles by changing their profile picture and cover photo, as well as update their address with auto-fill 
from Google Maps. Buyers can browse the catalog, view opening hours, search for organizations or specific products, and even determine
their current location using Google Maps integration to find nearby organizations. Buyers can also set a radius within which they would 
like to find organizations. They can add products to the shopping cart dynamically without page reloads, decrease the quantity of items
in the cart, and remove items from the cart. They can place orders and make payments using PayPal, as well as view their order history
with pagination and access details of completed orders.<br>

On the other hand, sellers can also register using their email, but they are required to provide a license. After email verification 
and approval by the platform administrator, sellers can edit their profiles by updating their photo, organization name, cover photo, 
and address using Google Maps auto-fill. Sellers can dynamically update their working hours. In the menu builder, sellers can create 
\product categories and add individual products. They can also specify the availability of products. After a buyer places an order, 
\sellers can view their order history with pagination and access order details.<br>

After an order is placed, all participants, including the buyer and all sellers involved in the order, receive an email with the 
order details. The administration also has the ability to set taxes that are applicable to buyers in accordance with the legislation, 
and the final invoice dynamically adjusts without page reloads.<br>

## Stack:
- Python
- Django
- PostgreSQL
- PostGIS
- GDAL
- Google Geocoding, Google autocoplete, Google Maps API, Googla Place API, JS API
- AJAX Requests
- PayPal
- Deploy with Linode server (NGINX, Gunicorn)

## Local Developing
1. Firstly, create and activate a new virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
2. Install Packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
3. Run project dependencies, migrations, fill the database with the fixture data etc.:
```
./manage.py migrate
./manage.py loaddata backup.json
./manage.py runserver 
```








