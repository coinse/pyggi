from abc import ABC, abstractmethod

class Algorithm(ABC):
    def __init__(self, program):
	    """
	    :param program: The Program instance to optimize.
	    :type program: :py:class:`.Program`
	    """
	    self.program = program
	    self.best_fitness = None
	    self.setup()

    def setup(self):
        pass

    @abstractmethod
    def run(self):
    	pass