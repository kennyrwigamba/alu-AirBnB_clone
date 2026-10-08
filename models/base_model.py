#!/usr/bin/python3
"""Define the shared attributes and methods for application models."""

from datetime import datetime
import uuid


class BaseModel:
    """Represent a model with a unique ID and creation/update timestamps."""

    def __init__(self, *args, **kwargs):
        """Create a new model or restore attributes from a dictionary."""
        if kwargs:
            for key, value in kwargs.items():
                if key == "__class__":
                    continue
                if key in ("created_at", "updated_at"):
                    value = datetime.fromisoformat(value)
                setattr(self, key, value)
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()

    def __str__(self):
        """Return the model's class name, ID, and instance attributes."""
        return "[{}] ({}) {}".format(
            self.__class__.__name__, self.id, self.__dict__)

    def save(self):
        """Update the timestamp of the model's most recent change."""
        self.updated_at = datetime.now()

    def to_dict(self):
        """Return instance attributes with a class name and ISO timestamps."""
        model_dict = self.__dict__.copy()
        model_dict["__class__"] = self.__class__.__name__
        model_dict["created_at"] = self.created_at.isoformat()
        model_dict["updated_at"] = self.updated_at.isoformat()
        return model_dict
