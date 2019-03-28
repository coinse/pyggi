import ast
from abc import ABC, abstractmethod
from ..utils import have_the_same_file_extension, check_file_extension

class AtomicOperator(ABC):
    """
    
    PYGGI-defined Atomic Operator:
    User can generate the own custom edit operators
    which can be converted into a list of atomic operators.
    For example, **MOVE x -> y** operator can be represented as
    **[LineReplacement(x, None),LineInsertion(x, y)]**

    **Available List**

    * LineReplacement
    * LineInsertion
    * StmtReplacement
    * StmtInsertion

    """

    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        for prop in self.__dict__:
            if self.__dict__[prop] != other.__dict__[prop]:
                return False
        return True

    @property
    def atomic_operators(self):
        """
        :return: ``[self]``, the list that only contains the AtomicOperator instance itself.
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        return [self]

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @property
    @abstractmethod
    def modification_point(self):
        pass

    @abstractmethod
    def is_valid_for(self, program):
        """
        :param program: The program instance to which this edit will be applied
        :type program: :py:class:`.Program`
        :return: Whether the edit is able to be applied to the program
        :rtype: bool
        """
        pass

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
        :rtype: :py:class:`.atomic_operator.AtomicOperator`
        """
        pass

class CustomOperator(ABC):
    """
    CustomOperator is an abstact class which is designed to be used
    as a basic structure of custom edit operators.

    Every class that inherits CustomOperator class must override the
    methods marked with ``@abstractmethod`` to create instances.

    * :py:meth:`__str__`
    * :py:meth:`length_of_args`
    * :py:meth:`atomic_operators`
    """
    def __init__(self, *args):
        if len(args) != self.length_of_args:
            raise Exception("{} takes {} positional argument but {} were given.".format(
                self.__class__.__name__, self.length_of_args, len(args)))
        self.args = args
        assert isinstance(self.atomic_operators, list)
        assert all(isinstance(op, AtomicOperator) for op in self.atomic_operators)

    def __eq__(self, other):
        return self.atomic_operators == other.atomic_operators

    @property
    def detail(self) -> str:
        """
        :return: The detail of this custom edit
        :rtype: str

        .. note::
            If the edit is ``LineMoving(('Triangle.java', 10), ('Triangle.java', 4))``

            returns::

                1) Insert ('Triangle.java', 4) before ('Triangle.java', 10)
                2) Replace ('Triangle.java', 4) with None
        """
        return "\n".join(
            list(
                map(lambda x: "{}) {}".format(x[0] + 1, x[1]),
                    enumerate(self.atomic_operators))))

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def is_valid_for(self, program):
        """
        :param program: The program instance to which this edit will be applied
        :type program: :py:class:`.Program`
        :return: Whether the edit is able to be applied to the program
        :rtype: bool
        """
        pass

    @property
    @abstractmethod
    def length_of_args(self):
        """
        :return: The length of args the edit operator should take
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def atomic_operators(self):
        """
        :return: The list of instances of AtomicOperator.
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        pass