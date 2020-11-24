
# --- UTILITIES RESTAURANT ---
restaurant_examples = [
    dict(owner_id=1, name='Restaurant-1', lat=43.7216621, lon=10.4083723, phone='111111',  
        cuisine_type=["italian", "traditional"], prec_measures='leggeX', avg_time_of_stay=30,
        tables=[dict(name='yellow',capacity=2), dict(name='red',capacity=5)],
        dishes=[
            dict(name='pizza',price=4.5,ingredients='tomato,mozzarella'), 
            dict(name='pasta',price=6.5,ingredients='tomato')
        ],
        working_days=[
            dict(day='monday',work_shifts=[["00:01", "23:59"]]), 
            dict(day='tuesday',work_shifts=[["00:01", "23:59"]]),
            dict(day='wednesday',work_shifts=[["00:01", "23:59"]]), 
            dict(day='thursday',work_shifts=[["00:01", "23:59"]]),  
            dict(day='friday',work_shifts=[["00:01", "23:59"]]), 
            dict(day='saturday',work_shifts=[["00:01", "23:59"]]), 
            dict(day='sunday',work_shifts=[["00:01", "23:59"]])
        ]
    ),
    dict(owner_id=2, name='Restaurant-2', lat=43.7316621, lon=10.4183723, phone='222222',  
        cuisine_type=["mexican"], prec_measures='leggeX', avg_time_of_stay=40,
        tables=[dict(name='yellow',capacity=2), dict(name='red',capacity=5)],
        dishes=[
            dict(name='pizza',price=4.5,ingredients='tomato,mozzarella'), 
            dict(name='pasta',price=6.5,ingredients='tomato')
        ],
        working_days=[
            dict(day='tuesday',work_shifts=[["00:01", "23:59"]]),
            dict(day='wednesday',work_shifts=[["00:01", "23:59"]]), 
            dict(day='thursday',work_shifts=[["00:01", "23:59"]]),  
            dict(day='friday',work_shifts=[["00:01", "23:59"]]), 
            dict(day='saturday',work_shifts=[["00:01", "23:59"]])
        ]
    ),
    dict(owner_id=1, name='Restaurant 3', lat=43.4702169, lon=11.152609, phone='333333',  
        cuisine_type=["italian", "chinese"], prec_measures='', avg_time_of_stay=15,
        tables=[dict(name='yellow',capacity=3)],
        dishes=[
            dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')
        ],
        working_days=[
            dict(day='monday',work_shifts=[["00:01", "23:59"]])
        ]
    )
]


def create_restaurant_by_API(test_client, data_dict=restaurant_examples[0]):
    return test_client.put('/restaurants', json=data_dict, follow_redirects=True)


def get_restaurants_by_API(test_client, owner_id=None, name=None, lat=None, lon=None, cuisine_types=[]):
    url = '/restaurants'
    queries = 0 
    if owner_id is not None:
        url += '?owner_id=' + str(owner_id)
        queries += 1
    if name is not None:
        if queries == 0:
            url += '?name=' + name.replace(" ", "%")
        else: 
            url += '&name=' + name.replace(" ", "%")
        queries += 1
    if lat is not None:
        if queries == 0:
            url += '?lat=' + str(lat)
        else: 
            url += '&lat=' + str(lat)
        queries += 1
    if lon is not None:
        if queries == 0:
            url += '?lon=' + str(lon)
        else: 
            url += '&lon=' + str(lon)
        queries += 1
    for cuisine in cuisine_types:
        if queries == 0:
            url += '?cuisine_type=' + str(cuisine)
        else: 
            url += '&cuisine_type=' + str(cuisine)
        queries += 1
    return test_client.get(url, follow_redirects=True)


def get_restaurant_by_API(test_client, restaurant_id):
    return test_client.get('/restaurants/'+str(restaurant_id), follow_redirects=True)


def edit_restaurant_by_API(test_client, restaurant_id, data_dict):
    return test_client.post('/restaurants/'+str(restaurant_id), json=data_dict, follow_redirects=True)


def delete_restaurant_by_API(test_client, restaurant_id, owner_id):
    return test_client.delete('/restaurants/'+str(restaurant_id), json=dict(owner_id=owner_id), follow_redirects=True)


# --- UTILITIES REVIEWS ---
def get_reviews_by_API(test_client, user_id=None, restaurant_id=None):
    url = '/reviews'
    queries = 0 
    if user_id is not None:
        url += '?user_id=' + str(user_id)
        queries += 1
    if restaurant_id is not None:
        if queries == 0:
            url += '?restaurant_id=' + str(restaurant_id)
        else: 
            url += '&restaurant_id=' + str(restaurant_id)
        queries += 1
    return test_client.get(url, follow_redirects=True)