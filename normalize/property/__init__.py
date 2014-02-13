
from __future__ import absolute_import

import inspect
import weakref

from normalize.property.meta import MetaProperty
from normalize.coll import ListCollection


class _Default():
    pass


class Property(object):
    """This is the base class for all property types.  It is a data descriptor,
    so care should be taken before adding any SPECIALMETHODS which might change
    the way it behaves.
    """
    __metaclass__ = MetaProperty

    def __init__(self, default=None, required=False, check=None, traits=None):
        super(Property, self).__init__()
        self.default = default
        if callable(default):
            args = inspect.getargspec(default)
            if not args.args:
                required_args = 0
            else:
                required_args = len(args.args)
                if args.defaults:
                    required_args -= len(args.defaults)
                if required_args > 1:
                    raise Exception(
                        "default functions may take 0 or 1 arguments"
                    )
            self.default_wants_arg = bool(required_args)
        self.required = required
        self.check = check
        self.name = None
        self.class_ = None

    @property
    def bound(self):
        return bool(self.class_)

    def bind(self, class_, name):
        self.name = name
        self.class_ = weakref.ref(class_)

    @property
    def fullname(self):
        if not self.bound:
            return "(unbound)"
        elif not self.class_():
            classname = "(GC'd class)"
        else:
            classname = self.class_().__name__
        return "%s.%s" % (classname, self.name)

    def type_check(self, value):
        if self.required and value is None:
            raise ValueError("%s is required" % self.fullname)
        if self.check and not self.check(value):
            raise ValueError(
                "%s value '%r' failed type check" % (self.fullname, value)
            )

    def get_default(self, obj):
        if callable(self.default):
            if self.default_wants_arg:
                rv = self.default(obj)
            else:
                rv = self.default()
        else:
            rv = self.default
        return rv

    def init_prop(self, obj, value=_Default):
        if value is _Default:
            value = self.get_default(obj)
        self.type_check(value)
        obj.__dict__[self.name] = value

    def __get__(self, obj, type_=None):
        """Default getter; does NOT fall back to regular descriptor behavior
        """
        if self.name not in obj.__dict__:
            raise AttributeError
        return obj.__dict__[self.name]

    def __repr__(self):
        metaclass = str(type(self).__name__)
        return "<%s %s>" % (metaclass, self.fullname)


class LazyProperty(Property):
    """This declares a property which has late evaluation using its 'default'
    method.  This type uses the support built-in to python for lazy attribute
    setting, which means subsequent attribute assignments will not be prevented
    or checked.  See SafeLazyProperty for the descriptor version
    """
    __trait__ = "lazy"

    def __init__(self, lazy=True, **kwargs):
        if not lazy:
            raise Exception("To make an eager property, do not pass lazy")
        super(LazyProperty, self).__init__(**kwargs)

    def init_prop(self, obj, value=_Default):
        if value is _Default:
            return
        super(LazyProperty, self).init_prop(obj)

    def __get__(self, obj, type_=None):
        value = self.get_default(obj)
        self.type_check(value)
        obj.__dict__[self.name] = value
        return super(LazyProperty, self).__get__(obj, type_)


class ROProperty(Property):
    __trait__ = "ro"

    def __get__(self, obj, type_=None):
        return super(ROProperty, self).__get__(obj, type_)

    def __set__(self, obj, value):
        raise AttributeError("%s is read-only" % self.fullname)

    def __delete__(self, instance):
        """
        Note: instance is normally an instance of a Record
        """
        raise AttributeError("%s is read-only" % self.fullname)


class SlowLazyProperty(LazyProperty):
    __trait__ = "slow"

    def __get__(self, obj, type_=None):
        if self.name in obj.__dict__:
            return obj.__dict__[self.name]
        return super(SlowLazyProperty, self).__get__(obj, type_)


class ROLazyProperty(SlowLazyProperty, ROProperty):
    pass


class SafeProperty(Property):
    """A version of Property which always checks all assignments to
    properties"""
    __trait__ = "safe"

    def __set__(self, obj, value):
        self.type_check(value)
        obj.__dict__[self.name] = value

    def __delete__(self, obj):
        self.type_check(None)
        super(SafeProperty, self).__delete__(obj)


class LazySafeProperty(SafeProperty, SlowLazyProperty):
    pass


class CollectionProperty(Property):
    __trait__ = "coll"

    def __init__(self, of=None, coll=None, check_item=None, **kwargs):
        if coll is None:
            raise Exception(
                "coll is required; specify coll type or use a sub-class "
                "like ListProperty"
            )
        self.check_item = None
        self.of = of
        self.coll = coll
        super(CollectionProperty, self).__init__(**kwargs)

    def _coerce(self, value):
        if not isinstance(value, self.coll) or value.itemtype != self.of:
            value = self.coll(self.of, (value if value else tuple()))
        return value

    def __set__(self, obj, value):
        super(CollectionProperty, self).__set__(obj, self._coerce(value))

    def init_prop(self, obj, value=_Default):
        super(CollectionProperty, self).init_prop(obj, self._coerce(value))


class ListProperty(CollectionProperty):
    __trait__ = "list"

    def __init__(self, list_of=None, **kwargs):
        if list_of is None:
            list_of = kwargs.pop("of", None)
        if not list_of:
            raise Exception(
                "List Properties must have a defined item type; pass of= "
                "or list_of= to the declaration"
            )
        colltype = kwargs.pop('coll', ListCollection)
        if not issubclass(colltype, ListCollection):
            raise Exception(
                "List Property collections must derive ListCollection"
            )
        super(ListProperty, self).__init__(
            of=list_of, coll=ListCollection, **kwargs
        )
