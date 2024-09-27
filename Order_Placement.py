import unittest
from unittest import mock  # Import the mock module for simulating payment failures in tests.
from enum import Enum
import re
import datetime
from Restaurant_Browsing import RestaurantDatabase

# CartItem Class
class CartItem:
    """
    Represents an individual item in the shopping cart.
    
    Attributes:
        name (str): The name of the item.
        price (float): The price of the item.
        quantity (int): The quantity of the item in the cart.
    """
    def __init__(self, name, price, quantity):
        """
        Initializes a CartItem object with the given name, price, and quantity.
        
        Args:
            name (str): Name of the item.
            price (float): Price of the item.
            quantity (int): Quantity of the item in the cart.
        """
        self.name = name
        self.price = price
        self.quantity = quantity

    def update_quantity(self, new_quantity):
        """
        Updates the quantity of the item in the cart.
        
        Args:
            new_quantity (int): The new quantity of the item.
        """
        self.quantity = new_quantity

    def get_subtotal(self):
        """
        Calculates the subtotal price for this item based on its price and quantity.
        
        Returns:
            float: The subtotal price for this item.
        """
        return self.price * self.quantity


# Cart Class
class Cart:
    """
    Represents a shopping cart that can contain multiple CartItem objects.
    
    Attributes:
        items (list): A list of CartItem objects in the cart.
    """
    def __init__(self):
        """
        Initializes an empty Cart with no items.
        """
        self.items = []

    def add_item(self, name, price, quantity):
        """
        Adds a new item to the cart or updates the quantity of an existing item.
        
        Args:
            name (str): Name of the item.
            price (float): Price of the item.
            quantity (int): Quantity to be added to the cart.
        
        Returns:
            str: A message indicating whether the item was added or updated.
        """
        for item in self.items:
            if item.name == name:
                # If the item is already in the cart, update its quantity.
                item.update_quantity(item.quantity + quantity)
                return f"Updated {name} quantity to {item.quantity}"
        
        # If the item is not in the cart, add it as a new item.
        new_item = CartItem(name, price, quantity)
        self.items.append(new_item)
        return f"Added {name} to cart"

    def remove_item(self, name):
        """
        Removes an item from the cart by its name.
        
        Args:
            name (str): Name of the item to be removed.
        
        Returns:
            str: A message indicating the item was removed.
        """
        self.items = [item for item in self.items if item.name != name]
        return f"Removed {name} from cart"

    def update_item_quantity(self, name, new_quantity):
        """
        Updates the quantity of an item in the cart by its name.
        
        Args:
            name (str): Name of the item.
            new_quantity (int): The new quantity for the item.
        
        Returns:
            str: A message indicating whether the item's quantity was updated or if the item was not found.
        """
        for item in self.items:
            if item.name == name:
                item.update_quantity(new_quantity)
                return f"Updated {name} quantity to {new_quantity}"
        return f"{name} not found in cart"

    def calculate_total(self):
        """
        Calculates the total cost of the items in the cart, including tax and delivery fee.
        
        Returns:
            dict: A dictionary containing the subtotal, tax, delivery fee, and total cost.
        """
        subtotal = sum(item.get_subtotal() for item in self.items)
        tax = subtotal * 0.10  # Assume 10% tax rate.
        delivery_fee = 5.00  # Flat delivery fee.
        total = subtotal + tax + delivery_fee
        return {"subtotal": subtotal, "tax": tax, "delivery_fee": delivery_fee, "total": total}

    def view_cart(self):
        """
        Provides a view of the items in the cart.
        
        Returns:
            list: A list of dictionaries with each item's name, quantity, and subtotal price.
        """
        return [{"name": item.name, "quantity": item.quantity, "subtotal": item.get_subtotal()} for item in self.items]


