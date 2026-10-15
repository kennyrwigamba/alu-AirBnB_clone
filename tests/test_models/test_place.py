#!/usr/bin/python3
"""Validate the Place model and its inherited behavior."""

from models.place import Place
from tests.test_models import test_base_model


class TestPlace(test_base_model.TestBaseModel):
    """Check Place defaults and common model operations."""

    model_class = Place
    defaults = {
        'city_id': '',
        'user_id': '',
        'name': '',
        'description': '',
        'number_rooms': 0,
        'number_bathrooms': 0,
        'max_guest': 0,
        'price_by_night': 0,
        'latitude': 0.0,
        'longitude': 0.0,
        'amenity_ids': [],
    }

    def test_amenity_lists_are_independent(self):
        """Changing one place's amenities does not affect another place."""
        first, second = Place(), Place()
        first.amenity_ids.append("amenity-id")
        self.assertEqual(second.amenity_ids, [])
        self.assertEqual(Place.amenity_ids, [])
