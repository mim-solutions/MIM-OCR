from itertools import chain
from typing import Type, List


def get_subclass_by_name(base_class: Type, name: str):
    for subclass in _get_all_subclasses(base_class):
        if subclass.__name__ == name:
            return subclass
    raise KeyError("Subclass of this name not found.")


def _get_all_subclasses(base_class: Type) -> List[Type]:
    return list(chain.from_iterable([_get_all_subclasses(sub_class) for sub_class in base_class.__subclasses__()])) \
           + [base_class]
