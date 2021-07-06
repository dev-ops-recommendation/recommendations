"""
TestYourResourceModel API Service Test Suite

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
from service.models import db, Recommendation
from service.routes import app

BASE_URL = "/recommendations"
CONTENT_TYPE_JSON = "application/json"
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
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
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
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

    def test_create_recommendation(self):
        """ Create a new recommendation """
        test_recommendation = RecommendationFactory()
        logging.debug(test_recommendation)
        resp = self.app.post(
            "/recommendations", json=test_recommendation.serialize(), content_type="application/json"
        )  
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_recommendation = resp.get_json()
        self.assertEqual(new_recommendation["product_id1"], test_recommendation.product_id1, "product id1 does not match")
        self.assertEqual(new_recommendation["product_id2"], test_recommendation.product_id2, "product id2 does not match")
        
        self.assertEqual(
            new_recommendation["relationship"], test_recommendation.relationship.name, "Relationship does not match"
        )

    def test_create_recommendation_duplicate_data(self):
        """ Create a Recommendation with missing data """
        test_recommendation = RecommendationFactory()
        logging.debug(test_recommendation)
        self.app.post(
            "/recommendations", json=test_recommendation.serialize(), content_type="application/json"
        )  
        resp = self.app.post(
            "/recommendations", json=test_recommendation.serialize(), content_type="application/json"
        )  
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_no_content_type(self):
        """ Create a Recommendation with no content type """
        resp = self.app.post("/recommendations")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    
    def test_list_recommendations(self):
        """Get a list of recommendations"""
        self._list_recommendations(4)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data),4)


    def test_list_by_recommendation_type(self):
        """List Recommendations by recommendation_type"""
        recommendations = self._create_recommendations(10)
        test_recommendation_type = recommendations[0].recommendation_type
        recommendation_type_recommendations = [recommendation for recommendation in recommendations if recommendation.recommendation_type == test_recommendation_type]
        resp = self.app.get(BASE_URL, query_string="recommendation_type={}".format(test_recommendation_type))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(recommendation_type_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["recommendation_type"], test_recommendation_type)
    
    def test_list_recommendation_by_active(self):
        """List Recommendations by Active"""
        recommendations = self._create_recommendations(10)
        test_active = recommendations[0].active
        active_recommendations = [recommendation for recommendation in recommendations if recommendation.active == test_active]
        resp = self.app.get(BASE_URL, query_string="active={}".format(test_active))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(active_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["active"], test_active)

