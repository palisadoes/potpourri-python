#!/usr/bin/env python3
"""Script to test the concept of Meta and inner classes."""

from __future__ import print_function
from inspect import isclass


class _OldClass:
    pass


class _NewClass:
    pass


_all_vars = set(dir(_OldClass) + dir(_NewClass))


def props(x):
    return {
        key: vars(x).get(key, getattr(x, key)) for key in dir(x) if key not in _all_vars
    }


class SubclassWithMeta_Meta(type):
    _meta = None

    def __str__(cls):
        if cls._meta:
            return cls._meta.name
        return cls.__name__

    def __repr__(cls):
        return f"<{cls.__name__} meta={repr(cls._meta)}>"


class SubclassWithMeta(metaclass=SubclassWithMeta_Meta):
    """This class improves __init_subclass__ to receive automatically the options from meta"""

    def __init_subclass__(cls, **meta_options):
        """This method just terminates the super() chain"""
        _Meta = getattr(cls, "Meta", None)
        _meta_props = {}
        if _Meta:
            if isinstance(_Meta, dict):
                _meta_props = _Meta
            elif isclass(_Meta):
                _meta_props = props(_Meta)
            else:
                raise Exception(
                    f"Meta have to be either a class or a dict. Received {_Meta}"
                )
            delattr(cls, "Meta")
        options = dict(meta_options, **_meta_props)
        
        print('--')
        print('Meta', _Meta)
        print('Meta Options', meta_options)
        print('Meta Props', _meta_props)

        abstract = options.pop("abstract", False)
        if abstract:
            assert not options, (
                "Abstract types can only contain the abstract attribute. "
                f"Received: abstract, {', '.join(options)}"
            )
        else:
            super_class = super(cls, cls)
            if hasattr(super_class, "__init_subclass_with_meta__"):
                super_class.__init_subclass_with_meta__(**options)

    @classmethod
    def __init_subclass_with_meta__(cls, **meta_options):
        """This method just terminates the super() chain"""


BaseTypeMeta = SubclassWithMeta_Meta


class BaseType(SubclassWithMeta):
    @classmethod
    def create_type(cls, class_name, **options):
        return type(class_name, (cls,), {"Meta": options})

    @classmethod
    def __init_subclass_with_meta__(
        cls, name=None, description=None, _meta=None, **_kwargs
    ):
        assert "_meta" not in cls.__dict__, "Can't assign meta directly"
        if not _meta:
            return
        _meta.name = name or cls.__name__
        _meta.description = description or trim_docstring(cls.__doc__)
        _meta.freeze()
        cls._meta = _meta
        super(BaseType, cls).__init_subclass_with_meta__()


class Model:

    def __init__(self):
        pass


class Peter(BaseType):
    class Meta:
        model = Model
        fields = ("id", "question_text")
        interfaces = ('interface', )
        listing = list(range(10))
    
        def __init__(self, description='Hello World'):
            pass


def main():
    """Process data.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    peter = Peter()
    print(dir(peter))
    pass


if __name__ == "__main__":
    main()
