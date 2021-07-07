"""
Models for Recommendations

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
    
### -----------------------------------------------------------
### CLASS RECOMMENDATION
### -----------------------------------------------------------
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
    ### -----------------------------------------------------------
    ### INSTANCE METHODS
    ### -----------------------------------------------------------
    def __repr__(self):
        return "<Recommendation %r product_id1=[%s] product_id2=[%s]>" % (self.relationship, self.product_id1, self.product_id2)

    def create(self):
        """
        Creates a recommendation type to the database
        """
        logger.info("Creating %s between %s and %s", self.relationship, self.product_id1, self.product_id2)
        db.session.add(self)
        db.session.commit()


    def update(self):
        """
        update a recommendation type to the database
        """
        if not self.relationship:
            raise DataValidationError("Update called with empty relationship")
        logger.info("updating relationship between %s and %s", self.product_id1, self.product_id2)
        db.session.commit()

    def delete(self):
        """
        Removes a recommendation type from the database
        """
        logger.info("Deleting %s between %s and %s", self.relationship, self.product_id1, self.product_id2)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
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
                "Invalid Recommendation Model: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation Model: body of request contained bad or no data"
            )
        return self
    
    ### -----------------------------------------------------------
    ### CLASS METHODS
    ### -----------------------------------------------------------

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

    @classmethod
    def all(cls):
        """Returns all of the Pets in the database"""
        logger.info("Processing all recommendation")
        return cls.query.all()

    @classmethod
    def find_by_id_and_type(cls, product_id, type):
        """Returns all Recommendations with the given product id and type"""
        logger.info("Processing id and type query for id %s and type %s", product_id, type)
        return cls.query.filter(cls.product_id1 == product_id).filter(cls.relationship == type)

