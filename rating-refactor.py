import unittest
from Restaurant_Browsing import RestaurantDatabase
from Order_Placement import UserProfile

class RestaurantRater:
    '''Handles user ratings
        Contains restaurant database list 
        Contains Dictionary that uses user id as key and dictionaries with restaurant name and rating as value ( {UserID : {restaurant name : rating} } )
    '''
    def __init__(self, restaurant_list):
        self.restaurant_list = restaurant_list
        self.user_ratings = {}

    def rate_restaurant(self, restaurant_name, user_id, rating):
        '''Handles setting a rating between 1 and 5 to the specific restaurant'''
        if not self.is_valid_rating(rating):
            return False

        if user_id not in self.user_ratings:
            self.user_ratings[user_id] = {}

        if restaurant_name in self.user_ratings[user_id]:
            # Remove old rating from total ratings
            self.update_restaurant_ratings(restaurant_name, user_id, -self.user_ratings[user_id][restaurant_name])

        self.user_ratings[user_id][restaurant_name] = rating

        # Update restaurant's total ratings and average rating
        for restaurant in self.restaurant_list:
            if restaurant["name"] == restaurant_name:
                self.update_restaurant_ratings(restaurant_name, user_id, rating)
                break
        return True

    def edit_restaurant_rating(self, restaurant_name, user_id, rating):
        """Edits existing rating betwen 1 and 5 for the specfied restaurant."""
        if not self.is_valid_rating(rating):
            return False

        if user_id not in self.user_ratings:
            return False

        if restaurant_name not in self.user_ratings[user_id]:
            return False

        #remove old rating from restaurant and add new edited rating
        self.update_restaurant_ratings(restaurant_name, user_id, -self.user_ratings[user_id][restaurant_name])

        self.user_ratings[user_id][restaurant_name] = rating

        #calculate new rating for restaurant
        for restaurant in self.restaurant_list:
            if restaurant["name"] == restaurant_name:
                self.update_restaurant_ratings(restaurant_name, user_id, rating)
                break
        return True

    def is_valid_rating(self, rating):
        """Checks if the rating is between 1 ad 5."""
        return 1 <= rating <= 5

    def update_restaurant_ratings(self, restaurant_name, user_id, rating_change):
        """Updates a restaurant's ratings based on a given change in rating."""
        for restaurant in self.restaurant_list:
            if restaurant["name"] == restaurant_name:
                restaurant["totalRating"] += rating_change
                restaurant["timesRated"] += 1 if rating_change > 0 else -1
                restaurant["rating"] = round(restaurant["totalRating"] / restaurant["timesRated"], 2)
                break

class TestRating(unittest.TestCase):

    def setUp(self):
        self.db = RestaurantDatabase()
        self.rater = RestaurantRater(self.db.get_restaurants())

    def test_rating_a_restaurant(self):
        user1 = UserProfile("address1")
        restaurant1 = self.db.get_restaurants()[0]
        self.rater.rate_restaurant(restaurant1["name"], user1.ID, 2)

        self.assertTrue(restaurant1["rating"] != 4.5)

    def test_rating_0_does_not_change_rating(self):
        user1 = UserProfile("address1")
        restaurant1 = self.db.get_restaurants()[0]
        self.rater.rate_restaurant(restaurant1["name"], user1.ID, 0)

        self.assertTrue(restaurant1["rating"] == 4.5)

    def test_rating_6_does_not_change_rating(self):
        user1 = UserProfile("address1")
        restaurant1 = self.db.get_restaurants()[0]
        self.rater.rate_restaurant(restaurant1["name"], user1.ID, 6)

        self.assertTrue(restaurant1["rating"] == 4.5)

    def test_rating_decimal_changes_rating(self):
        user1 = UserProfile("address1")
        restaurant1 = self.db.get_restaurants()[0]
        self.rater.rate_restaurant(restaurant1["name"], user1.ID, 2.5)

        self.assertTrue(restaurant1["rating"] != 4.5)

    def test_editing_existing_rating(self):
        user1 = UserProfile("address1")
        restaurant1 = self.db.get_restaurants()[0]
        self.rater.rate_restaurant(restaurant1["name"], user1.ID, 4)

        self.rater.edit_restaurant_rating(restaurant1["name"], user1.ID, 3)

        self.assertTrue(restaurant1["rating"] == 3.75)



if __name__ == '__main__':
    unittest.main()


