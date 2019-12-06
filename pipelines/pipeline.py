from abc import ABC, abstractmethod


class OperationState:
    """State object for Operation components. Used for storing and transferring data through components in a pipeline.
    """
    def get_property(self, name):
        return getattr(self, name)

    def set_property(self, name, value):
        setattr(self, name, value)

    def del_property(self, name):
        delattr(self, name)

    def has_property(self, name):
        return hasattr(self, name)


class Operation(ABC):
    """ABC class for all operations available for the pipelines, following the composite pattern.
    """
    @abstractmethod
    def execute(self, op_state: OperationState):
        raise NotImplementedError

    @classmethod
    def handles_type(cls):
        return cls.__name__


class Pipeline:
    """Simplified implementation of a pipeline. Contains n number of operations that are executed sequentially

    Attributes:
        _operations(list): list of operations to be executed
    """
    _operations = None

    def __init__(self):
        self._operations = []

    def add_op(self, op):
        """Adds an operation to the pipeline.

        Args:
            op (Operation): operation that should be added
        """
        self._operations.append(op)

    def remove_op(self, op):
        """Removes an operation from the pipeline.

        Args:
            op (Operation): operation that should be removed
        """
        self._operations.remove(op)

    def execute(self, op_state: OperationState = None):
        """Executes all operations on the pipeline.

        Args:
            op_state (OperationState): an OperationState object, usually containing the attribute "data_or_buffer"

        Returns:
            op_state (OperationState): the final operation state of the pipeline
        """
        if op_state is None:
            op_state = OperationState()

        for op in self._operations:
            op_state = op.execute(op_state)

        return op_state