# OrderPlacement Class
class OrderPlacement:
    """
    Represents the process of placing an order, including validation, checkout, and confirmation.
    
    Attributes:
        cart (Cart): The shopping cart containing the items for the order.
        user_profile (UserProfile): The user's profile, including delivery address.
        restaurant_menu (RestaurantMenu): The menu containing available restaurant items.
    """
    def __init__(self, cart, user_profile, restaurant_menu, restaurant):
        """
        Initializes an OrderPlacement object with the cart, user profile, and restaurant menu.
        
        Args:
            cart (Cart): The shopping cart.
            user_profile (UserProfile): The user's profile.
            restaurant_menu (RestaurantMenu): The restaurant menu with available items.
            restaurant (Dictionary): restaurant that is being ordered from
        """
        self.cart = cart
        self.user_profile = user_profile
        self.restaurant_menu = restaurant_menu

        self.paymentDone = False # bool to reflect that order has been payed
        self.orderStatus = OrderStatus.NotOrdered # Enum to reflect order  status
        self.preorder = False # bool to reflect has the order been pre ordered
        self.preorderDeliveryTime = datetime.date(1,1,1) # placeholder date value for preorder date
        self.restaurant = restaurant # dictionary object  containing restaurant data
        

    def validate_order(self):
        """
        Validates the order by checking if the cart is empty and if all items are available in the restaurant menu.
        
        Returns:
            dict: A dictionary indicating whether the order is valid and an accompanying message.
        """
        if not self.cart.items:
            return {"success": False, "message": "Cart is empty"}

        # Validate the availability of each item in the cart.
        for item in self.cart.items:
            if not self.restaurant_menu.is_item_available(item.name):
                return {"success": False, "message": f"{item.name} is not available"}
        return {"success": True, "message": "Order is valid"}

    def proceed_to_checkout(self):
        """
        Prepares the order for checkout by calculating the total and retrieving the delivery address.
        
        Returns:
            dict: A dictionary containing the cart items, total cost details, and delivery address.
        """
        total_info = self.cart.calculate_total()
        return {
            "items": self.cart.view_cart(),
            "total_info": total_info,
            "delivery_address": self.user_profile.delivery_address,
        }

    def confirm_order(self, payment_method):
        """
        Confirms the order by validating it and processing the payment.
        
        Args:
            payment_method (PaymentMethod): The method of payment to be used.
        
        Returns:
            dict: A dictionary indicating whether the order was confirmed and an order ID if successful.
        """
        if not self.validate_order()["success"]:
            return {"success": False, "message": "Order validation failed"}

        # Process payment using the given payment method.
        payment_success = payment_method.process_payment(self.cart.calculate_total()["total"])

        if payment_success:
            self.paymentDone = True
            return {
                "success": True,
                "message": "Order confirmed",
                "order_id": "ORD123456",  # Simulate an order ID.
                "estimated_delivery": "45 minutes"
            }
        return {"success": False, "message": "Payment failed"}
    
    def AdvanceOrderStatus(self):
        ''' Moves order status to the next state
        '''
        if (not self.paymentDone): # return if order has not been payed
            return
        
        if (self.orderStatus.value < OrderStatus.Delivered.value): # check if order status is in final state
            self.orderStatus = OrderStatus(self.orderStatus.value +1)

    def Preorder(self, date):
        ''' Sets order's preorder delivery date
        '''

        if not self.restaurant["preorderAvailable"]: # check if restaurant supports preordering
            return
        
        if self.paymentDone: #check if order has been payed
            return
        
        currentDateTime = datetime.datetime.now()
        if date < currentDateTime: # check if preordering date is set in past
            return
        
        if self.restaurant["openingTime"] < date.hour and self.restaurant["closingTime"] > date.hour: # if restaurant is open during delivery time

            self.preorderDeliveryTime = date
            self.preorder = True

    def EditPreorderDeliveryTime(self, date):
        ''' Enables editing preorder delivery date
        '''
        if not self.preorder: #if order has not a set delivery time, there is nothing to edit
            return

        currentDateTime = datetime.datetime.now()

        dateDifference = date - currentDateTime

        dateDifferenceInHours = dateDifference.total_seconds() / 3600 
        
        if (dateDifferenceInHours < 30): # if delivery is set under 30 hours from now, disable editing
            return
        
        self.preorderDeliveryTime = date

    def ValidPreorderTime(self, date):
        ''' Check if given date is during restaurant operating time 
        '''
        return (float(date.hour) > self.restaurant["openingTime"]) & (float(date.hour) < self.restaurant["closingTime"])
        

    

