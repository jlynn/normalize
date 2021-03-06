#
# This file is a part of the normalize python library
#
# normalize is free software: you can redistribute it and/or modify
# it under the terms of the MIT License.
#
# normalize is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# MIT License for more details.
#
# You should have received a copy of the MIT license along with
# normalize.  If not, refer to the upstream repository at
# http://github.com/hearsaycorp/normalize
#

"""
Structured exception module.

This makes structured exceptions as easy to use as string exceptions.  Simply
define an exception name and a format string; the base class takes care of the
rest.  Should you need any more sophisticated handling of an exception, it is
easy to change without affecting downstream users.
"""


class StringFormatException(Exception):
    message = "(uncustomized exception!)"

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        try:
            self.formatted = self.message.format(*args, **kwargs)
        except IndexError:
            raise PositionalExceptionFormatError(
                typename=type(self).__name__,
                received=repr(args),
            )
        except KeyError, e:
            raise KeywordExceptionFormatError(
                typename=type(self).__name__,
                missing=e[0],
                passed=repr(kwargs.keys()),
            )

    def __str__(self):
        return self.formatted

    def __getattr__(self, attrname):
        try:
            return self.kwargs[attrname]
        except KeyError:
            raise AttributeError(
                "no such attribute %s of %s" % (
                    attrname, type(self).__name__,
                )
            )

    def __getitem__(self, key):
        return self.args[key]

    def __repr__(self):
        return "%s%s(%s)" % (
            "exc." if self.__module__.endswith(".exc") else "",
            type(self).__name__, ", ".join(
                tuple("%r" % x for x in self.args) +
                tuple("%s=%r" % (k, v) for k, v in self.kwargs.iteritems())
            )
        )


# exception base classes
class CoercionError(StringFormatException, ValueError):
    pass


class FieldSelectorException(StringFormatException):
    pass


class PropertyDefinitionError(StringFormatException):
    pass


class PropertyTypeDefinitionError(StringFormatException):
    pass


class RecordDefinitionError(StringFormatException):
    pass


class StringFormatExceptionError(StringFormatException):
    pass


class SubclassError(StringFormatException):
    pass


class UsageException(StringFormatException):
    pass


class VisitorException(StringFormatException):
    pass


# concrete exception types
class AmbiguousConstruction(UsageException):
    message = "only init_dict or kwargs may be specified"


class CoerceError(CoercionError):
    message = (
        "coerce to {valuetype} for {prop} failed with value {value}: "
        "{func} raised: {exc}"
    )


class CoerceWithoutType(PropertyDefinitionError):
    message = (
        "In order to coerce types, the intended type must be known; "
        "pass isa=TYPE or isa=(TYPE, TYPE, ...) to Property()"
    )


class CollectionCoerceError(CoercionError):
    message = "Cannot interpret {giventype} as a {fortype} constructor"


class CollectionDefinitionError(SubclassError):
    message = "{property} must be defined in a {coll} subclass"


class CollRequiredError(PropertyDefinitionError):
    message = (
        "coll is required; specify coll type or use a sub-class "
        "like ListProperty"
    )


class CollTypeMismatch(PropertyDefinitionError):
    message = (
        "collection property 'isa' must match collection type"
    )


class CompareAsSignatureError(PropertyDefinitionError):
    message = (
        "compare_as functions may take 0 or 1 arguments; {module}.{func} "
        "wants {nargs}"
    )


class DefaultSignatureError(PropertyDefinitionError):
    message = (
        "default functions must have no required arguments (except "
        "'self'); {module}.{func} wants {nargs}"
    )


class DiffOptionsException(UsageException):
    message = "pass options= or DiffOptions constructor arguments; not both"


class FieldSelectorAttributeError(FieldSelectorException, AttributeError):
    message = "Could not find property specified by name: {name}"


class FieldSelectorKeyError(FieldSelectorException, KeyError):
    message = "Could not find Record specified by index: {key}"


class KeyHashError(StringFormatException):
    message = (
        "PK for {prop} returned an unhashable value; try setting "
        "a primary key in type {typename}"
    )


class KeywordExceptionFormatError(StringFormatExceptionError):
    message = (
        "{typename} raised without passing {missing}; saw only: {passed}"
    )


