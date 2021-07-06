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

    def test_deserialize_a_pet(self):
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
    
    def test_find_recommendation(self):
        """Find a Recommendation by ID"""
        recommendations = RecommendationFactory.create_batch(3)
        for recommendation in recommendations:
            recommendation.create()
        logging.debug(recommendations)
        # log data
        self.assertEqual(len(recommendation.all()), 3)
        recommendation = Recommendation.find(recommendations[1].id)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, recommendations[1].id)
        self.assertEqual(recommendation.title, recommendations[1].title)
        self.assertEqual(recommendation.recommendation_type,recommendations[1].recommendation_type)
    
    def test_list_by_recommendation_type(self):
        """Test listing a Recommendation by recommendation_type"""
        Recommendation(title="Recommendation one", recommendation_type="Upsell", active=True).create()
        Recommendation(title="Recommendation two", recommendation_type="Cross_sell", active=False).create()
        Recommendations = Recommendation.find_by_recommendation_type("Cross_sell")
        self.assertEqual(recommendations[0].title, "Recommendation one")
        self.assertEqual(recommendations[0].recommendation_type, "Upsell")
        self.assertEqual(recommendations[0].title, "Recommendation two")
        self.assertEqual(recommendations[0].recommendation_type, "Cross_sell")
        self.assertEqual(recommendations[0].active, False)

    def test_list_by_active(self):
        """Test listing Recommendation by active"""
        Recommendation(title="Recommendation three", recommendation_type="Accessory", active=True).create()
        Reommendation(title="Reommendation four", recommendation_type="Bundle", active=False).create()
        Recommendations = Recommendation.find_by_active(False)
        self.assertEqual(recommendations[0].title, "Recommendation three")
        self.assertEqual(recommendations[0].recommendation_type, "Accessory")
        self.assertEqual(recommendations[0].title, "Recommendation four")
        self.assertEqual(recommendations[0].recommendation_type, "Bundle")
        self.assertEqual(recommendations[0].active, False)


    