class OrderStatus(Enum):
    ''' Represents phases during delivery
    '''
    NotOrdered = 0
    OrderReceived = 1
    BeingDelivered = 2
    Delivered = 3

    def __str__(self):
        ''' Changes enum names to add a whitespace between two words
        '''

        match = re.search(".[A-Z].", self.name)
        if not match:
            return self.name
        indexOfInsert = match.span(0)[0]
        enumWithWhiteSpace = self.name[:indexOfInsert +1] + " " + self.name[indexOfInsert + 1:]
        return enumWithWhiteSpace


# PaymentMethod Class
class PaymentMethod:
    """
    Represents the method of payment for an order.
    """
    def process_payment(self, amount):
        """
        Processes the payment for the given amount.
        
        Args:
            amount (float): The amount to be paid.
        
        Returns:
            bool: True if the payment is successful, False otherwise.
        """
        if amount > 0:
            return True
        return False


# UserProfile Class (for simulating the user's details)
class UserProfile:
    """
    Represents the user's profile, including delivery address.
    
    Attributes:
        delivery_address (str): The user's delivery address.
        ID : unique identifier for each user.
        favourites : list of user's favourite restaurants.
    """
    __availableID = 0
    def __init__(self, delivery_address):
        """
        Initializes a UserProfile object with a delivery address.
        
        Args:
            delivery_address (str): The user's delivery address.
        """
        self.delivery_address = delivery_address
        self.ID = UserProfile.__availableID #Add unique id to this object on creation
        UserProfile.__availableID += 1 # Increment static class field for next object

        self.favourites = [] #list of restaurants

    def AddRestaurantToFavourites(self, restaurant):

        if restaurant in self.favourites:
            return
        
        self.favourites.append(restaurant)

    def RemoveRestaurantFromFavourites(self, restaurant):

        if restaurant not in self.favourites:
            return

        self.favourites.remove(restaurant)

    def GetFavouriteRestaurants(self):

        return self.favourites


# RestaurantMenu Class (for simulating available menu items)
class RestaurantMenu:
    """
    Represents the restaurant's menu, including available items.
    
    Attributes:
        available_items (list): A list of items available on the restaurant's menu.
    """
    def __init__(self, available_items):
        """
        Initializes a RestaurantMenu with a list of available items.
        
        Args:
            available_items (list): A list of available menu items.
        """
        self.available_items = available_items

    def is_item_available(self, item_name):
        """
        Checks if a specific item is available in the restaurant's menu.
        
        Args:
            item_name (str): The name of the item to check.
        
        Returns:
            bool: True if the item is available, False otherwise.
        """
        return item_name in self.available_items


