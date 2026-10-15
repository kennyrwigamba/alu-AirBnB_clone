#!/usr/bin/python3
"""Command interpreter for the AirBnB clone."""

import cmd
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
        """Print the string representation of a model instance."""
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
        """Delete and persist the removal of a model instance."""
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
        """Print string representations of all matching model instances."""
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

    def do_update(self, line):
        """Update one simple attribute and persist the model instance."""
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
        if len(arguments) < 3:
            print("** attribute name missing **")
            return
        if len(arguments) < 4:
            print("** value missing **")
            return

        attribute = arguments[2]
        value = arguments[3]
        current_value = getattr(instance, attribute, None)
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
