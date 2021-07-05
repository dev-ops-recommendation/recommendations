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
from service.models import Recommendation

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
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
    recommendations = []
    recommendation_type = request.args.get("recommendation_type")
    active = request.args.get("active")
    if recommendation_type:
        recommendations = Recommendation.find_by_recommendation_type(recommendation_type)
    elif active:
        recommendations = Recommendation.find_by_active(active)
    else:
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
        raise BadRequest("Cannot create relationship between product {} and {}".format(recommendation.product_id1, recommendation.product_id2))

    message = recommendation.serialize()
    return make_response(
        jsonify(message), status.HTTP_201_CREATED
    )

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be {}".format(content_type))
