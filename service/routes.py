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
from service.models import Recommendation, Type
import service.error_handlers

# Import Flask application
from . import app

"""
Recommendations Service

Paths:
------
GET /recommendations - Returns a list all of the Recommendations
POST /recommendations - creates a new Recommendation record in the database
DELETE /recommendations - deletes all Recommendation record in the database

GET /recommendations/{id}/recommended-products/{id} - Returns the Recommendation with a given id number and related product id
GET /recommendations/{id}?type={relationship-type}
PUT /recommendations/{id}/recommended-products/{id} - updates a Recommendation record in the database
DELETE /recommendations/{id}/recommended-products/{id} - deletes a Recommendation record in the database

"""

# Document the type of autorization required
# authorizations = {
#     'apikey': {
#         'type': 'apiKey',
#         'in': 'header',
#         'name': 'X-Api-Key'
#     }
# }

######################################################################
# Configure the Root route before OpenAPI
######################################################################


@app.route('/')
def index():
    """ Index page """
    return app.send_static_file('index.html')


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
    version='1.0.0',
    title='Recommendations REST API Service',
    description='This is a recommendations server.',
    default='recommendations',
    default_label='recommendation operations',
    doc='/apidocs',  # default also could use doc='/apidocs/'
    prefix='/api'
    )

# Define the model so that the docs reflect what can be sent
recommendation_model = api.model('Recommendation',{

    'product_id': fields.Integer(required=True readOnly=True,
                    description='The product ID'),
    'recommendation_product_id': fields.Integer(readOnly=True,
                    description='The recommendation ID'),
    'relationship': fields.Integer(required=False,
                    description='Relationship between the product and the recommendation'),
    'likes': fields.Integer(required=False,
                    description='Likes on recommendations'),

})

# query string arguments
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument('product_id', type=int, required=False,
        location='args', help='List Recommendations by Product ID')
recommendation_args.add_argument('recommendation_product_id', type=int, required=False,
        location='args', help='List Recommendations by Recommendation ID')
Recommendation_args.add_argument('relationship', type=int, required=False,
        location='args', help='List Recommendations by Recommendation ID')
recommendation_args.add_argument(
    'likes', type=int, required=False, location='args', help='List Recommendations by likes')

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
# Authorization Decorator
######################################################################
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if 'X-Api-Key' in request.headers:
#             token = request.headers['X-Api-Key']
#
#         if app.config.get('API_KEY') and app.config['API_KEY'] == token:
#             return f(*args, **kwargs)
#         else:
#             return {'message': 'Invalid or missing token'}, 401
#     return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
# def generate_apikey():
#     """ Helper function used when testing API keys """
#     return uuid.uuid4().hex

######################################################################
#  PATH: /recommendations
######################################################################
@api.route('/recommendations', strict_slashes=False)
class RecommendationCollection(Resource):
    """ Handles all interactions with collections of Recommendations """
    #------------------------------------------------------------------
    # LIST ALL RECOMMENDATIONS
    #------------------------------------------------------------------
    @api.doc('list_recommendations')
    @api.expect(recommendation_args, validate=True)
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """ Returns all of the Recommendations"""
        app.logger.info('Request to list Recommendations...')
        recommendations = []
        args = recommendation_args.parse_args()
        app.logger.info('Returning Recommendations list.')
        recommendations = Recommendation.all()

        app.logger.info('[%s] Recommendations returned', len(recommendations))
        results = [recommendation.serialize()
                                            for recommendation in recommendations]
        return results, status.HTTP_200_OK

    #------------------------------------------------------------------
    # ADD A NEW RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('create_recommendations')
    @api.response(400, 'The posted data was not valid')
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model, code=201)
    # @token_required
    def post(self):
        """
        Creates a Recommendation
        This endpoint will create a Recommendation based the data in the body that is posted
        """
        app.logger.info('Request to Create a Recommendation')
        recommendation = Recommendation()
        app.logger.debug('Payload = %s', api.payload)
        recommendation.deserialize(api.payload)
        recommendation.create()
        if not recommendation.create:
            abort(status.HTTP_404_NOT_FOUND, 'Cannot create relationship between product {} and {}'.format(
                recommendation.product_id, recommendation.recommendation_product_id))
        app.logger.info(
            'Recommendation with new id [%s] created!', recommendation.id)

        location_url = url_for("get_recommendations", product_id=recommendation.product_id,recommendation_product_id=recommendation.recommendation_product_id, _external=True)
        return recommendation.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

    #------------------------------------------------------------------
    # DELETE/CLEAR ALL RECOMMENDATIONS (for testing only)
    #------------------------------------------------------------------
    @api.doc('delete_all_recommendations')
    @api.response(204, 'All Recommendations deleted')
    # @token_required
    def delete(self):
        """
        Delete all Recommendation

        This endpoint will delete all Recommendations only if the system is under test
        """
        app.logger.info('Request to Delete all recommendations...')
        if "TESTING" in app.config and app.config["TESTING"]:
            Recommendation.remove_all()
            app.logger.info("Removed all Recommendations from the database")
        else:
            app.logger.warning(
                "Request to clear database while system not under test")

        return '', status.HTTP_204_NO_CONTENT

