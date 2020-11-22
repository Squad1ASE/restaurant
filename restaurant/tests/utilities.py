
# --- UTILITIES RESTAURANT  ---
restaurant_examples = [
    dict(owner_id=1, name='Restaurant 1', lat=43.7216621, lon=10.4083723, phone='111111',  
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
    )
]

'''
restaurant_example = [
    { 
        'name':'Restaurant 1', 'lat':43.7216621, 'lon':10.4083723, 'phone':'111111', 
        'cuisine_type':["italian", "traditional"], 'prec_measures':'leggeX', 'avg_time_of_stay':40,
        'tables-0-table_name':'res1red', 'tables-0-capacity':2, 
        'dishes-0-dish_name':'pizza', 'dishes-0-price':4, 'dishes-0-ingredients':'pomodoro, mozzarella',
        'dishes-1-dish_name':'pasta agli scampi', 'dishes-1-price':4, 'dishes-1-ingredients':'pasta, scampi',
        'workingdays-0-day': WorkingDay.WEEK_DAYS(1), 'workingdays-0-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-1-day': WorkingDay.WEEK_DAYS(2), 'workingdays-1-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-2-day': WorkingDay.WEEK_DAYS(3), 'workingdays-2-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-3-day': WorkingDay.WEEK_DAYS(4), 'workingdays-3-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-4-day': WorkingDay.WEEK_DAYS(5), 'workingdays-4-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-5-day': WorkingDay.WEEK_DAYS(6), 'workingdays-5-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-6-day': WorkingDay.WEEK_DAYS(7), 'workingdays-6-work_shifts':"('12:00','15:00'),('19:00','23:00')"
    },
    { 
        'name':'Restaurant 2', 'lat':43.7176394, 'lon':10.4032292, 'phone':'222222', 
        'cuisine_type':[Restaurant.CUISINE_TYPES(1),Restaurant.CUISINE_TYPES(3)], 'prec_measures':'leggeX', 'avg_time_of_stay':25,
        'tables-0-table_name':'res2red', 'tables-0-capacity':6, 
        'tables-1-table_name':'res2blue', 'tables-1-capacity':4, 
        'dishes-0-dish_name':'pasta al pesto', 'dishes-0-price':4, 'dishes-0-ingredients':'pasta, pesto, basilico',
        'dishes-1-dish_name':'burrito', 'dishes-1-price':3, 'dishes-1-ingredients':'carne,fagioli',
        'workingdays-0-day': WorkingDay.WEEK_DAYS(1), 'workingdays-0-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-1-day': WorkingDay.WEEK_DAYS(2), 'workingdays-1-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-2-day': WorkingDay.WEEK_DAYS(3), 'workingdays-2-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-3-day': WorkingDay.WEEK_DAYS(4), 'workingdays-3-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-4-day': WorkingDay.WEEK_DAYS(5), 'workingdays-4-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-5-day': WorkingDay.WEEK_DAYS(6), 'workingdays-5-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-6-day': WorkingDay.WEEK_DAYS(7), 'workingdays-6-work_shifts':"('12:00','15:00'),('19:00','23:00')"
    },
    { 
        'name':'Restaurant 3', 'lat':43.7176589, 'lon':10.4015256, 'phone':'333333', 
        'cuisine_type':[Restaurant.CUISINE_TYPES(2)], 'prec_measures':'leggeX', 'avg_time_of_stay':40,
        'tables-0-table_name':'res3green', 'tables-0-capacity':4, 
        'tables-1-table_name':'res3red', 'tables-1-capacity':4, 
        'tables-2-table_name':'res3blue', 'tables-2-capacity':6, 
        'tables-3-table_name':'res3yellow', 'tables-3-capacity':10, 
        'dishes-0-dish_name':'riso', 'dishes-0-price':4, 'dishes-0-ingredients':'funghi',
        'workingdays-0-day': WorkingDay.WEEK_DAYS(2), 'workingdays-0-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-1-day': WorkingDay.WEEK_DAYS(3), 'workingdays-1-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-2-day': WorkingDay.WEEK_DAYS(4), 'workingdays-2-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-3-day': WorkingDay.WEEK_DAYS(5), 'workingdays-3-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-4-day': WorkingDay.WEEK_DAYS(6), 'workingdays-4-work_shifts':"('12:00','15:00'),('19:00','23:00')",
        'workingdays-5-day': WorkingDay.WEEK_DAYS(7), 'workingdays-5-work_shifts':"('12:00','15:00'),('19:00','23:00')"
    },
    { 
        'name':'Restaurant 4', 'lat':43.7174589, 'lon':10.4012256, 'phone':'444444', 
        'cuisine_type':[Restaurant.CUISINE_TYPES(4),Restaurant.CUISINE_TYPES(5)], 'prec_measures':'leggeX', 'avg_time_of_stay':15,
        'tables-0-table_name':'res4green', 'tables-0-capacity':4, 
        'tables-1-table_name':'res4red', 'tables-1-capacity':4, 
        'tables-2-table_name':'res4blue', 'tables-2-capacity':4,
        'dishes-0-dish_name':'panino con carne', 'dishes-0-price':3, 'dishes-0-ingredients':'pane, carne',
        'dishes-1-dish_name':'panino con pesce', 'dishes-1-price':3, 'dishes-1-ingredients':'pane, pesce',
        'workingdays-0-day': WorkingDay.WEEK_DAYS(2), 'workingdays-0-work_shifts':"('19:00','23:00')",
        'workingdays-1-day': WorkingDay.WEEK_DAYS(3), 'workingdays-1-work_shifts':"('19:00','23:00')",
        'workingdays-2-day': WorkingDay.WEEK_DAYS(5), 'workingdays-2-work_shifts':"('19:00','23:00')",
        'workingdays-3-day': WorkingDay.WEEK_DAYS(6), 'workingdays-3-work_shifts':"('19:00','23:00')"
    }
]
'''

def create_restaurant_by_API(test_client, data_dict=restaurant_examples[0]):
    return test_client.put('/restaurants', json=data_dict, follow_redirects=True)

def get_restaurant_by_API(test_client, restaurant_id=None):
    if restaurant_id is None:
        return test_client.get('/restaurants', follow_redirects=True)
    else:
        return test_client.get('/restaurants/'+str(restaurant_id), follow_redirects=True)

'''
assert create_restaurant_by_API(test_client).status_code == 200
response = get_restaurant_by_API(test_client, 1)
assert response.status_code == 200
print(response.json)
'''