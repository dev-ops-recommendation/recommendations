"""
Test cases for YourResourceModel Model

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
    """ Test Cases for YourResourceModel Model """

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
        recommendation = Recommendation(product_id1=1, product_id2=2, relationship=Type.UP_SELL)
        self.assertTrue(recommendation != None)
        self.assertEquals(recommendation.relationship, Type.UP_SELL)
        self.assertEquals(recommendation.product_id1, 1)
        self.assertEquals(recommendation.product_id2, 2)

    def test_serialize_a_recommendation(self):
        """ Test serialization of a Recommendation """
        recommendation = Recommendation(product_id1=1, product_id2=2, relationship=Type.UP_SELL)
        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("product_id1", data)
        self.assertEqual(data["product_id1"], recommendation.product_id1)
        self.assertIn("product_id2", data)
        self.assertEqual(data["product_id2"], recommendation.product_id2)
        self.assertIn("relationship", data)
        self.assertEqual(data["relationship"], recommendation.relationship.name)

    def test_deserialize_a_recommendation(self):
        """ Test deserialization of a Recommendation """
        data = {
            "product_id1": 1,
            "product_id2": 2,
            "relationship": Type.UP_SELL
        }
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.product_id1, 1)
        self.assertEqual(recommendation.product_id2, 2)
        self.assertEqual(recommendation.relationship, Type.UP_SELL)

    def test_deserialize_missing_data(self):
        """ Test deserialization of a Recommendation with missing data """
        data = {"product_id1": 1}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)


    def test_find_recommendation_type(self):
        """Find a recommendation type by two product ids"""
        recommendations = RecommendationFactory.create_batch(2)
        for recommendation in recommendations:
            recommendation.create()
        logging.debug(recommendations)

        # find the 2nd recommendation in the list
        recommendation = Recommendation.find(recommendations[1].product_id1, recommendations[1].product_id2)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.product_id1, recommendations[1].product_id1)
        self.assertEqual(recommendation.product_id2, recommendations[1].product_id2)
        self.assertEqual(recommendation.relationship, recommendations[1].relationship)

    def test_update_a_recommendation(self):
        """Update a recommendation type by two product ids"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.create()
        logging.debug(recommendation)
        recommendation.relationship.name = 'CROSS_SELL'
        recommendation.update()
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.relationship.name, 'CROSS_SELL')
        recommendations = recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].product_id1, recommendation.product_id1)
        self.assertEqual(recommendations[0].product_id2, recommendation.product_id2)
        self.assertEqual(recommendations[0].relationship, recommendation.relationship)

