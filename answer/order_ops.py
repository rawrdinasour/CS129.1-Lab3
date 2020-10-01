#!/usr/bin/env python3
import boto3
from boto3.dynamodb.conditions import Key
import hashlib
import random
from decimal import Decimal

def add_item(order_id, product_name, quantity, price, date): 
    # Generate item ID. In real life, there are better
    # ways of doing this
    item_id = hashlib.sha256(product_name.encode()).hexdigest()[:8]
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('users-orders_table')
    
    item = {
        'pk'           : '#ITEM#{0}'.format(item_id), 
        'sk'           : '#ORDER#{0}'.format(order_id),
        'product_name' : product_name,
        'quantity'     : quantity,
        'price'        : price,
        'status'       : "Pending",
        'date'         : date,
        'gsi2sk'       : '#STATUS#{0}#DATE#{1}'.format("Pending", date)
    }
    table.put_item(Item=item)
    print("Added {0} to order {1}".format(product_name, order_id))
    
def checkout(username, address, items, date): 
    # Generate order ID. In real life, there are better
    # ways of doing this
    order_id = hashlib.sha256(str(random.random()).encode()).hexdigest()[:random.randrange(1, 20)]
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('users-orders_table')
    
    item = {
        'pk'      : '#USER#{0}'.format(username), 
        'sk'      : '#ORDER#{0}'.format(order_id),
        'address' : address,
        'status'  : "Placed",
    }
    table.put_item(Item=item)
    
    for item in items:
        add_item(order_id, item['product_name'], item['quantity'], item['price'], date)

def query_user_orders(username):
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('users-orders-items')
    response = table.query(
        KeyConditionExpression=Key('pk').eq('#USER#{0}'.format(username)) &
                              Key('sk').begins_with('#ORDER#')
    )
    return response['Items']
    
def query_order_items(order_id):
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('users-orders-items')
    response = table.query(
        IndexName='inverted-index',
        KeyConditionExpression=Key('sk').eq('#ORDER#{0}'.format(order_id)) & 
                               Key('pk').begins_with('#ITEM#')
    )
    return response['Items']
    
    
# TEST DELETE LATER    
if __name__ == '__main__':
    shopping_cart3 = [
        {
            'product_name' : 'HyperX Fury 16GB',
            'price'        : Decimal('39.99'),
            'quantity'     : 2
        },
        {
            'product_name' : 'Jenga Classic Game',
            'price'        : Decimal('19.99'),
            'quantity'     : 1
        },
        {
            'product_name' : 'Tasha\'s Cauldron of Everything',
            'price'        : Decimal('49.95'),
            'quantity'     : 3
        }
        ]
    checkout("loyd98", "home", shopping_cart3, "10-01-2020")