from abc import abstractmethod
from ..base import AbstractEngine

class AbstractTreeEngine(AbstractEngine):
    @classmethod
    @abstractmethod
    def do_replace(cls, program, op, new_contents, modification_points):
        pass

    @classmethod
    @abstractmethod
    def do_insert(cls, program, op, new_contents, modification_points):
        pass

    @classmethod
    @abstractmethod
    def do_delete(cls, program, op, new_contents, modification_points):
        pass
