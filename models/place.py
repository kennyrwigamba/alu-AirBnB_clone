#!/usr/bin/python3
"""Place model."""

from models.base_model import BaseModel


class Place(BaseModel):
    """Represent a property listed for booking."""

    city_id = ""
    user_id = ""
    name = ""
    description = ""
    number_rooms = 0
    number_bathrooms = 0
    max_guest = 0
    price_by_night = 0
    latitude = 0.0
    longitude = 0.0
    amenity_ids = []

    def __init__(self, *args, **kwargs):
        """Initialize a place with its listing information."""
        super().__init__(*args, **kwargs)
        self.city_id = getattr(self, "city_id", "")
        self.user_id = getattr(self, "user_id", "")
        self.name = getattr(self, "name", "")
        self.description = getattr(self, "description", "")
        self.number_rooms = getattr(self, "number_rooms", 0)
        self.number_bathrooms = getattr(self, "number_bathrooms", 0)
        self.max_guest = getattr(self, "max_guest", 0)
        self.price_by_night = getattr(self, "price_by_night", 0)
        self.latitude = getattr(self, "latitude", 0.0)
        self.longitude = getattr(self, "longitude", 0.0)
        self.amenity_ids = list(getattr(self, "amenity_ids", []))
