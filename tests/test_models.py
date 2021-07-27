"""
Test cases for Recommendations Model

"""
import logging

import unittest
import os
from service.models import Recommendation, DataValidationError, db, Type
from service import app
from .factories import RecommendationFactory
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)
######################################################################
#  RECOMMENDATIONS   M O D E L   T E S T   C A S E S
######################################################################
class TestRecommendationModel(unittest.TestCase):
    """ Test Cases for Recommendations Model """

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Recommendation.init_db(app)
    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_recommendation(self):
        """ Test create a recommendation """
        recommendation = Recommendation(product_id=1, recommendation_product_id=2, relationship=Type.UP_SELL)
        self.assertTrue(recommendation != None)
        self.assertEquals(recommendation.relationship, Type.UP_SELL)
        self.assertEquals(recommendation.product_id, 1)
        self.assertEquals(recommendation.recommendation_product_id, 2)

    def test_delete_a_recommendation(self): 
        """ Delete a recommendation from the database """
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)
        recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)

    def test_serialize_a_recommendation(self):
        """ Test serialization of a Recommendation """
        recommendation = Recommendation(product_id=1, recommendation_product_id=2, relationship=Type.UP_SELL)
        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], recommendation.product_id)
        self.assertIn("recommendation_product_id", data)
        self.assertEqual(data["recommendation_product_id"], recommendation.recommendation_product_id)
        self.assertIn("relationship", data)
        self.assertEqual(data["relationship"], recommendation.relationship.name)

    def test_deserialize_a_recommendation(self):
        """ Test deserialization of a Recommendation """
        data = {
            "product_id": 1,
            "recommendation_product_id": 2,
            "relationship": Type.UP_SELL
        }
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.product_id, 1)
        self.assertEqual(recommendation.recommendation_product_id, 2)
        self.assertEqual(recommendation.relationship, Type.UP_SELL)

    def test_deserialize_missing_data(self):
        """ Test deserialization of a Recommendation with missing data """
        data = {"product_id": 1}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)
    
    def test_list_recommendation(self):
        """Test list recommendations"""
        recommendations = RecommendationFactory.create_batch(1)
        for recommendation in recommendations:
            recommendation.create()
        logging.debug(recommendations)
        # log data
        self.assertEqual(len(recommendation.all()),1)
    



    def test_find_recommendation_type(self):
        """Find a recommendation type by two product ids"""
        recommendations = RecommendationFactory.create_batch(2)
        for recommendation in recommendations:
            recommendation.create()
        logging.debug(recommendations)

        # find the 2nd recommendation in the list
        recommendation = Recommendation.find(recommendations[1].product_id, recommendations[1].recommendation_product_id)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.product_id, recommendations[1].product_id)
        self.assertEqual(recommendation.recommendation_product_id, recommendations[1].recommendation_product_id)
        self.assertEqual(recommendation.relationship, recommendations[1].relationship)

    def test_update_a_recommendation(self):
        """Update a recommendation type by two product ids"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.create()
        logging.debug(recommendation)
        logging.debug(type(recommendation.relationship.name))
        recommendation.relationship = Type.CROSS_SELL
        recommendation.update()
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.relationship.name, 'CROSS_SELL')
        recommendations = recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].product_id, recommendation.product_id)
        self.assertEqual(recommendations[0].recommendation_product_id, recommendation.recommendation_product_id)
        self.assertEqual(recommendations[0].relationship, recommendation.relationship)

    def test_update_a_recommendation_no_relationship(self):
        """Update a recommendation type by two product ids without relationship"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.create()
        logging.debug(recommendation)
        recommendation.relationship = None
        self.assertRaises(DataValidationError, recommendation.update)

    def test_find_recommendation_by_id_and_type(self):
        """Find a recommendation type by product id and relationship id"""
        query_id = 1
        query_type = Type.UP_SELL
        recommendations = [Recommendation(product_id = query_id, recommendation_product_id = 2, relationship = query_type),
                            Recommendation(product_id = query_id, recommendation_product_id = 10, relationship = query_type), 
                            Recommendation(product_id = query_id, recommendation_product_id = 15, relationship = Type.ACCESSORY)]

        for recommendation in recommendations:
            recommendation.create()
        logging.debug(recommendations)

        # find the 2nd recommendation in the list
        results = Recommendation.find_by_id_and_type(query_id, Type.UP_SELL)
        for recommendation in results:
            self.assertIsNot(recommendation, None)
            self.assertEqual(recommendation.product_id, query_id)
            self.assertEqual(recommendation.relationship, query_type)



    def test_update_a_recommendation_likes(self):
        """Like a recommendation"""
        recommendation = RecommendationFactory()
        
        recommendation.create()
        
        self.assertEquals(recommendation.likes, 0)
        recommendation.likes += 1
        recommendation.update()
        self.assertEqual(recommendation.likes, 1)
        
    def test_clear_data(self):
        '''Clear all data entries'''
        recommendations = RecommendationFactory.create_batch(2)
        for recommendation in recommendations:
            recommendation.create()
        self.assertEqual(len(Recommendation.all()), 2)

        Recommendation.clear()
        self.assertEqual(len(Recommendation.all()), 0)



