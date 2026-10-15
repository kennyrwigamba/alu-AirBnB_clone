#!/usr/bin/python3
"""Exercise standard and dotted console commands with isolated storage."""

import ast
import cmd
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import UUID

from console import HBNBCommand
from models import storage
from models.engine.file_storage import FileStorage
from models.place import Place
from models.user import User


class TestHBNBCommand(unittest.TestCase):
    """Check console output, error handling, and persistent changes."""

    def setUp(self):
        """Use a temporary file and object mapping for each test."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "file.json"
        objects = patch.object(FileStorage, "_FileStorage__objects", {})
        file_path = patch.object(
            FileStorage, "_FileStorage__file_path", str(self.path)
        )
        objects.start()
        self.addCleanup(objects.stop)
        file_path.start()
        self.addCleanup(file_path.stop)

    def command(self, line):
        """Run through onecmd and return intercepted standard output."""
        with patch("sys.stdout", new=StringIO()) as output:
            HBNBCommand().onecmd(line)
            return output.getvalue()

    def persisted(self):
        """Read the JSON written by a console command."""
        return json.loads(self.path.read_text(encoding="utf-8"))

    def test_interpreter_and_prompt(self):
        """The entry point subclasses cmd.Cmd and uses the required prompt."""
        self.assertIsInstance(HBNBCommand(), cmd.Cmd)
        self.assertEqual(HBNBCommand.prompt, "(hbnb) ")

    def test_exit_commands(self):
        """Both exit commands stop command processing."""
        for command in ("quit", "EOF", "quit ignored", "EOF ignored"):
            with self.subTest(command=command):
                with patch("sys.stdout", new=StringIO()) as output:
                    self.assertTrue(HBNBCommand().onecmd(command))
                expected = "\n" if command.startswith("EOF") else ""
                self.assertEqual(output.getvalue(), expected)

    def test_empty_lines_do_not_repeat_commands(self):
        """Empty lines and whitespace never repeat the previous command."""
        with patch("sys.stdout", new=StringIO()) as output:
            console = HBNBCommand()
            console.onecmd("create User")
            output.seek(0)
            output.truncate(0)
            for line in ("", " ", "   ", "\t"):
                self.assertFalse(console.onecmd(line))
            self.assertEqual(output.getvalue(), "")
        self.assertEqual(len(storage.all()), 1)

    def test_help(self):
        """Help lists documented commands and explains each command."""
        commands = (
            "EOF", "help", "quit", "create", "show", "destroy", "all",
            "count", "update",
        )
        output = self.command("help")
        self.assertIn("Documented commands", output)
        for command in commands:
            with self.subTest(command=command):
                self.assertIn(command, output)
                details = self.command("help " + command)
                self.assertTrue(details.strip())
                self.assertNotIn("No help", details)
        self.assertIn("Quit command to exit the program", self.command(
            "help quit"
        ))
        self.assertIn(".update(", self.command("help update"))

    def test_unknown_command(self):
        """Unknown commands use the standard cmd error message."""
        self.assertEqual(
            self.command("unknown"), "*** Unknown syntax: unknown\n"
        )

    def test_create_all_classes(self):
        """Creation prints a UUID and saves each supported model class."""
        for name, model_class in HBNBCommand.classes.items():
            with self.subTest(model=name):
                object_id = self.command("create " + name).strip()
                self.assertEqual(str(UUID(object_id)), object_id)
                key = name + "." + object_id
                self.assertIsInstance(storage.all()[key], model_class)
                self.assertEqual(
                    self.persisted()[key], storage.all()[key].to_dict()
                )

    def test_missing_class_errors(self):
        """Commands requiring a class report its absence first."""
        for command in ("create", "show", "destroy", "count", "update"):
            with self.subTest(command=command):
                self.assertEqual(
                    self.command(command), "** class name missing **\n"
                )

    def test_unknown_class_errors(self):
        """Both syntaxes reject classes before checking other arguments."""
        for command in ("create", "show", "destroy", "all", "count",
                        "update"):
            with self.subTest(command=command):
                self.assertEqual(
                    self.command(command + " Unknown"),
                    "** class doesn't exist **\n",
                )
                if command != "create":
                    self.assertEqual(
                        self.command("Unknown." + command + "()"),
                        "** class doesn't exist **\n",
                    )

    def test_missing_id_errors(self):
        """Both syntaxes require IDs for show, destroy, and update."""
        for name in HBNBCommand.classes:
            for command in ("show", "destroy", "update"):
                for line in (command + " " + name,
                             name + "." + command + "()"):
                    with self.subTest(line=line):
                        self.assertEqual(
                            self.command(line), "** instance id missing **\n"
                        )

    def test_nonexistent_id_errors(self):
        """Unknown IDs report the same error through either syntax."""
        for name in HBNBCommand.classes:
            for command in ("show", "destroy", "update"):
                for line in (command + " " + name + " missing",
                             name + "." + command + '("missing")'):
                    with self.subTest(line=line):
                        self.assertEqual(
                            self.command(line), "** no instance found **\n"
                        )

    def test_show_all_classes(self):
        """Both show forms print the requested instance exactly."""
        for name, model_class in HBNBCommand.classes.items():
            instance = model_class()
            for line in ("show {} {}".format(name, instance.id),
                         '{}.show("{}")'.format(name, instance.id)):
                with self.subTest(line=line):
                    self.assertEqual(self.command(line), str(instance) + "\n")

    def test_id_belongs_to_requested_class(self):
        """A real ID from another class does not match an instance."""
        user = User()
        for command in ("show", "destroy", "update"):
            for line in ("{} Place {}".format(command, user.id),
                         'Place.{}("{}")'.format(command, user.id)):
                with self.subTest(line=line):
                    self.assertEqual(
                        self.command(line), "** no instance found **\n"
                    )
        self.assertIn("User." + user.id, storage.all())

    def test_all_empty(self):
        """Listing empty storage prints an empty list."""
        for line in ("all", "all User", "User.all()"):
            with self.subTest(line=line):
                self.assertEqual(self.command(line), "[]\n")

    def test_all_lists_and_filters_classes(self):
        """Global listings include all objects; class listings filter them."""
        instances = [model() for model in HBNBCommand.classes.values()]
        instances.append(User())
        self.assertEqual(
            ast.literal_eval(self.command("all")),
            [str(instance) for instance in instances],
        )
        for name in HBNBCommand.classes:
            expected = [str(obj) for obj in instances
                        if type(obj).__name__ == name]
            for line in ("all " + name, name + ".all()"):
                with self.subTest(line=line):
                    self.assertEqual(
                        ast.literal_eval(self.command(line)), expected
                    )

    def test_count_filters_classes(self):
        """Counts start at zero and include only the requested class."""
        for name, model_class in HBNBCommand.classes.items():
            with self.subTest(model=name):
                self.assertEqual(self.command(name + ".count()"), "0\n")
                model_class()
                model_class()
                self.assertEqual(self.command(name + ".count()"), "2\n")
                self.assertEqual(self.command("count " + name), "2\n")

    def test_destroy_all_classes(self):
        """Both destroy forms remove the object from memory and disk."""
        for name, model_class in HBNBCommand.classes.items():
            for dotted in (False, True):
                with self.subTest(model=name, dotted=dotted):
                    instance = model_class()
                    survivor = model_class()
                    instance.save()
                    line = ('{}.destroy("{}")'.format(name, instance.id)
                            if dotted else
                            "destroy {} {}".format(name, instance.id))
                    self.assertEqual(self.command(line), "")
                    key = name + "." + instance.id
                    self.assertNotIn(key, storage.all())
                    self.assertNotIn(key, self.persisted())
                    self.assertIn(name + "." + survivor.id, storage.all())

    def test_update_missing_attribute_or_value(self):
        """Updates distinguish missing attribute names and missing values."""
        user = User()
        cases = {
            "update User " + user.id: "attribute name",
            'User.update("{}")'.format(user.id): "attribute name",
            "update User {} first_name".format(user.id): "value",
            'User.update("{}", "first_name")'.format(user.id): "value",
        }
        for line, missing in cases.items():
            with self.subTest(line=line):
                self.assertEqual(
                    self.command(line), "** {} missing **\n".format(missing)
                )

    def test_standard_update(self):
        """Standard updates preserve spaces and persist the changed object."""
        user = User()
        created = user.created_at
        updated = user.updated_at
        self.assertEqual(self.command(
            'update User {} first_name "John Smith"'.format(user.id)
        ), "")
        self.assertEqual(user.first_name, "John Smith")
        self.assertEqual(user.created_at, created)
        self.assertGreaterEqual(user.updated_at, updated)
        self.assertEqual(
            self.persisted()["User." + user.id], user.to_dict()
        )

    def test_standard_update_ignores_extra_arguments(self):
        """Only the first attribute/value pair is used in standard updates."""
        user = User()
        self.command("update User {} first_name John last_name Doe".format(
            user.id
        ))
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "")

    def test_update_existing_numeric_attributes(self):
        """Standard updates cast existing integer and float attributes."""
        place = Place()
        self.command("update Place {} number_rooms 3".format(place.id))
        self.command("update Place {} latitude 1.25".format(place.id))
        self.assertEqual(place.number_rooms, 3)
        self.assertIs(type(place.number_rooms), int)
        self.assertEqual(place.latitude, 1.25)
        self.assertIs(type(place.latitude), float)

    def test_dotted_update_all_classes(self):
        """Dotted updates work for every supported model."""
        for name, model_class in HBNBCommand.classes.items():
            with self.subTest(model=name):
                instance = model_class()
                self.assertEqual(self.command(
                    '{}.update("{}", "custom_text", "John Smith")'.format(
                        name, instance.id
                    )
                ), "")
                self.assertEqual(instance.custom_text, "John Smith")
                self.assertEqual(
                    self.persisted()[name + "." + instance.id],
                    instance.to_dict(),
                )

    def test_dotted_update_value_types(self):
        """New dotted attributes keep string, integer, and float types."""
        user = User()
        for name, value in (("age", 89), ("score", 1.25), ("label", "89"),
                            ("negative", -4), ("empty", "")):
            with self.subTest(attribute=name):
                self.command('User.update("{}", {!r}, {!r})'.format(
                    user.id, name, value
                ))
                self.assertEqual(getattr(user, name), value)
                self.assertIs(type(getattr(user, name)), type(value))

    def test_dictionary_update_all_classes(self):
        """A dictionary updates multiple attributes and persists them."""
        attributes = {"first_name": "John", "age": 89, "score": 1.25}
        for name, model_class in HBNBCommand.classes.items():
            with self.subTest(model=name):
                instance = model_class()
                self.assertEqual(self.command(
                    '{}.update("{}", {!r})'.format(
                        name, instance.id, attributes
                    )
                ), "")
                for attribute, value in attributes.items():
                    self.assertEqual(getattr(instance, attribute), value)
                    self.assertIs(type(getattr(instance, attribute)),
                                  type(value))
                self.assertEqual(
                    self.persisted()[name + "." + instance.id],
                    instance.to_dict(),
                )

    def test_dictionary_with_punctuation(self):
        """Dictionary strings preserve commas, braces, and escaped quotes."""
        user = User()
        attributes = {"first_name": "O'Neil, Jane", "note": 'a "quote" {x}'}
        self.command('User.update("{}", {!r})'.format(user.id, attributes))
        for attribute, value in attributes.items():
            self.assertEqual(getattr(user, attribute), value)

    def test_empty_dictionary(self):
        """An empty update dictionary leaves model data intact."""
        user = User()
        data = user.to_dict()
        self.assertEqual(self.command(
            'User.update("{}", {{}})'.format(user.id)
        ), "")
        after = user.to_dict()
        data.pop("updated_at")
        after.pop("updated_at")
        self.assertEqual(after, data)

    def test_update_preserves_identity_and_creation_time(self):
        """Reserved attributes cannot break storage keys or timestamps."""
        user = User()
        object_id = user.id
        created = user.created_at
        for attribute in ("id", "created_at", "updated_at"):
            self.command("update User {} {} changed".format(
                object_id, attribute
            ))
        self.command('User.update("{}", {{"id": "other", '
                     '"created_at": "other", "first_name": "John"}})'.format(
                         object_id
                     ))
        self.assertEqual(user.id, object_id)
        self.assertEqual(user.created_at, created)
        self.assertIs(storage.all()["User." + object_id], user)
        self.assertEqual(user.first_name, "John")

    def test_dotted_quotes_whitespace_and_trailing_comma(self):
        """Python-style literal quoting and argument spacing are accepted."""
        user = User()
        for line in ("User.show('{}')".format(user.id),
                     '  User.show( "{}", )  '.format(user.id)):
            with self.subTest(line=line):
                self.assertEqual(self.command(line), str(user) + "\n")

    def test_malformed_commands_do_not_execute_code(self):
        """Invalid dotted commands fall back without executing expressions."""
        lines = (
            "User.unknown()", "User.all(", "User.show(unquoted)",
            "User.show(id='missing')", 'User.show("unterminated)',
            "User.show() or dangerous())",
            "User.update('id', {'age': dangerous()})",
            "User.show(__import__('os').getcwd())",
        )
        with patch("builtins.__import__", side_effect=AssertionError):
            for line in lines:
                with self.subTest(line=line):
                    self.assertEqual(
                        self.command(line),
                        "*** Unknown syntax: " + line + "\n",
                    )

    def test_malformed_standard_quotes(self):
        """Unmatched standard-command quotes do not crash the console."""
        self.assertEqual(
            self.command('show "unterminated'),
            "** class name missing **\n",
        )

    def test_destroy_changes_count(self):
        """The advanced count/destroy workflow sees updated storage."""
        first, second = User(), User()
        self.assertEqual(self.command("User.count()"), "2\n")
        self.command('User.destroy("{}")'.format(first.id))
        self.assertEqual(self.command("User.count()"), "1\n")
        self.assertEqual(
            self.command('User.show("{}")'.format(second.id)),
            str(second) + "\n",
        )

    def run_process(self, arguments, input_text=""):
        """Run a fresh interpreter away from the repository storage file."""
        environment = os.environ.copy()
        root = Path(__file__).resolve().parents[1]
        environment["PYTHONPATH"] = str(root)
        return subprocess.run(
            [sys.executable, "-B"] + arguments,
            input=input_text, cwd=self.path.parent, env=environment,
            capture_output=True, text=True, timeout=5, check=True,
        )

    def test_import_has_no_command_loop(self):
        """Importing console is silent and does not enter cmdloop."""
        result = self.run_process(["-c", "import console"])
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_noninteractive_command_loop(self):
        """Piped commands accept both syntaxes and exit without errors."""
        root = Path(__file__).resolve().parents[1]
        result = self.run_process(
            [str(root / "console.py")],
            "create User\nUser.count()\nUser.all()\n\n   \nquit\n",
        )
        self.assertEqual(result.stderr, "")
        self.assertIn("(hbnb) 1\n", result.stdout)
        self.assertIn("[User]", result.stdout)
        self.assertEqual(len(self.persisted()), 1)

    def test_real_end_of_input_exits(self):
        """Actual end-of-input exits even without a literal EOF command."""
        root = Path(__file__).resolve().parents[1]
        result = self.run_process([str(root / "console.py")])
        self.assertEqual(result.stdout, "(hbnb) \n")
        self.assertEqual(result.stderr, "")


if __name__ == '__main__':
    unittest.main()
