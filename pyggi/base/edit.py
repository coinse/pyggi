import ast
import inspect
from abc import ABC, abstractmethod

class AbstractEdit(ABC):
    @abstractmethod
    def __init__(self):
        """
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for name in args:
            if name != 'self':
                setattr(o, name, values[name])
        print(self.__dict__)
        """
        pass

    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        for prop in self.__dict__:
            if self.__dict__[prop] != other.__dict__[prop]:
                return False
        return True

    @property
    @abstractmethod
    def domain(self):
        pass

    def __str__(self):
        """
        :return: ``LineReplacement([target], [ingredient])``
        """
        return "{}({})".format(self.__class__.__name__, self.__dict__)

    @abstractmethod
    def apply(self, program, new_contents, modification_points):
        """"
        Apply the operator to the contents of program
        :param program: The original program instance
        :type program: :py:class:`.Program`
        :param new_contents: The new contents of program to which the edit will be applied
        :type new_contents: dict(str, list(?))
        :param modification_points: The original modification points
        :type modification_points: list(?)
        :return: success or not
        :rtype: bool
        """
        pass

    @classmethod
    @abstractmethod
    def create(cls):
        """
        :return: The operator instance with randomly-selected properties.
        """
        pass

class Replacement(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def apply(self, program, new_contents, modification_points):
        return program.do_replace(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'))

class Insertion(AbstractEdit):
    def __init__(self, target, ingredient, direction='before'):
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    def apply(self, program, new_contents, modification_points):
        return program.do_insert(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction='before', method='random'):
        return cls(program.random_target(target_file, 'random'),
                   program.random_target(ingr_file, 'random'),
                   direction)

class Deletion(AbstractEdit):
    def __init__(self, target):
        self.target = target

    def apply(self, program, new_contents, modification_points):
        return program.do_delete(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        return cls(program.random_target(target_file, method))

class Moving(AbstractEdit):
    def __init__(self, target, ingredient, direction='before'):
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    def apply(self, program, new_contents, modification_points):
        program.do_insert(self, new_contents, modification_points)
        program.do_delete(self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction='before', method='random'):
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)