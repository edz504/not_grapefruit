class Grove:

   months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', ...
             'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']

   def __init__(self, name):
      self.name = name
      self.month = months[0]

   def realize_month_price():
      # Simulate and return price for the current month

   def realize_week_harvest():
      # Simulate and return harvest quantity for a given week

   def spot_purchase(amount, shipping):
      # buy spot purchases from this grove as min(amount, realize_week_harvest(month))
      # and create Delivery’s according to the shipping provided.

      price = realize_month_price()
      quantity_available = realize_week_harvest()
      quantity_to_ship = min(quantity_available, amount)
      return [Delivery(self, shipping, 'ORA', quantity_to_ship*p/100) for p in shipping]

class Delivery:
   products = ['ORA', 'POJ', 'ROJ', 'FCOJ']

   def __init__(self, sender, receiver, product, amount):
      self.sender = sender
      self.receiver = receiver
      self.product = product
      self.amount = amount


class Storage:
   def __init__(self, name):
      self.name = name
      self.inventory = [(0, 0, 0, 0)] * 48

   def reconstitute(ratio):
      # create a Delivery of ROJ from this storage to itself, with a 1-week delivery
      return Delivery(self, self, t, product, amount)

   def check_rotten():
      # dispose of rotten inventory

   def dispose_capacity(shortage):
      # dispose of inventory using capacity shortage rules, given that shortage tons of product needs to be tossed out

class ProcessingPlant:
   def __init__(self, name, capacity):
      self.name = name
      self.capacity = capacity
      self.raw_inventory = 

class Market:

   def __init__(self, name):
      self.name = name
      self.region = regions[name]

