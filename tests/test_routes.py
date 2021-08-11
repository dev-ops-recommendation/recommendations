"""
TestRecommendationsModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from tests.factories import RecommendationFactory
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import status  # HTTP Status Codes
from service.models import db, Recommendation, Type
from service.routes import app
import json

BASE_URL = "/api/recommendations"
CONTENT_TYPE_JSON = "application/json"
TEST_DATABASE_URI = os.getenv(
    "TEST_DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)
######################################################################
#  T E S T   C A S E S
######################################################################
class TestRecommendationServer(TestCase):
    """ REST API Recommendation Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Recommendation.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def _create_recommendations(self, count):
        """Factory method to create pets in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            resp = self.app.post(
                BASE_URL, json=test_recommendation.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test recommendation"
            )
            recommendations.append(test_recommendation)
        return recommendations

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_recommendation(self):
        """ Get a single Recommendation """
        # get the id of a pet
        test_recommendation = self._create_recommendations(1)[0]
        resp = self.app.get(
            "/api/recommendations/{}/recommended-products/{}".format(test_recommendation.product_id, test_recommendation.recommendation_product_id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["relationship"], test_recommendation.relationship.name)
    
    def test_get_recommendation_not_found(self):
        """ Get a Recommendation thats not found """
        resp = self.app.get("/api/recommendations/0/recommended-products/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_create_recommendation(self):
        """ Create a new recommendation """
        test_recommendation = RecommendationFactory()
        logging.debug(test_recommendation)
        resp = self.app.post(
            BASE_URL, json=test_recommendation.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_recommendation = resp.get_json()
        self.assertEqual(new_recommendation["product_id"], test_recommendation.product_id, "product id1 does not match")
        self.assertEqual(new_recommendation["recommendation_product_id"], test_recommendation.recommendation_product_id, "product id2 does not match")
        
        self.assertEqual(
            new_recommendation["relationship"], test_recommendation.relationship.name, "Relationship does not match"
        )

    def test_delete_recommendation(self):
        """ Delete a recommendation """
        test_recommendation = self._create_recommendations(1)[0]
        resp = self.app.delete(
            "/api/recommendations/{}/recommended-products/{}".format(test_recommendation.product_id, test_recommendation.recommendation_product_id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        resp = self.app.get(
            "/api/recommendations/{}/recommended-products/{}".format(test_recommendation.product_id, test_recommendation.recommendation_product_id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recommendation_duplicate_data(self):
        """ Create a Recommendation with missing data """
        test_recommendation = RecommendationFactory()
        logging.debug(test_recommendation)
        self.app.post(
            "/api/recommendations", json=test_recommendation.serialize(), content_type="application/json"
        )  
        resp = self.app.post(
            "/api/recommendations", json=test_recommendation.serialize(), content_type="application/json"
        )  
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_no_content_type(self):
        """ Create a Recommendation with no content type """
        resp = self.app.post("/api/recommendations")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    
    def test_list_recommendations(self):
        """Get a list of recommendations"""
        test_recommendation = RecommendationFactory()
        logging.debug(test_recommendation)
        resp = self.app.post(
            "/api/recommendations", json=test_recommendation.serialize(), content_type="application/json"
        )  
        resp = self.app.get("/api/recommendations")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.get_json()
        self.assertEqual(len(result), 1)
        result_recommendation = result[0]

        self.assertEqual(result_recommendation['product_id'], test_recommendation.product_id)
        self.assertEqual(result_recommendation['recommendation_product_id'], test_recommendation.recommendation_product_id)
        self.assertEqual(result_recommendation['relationship'], test_recommendation.relationship.name)

    def test_update_recommendation(self):
        """Update an existing recommendation"""
        # create a recommendation to update
        test_recommendation = RecommendationFactory()
        logging.debug(test_recommendation)
        resp = self.app.post(
            "/api/recommendations", json=test_recommendation.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the recommendation
        new_recommendation = resp.get_json()
        new_recommendation["relationship"] = "CROSS_SELL"
        logging.debug(new_recommendation)
        resp = self.app.put(
            "/api/recommendations/{}/recommended-products/{}".format(test_recommendation.product_id,
                                                                      test_recommendation.recommendation_product_id),
            json=new_recommendation,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_recommendation = resp.get_json()
        self.assertEqual(updated_recommendation["relationship"], "CROSS_SELL")

    def test_update_recommendation_not_found(self):
        """ update a Recommendation that is not found """
        test_recommendation = RecommendationFactory()
        test_recommendation.product_id = 0
        test_recommendation.recommendation_product_id = 0
        logging.debug(test_recommendation)
        resp = self.app.put("/api/recommendations/0/recommended-products/0",json=test_recommendation.serialize(),
            content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_recommendation_no_content_type(self):
        """ create a Recommendation with no content type """
        resp = self.app.put("/api/recommendations/0/recommended-products/0")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_query_recommendation_by_id_and_type(self):
        """Query recommendations for a specific id and type"""
        # create a recommendation to update
        test_recommendation = RecommendationFactory()
        logging.debug(test_recommendation)
        resp = self.app.post(
            "/api/recommendations", json=test_recommendation.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # query the recommendation
        
        resp = self.app.get(
            "/api/recommendations/{}?type={}".format(test_recommendation.product_id,
                                                                      test_recommendation.relationship.name)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.get_json()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["relationship"], test_recommendation.relationship.name)

    def test_clear_all_recommendations(self):
        """ Delete all recommendations"""
        self._create_recommendations(1)[0]

        #Expecting one recommendation
        resp = self.app.get("/api/recommendations")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.get_json()
        self.assertEqual(len(result), 1)
        
        #Calling clear the database
        resp = self.app.delete("/api/recommendations")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

        #Expecing 0 recommendation now
        resp = self.app.get("/api/recommendations")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        result = resp.get_json()
        self.assertEqual(len(result), 0)

    
    def test_like_recommendation(self):
        """Like an existing recommendation"""
        # create a recommendation to like
        test_recommendation = RecommendationFactory()
        
        resp = self.app.post(
            "/api/recommendations", json=test_recommendation.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # like the recommendation
       
        resp = self.app.put(
            "/api/recommendations/{}/recommended-products/{}/like".format(test_recommendation.product_id,
                                                                      test_recommendation.recommendation_product_id),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get(
            "/api/recommendations/{}/recommended-products/{}".format(test_recommendation.product_id, test_recommendation.recommendation_product_id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["likes"], 1)

    def test_like_recommendation_not_found(self):
        """ Like a Recommendation thats not found """
        resp = self.app.put("/api/recommendations/0/recommended-products/0/like")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    
