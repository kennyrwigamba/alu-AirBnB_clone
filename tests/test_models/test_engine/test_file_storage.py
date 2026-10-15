#!/usr/bin/python3
"""Validate JSON persistence and application storage initialization."""

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from models import storage
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.engine.file_storage import FileStorage
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
from tests.test_models import test_base_model


class TestFileStorage(unittest.TestCase):
    """Check the storage engine with isolated files and object mappings."""

    setUp = test_base_model.TestBaseModel.setUp

    def test_all_returns_live_dictionary(self):
        """The all method returns the shared dictionary of stored objects."""
        self.assertIsInstance(storage.all(), dict)
        self.assertIs(storage.all(), storage.all())
        self.assertIs(storage.all(), FileStorage().all())

    def test_new_uses_class_and_id(self):
        """The new method indexes the original object by class and ID."""
        model = User()
        storage.all().clear()
        storage.new(model)
        self.assertEqual(storage.all(), {"User." + model.id: model})

    def test_save_and_reload_all_classes(self):
        """Saving and reloading restores every supported model class."""
        classes = (BaseModel, User, State, City, Amenity, Place, Review)
        expected = {}
        for model_class in classes:
            model = model_class()
            model.custom_text = "Text with spaces"
            key = "{}.{}".format(model_class.__name__, model.id)
            expected[key] = model.to_dict()
        storage.save()
        self.assertEqual(json.loads(self.path.read_text()), expected)
        storage.all().clear()
        storage.reload()
        self.assertEqual(set(storage.all()), set(expected))
        for key, model in storage.all().items():
            self.assertEqual(model.to_dict(), expected[key])
            self.assertEqual(type(model).__name__, expected[key]["__class__"])

    def test_reload_missing_file(self):
        """A missing storage file raises no error and preserves objects."""
        model = BaseModel()
        storage.reload()
        self.assertIs(storage.all()["BaseModel." + model.id], model)
        self.assertFalse(self.path.exists())

    def test_empty_storage(self):
        """An empty mapping saves and reloads as an empty JSON object."""
        storage.save()
        self.assertEqual(json.loads(self.path.read_text()), {})
        storage.reload()
        self.assertEqual(storage.all(), {})

    def test_deletion_persists(self):
        """Removing and saving an object keeps it absent after reload."""
        model = BaseModel()
        model.save()
        del storage.all()["BaseModel." + model.id]
        storage.save()
        storage.reload()
        self.assertEqual(storage.all(), {})

    def test_application_startup_reloads(self):
        """Importing models in a fresh process restores saved objects."""
        model = User()
        model.first_name = "Nadiv"
        model.save()
        environment = os.environ.copy()
        root = str(Path(__file__).resolve().parents[3])
        environment["PYTHONPATH"] = root
        code = (
            "import json; from models import storage; "
            "print(json.dumps({k: v.to_dict() "
            "for k, v in storage.all().items()}))"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=self.path.parent, env=environment,
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(
            json.loads(result.stdout), {"User." + model.id: model.to_dict()}
        )
