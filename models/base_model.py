#!/usr/bin/python3
"""Base model shared by all application entities."""

from datetime import datetime
from uuid import uuid4


class BaseModel:
    """Provide identity, timestamps, and serialization for a model."""

    def __init__(self, *args, **kwargs):
        """Create a model from keyword data or default values."""
        if kwargs:
            for key, value in kwargs.items():
                if key == "created_at" or key == "updated_at":
                    value = datetime.fromisoformat(value)
                if key != "__class__":
                    setattr(self, key, value)
            return

        self.id = str(uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        from models import storage

        storage.new(self)

    def __str__(self):
        """Return a readable representation of the model."""
        return "[{}] ({}) {}".format(
            self.__class__.__name__, self.id, self.__dict__
        )

    def save(self):
        """Update the modification timestamp and persist the model."""
        self.updated_at = datetime.now()
        from models import storage

        storage.save()

    def to_dict(self):
        """Return a JSON-serializable dictionary representation."""
        result = self.__dict__.copy()
        result["__class__"] = self.__class__.__name__
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        return result
