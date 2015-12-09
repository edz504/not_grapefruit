'''Contains Class definitions for all objects used in simulate.py'''


### Constants
PRODUCTS = ['ORA', 'POJ', 'ROJ', 'FCOJ']
REGIONS = ['NE', 'MA', 'SE', 'MW', 'DS', 'NW', 'SW']


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

    def __init__(self, name, capacity, reconstitution_percentages, inventory):
        self.name = name
        self.capacity = capacity
        self.reconstitution_percentages = reconstitution_percentages
        self.inventory = inventory

    def reconstitute(percentage, t):
        pass

    def dispose_capacity(shortage):
        pass

    def age():
        pass


class ProcessingPlant(object):

    def __init__(self, name, capacity, poj_proportion, inventory, tanker_cars,
                 shipping_plan):
        self.name = name
        self.capacity = capacity
        self.poj_proportion = poj_proportion
        self.inventory = inventory
        self.tanker_cars = tanker_cars
        self.shipping_plan = shipping_plan

    def manufacture(percentage, t):
        pass

    def dispose_capacity(shortage):
        pass

    def age():
        pass


class Grove(object):

    def __init__(self, name, price_stats, harvest_stats, desired_quantities,
                 multipliers, shipping_plan):
        self.name = name
        self.price_stats = price_stats
        self.harvest_stats = harvest_stats
        self.desired_quantities = desired_quantities
        self.multipliers = multipliers
        self.shipping_plan = shipping_plan

    def realize_price_month(month_index):
        pass

    def realize_week_harvest(week):
        pass

    def apply_multipliers(price, quantity, t):
        desired_quantity = self.desired_quantities[int(t / 4)]

        if price < self.multipliers['Price 1']:
            return desired_quantity * self.multipliers[0]
        elif price < self.multipliers['Price 2']:
            return desired_quantity * self.multipliers[2]
        elif price < self.multipliers['Price 3']:
            return desired_quantity * self.multipliers[4]
        else:
            return 0

    def spot_purchase(amount, shipping_plan, t):
        price = self.realize_price_month(int(t / 4))



class Market(object):

    def __init__(self, name, region, prices, demand_function_coefs,
                 demand_stats):
        self.name = name
        self.region = region
        self.prices = prices
        self.demand_function_coefs = demand_function_coefs
        self.demand_stats = demand_stats

    def realize_demand(price, product):
        pass


