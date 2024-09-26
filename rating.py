import unittest
from Restaurant_Browsing import RestaurantDatabase
from Order_Placement import UserProfile

class RestaurantRater:
    '''Handles user ratings'''
    def __init__(self, restaurantList):
        self.userRatings = {}
        self.restaurants = restaurantList

    def RateRestaurant(self, restaurantName, userID, rating):
        if rating < 1 or rating > 5:
            return
        if userID not in self.userRatings.keys():
            self.userRatings[userID] = {}

        self.userRatings[userID][restaurantName] = rating
        self.restaurants

        for restaurant in self.restaurants:
            if restaurant["name"] == restaurantName:

                restaurant["totalRating"] += rating
                restaurant["timesRated"] += 1
                restaurant["rating"] = restaurant["totalRating"] / restaurant["timesRated"]
                break

    def EditRestaurantRating(self, restaurantName, userID, rating):
        if (rating < 1 | rating > 5):
            return
        if userID not in self.userRatings.keys():
            return
        if restaurantName not in self.userRatings[userID]:
            return
        
        for restaurant in self.restaurants:
            if restaurant["name"] == restaurantName:
                restaurant["totalRating"] -= self.userRatings[userID][restaurantName]
                restaurant["totalRating"] += rating
                restaurant["rating"] = restaurant["totalRating"] / restaurant["timesRated"]

class TestRating(unittest.TestCase):

    def setUp(self):
        self.db = RestaurantDatabase()
        self.rater = RestaurantRater(self.db.get_restaurants())

    def test_rating_a_restaurant(self):
        user1 = UserProfile("address1")
        restaurant1 = self.db.get_restaurants()[0]
        self.rater.RateRestaurant(restaurant1["name"], user1.ID, 2)

        self.assertTrue(restaurant1["rating"] != 4.5)

    def test_rating_0_does_not_change_rating(self):
        user1 = UserProfile("address1")
        restaurant1 = self.db.get_restaurants()[0]
        self.rater.RateRestaurant(restaurant1["name"], user1.ID, 0)

        self.assertTrue(restaurant1["rating"] == 4.5)

    def test_rating_6_does_not_change_rating(self):
        user1 = UserProfile("address1")
        restaurant1 = self.db.get_restaurants()[0]
        self.rater.RateRestaurant(restaurant1["name"], user1.ID, 6)

        self.assertTrue(restaurant1["rating"] == 4.5)

    def test_rating_decimal_changes_rating(self):
        user1 = UserProfile("address1")
        restaurant1 = self.db.get_restaurants()[0]
        self.rater.RateRestaurant(restaurant1["name"], user1.ID, 2.5)

        self.assertTrue(restaurant1["rating"] != 4.5)

    def test_editing_existing_rating(self):
        user1 = UserProfile("address1")
        restaurant1 = self.db.get_restaurants()[0]
        self.rater.RateRestaurant(restaurant1["name"], user1.ID, 4)

        self.rater.EditRestaurantRating(restaurant1["name"], user1.ID, 3)

        self.assertTrue(restaurant1["rating"] == 3.75)



if __name__ == '__main__':
    unittest.main()


