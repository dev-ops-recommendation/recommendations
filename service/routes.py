"""
My Service

Describe what your service does here
"""

import os
import uuid
from functools import wraps
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound, BadRequest

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Recommendation,Type, DataValidationError, DatabaseConnectionError
from flask_restx import Api, Resource, fields, reqparse
import service.error_handlers

# Import Flask application
from . import app

"""
Recommendations Service

Paths:
------
GET /recommendations - Returns a list all of the Recommendations
GET /recommendations/{id}/recommended-products/{id} - Returns the Recommendation with a given id number and related product id
GET /recommendations/{id}?type={relationship-type}
POST /recommendations - creates a new Recommendation record in the database
PUT /recommendations/{id}/recommended-products/{id} - updates a Recommendation record in the database
DELETE /recommendations/{id}/recommended-products/{id} - deletes a Recommendation record in the database
DELETE /recommendations - deletes all Recommendation record in the database
"""

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Recommendation REST API Service',
          description='This is a recommendation server.',
          default='recommendation',
          default_label='Recommendation operations',
          doc='/apidocs',
          prefix='/api'
          )

# Define the model so that the docs reflect what can be sent
create_model = api.model('Recommendation', {
    'product_id': fields.Integer(required=True,
                          description='The id of a Product'),
    'recommendation_product_id': fields.Integer(required=True,
                              description='The id of the recommended product based on previous one'),
    'relationship': fields.Integer(required=True,
                                 description='The recommendation type')
})

recommendation_model = api.model('Recommendation', {
    'product_id': fields.Integer(required=True,
                          description='The id of a Product'),
    'recommendation_product_id': fields.Integer(required=True,
                              description='The id of the recommended product based on previous one'),
    'relationship': fields.Integer(required=True,
                                 description='The recommendation type'),
    'like': fields.Integer(required=True,
                          description='Like a recommendation')
})

# query string arguments
recommendations_args = reqparse.RequestParser()
recommendations_args.add_argument('product_id', type=int, required=False, help='List recommendation by product_id')
recommendations_args.add_argument('recommendation_product_id', type=int, required=False, help='List recommendation by recommendation_product_id')
recommendations_args.add_argument('relationship', type=Type, required=False, help='List recommendation by relationship')


######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST

@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = str(error)
    app.logger.critical(message)
    return {
        'status_code': status.HTTP_503_SERVICE_UNAVAILABLE,
        'error': 'Service Unavailable',
        'message': message
    }, status.HTTP_503_SERVICE_UNAVAILABLE


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file("index.html")

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Recommendation.init_db(app)


