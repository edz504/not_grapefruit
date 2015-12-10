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

    def reconstitute(t):
        recon_percentage = self.reconstitution_percentages[t]
        fcoj_inventory = sum(self.inventory['FCOJ'])
        amount_to_recon = recon_percentage * fcoj_inventory

        self.remove_product('FCOJ', amount_to_recon)
        self.add_product('XOJ', amount_to_recon)

        recon_process = Process(self, t + 1, 'FCOJ', 'ROJ', amount_to_recon)
        recon_cost = 650 * amount_to_recon

        return (recon_process, recon_cost)

    def dispose_capacity(shortage):
        if shortage <= 0:
            return
        else:
            # indices to be used to check inventory amount
            indices = [3, 7, 11, 47]

            amount_to_remove = shortage
            while amount_to_remove > 0:
                # Calculate weekly inventories for each product
                weekly_inventories = [self.inventory['ORA'][indices[0]],
                                      self.inventory['POJ'][indices[1]],
                                      self.inventory['ROJ'][indices[2]],
                                      self.inventory['FCOJ'][indices[3]]]

                week_total = sum(weekly_inventories)
                if week_total < amount_remove:
                    self.remove_product('ORA', weekly_inventories[0])
                    self.remove_product('POJ', weekly_inventories[1])
                    self.remove_product('ROJ', weekly_inventories[2])
                    self.remove_product('FCOJ', weekly_inventories[3])


                else:
                    # Calculate proportion to remove for each product
                    p = amount_to_remove/week_total

                    self.remove_product('ORA', weekly_inventories[0]*p)
                    self.remove_product('POJ', weekly_inventories[1]*p)
                    self.remove_product('ROJ', weekly_inventories[2]*p)
                    self.remove_product('FCOJ', weekly_inventories[3]*p)

                amount_to_remove -= week_total
                indices = [i - 1 for i in indices]

            return
    def age():
        pass

    def add_product(product, amount):
        pass

    def remove_product(product, amount):
        if amount == 0:
            return
        pass

    def get_total_inventory(product=None):
        if product is None:
            return sum([sum(vals) for vals in self.inventory.values()])
        else:
            return sum(self.inventory[product])


class ProcessingPlant(object):

    def __init__(self, name, capacity, poj_proportion, inventory, tanker_cars,
                 shipping_plan):
        self.name = name
        self.capacity = capacity
        self.poj_proportion = poj_proportion
        self.inventory = inventory
        self.tanker_cars = tanker_cars
        self.shipping_plan = shipping_plan

    def manufacture(t):
        pass

    def dispose_capacity(shortage):
        pass

    def age():
        pass

    def add_product(product, amount):
        pass

    def remove_product(product, amount):
        pass

    def get_total_inventory(product=None):
        return sum([sum(vals) for vals in self.inventory.values()])


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

    def spot_purchase(t):
        pass



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


