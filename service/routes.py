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
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Recommendations REST API Service",
            version="1.0",
            paths=url_for("list_recommendations", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Recommendation.init_db(app)


######################################################################
# LIST RECOMMENDATIONS
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """ Returns all of the Recommendations """
    app.logger.info("Request for recommendations list")
    recommendations = Recommendation.all()

    results = [recommendation.serialize() for recommendation in recommendations]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# ADD A NEW RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
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
# GET A RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
######################################################################
@app.route("/recommendations/<int:product_id>/recommended-products/<int:recommendation_product_id>", methods=["GET"])
def get_recommendations(product_id, recommendation_product_id):
    """
    Retrieve recommendations for (product_id, recommendation_product_id)

    This endpoint will return a relationship between two product ids. 
    """
    app.logger.info("Request for relationship between product ids: %s %s", product_id, recommendation_product_id)
    recommendation = Recommendation.find(product_id, recommendation_product_id)
    if not recommendation:
        raise NotFound("Recommendation for product id {} and {} was not found.".format(product_id, recommendation_product_id))
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)

##############################################################
# UPDATE A RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
######################################################################
@app.route("/recommendations/<int:product_id>/recommended-products/<int:recommendation_product_id>", methods=["PUT"])
def update_recommendations(product_id, recommendation_product_id):
    """
    update a relationship
    This endpoint will update a relationship based the data in the body that is posted
    """
    app.logger.info("Request to update a ")
    check_content_type("application/json")
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    old_recommendation = recommendation.find(product_id, recommendation_product_id)
    if not old_recommendation:
        raise NotFound("Recommendation for product id {} and {} was not found.".format(product_id, recommendation_product_id))
    old_recommendation.relationship = recommendation.relationship
    recommendation.update()
    message = old_recommendation.serialize()
    return make_response(
        jsonify(message), status.HTTP_200_OK
    )


##############################################################
# LIKE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:product_id>/recommended-products/<int:recommendation_product_id>/like", methods=["PUT"])
def like_recommendations(product_id, recommendation_product_id):
    """
    like a relationship
    """
    app.logger.info("Request to like a recommendation between %s and %s", product_id, recommendation_product_id)
    check_content_type("application/json")
    
    old_recommendation = Recommendation.find(product_id, recommendation_product_id)
    if not old_recommendation:
        raise NotFound("Recommendation for product id {} and {} was not found.".format(product_id, recommendation_product_id))
    recommendation = old_recommendation
    recommendation.likes += 1
    recommendation.update()
    message = recommendation.serialize()
    return make_response(
        jsonify(message), status.HTTP_200_OK
    )

##############################################################
# DELETE A RECOMMENDATION (RELATIONSHIP BETWEEN PRODUCTS)
######################################################################
@app.route("/recommendations/<int:product_id>/recommended-products/<int:recommendation_product_id>", methods=["DELETE"])
def delete_recommendations(product_id, recommendation_product_id):
    """
    Delete a relationship
    This endpoint will delete a relationship based the product ids specified in the path
    """
    app.logger.info("Request to delete relationship between product ids: %s %s", product_id, recommendation_product_id)
    recommendation = Recommendation.find(product_id, recommendation_product_id)
    if recommendation:
        recommendation.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be {}".format(content_type))

######################################################################
# QUERY RECOMMENDATIONS FOR ID AND TYPE
######################################################################
@app.route("/recommendations/<int:product_id>", methods=["GET"])
def query_recommendations(product_id):
    """ Returns all of the Recommendations """
    type = request.args.get('type')
    app.logger.info("Request for recommendations query for id %s and type %s", product_id, type)
    recommendations = Recommendation.find_by_id_and_type(product_id, type)

    results = [recommendation.serialize() for recommendation in recommendations]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# CLEAR ALL RECOMMENDATIONS 
######################################################################
@app.route("/recommendations", methods=["DELETE"])
def clear_recommendations():
    """ Clear all of the Recommendations """
    app.logger.info("Request for clear all recommendations")
    Recommendation.clear()
    return make_response("", status.HTTP_204_NO_CONTENT)

