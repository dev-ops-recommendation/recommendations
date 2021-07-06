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
    location_url = url_for("get_recommendations", product_id1=recommendation.product_id1, product_id2=recommendation.product_id2, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )
##############################################################
@app.route("/recommendations/products/<int:product_id1>/related-products/<int:product_id2>", methods=["GET"])
def get_recommendations(product_id1, product_id2):
    """
    Retrieve recommendations for (product_id1, product_id2)

    This endpoint will return a relationship between two product ids. 
    """
    app.logger.info("Request for relationship between product ids: %s %s", product_id1, product_id2)
    recommendation = Recommendation.find(product_id1, product_id2)
    if not recommendation:
        raise NotFound("Recommendation for product id {} and {} was not found.".format(product_id1, product_id2))
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)

@app.route("/recommendations/products/<int:product_id1>/related-products/<int:product_id2>", methods=["PUT"])
def update_recommendations(product_id1, product_id2):
    """
    update a relationship
    This endpoint will update a relationship based the data in the body that is posted
    """
    app.logger.info("Request to update a ")
    check_content_type("application/json")
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    old_recommendation = recommendation.find(product_id1, product_id2)
    if not old_recommendation:
        raise BadRequest("No existing relationship between product {} and {}".format(product_id1, product_id2))
    if recommendation.relationship == "GO_TOGETHER":
        old_recommendation.relationship = Type.GO_TOGETHER
    elif recommendation.relationship == "CROSS_SELL":
        old_recommendation.relationship = Type.CROSS_SELL
    elif recommendation.relationship == "UP_SELL":
        old_recommendation.relationship = Type.UP_SELL
    elif recommendation.relationship == "ACCESSORY":
        old_recommendation.relationship = Type.ACCESSORY
    recommendation.update()
    message = old_recommendation.serialize()
    return make_response(
        jsonify(message), status.HTTP_200_OK
    )

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be {}".format(content_type))
