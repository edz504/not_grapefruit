'''Contains Class definitions for all objects used in simulate.py'''
import numpy as np

### Constants
PRODUCTS = ['ORA', 'POJ', 'ROJ', 'FCOJ']
REGIONS = ['NE', 'MA', 'SE', 'MW', 'DS', 'NW', 'SW']
MONTHS = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug']

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

    def __init__(self, name, capacity, reconstitution_percentages, inventory,
                 markets=None): # in sim, market provided after creation
        self.name = name
        self.capacity = capacity
        self.reconstitution_percentages = reconstitution_percentages
        self.inventory = inventory
        self.markets = markets

    def reconstitute(t):
        recon_percentage = self.reconstitution_percentages[(t - 1)/4]
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
                weekly_inventories = []
                available_products = []

                for i, product in zip(indices, PRODUCTS):
                    # Each index needs to be at least 0 for disposal to occur
                    if i >= 0:
                        weekly_inventories.append(self.inventory[product][i])
                        available_products.append(product)

                week_total = sum(weekly_inventories)

                if week_total < amount_to_remove:
                    for x, product in zip(weekly_inventories, available_products):
                        self.remove_product(product, x)

                else:
                    # Calculate proportion to remove for each product
                    p = amount_to_remove/week_total

                    for x, product in zip(weekly_inventories, available_products):
                        self.remove_product(product, x * p)

                amount_to_remove -= week_total
                indices = [i - 1 for i in indices]

            return
    def age():
        for vals in self.inventory.values():
            for i in range(len(vals)):
                vals[i + 1] = vals[i]
            vals[0] = 0
        return

    def add_product(product, amount):
        self.inventory[product][0] += amount

        return

    def remove_product(product, amount):
        if amount == 0:
            return
        else:
            amount_to_remove = amount
            i = len(inventory[product]) - 1

            # Check weekly inventory starting with final week
            while amount_to_remove > 0 and i >= 0:
                inventory_this_age = inventory[product][i]
                if inventory_this_age > amount_to_remove:
                    inventory[product][i] -= amount_to_remove
                else:
                    inventory[product][i] = 0

                # Should work for this loop, but calculation could be better
                amount_to_remove -= inventory_this_age
                i -= 1

        return

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
        ORA_inventory = self.get_total_inventory()
        p = self.poj_proportion / 100.0

        # For manufacturing breakdown
        U = np.random.uniform()

        if U < 0.95:
            amount_poj = p*ORA_inventory
            amount_fcoj = (1-p)*ORA_inventory
            process_poj = Process(self, t+1, 'ORA', 'POJ', amount_poj)
            process_fcoj = Process(self, t+1, 'ORA', 'FCOJ', amount_fcoj)

            cost_poj = 2000*amount_poj
            cost_fcoj = 1000*amount_fcoj

            return ([process_poj, process_fcoj], cost_poj, cost_fcoj)
        
        else:
            return ([], 0, 0)

    def dispose_capacity(shortage):
        if shortage <= 0:
            return
        else:
            self.remove_product('ORA', shortage)
            return


    def age():
        for i in range(4):
            self.inventory[i + 1] = vals[i]
        self.inventory[0] = 0
        
        return

    def add_product(product, amount):
        if product not 'ORA':
            raise ValueError()
        else:
            self.inventory[product][0] += amount
        return

    def remove_product(product, amount):
        if product not 'ORA':
            raise ValueError()
        else:
            amount_to_remove = amount
            i = 3

            # Check weekly inventory starting with final week
            while amount_to_remove > 0 and i >= 0:
                inventory_this_age = inventory[i]
                if inventory_this_age > amount_to_remove:
                    inventory[i] -= amount_to_remove
                else:
                    inventory[i] = 0

                # Should work for this loop, but calculation could be better
                amount_to_remove -= inventory_this_age
                i -= 1
        return

    def get_total_inventory(product=None):
        if product not ('ORA' or None):
            raise ValueError()

        return sum(self.inventory)

class Grove(object):

    def __init__(self, name, price_stats, exchange_stats, harvest_stats,
                 desired_quantities, multipliers, shipping_plan):
        self.name = name
        self.price_stats = price_stats
        self.exchange_stats = exchange_stats
        self.harvest_stats = harvest_stats
        self.desired_quantities = desired_quantities
        self.multipliers = multipliers
        self.shipping_plan = shipping_plan

    def realize_price_month(month_index):
        pass

    def realize_week_harvest(week):
        pass

    def apply_multipliers(price, quantity, t):
        desired_quantity = self.desired_quantities[int((t - 1) / 4)]

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

    def __init__(self, name, region, prices, demand_function_coefs):
        self.name = name
        self.region = region
        self.prices = prices
        self.demand_function_coefs = demand_function_coefs

    def realize_demand(product, t):
        pass


class TankerCarFleet(object):

    def __init__(self, plant, arrival_time, size):
        self.plant = plant
        self.arrival_time = arrival_time
        self.size = size