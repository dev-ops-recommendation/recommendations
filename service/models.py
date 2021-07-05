"""
Models for YourResourceModel

All of the models are stored in this module
"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

class Type(Enum):
    """ Enumeration of valid Pet Genders """

    GO_TOGETHER = 0
    CROSS_SELL = 1
    UP_SELL = 2
    ACCESSORY = 3
    

class Recommendation(db.Model):
    """
    Class that represents a relationship/recommendation
    """

    app = None

    # Table Schema
    product_id1 = db.Column(db.Integer, primary_key=True)
    product_id2 = db.Column(db.Integer, primary_key=True)
    relationship = db.Column(
        db.Enum(Type), nullable=False, server_default=(Type.GO_TOGETHER.name)
        )
    def __repr__(self):
        return "<Recommendation %r product_id1=[%s] product_id2=[%s]>" % (self.relationship, self.product_id1, self.product_id2)

    def create(self):
        """
        Creates a recommendation type to the database
        """
        logger.info("Creating %s between %s and %s", self.relationship, self.product_id1, self.product_id2)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Removes a recommendation type from the database
        """
        logger.info("Deleting %s between %s and %s", self.relationship, self.product_id1, self.product_id2)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a YourResourceModel into a dictionary """
        return {"product_id1": self.product_id1, "product_id2": self.product_id2, "relationship": self.relationship.name}

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id1 = data["product_id1"]
            self.product_id2 = data["product_id2"]
            self.relationship = data["relationship"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def find(cls, product_id1, product_id2):
        """ Finds relationship between two product ids """
        logger.info("Processing lookup for id %s %s", product_id1, product_id2)
        return cls.query.get((product_id1, product_id2))
        