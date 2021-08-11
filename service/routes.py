"""
My Service

Describe what your service does here
"""

import os

import sys
import logging

from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound, BadRequest

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Recommendation,Type
import service.error_handlers

# Import Flask application
from . import app

import sys
import uuid
import logging
from functools import wraps
from flask import jsonify, request, url_for, make_response, render_template
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models import Recommendation, DataValidationError
from . import app, status    # HTTP Status Codes

# Document the type of autorization required
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Api-Key'
    }
}
######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """ Helper function used when testing API keys """
    return uuid.uuid4().hex

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
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be {}".format(content_type))

def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file("index.html")

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Recommendation Demo REST API Service',
          description='This is a sample server Recommendation server.',
          default='recommendations',
          default_label='Recommendation operations',
          doc='/apidocs', # default also could use doc='/apidocs/'
          authorizations=authorizations,
          prefix='/api'
         )

# Define the model so that the docs reflect what can be sent
create_model = api.model('Recommendation', {
    'product_id': fields.Integer(required=True,
                          description='The id of the product'),
    'recommendation_product_id': fields.Integer(required=True,
                              description='The id of the recommended product'),
    'relationship': fields.String(required=True,
                                description='Relationship between two products')
})

recommendation_model = api.inherit(
    'RecommendationModel', 
    create_model,
    {
        'likes': fields.Integer(readOnly=True,
                            description='The like count by customers'),
    }
)


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
######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Recommendation.init_db(app)

@api.route("/recommendations/<int:product_id>/recommended-products/<int:recommendation_product_id>")
@api.param('product_id', 'The product identifier')
@api.param('recommendation_product_id', 'The recommendation product identifier')
class RecommendationResource(Resource):
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
        if not recommendation or not recommendation.relationship:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation for product id {} and {} was not found.".format(product_id, recommendation_product_id))
        return recommendation.serialize(), status.HTTP_200_OK

    ##############################################################
    # UPDATE A RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
    ######################################################################
    @api.doc('update_recommendations', security='apikey')
    @api.response(404, 'Recommendation not found')
    @api.response(400, 'The posted Recommendation data was not valid')
    @api.expect(create_model)
    @api.marshal_with(recommendation_model)
    def put(self, product_id, recommendation_product_id):
        """
        Update relationship between product id and recommended product id
        This endpoint will update a relationship based the data in the body that is posted
        """
        app.logger.info("Request to update a recommenation")
        check_content_type("application/json")
        supported_relationships = [t.name for t in Type]
        data = api.payload
        if 'relationship' not in data or data['relationship'] not in supported_relationships:
            message = "Bad relationship input. Supported relationships are {}".format(supported_relationships)
            abort(status.HTTP_400_BAD_REQUEST, message)

        recommendation = Recommendation.find(product_id, recommendation_product_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation for product id {} and {} was not found.".format(product_id, recommendation_product_id))
        
        recommendation.deserialize(data)

    
        recommendation.update()
        return recommendation.serialize(), status.HTTP_200_OK


    ##############################################################
    # DELETE A RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
    ######################################################################
    @api.doc('delete_recommendations', security='apikey')
    @api.response(204, 'Recommendation deleted')
    @api.response(400, 'Bad request')
    def delete(self, product_id, recommendation_product_id):
        """
        Delete a relationship
        This endpoint will delete a relationship based the product ids specified in the path
        """
        app.logger.info("Request to delete relationship between product ids: %s %s", product_id, recommendation_product_id)
        recommendation = Recommendation.find(product_id, recommendation_product_id)
        if recommendation:
            recommendation.delete()
        return '', status.HTTP_204_NO_CONTENT

@api.route('/recommendations/<int:product_id>', strict_slashes=False)
class RecommendationGroup(Resource):
    ######################################################################
    # QUERY RECOMMENDATIONS FOR ID AND TYPE
    ######################################################################
    @api.doc('query_recommendations')
    @api.marshal_list_with(recommendation_model)
    @api.response('400', 'Bad request')
    def get(self, product_id):
        """ Returns all of the Recommendations """
        type = request.args.get('type')
        
        app.logger.info("Request for recommendations query for id %s and type %s", product_id, type)
        recommendations = Recommendation.find_by_id_and_type(product_id, type)

        results = [recommendation.serialize() for recommendation in recommendations]
        return results, status.HTTP_200_OK

@api.route('/recommendations', strict_slashes=False)
class RecommendationCollection(Resource):

    ######################################################################
    # LIST RECOMMENDATIONS
    ######################################################################
    @api.doc('list_recommendations')
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """ Returns all of the Recommendations """
        app.logger.info("Request for recommendations list")

        recommendations = Recommendation.all()

        results = [recommendation.serialize() for recommendation in recommendations]
        return results, status.HTTP_200_OK


    ######################################################################
    # ADD A NEW RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
    ######################################################################
    @api.doc('create_recommendations', security='apikey')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """
        Creates a Recommendation between a product id and associated recommended product id. 
        Supported relationship  ['GO_TOGETHER', 'CROSS_SELL', 'UP_SELL', 'ACCESSORY']
        """
        app.logger.info("Request to create a Recommendation")
        check_content_type("application/json")
        recommendation = Recommendation()
        app.logger.info('Payload = %s', api.payload)
        recommendation.deserialize(api.payload)
        supported_relationships = [t.name for t in Type]
        if recommendation.relationship not in supported_relationships:
            message = "Bad relationship input. Supported relationships are {}".format(supported_relationships)
            abort(status.HTTP_400_BAD_REQUEST, message)
        app.logger.info('Payload = %s', api.payload)
        recommendation.create()
        location_url = api.url_for(RecommendationResource, product_id=recommendation.product_id, recommendation_product_id=recommendation.recommendation_product_id, _external=True)
        return recommendation.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

    #------------------------------------------------------------------
    # DELETE ALL RECOMMENDATIONS (for testing only)
    #------------------------------------------------------------------
    @api.doc('delete_all_recommendation', security='apikey')
    @api.response(204, 'All Recommendations deleted')
    @api.response(400, 'Bad request')
    def delete(self):
        """ Clear all of the Recommendations """
        app.logger.info("Request for clear all recommendations")
        Recommendation.clear()
        return '', status.HTTP_204_NO_CONTENT

@api.route("/recommendations/<int:product_id>/recommended-products/<int:recommendation_product_id>/like")
@api.param('product_id', 'The product identifier')
@api.param('recommendation_product_id', 'The recommended product identifier')
class LikeResource(Resource):

    ##############################################################
    # LIKE A RECOMMENDATION
    ######################################################################
    @api.doc('like_recommendations')
    @api.response(404, 'Recommendation not found')
    def put(self, product_id, recommendation_product_id):
        """
        Like a recommendation
        """
        app.logger.info("Request to like a recommendation between %s and %s", product_id, recommendation_product_id)
        
        recommendation = Recommendation.find(product_id, recommendation_product_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation for product id {} and {} was not found.".format(product_id, recommendation_product_id))
        
        recommendation.likes += 1
        recommendation.update()
        return recommendation.serialize(), status.HTTP_200_OK


