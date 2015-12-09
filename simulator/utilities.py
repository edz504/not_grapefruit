'''Contains Class definitions for all objects used in simulate.py'''


### Constants
PRODUCTS = ['ORA', 'POJ', 'ROJ', 'FCOJ']



### Classes 
class Delivery(object):

    def __init__(self, sender, receiver, arrival_time, product, amount):
        self.sender = sender
        self.receiver = receiver
        self.arrival_time = arrival_time
        if product in PRODUCTS:
            self.product = product
        else:
            raise ValueError('Bad product given')
        self.amount = amount


class Process(object):

    def __init__(self, location, finish_time, start_product, end_product,
                 amount):
        self.location = location
        self.finish_time = finish_time
        if (start_product in ['ORA', 'FCOJ'] and # different product check
            end_product in ['POJ', 'ROJ', 'FCOJ']):
            self.start_product = start_product
            self.end_product = end_product
        else:
            raise ValueError('Bad product given')
        self.amount = amount


class Storage(object):

    def __init__(self, name, capacity, inventory):
        self.name = name
        self.capacity = capacity
        self.inventory = inventory

    def reconstitute(percentage, t):
        pass

    def dispose_capacity(shortage):
        pass

    def age():
        pass


class ProcessingPlant(object):

    def __init__(self, name, capacity, inventory, tanker_cars):
        self.name = name
        self.capacity = capacity
        self.inventory = inventory
        self.tanker_cars = tanker_cars

    def manufacture(percentage, t):
        pass

    def dispose_capacity(shortage):
        pass

    def age():
        pass


class Grove(object):

    def __init__(self, name, price_stats, harvest_stats, desired_quantities,
                 multipliers):
        self.name = name
        self.price_stats = price_stats
        self.harvest_stats = harvest_stats
        self.desired_quantities = desired_quantities
        self.multipliers = multipliers

    def realize_price_month(month_index):
        pass

    def realize_week_harvest(week):
        pass

    def apply_multipliers(quantity):
        pass

    def spot_purchase(amount, shipping_plan, t):
        pass


class Market(object):

    def __init__(self, name, region, demand_function_coefs, demand_stats):
        self.name = name
        self.region = region
        self.demand_function_coefs = demand_function_coefs
        self.demand_stats = demand_stats

    def realize_demand(price, product):
        pass


