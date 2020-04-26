from flask import Flask, jsonify, request
from flask.json import JSONEncoder

import mysql.connector
from mysql.connector import Error

#from flask_cors import CORS

from datetime import date

import collections


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

app.config["DEBUG"] = True
#CORS(app)

@app.route('/api/', methods=['GET'])
def home():
    return '<h1>Hello</h1><p>there!. The api is up and running!</p>'


@app.route('/api/v1/resources/items/all', methods = ["GET"])
def api_get_all_items():
    # returns all the records in database in a list
    query = "select * from items;"
    record = connect_and_query(query)

    return jsonify(record)


@app.route('/api/v1/resources/items/', methods=["GET"])
def api_get_item_by_id():
    # this function allows items to be fetched from the items table in the
    # database by either their product_id or their url
    # to access these functions (example below:)
    # /api/v1/resources/items/?id=74443
    # or
    # /api/v1/resources/items/?url=/us/mens/shorts/details/74443/international-linen-chino-shorts--cream

    product_id = request.args.get("id") # returns a tuple to be used in cursor.execute()
    url = request.args.get("url")

    query = "SELECT * FROM items WHERE"

    to_filter = [] # list to store the tuple

    if product_id:
        query += " product_id= %s;"
        to_filter.append(product_id)
    if url:
        query += " url= %s;"
        to_filter.append(url)
    if not (product_id or url):
        return page_not_found(404)

    #query = query [: -4] + ";"
    #DEBUG
   # print(to_filter)

    record = connect_and_query(query,to_filter)
    #print("record : ",record[0][0])
    return jsonify(item_id=record[0][0],
    name=record[0][1],
    url=record[0][2],
    img_url=record[0][3])

@app.route('/api/v1/resources/prices/', methods=["GET"])
def api_get_price_by_id():
    product_id = request.args.get("id")

    query = "SELECT * FROM price_history WHERE"

    to_filter = []


    if product_id:
        query += " product_id= %s ORDER BY date_stored DESC;"
        to_filter.append(product_id)
    if not (product_id):
        return page_not_found(404)

    #print(to_filter)

    record = connect_and_query(query, to_filter)
  


    return jsonify(item_price=record)


@app.route('/api/v1/resources/topprices/', methods=["GET"])
def api_get_top_price_drops():

    # may need to remove limit from query in anticipation for bug where it will grow bigger than the limit
    #query_set = "SET @row_number := 0;"
    #query = "SELECT *, a.product_id, IFNULL(a.price, 0) - IFNULL(b.price, a.price) AS price_difference FROM ( SELECT * FROM (SELECT @row_number:= CASE WHEN @product_no = product_id THEN @row_number + 1 ELSE 1 END AS row_num, @product_no:=product_id AS product_id, date_stored, price FROM price_history WHERE product_id IS NOT NULL ORDER BY product_id, date_stored DESC) AS pairs WHERE row_num <= 2) AS a LEFT JOIN ( SELECT * FROM (SELECT * FROM (SELECT @row_number:= CASE WHEN @product_no = product_id THEN @row_number + 1 ELSE 1 END AS row_num, @product_no:=product_id AS product_id, date_stored, price FROM price_history WHERE product_id IS NOT NULL ORDER BY product_id, date_stored DESC) AS pairs WHERE row_num <= 2) as sub_b WHERE row_num = 2) AS b ON b.product_id = a.product_id WHERE a.row_num = 1 ORDER BY price_difference ASC LIMIT 50;"

    query = "SELECT *, A.product_id, IFNULL(A.price, B.price) - IFNULL(B.price, A.price) AS price_difference FROM ( SELECT * FROM (SELECT product_id, price, date_stored, ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY product_id, date_stored DESC) AS row_num FROM price_history WHERE product_id IS NOT NULL) AS pair WHERE row_num <= 2) AS A LEFT JOIN ( SELECT * FROM (SELECT * FROM (SELECT product_id, price, date_stored, ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY product_id, date_stored DESC) AS row_num FROM price_history WHERE product_id IS NOT NULL) AS pairs WHERE row_num <= 2) as `p*` WHERE row_num = 2) AS B ON B.product_id=A.product_id ORDER BY price_difference ASC LIMIT 30;"

    record = connect_and_query(query)
    
    #ordered_record = collections.OrderedDict() # the query returns duplicates, therefore an ordered Dictionary is needed to remove the duplicates in the list

    #for i in record:
        #ordered_record[i[1]] = i # the key in the ordered dict is the item number
    
    # DEBUG
    # print(ordered_record)

    #record_list = []
    #for i in range (0, len(ordered_record)):
        #record_list.append(ordered_record.popitem(False)) # turn it back into a list by FIFO popping the dictionary


    return jsonify(top_price_drops= record)


@app.route('/api/v1/subscriptions/alerts/', methods=["POST"])
def api_post_get_notified():
    user_data = request.get_json()
    res = ""

    email = tuple(user_data['email'])
    itemid = tuple(user_data['itemId'])
    price = tuple(user_data['price'])

    to_filter = [user_data['email'], user_data['itemId'], user_data['price']]

    query = "INSERT INTO price_watch (email, product_id, price) VALUES(%s, %s, %s)"

    try:
        connect_and_query(query, to_filter, insert=True)
        res = {'status': 'ok'}
    except Error as e:
        res = {'status': 'SOMETHING WENT WRONG WHEN TRYING TO ADD PRICE WATCH'}

    return jsonify(res)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404



def connect_and_query(query, to_filter=None, query_2=None, insert=None):
    try:
        connection = mysql.connector.connect(host = open("myUrl").read(),
                                         database = open("database").read(),
                                         user = open("username").read(),
                                         password = open("mysql").read())
        if connection.is_connected():
            db_info = connection.get_server_info()
            # print("connected to mysql server", db_info)
            cursor = connection.cursor()
            if to_filter is not None:
                cursor.execute(query,to_filter) # for every %s in the query, the to_filter encompasses it
            elif query_2 is not None:
                # print(" Accessed elif statement ")
                cursor.execute(query)
                cursor.execute(query_2)

            else:
                cursor.execute(query)

            if insert is not None:
                record = cursor.rowcount
            else:
                record = cursor.fetchall()
            #print("here's your record: ", record)
            return record


    except Error as e:
        print("Error while connection to MySQL", e)

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL is closed")

if __name__ == '__main__':
    app.run()

