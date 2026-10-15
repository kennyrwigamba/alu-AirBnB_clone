#!/usr/bin/python3
"""Validate the Review model and its inherited behavior."""

from models.review import Review
from tests.test_models import test_base_model


class TestReview(test_base_model.TestBaseModel):
    """Check Review defaults and common model operations."""

    model_class = Review
    defaults = {
        'place_id': '',
        'user_id': '',
        'text': '',
    }
