# Collie_api - API written in Python Utilizing Flask for wwww.colliecolliecollie.ninja

## What is this?

An API that acts as a way for Flutter to access information from the MySQL database within this project. 

This API has the following dependencies

 * Python 3
 * Flask 1.1.2
 * mysql-connector 2.2.9
 * Flask-Cors 3.0.8

# Program Behavior

This api runs on a uWSGI server and serves as a way to bring content to display within the Front-End. 
Each function interacts with the database via SQL queries depending on the needs of the function.

it primarily works through 4 different functions:
 -  the api_get_item_by_id() function maps to /api/v1/resources/items/
    - it allows accessing item information through passing an argument such as /api/v1/resources/items/?id=74443
 - api_get_price_by_id() function maps to /api/v1/resources/prices/
    - it allows accessing historical price information based on item id. Takes similar argument as above
 - api_get_top_price_drops() maps to /api/v1/resources/topprices/
    - This function uses a complex SQL query to returns a list of top 30 items with the largest price drops based on the last and second to last price of each item.
 - api_post_get_notified() maps to /api/v1/subscriptions/alerts/
    - This is called when a user submits a form that allows them to enter their email, product they want to track and a price threshold for when they should be notifed. this then stores that information in the database to be used when the Java webscraper runs and is in the phase to send emails.


#

One part of www.colliecolliecollie.ninja - a site that stores historical data of prices of items and provides tools for users to be notified of price decreases.

Java: Jsoup + Selenium scraper to get prices/items - PriceSpider - https://github.com/skirillex/PriceSpider
Python: Flask + uwsgi server - collie_api - https://github.com/skirillex/collie_api
SQL: Relational database to store data - MySQL
Dart/Flutter front end