# Unit tests for OrderPlacement class
class TestOrderPlacement(unittest.TestCase):
    """
    Unit tests for the OrderPlacement class.
    """
    def setUp(self):
        """
        Sets up the test environment by creating instances of necessary classes.
        """
        self.restaurant_menu = RestaurantMenu(available_items=["Burger", "Pizza", "Salad"])
        self.user_profile = UserProfile(delivery_address="123 Main St")
        self.cart = Cart()
        self.order = OrderPlacement(self.cart, self.user_profile, self.restaurant_menu, RestaurantDatabase().get_restaurants()[0])

    def test_validate_order_empty_cart(self):
        """
        Test case for validating an order with an empty cart.
        """
        result = self.order.validate_order()
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Cart is empty")

    def test_validate_order_item_not_available(self):
        """
        Test case for validating an order with an unavailable item.
        """
        self.cart.add_item("Pasta", 15.99, 1)
        result = self.order.validate_order()
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Pasta is not available")

    def test_validate_order_success(self):
        """
        Test case for successfully validating an order.
        """
        self.cart.add_item("Burger", 8.99, 2)
        result = self.order.validate_order()
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Order is valid")

    def test_confirm_order_success(self):
        """
        Test case for confirming an order with successful payment.
        """
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()
        result = self.order.confirm_order(payment_method)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Order confirmed")
        self.assertEqual(result["order_id"], "ORD123456")

    def test_confirm_order_failed_payment(self):
        """
        Test case for confirming an order with failed payment.
        """
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()

        # Use unittest.mock.patch to simulate failed payment processing.
        with mock.patch.object(payment_method, 'process_payment', return_value=False):
            result = self.order.confirm_order(payment_method)
            self.assertFalse(result["success"])
            self.assertEqual(result["message"], "Payment failed")

    def test_order_status_not_advancing_without_successfull_payment(self):
        '''Does not advance order status if order has not been payed'''
        self.order.AdvanceOrderStatus()
        self.assertTrue(self.order.orderStatus == OrderStatus.NotOrdered)

    def test_order_status_advances_when_order_done(self):
        '''Delivery status can be advanced after payment'''
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()
        result = self.order.confirm_order(payment_method)

        self.order.AdvanceOrderStatus()
        self.assertTrue(self.order.orderStatus == OrderStatus.OrderReceived)

    def test_order_status_does_not_advance_after_delivered_status(self):
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()
        result = self.order.confirm_order(payment_method)

        for i in range(10):
            self.order.AdvanceOrderStatus()

        self.assertTrue(self.order.orderStatus == OrderStatus.Delivered)

    def test_preorder_sets_delivery_date(self):
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()
        orderDate = datetime.datetime.now() + datetime.timedelta(hours=3)

        while not self.order.ValidPreorderTime(orderDate):
            orderDate = orderDate + datetime.timedelta(hours=3)

        self.order.Preorder(orderDate)

        self.assertTrue(self.order.preorderDeliveryTime == orderDate)

    def test_cannot_set_preorder_date_past_date(self):
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()
        orderDate = datetime.datetime.now() - datetime.timedelta(hours=10)
        self.order.Preorder(orderDate)

        self.assertTrue(self.order.preorderDeliveryTime != orderDate)

    def test_cannot_edit_preorder_date_under_thirty_hours_of_preorder_date(self):
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()
        
        orderDate = datetime.datetime.now() + datetime.timedelta(hours=2)
        
        while not self.order.ValidPreorderTime(orderDate):
            orderDate = orderDate + datetime.timedelta(hours=3)

        self.order.Preorder(orderDate)
        self.order.EditPreorderDeliveryTime(datetime.datetime.now() + datetime.timedelta(minutes=30))


        self.assertTrue(self.order.preorderDeliveryTime == orderDate)

    def test_cannot_set_preorder_delivery_time_outside_of_restaurant_open_hours(self):
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()
        
        orderDate = datetime.datetime.now() + datetime.timedelta(hours=2)
        
        while self.order.ValidPreorderTime(orderDate):
            orderDate = orderDate + datetime.timedelta(hours=3)

        self.order.Preorder(orderDate)
        


        self.assertTrue(self.order.preorderDeliveryTime != orderDate)

    def test_cannot_preorder_from_non_preorderable_restaurant(self):

        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()
        
        orderDate = datetime.datetime.now() + datetime.timedelta(hours=2)
        
        while not self.order.ValidPreorderTime(orderDate):
            orderDate = orderDate + datetime.timedelta(hours=3)

        self.order.restaurant = RestaurantDatabase().get_restaurants()[1]
        self.order.Preorder(orderDate)

        self.assertTrue(self.order.preorderDeliveryTime != orderDate)

    def test_user_has_added_restaurant_as_favourite(self):
        restaurantToAdd = RestaurantDatabase().get_restaurants()[0]

        self.user_profile.AddRestaurantToFavourites(restaurantToAdd)

        self.assertTrue(self.user_profile.GetFavouriteRestaurants()[0] == restaurantToAdd)

    def test_users_favourite_restaurant_can_be_removed(self):
        restaurantToUse = RestaurantDatabase().get_restaurants()[0]

        self.user_profile.AddRestaurantToFavourites(restaurantToUse)
        self.user_profile.RemoveRestaurantFromFavourites(restaurantToUse)

        self.assertTrue(len(self.user_profile.GetFavouriteRestaurants()) == 0)

    def test_user_cannot_have_same_restaurant_twice_at_same_time_in_favourites(self):
        restaurantToUse = RestaurantDatabase().get_restaurants()[0]
        
        self.user_profile.AddRestaurantToFavourites(restaurantToUse)
        self.user_profile.AddRestaurantToFavourites(restaurantToUse)

        self.assertTrue(len(self.user_profile.GetFavouriteRestaurants()) == 1)




if __name__ == "__main__":
    
    unittest.main()
