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
    

class Relationship(db.Model):
    """
    Class that represents a <your resource model name>
    """

    app = None

    # Table Schema
    product_id1 = db.Column(db.Integer, primary_key=True)
    product_id2 = db.Column(db.Integer, primary_key=True)
    relationship = db.Enum(Type), nullable=False, server_default=(Type.GO_TOGETHER.name)
    def __repr__(self):
        return "<Recommendation %r product_id1=[%s] product_id2=[%s]>" % (self.relationship, self.product_id1, self.product_id2)

    def create(self):
        """
        Creates a YourResourceModel to the database
        """
        logger.info("Creating %s between %s and %s", self.relationship, self.product_id1, self.product_id2)
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a YourResourceModel to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a YourResourceModel from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a YourResourceModel into a dictionary """
        return {"product_id1": self.product_id1, "product_id2": self.product_id2, "relationship": self.relationship}

    def deserialize(self, data):
        """
        Deserializes a Relationship from a dictionary

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
    def all(cls):
        """ Returns all of the YourResourceModels in the database """
        logger.info("Processing all YourResourceModels")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a YourResourceModel by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a YourResourceModel by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all YourResourceModels with the given name

        Args:
            name (string): the name of the YourResourceModels you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