###########################################################################################
#  PATH: /recommendations/{product_id}/recommendation-products/{recommendation_product_id}
############################################################################################

@api.route('/recommendations/<product_id>/recommendation-product/<recommendation_product_id')
@api.param('product_id', 'The product identifier', 'recommendation_product_id', 'The recommendation identifier')
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single Recommendation
    GET /recommendations/{id}/recommended-products/{id} - Returns the Recommendation with a given id number and related product id
    GET /recommendations/{id}?type={relationship-type}
    DELETE /recommendations/{id}/recommended-products/{id} - deletes a Recommendation record in the database
    """

    #------------------------------------------------------------------
    # RETRIEVE A RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('get_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.marshal_with(recommendation_model)
    def get(self, product_id, recommendation_product_id):
        """
        Retrieve a single Recommendation

        This endpoint will return a Recommendation based on it's product id and recommendation product id
        """
        app.logger.info("Request for relationship between product ids: %s %s",
                        product_id, recommendation_product_id)
        recommendation = Recommendation.find(
            product_id, recommendation_product_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation for product id {} and {} was not found.".format(
                product_id, recommendation_product_id))
        return recommendation.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('update_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.response(400, 'The posted Recommendation data was not valid')
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model)
    def put(self, product_id, recommendation_product_id):
        """
        Update a Recommendation

        This endpoint will update a relationship based the data in the body that is posted
        """
        app.logger.info("Request to Update a Recommendation for product id {} and {}", product_id, recommendation_product_id)
        check_content_type("application/json")
        recommendation = Recommendation()
        old_recommendation = recommendation.find(
            product_id, recommendation_product_id)
        if not old_recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation for product id {} and {} was not found.".format(
                product_id, recommendation_product_id))
        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        recommendation.deserialize(data)
        old_recommendation.relationship = recommendation.relationship
        recommendation.update()
        return old_recommendation.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('delete_recommendations')
    @api.response(204, 'Recommendation deleted')
    def delete(self, product_id, recommendation_product_id):
        """
        Delete a relationship
        This endpoint will delete a relationship based the product ids specified in the path
        """
        app.logger.info("Request to delete relationship between product ids: %s %s",
                        product_id, recommendation_product_id)
        recommendation = Recommendation.find(
            product_id, recommendation_product_id)
        if recommendation:
            recommendation.delete()
            app.logger.info('Recommendation with id [%s] was deleted'.format(
                product_id, recommendation_product_id))
        return '', status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /recommendations/{product_id}?type={relationship-type}
######################################################################
@api.route('/recommendations/<product_id>')
@api.param('product_id', 'The product identifier')
class RecommendationResource(Resource):
    """
    RecommendationResource class
    """
    #------------------------------------------------------------------
    # RETRIEVE A RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('get_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.marshal_with(recommendation_model)
    def get(self, product_id):

        """ Returns all of the Recommendations """
        type = request.args.get('type')
        app.logger.info("Request for recommendations query for id %s and type %s", product_id, type)
        recommendations = Recommendation.find_by_id_and_type(product_id, type)

        if not recommendations:
            abort(status.HTTP_404_NOT_FOUND,
            "Request for recommendations query for id %s and type %s".format(product_id, type))
        return recommendations.serialize(), status.HTTP_200_OK

###############################################################################################################
#  PATH: /recommendations/{product_id}/recommendation-products/{recommendation_product_id}/like
###############################################################################################################
@api.route('/recommendations/<product_id>/recommendation-products/<recommendation_product_id>')
@api.param('product_id', 'The Recommendation identifier', 'recommendation_product_id', 'The Recommendation identifier')
class RecommendationResource(Resource):
    #------------------------------------------------------------------
    # LIKE A RECOMMENDATION
    #------------------------------------------------------------------

    """ Like a Recommendation """
    @api.doc('likes_recommendations')
    @api.response(404, 'Likes not found')
    def put(product_id, recommendation_product_id):
        """
        like a relationship

        """
        app.logger.info("Request to like a recommendation between %s and %s",
                        product_id, recommendation_product_id)
        recommendation=Recommendation.find(product_id, recommendation_product_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation for product id {} and {} was not found.".format(product_id, recommendation_product_id))
        recommendation.likes += 1
        recommendation.update()
        return recommendation.serialize(), status.HTTP_200_OK

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)

@ app.before_first_request
def init_db(dbname = "pets"):
    """ Initlaize the model """
    Pet.init_db(dbname)

# load sample data
def data_load(payload):
    """ Loads a Pet into the database """
    pet=Pet(payload['name'], payload['category'], payload['available'])
    pet.create()

def data_reset():
    """ Removes all Pets from the database """
    Pet.remove_all()

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error(
        "Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,"Content-Type must be {}".format(content_type))