######################################################################
#  PATH: /recommendations/{product_id}/recommended-products/{recommendation_product_id}
######################################################################
@api.route('/recommendations/<product_id>/recommended-products/<recommendation_product_id>')
@api.param('product_id', 'The Product identifier')
@api.param('recommendation_product_id', 'The recommended Product identifier')
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single recommendation
    GET /recommendations{product_id}/recommended-products{recommendation_product_id} - Returns a recommendation relationship with two ids
    PUT /recommendations{product_id}/recommended-products{recommendation_product_id} - Update a recommendation relationship with two ids
    DELETE /recommendations{product_id}/recommended-products{recommendation_product_id} -  Deletes a recommendation with two ids
    """

    ######################################################################
    # GET A RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
    ######################################################################
    @api.doc('get_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.marshal_with(recommendation_model)
    def get(self, product_id, recommendation_product_id):
        """
        Retrieve recommendations for (product_id, recommendation_product_id)

        This endpoint will return a relationship between two product ids.
        """
        app.logger.info("Request for relationship between product ids: %s %s", product_id, recommendation_product_id)
        recommendation = Recommendation.find(product_id, recommendation_product_id)
        if not recommendation:
            raise NotFound(
                "Recommendation for product id {} and {} was not found.".format(product_id, recommendation_product_id))
        return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)

    ##############################################################
    # UPDATE A RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
    ######################################################################
    @api.doc('update_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model)
    def put(self, product_id, recommendation_product_id):
        """
        update a relationship
        This endpoint will update a relationship based the data in the body that is posted
        """
        app.logger.info("Request to update a ")
        check_content_type("application/json")
        recommendation = Recommendation()
        recommendation.deserialize(request.get_json())
        old_recommendation = recommendation.find( product_id, recommendation_product_id)
        if not old_recommendation:
            raise NotFound(
                "Recommendation for product id {} and {} was not found.".format(product_id, recommendation_product_id))
        old_recommendation.relationship = recommendation.relationship
        recommendation.update()
        message = old_recommendation.serialize()
        return make_response(
            jsonify(message), status.HTTP_200_OK
        )

    ##############################################################
    # DELETE A RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
    ######################################################################
    @api.doc('delete_ recommendation')
    @api.response(204, ' recommendation deleted')
    def delete(self, product_id, recommendation_product_id):
        """
        Delete a relationship
        This endpoint will delete a relationship based the product ids specified in the path
        """
        app.logger.info("Request to delete relationship between product ids: %s %s", product_id,
                        recommendation_product_id)
        recommendation = Recommendation.find(product_id, recommendation_product_id)
        if recommendation:
            recommendation.delete()
        return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
#  PATH: /recommendations
######################################################################
@api.route('/recommendations', strict_slashes=False)
class RecommendationCollection(Resource):
    """ Handles all interactions with collections of recommendations """

    ######################################################################
    # LIST RECOMMENDATIONS
    ######################################################################
    @api.doc('list_recommendations')
    @api.expect(recommendations_args, validate=True)
    @api.response(200, 'Recommendation are listed')
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """ Returns all of the Recommendations """
        app.logger.info("Request for recommendations list")
        recommendations = Recommendation.all()

        results = [recommendation.serialize() for recommendation in recommendations]
        return make_response(jsonify(results), status.HTTP_200_OK)


    ######################################################################
    # ADD A NEW RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
    ######################################################################
    @api.doc('create_recommendations')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'recommendations created successfully')
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """
        Creates a relationship
        This endpoint will create a relationship based the data in the body that is posted
        """
        app.logger.info("Request to create a ")
        check_content_type("application/json")
        recommendation = Recommendation()
        recommendation.deserialize(request.get_json())
        try:
            recommendation.create()
        except:
            raise BadRequest("Cannot create relationship between product {} and {}".format(recommendation.product_id, recommendation.recommendation_product_id))

        message = recommendation.serialize()
        location_url = url_for("get_recommendations", product_id=recommendation.product_id, recommendation_product_id=recommendation.recommendation_product_id, _external=True)
        return make_response(
            jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
        )

    ######################################################################
    # CLEAR ALL RECOMMENDATIONS
    ######################################################################
    @api.doc('delete_all_recommendation', security='apikey')
    @api.response(204, 'All recommendation deleted')
    def delete(self):
        """ Clear all of the Recommendations """
        app.logger.info("Request for clear all recommendations")
        Recommendation.clear()
        return make_response("", status.HTTP_204_NO_CONTENT)


##############################################################
# LIKE A RECOMMENDATION
#  PATH: /recommendations/<product_id>/recommended-products/<recommendation_product_id>/like
######################################################################
@api.route('/recommendations/<product_id>/recommended-products/<recommendation_product_id>/like', strict_slashes=False)
@api.param('product_id', 'The Product identifier')
@api.param('recommendation_product_id', 'The recommended Product identifier')
class LikeResource(Resource):
    """ Like actions on a recommendation """
    @api.doc('Like_pets')
    @api.expect(recommendation_model)
    @api.response(404, 'Recommendation not found')
    @api.response(200, 'The recommendation is liked')
    @api.marshal_list_with(recommendation_model)
    def like_recommendations(self, product_id, recommendation_product_id):
        """
        like a relationship
        """
        app.logger.info("Request to like a recommendation between %s and %s", product_id, recommendation_product_id)
        recommendation = Recommendation.find(product_id, recommendation_product_id)
        if not recommendation:
            raise NotFound(
                "Recommendation for product id {} and {} was not found.".format(product_id, recommendation_product_id))

        recommendation.likes += 1
        recommendation.update()
        message = recommendation.serialize()
        return make_response(
            jsonify(message), status.HTTP_200_OK
        )


##############################################################
# QUERY RECOMMENDATIONS FOR ID AND TYPE
#  PATH: /recommendations/<product_id>/recommended-products/<recommendation_product_id>/like
######################################################################
@api.route('/recommendations/<product_id>', strict_slashes=False)
@api.param('product_id', 'The Product identifier')
class QueryResource(Resource):
    @api.doc('query_all_recommendations_by_ID_Type')
    @api.response(200, 'Get all recommendation of the product')
    def query_recommendation(self,product_id):
        """ Returns all of the Recommendations """
        type = request.args.get('type')
        app.logger.info("Request for recommendations query for id %s and type %s", product_id, type)
        recommendations = Recommendation.find_by_id_and_type(product_id, type)
        results = [recommendation.serialize() for recommendation in recommendations]
        return make_response(jsonify(results), status.HTTP_200_OK)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be {}".format(content_type))





