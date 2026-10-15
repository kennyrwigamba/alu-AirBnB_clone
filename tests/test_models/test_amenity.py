#!/usr/bin/python3
"""Validate the Amenity model and its inherited behavior."""

from models.amenity import Amenity
from tests.test_models import test_base_model


class TestAmenity(test_base_model.TestBaseModel):
    """Check Amenity defaults and common model operations."""

    model_class = Amenity
    defaults = {
        'name': '',
    }
