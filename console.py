#!/usr/bin/python3
"""Command interpreter for the AirBnB clone."""

import ast
import cmd
import re
import shlex

from models import storage
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


class HBNBCommand(cmd.Cmd):
    """Interactive command interpreter for model objects."""

    prompt = "(hbnb) "

    classes = {
        "Amenity": Amenity,
        "BaseModel": BaseModel,
        "City": City,
        "Place": Place,
        "Review": Review,
        "State": State,
        "User": User,
    }

    def emptyline(self):
        """Do nothing when the user enters an empty line."""
        pass

    def default(self, line):
        """Dispatch Class.all/count/show/destroy/update(...) commands.

        Update accepts either an ID, attribute name and value, or an ID
        and a dictionary. Arguments are literals, never executable code.
        """
        match = re.fullmatch(r"(\w+)\.(\w+)\((.*)\)", line.strip())
        if match is None:
            return super().default(line)
        class_name, command, values = match.groups()
        if command not in {"all", "count", "show", "destroy", "update"}:
            return super().default(line)
        try:
            call = ast.parse("command({})".format(values), mode="eval").body
            if not isinstance(call, ast.Call) or call.keywords:
                return super().default(line)
            arguments = [ast.literal_eval(value) for value in call.args]
        except (SyntaxError, ValueError, TypeError):
            return super().default(line)
        if command == "update":
            return self._update([class_name] + arguments)
        arguments = " ".join(
            shlex.quote(str(value)) for value in [class_name] + arguments
        )
        return getattr(self, "do_" + command)(arguments)

    def _arguments(self, line):
        """Split a command line while preserving quoted values."""
        try:
            return shlex.split(line)
        except ValueError:
            return []

    def _get_object(self, class_name, object_id):
        """Return an object matching its class and ID, if it exists."""
        key = "{}.{}".format(class_name, object_id)
        return storage.all().get(key)

    def do_quit(self, line):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, line):
        """Exit when end-of-file is received."""
        print()
        return True

    def do_create(self, line):
        """Create, persist, and print the ID of a model instance."""
        arguments = self._arguments(line)
        if not arguments:
            print("** class name missing **")
            return
        model_class = self.classes.get(arguments[0])
        if model_class is None:
            print("** class doesn't exist **")
            return
        instance = model_class()
        instance.save()
        print(instance.id)

    def do_show(self, line):
        """Print an instance: show <class> <id> or <class>.show(<id>)."""
        arguments = self._arguments(line)
        if not arguments:
            print("** class name missing **")
            return
        if arguments[0] not in self.classes:
            print("** class doesn't exist **")
            return
        if len(arguments) < 2:
            print("** instance id missing **")
            return
        instance = self._get_object(arguments[0], arguments[1])
        if instance is None:
            print("** no instance found **")
            return
        print(instance)

    def do_destroy(self, line):
        """Delete via destroy <class> <id> or <class>.destroy(<id>)."""
        arguments = self._arguments(line)
        if not arguments:
            print("** class name missing **")
            return
        if arguments[0] not in self.classes:
            print("** class doesn't exist **")
            return
        if len(arguments) < 2:
            print("** instance id missing **")
            return
        key = "{}.{}".format(arguments[0], arguments[1])
        if self._get_object(arguments[0], arguments[1]) is None:
            print("** no instance found **")
            return
        del storage.all()[key]
        storage.save()

    def do_all(self, line):
        """List instances: all [<class>] or <class>.all()."""
        arguments = self._arguments(line)
        if arguments and arguments[0] not in self.classes:
            print("** class doesn't exist **")
            return
        class_name = arguments[0] if arguments else None
        objects = storage.all().values()
        if class_name is not None:
            objects = (
                instance for instance in objects
                if instance.__class__.__name__ == class_name
            )
        print([str(instance) for instance in objects])

    def do_count(self, line):
        """Count instances: count <class> or <class>.count()."""
        arguments = self._arguments(line)
        if not arguments:
            print("** class name missing **")
            return
        if arguments[0] not in self.classes:
            print("** class doesn't exist **")
            return
        print(sum(
            instance.__class__.__name__ == arguments[0]
            for instance in storage.all().values()
        ))

    def do_update(self, line):
        """Update <class> <id> <attribute> <value>.

        Also accepts <class>.update(<id>, <attribute>, <value>) or
        <class>.update(<id>, {<attribute>: <value>, ...}).
        """
        return self._update(self._arguments(line))

    def _update(self, arguments):
        """Validate an update and persist its supplied attributes."""
        if not arguments:
            print("** class name missing **")
            return
        if arguments[0] not in self.classes:
            print("** class doesn't exist **")
            return
        if len(arguments) < 2:
            print("** instance id missing **")
            return
        instance = self._get_object(arguments[0], arguments[1])
        if instance is None:
            print("** no instance found **")
            return
        if len(arguments) < 3:
            print("** attribute name missing **")
            return
        if isinstance(arguments[2], dict):
            attributes = arguments[2]
        else:
            if len(arguments) < 4:
                print("** value missing **")
                return
            attributes = {arguments[2]: arguments[3]}

        for attribute, value in attributes.items():
            if attribute in {"id", "created_at", "updated_at"}:
                continue
            current_value = getattr(instance, attribute, None)
            if isinstance(value, str):
                if isinstance(current_value, bool):
                    value = value.lower() == "true"
                elif isinstance(current_value, int):
                    value = int(value)
                elif isinstance(current_value, float):
                    value = float(value)
            setattr(instance, attribute, value)
        instance.save()


if __name__ == '__main__':
    HBNBCommand().cmdloop()
