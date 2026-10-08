#!/usr/bin/python3
"""Test the shared attributes and methods of BaseModel."""

from datetime import datetime
import unittest
import uuid

from models.base_model import BaseModel


class TestBaseModel(unittest.TestCase):
    """Check model creation, display, saving, and dictionary conversion."""

    def test_id_is_uuid_string(self):
        """A new model receives a valid UUID version 4 as a string."""
        model = BaseModel()
        self.assertIsInstance(model.id, str)
        self.assertEqual(uuid.UUID(model.id).version, 4)
        self.assertEqual(str(uuid.UUID(model.id)), model.id)

    def test_ids_are_unique(self):
        """Separate model instances receive different identifiers."""
        first_model = BaseModel()
        second_model = BaseModel()
        self.assertNotEqual(first_model.id, second_model.id)

    def test_timestamps_are_current_datetimes(self):
        """Creation assigns both timestamps within the creation interval."""
        before = datetime.now()
        model = BaseModel()
        after = datetime.now()
        self.assertIsInstance(model.created_at, datetime)
        self.assertIsInstance(model.updated_at, datetime)
        self.assertLessEqual(before, model.created_at)
        self.assertLessEqual(model.created_at, model.updated_at)
        self.assertLessEqual(model.updated_at, after)

    def test_string_representation(self):
        """The displayed model includes its class, ID, and attributes."""
        model = BaseModel()
        model.name = "My First Model"
        expected = "[BaseModel] ({}) {}".format(model.id, model.__dict__)
        self.assertEqual(str(model), expected)

    def test_save_updates_only_updated_at(self):
        """Saving refreshes updated_at and preserves other attributes."""
        model = BaseModel()
        model.name = "My First Model"
        model.updated_at = datetime(2000, 1, 1)
        original_attributes = model.__dict__.copy()
        before = datetime.now()
        model.save()
        after = datetime.now()
        self.assertLessEqual(before, model.updated_at)
        self.assertLessEqual(model.updated_at, after)
        self.assertNotEqual(
            model.updated_at, original_attributes["updated_at"])
        for attribute in original_attributes:
            if attribute != "updated_at":
                self.assertEqual(
                    getattr(model, attribute), original_attributes[attribute])

    def test_to_dict_includes_instance_attributes_and_class(self):
        """The dictionary includes custom attributes and the class name."""
        model = BaseModel()
        model.name = "My First Model"
        model.my_number = 89
        model_dict = model.to_dict()
        self.assertIsInstance(model_dict, dict)
        self.assertEqual(model_dict["id"], model.id)
        self.assertEqual(model_dict["name"], "My First Model")
        self.assertEqual(model_dict["my_number"], 89)
        self.assertEqual(model_dict["__class__"], "BaseModel")
        self.assertEqual(
            set(model_dict), set(model.__dict__) | {"__class__"})

    def test_to_dict_converts_timestamps_to_iso_strings(self):
        """Both timestamps are serialized using ISO datetime formatting."""
        model = BaseModel()
        model.created_at = datetime(2026, 1, 2, 3, 4, 5, 123456)
        model.updated_at = datetime(2026, 1, 2, 6, 7, 8, 654321)
        model_dict = model.to_dict()
        self.assertEqual(
            model_dict["created_at"], "2026-01-02T03:04:05.123456")
        self.assertEqual(
            model_dict["updated_at"], "2026-01-02T06:07:08.654321")

    def test_to_dict_does_not_change_instance(self):
        """Dictionary conversion leaves the instance attributes intact."""
        model = BaseModel()
        original_attributes = model.__dict__.copy()
        model.to_dict()
        self.assertEqual(model.__dict__, original_attributes)
        self.assertIsInstance(model.created_at, datetime)
        self.assertIsInstance(model.updated_at, datetime)
        self.assertNotIn("__class__", model.__dict__)

    def test_to_dict_returns_a_separate_dictionary(self):
        """Changing a returned dictionary does not replace model values."""
        model = BaseModel()
        model.name = "Original name"
        model_dict = model.to_dict()
        model_dict["name"] = "Changed name"
        self.assertIsNot(model_dict, model.__dict__)
        self.assertEqual(model.name, "Original name")


if __name__ == "__main__":
    unittest.main()