class LazyIsFalse(PropertyDefinitionError):
    message = "To make an eager property, do not pass lazy= to Property()"


class ListOfWhat(PropertyDefinitionError):
    message = (
        "List Properties must have a defined item type; pass of= "
        "or list_of= to the declaration"
    )


class ListPropertyMustDeriveListCollection(PropertyDefinitionError):
    message = (
        "List Property collections must derive ListCollection, and "
        "{got} doesn't"
    )


class MultipleInheritanceClash(SubclassError):
    message = (
        "Property {propname} defined by multiple base "
        "classes of {typename}"
    )


class PositionalArgumentsProhibited(PropertyDefinitionError):
    message = (
        "Positional arguments to Property constructors will only end "
        "in tears.  Convert to keyword argument form."
    )


class PositionalExceptionFormatError(StringFormatExceptionError):
    message = (
        "{typename} expects a positional format string; passed: "
        "{received}"
    )


class PropertiesNotKnown(RecordDefinitionError):
    message = (
        "{proplist} cannot be interpreted as a sequence of Properties "
        "in this class (string names or Property objects); first bad "
        "value: {badprop}"
    )


class PropertyArgumentNotKnown(PropertyDefinitionError, TypeError):
    message = (
        "No such keyword argument '{badkwarg}' of {proptypename} "
        "or any loaded subclass' constructor"
    )


class PropertyNotKnown(UsageException):
    message = "unknown property {propname} in {typename}"


class PropertyNotUnique(PropertyTypeDefinitionError):
    message = (
        "Duplicate ListProperties of the same class name defined in the "
        "same module.  Both end up being called {key} in my global map.  "
        "I'm sorry Dave, I'm afraid I can't let you do that."
    )


class PropertyTypeClash(StringFormatException):
    message = (
        "Both {oldtype} and {newtype} purport to provide the mix of "
        "traits: {traitlist} (perhaps a module import error is causing "
        "module initialization to happen multiple times?)"
    )


class PropertyTypeMismatch(PropertyDefinitionError):
    message = "Can't create {selected} property using {base} constructor"


class PropertyTypeMixNotFound(StringFormatException):
    message = (
        "Failed to find a Property type which provides traits {traitlist}"
    )


class PropertyTypeMixinNotPossible(PropertyTypeMixNotFound):
    message = (
        "Can't mix together a Property type for traits {traitlist}; "
        "none of the types which provide those traits provide: {missing}"
    )


class PropertyTypeMixinFailure(PropertyTypeMixNotFound):
    message = (
        "Failed to find a Property type which provides traits {traitlist}; "
        "but I did make these types: {newtypelist}"
    )


class ReadOnlyAttributeError(StringFormatException, AttributeError):
    message = "{attrname} is read-only"


class JsonRecordCoerceError(CoercionError):
    message = "Cannot interpret {given} as a {typename} constructor"


class ReservedPropertyName(RecordDefinitionError):
    message = "Attribute {attrname} is reserved"


class ValueCoercionError(CoercionError):
    message = (
        "Coerce function on proprety {prop} returned a bad coerced "
        "value {coerced} from input {value}"
    )


class VisitorOptionsException(UsageException):
    message = (
        "pass options= or Visitor.Options constructor arguments; not both"
    )


class VisitorPropError(VisitorException):
    message = (
        "failed to get '{prop_name}' from {record_type_name} instance at "
        "{fs}; {exception}"
    )


class VisitorGrokRecordError(VisitorException):
    message = (
        u"{val} found where I'm expecting to unpack a "
        u"{record_type_name} record at {field_selector}"
    )


class VisitorGrokCollectionError(VisitorGrokRecordError):
    message = (
        u"{val} found where I'm expecting to unpack a "
        u"{record_type_name} collection at {field_selector}"
    )


class VisitorTooSimple(VisitorException):
    message = (
        "{visitor} mapped over a Collection ({value_type_name}) with "
        "properties but the default reduce method clashed with a property; "
        "override reduce in your VisitorPattern class to resolve."
    )


class VisitorUnpackError(VisitorException, TypeError):
    message = (
        "Can't unpack collection at {fs}; expected {colltype}, got {value}"
    )
