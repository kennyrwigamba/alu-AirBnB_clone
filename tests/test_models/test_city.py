#!/usr/bin/python3
"""Validate the City model and its inherited behavior."""

from models.city import City
from tests.test_models import test_base_model


class TestCity(test_base_model.TestBaseModel):
    """Check City defaults and common model operations."""

    model_class = City
    defaults = {
        'state_id': '',
        'name': '',
    }
