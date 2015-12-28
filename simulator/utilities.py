'''Contains Class definitions for all objects used in simulate.py'''
import numpy as np
import copy

### Constants
PRODUCTS = ['ORA', 'POJ', 'ROJ', 'FCOJ']
REGIONS = ['NE', 'MA', 'SE', 'MW', 'DS', 'NW', 'SW']
MONTHS = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug']
REGION_SIZES = {'NE': 14, 'MA': 17, 'SE': 12,
                'MW': 22, 'DS': 16, 'NW': 8,
                'SW': 11}

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

    def __str__(self):
        if type(self.sender) is str:
            s = self.sender
        else:
            s = self.sender.name
        return '{0}->{1} of {2} x {3}, due {4}'.format(
            s, self.receiver.name, self.amount,
            self.product, self.arrival_time)


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

    def __str__(self):
        return '@{0} of {1}->{2} x {3}, due {4}'.format(
            self.location.name, self.start_product, self.end_product,
            self.amount, self.finish_time)


class Storage(object):

    def __init__(self, name, capacity, reconstitution_percentages, inventory,
                 markets=None): # in sim, market provided after creation
        self.name = name
        self.capacity = capacity
        self.reconstitution_percentages = reconstitution_percentages
        self.inventory = inventory
        self.markets = markets

    def reconstitute(self, t):
        recon_percentage = self.reconstitution_percentages[(t - 1) / 4]
        if recon_percentage is None:
            recon_percentage = 0
        fcoj_inventory = self.get_total_inventory('FCOJ')
        amount_to_recon = (recon_percentage / 100.) * fcoj_inventory

        self.remove_product('FCOJ', amount_to_recon)
        self.add_product('XOJ', amount_to_recon)

        recon_process = Process(self, t + 1, 'FCOJ', 'ROJ', amount_to_recon)
        recon_cost = 650 * amount_to_recon

        return ([recon_process], recon_cost)

    def dispose_capacity(self, shortage):
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
                    p = float(amount_to_remove) / week_total

                    for x, product in zip(weekly_inventories, available_products):
                        self.remove_product(product, x * p)

                amount_to_remove -= week_total
                indices = [i - 1 for i in indices]

            return

    def age(self):
        for vals in self.inventory.values():
            old_vals = list(vals)
            for i in range(len(vals) - 1): # -1 takes care of rotting
                vals[i + 1] = old_vals[i]
            vals[0] = 0
        return

    def add_product(self, product, amount):
        self.inventory[product][0] += amount
        return

    def remove_product(self, product, amount):
        if amount == 0:
            return
        else:
            amount_to_remove = amount
            i = len(self.inventory[product]) - 1

            # Check weekly inventory starting with final week
            while amount_to_remove > 0 and i >= 0:
                inventory_this_age = self.inventory[product][i]
                if inventory_this_age > amount_to_remove:
                    self.inventory[product][i] -= amount_to_remove
                else:
                    self.inventory[product][i] = 0

                # Should work for this loop, but calculation could be better
                amount_to_remove -= inventory_this_age
                i -= 1

        return

    def get_total_inventory(self, product=None):
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

    def manufacture(self, t):
        ORA_inventory = self.get_total_inventory()
        # No point in creating 0-amount inventories if there is no ORA.
        if ORA_inventory == 0:
            return ([], 0, 0)

        p = self.poj_proportion / 100.0

        # For manufacturing breakdown
        U = np.random.uniform()

        if U < 0.95:
            amount_poj = p * ORA_inventory
            amount_fcoj = (1 - p) * ORA_inventory
            process_poj = Process(self, t + 1, 'ORA', 'POJ', amount_poj)
            process_fcoj = Process(self, t + 1, 'ORA', 'FCOJ', amount_fcoj)

            cost_poj = 2000 * amount_poj
            cost_fcoj = 1000 * amount_fcoj

            return ([process_poj, process_fcoj], cost_poj, cost_fcoj)
        
        else:
            print 'Breakdown of {0} at time {1}'.format(self.name, t)
            return ([], 0, 0)

    def dispose_capacity(self, shortage):
        if shortage <= 0:
            return
        else:
            self.remove_product('ORA', shortage)
            return


    def age(self):
        old_inv = list(self.inventory)
        for i in range(3): # 3 not 4 to deal with rotting
            self.inventory[i + 1] = old_inv[i]
        self.inventory[0] = 0
        return

    def add_product(self, product, amount):
        if product != 'ORA':
            raise ValueError('Can only add ORA to processing inventory')
        else:
            self.inventory[0] += amount
        return

    def remove_product(self, product, amount):
        if product != 'ORA':
            raise ValueError('Can only remove ORA from processing inventory')
        else:
            amount_to_remove = amount
            i = 3

            # Check weekly inventory starting with final week
            while amount_to_remove > 0 and i >= 0:
                inventory_this_age = self.inventory[i]
                if inventory_this_age > amount_to_remove:
                    self.inventory[i] -= amount_to_remove
                else:
                    self.inventory[i] = 0

                # Should work for this loop, but calculation could be better
                amount_to_remove -= inventory_this_age
                i -= 1
        return

    def get_total_inventory(self, product=None):
        if (product != 'ORA') and (product is not None):
            raise ValueError(
                'There should only be ORA in processing inventories.')

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

    def realize_price_month(self, month_index):
        mu = self.price_stats[month_index][0]
        sigma = self.price_stats[month_index][1]
        price = np.random.normal(mu, sigma)
        while price < 0:
            price = np.random.normal(mu, sigma)
        return price

    def realize_week_harvest(self, month_index):
        if month_index not in range(0, 12):
            raise ValueError()

        mu = self.harvest_stats[month_index][0]
        sigma = self.harvest_stats[month_index][1]
        if sigma == 0:
            return mu
        harvest = np.random.normal(mu, sigma)
        while harvest < 0:
            harvest = np.random.normal(mu, sigma)
        return harvest

    def apply_multipliers(self, price, t):
        if t == 0:
            desired_quantity = self.desired_quantities[0]
        else:
            desired_quantity = self.desired_quantities[int((t - 1) / 4)]
        if desired_quantity is None:
            desired_quantity = 0

        if price < self.multipliers[1]:
            return desired_quantity * self.multipliers[0]
        elif price < self.multipliers[3]:
            return desired_quantity * self.multipliers[2]
        elif price < self.multipliers[5]:
            return desired_quantity * self.multipliers[4]
        else:
            return 0

    def spot_purchase(self, t, storages, processing_plants):
        # This special case for month_index is in the first spot purchase,
        # when we want arrival time to be 1, but the month_index must be 0,
        # not -1.
        if t == 0:
            month_index = 0
        else:
            month_index = int((t - 1) / 4)
        price = self.realize_price_month(month_index)
        harvest = self.realize_week_harvest(month_index)

        if self.apply_multipliers(price, t) > harvest:
            amount_purchased = harvest
        else:
            amount_purchased = self.apply_multipliers(price, t)

        deliveries = []
        raw_cost = price * amount_purchased
        shipping_cost = 0
        for key in self.shipping_plan:
            if (self.shipping_plan[key][0] is None or
                self.shipping_plan[key][0] == 0):
                continue
            else:
                p = self.shipping_plan[key][0] / 100.0
            distance = self.shipping_plan[key][1]

            if key[0] == 'P':
                receiver = processing_plants[key]
            else:
                receiver = storages[key]

            deliveries.append(Delivery(self, receiver, t + 1, 'ORA',
                                       p * amount_purchased))
            shipping_cost += 0.22 * p * amount_purchased * distance

        return (deliveries, raw_cost * 2000, shipping_cost)


class Market(object):

    def __init__(self, name, region, prices, demand_function_coefs):
        self.name = name
        self.region = region
        self.prices = prices
        self.demand_function_coefs = demand_function_coefs

    def realize_demand(self, product, t):
        these_coefs = self.demand_function_coefs[product]
        a = these_coefs[0]
        b = these_coefs[1]
        price = self.prices[product][int((t - 1) / 4)]
        expected_demand = a / (price ** 2) + b
        regional_demand = np.random.normal(loc=expected_demand,
                                           scale=0.1 * expected_demand)
        # Return regional_demand / N, where N is the number of market
        # in this market's region.
        return regional_demand / REGION_SIZES[self.region]


class TankerCarFleet(object):

    def __init__(self, plant, arrival_time, size):
        self.plant = plant
        self.arrival_time = arrival_time
        self.size = size