from functools import wraps
from typing import List, Sequence, Union


class JsonOperationError(Exception):
    pass




def get_json_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema",
        "definitions": {
            "operationOrLiteral": {
                "anyOf": [
                    {"$def": "#"},
                    {"type": ["string", "number", "boolean", "null"]},
                ]
            },
        },
        "oneOf": [
            {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": [
                    {"enum": ["=", "==", "!=", ">", ">=", "<", "<=", "in"]},
                    {
                        "$def": "#/definitions/operationOrLiteral",
                    },
                    {
                        "$def": "#/definitions/operationOrLiteral",
                    },
                ],
                "additionalItems": False
            },
            {
                "type": "array",
                "minItems": 2,
                "maxItems": 2,
                "items": [
                    {"enum": ["null", "!null", "key"]},
                    {
                        "$def": "#/definitions/operationOrLiteral",
                    },
                ],
                "additionalItems": False
            },
            {
                "type": "array",
                "minItems": 3,
                "items": [
                    {"enum": ["and", "or"]},
                    {
                        "$def": "#/definitions/operationOrLiteral",

                    },
                    {
                        "$def": "#/definitions/operationOrLiteral",
                    },
                ],
            },
        ],
    }

def _get_type_from_val(val):
    if _is_number(val):
        return "number"
    elif isinstance(val, str):
        return "string"

def _use_type_from_val(operator):
    return operator in {">", "<", ">=", "<=", "=", "==", "!="}


def _get_type_from_operator(operator, index):
    if operator in {">", "<", ">=", "<="}:
        return "number"
    elif operator in {"=", "==", "!="}:
        return ["number", "string"]
    elif operator in {"in"}:
        if index == 0:
            return ["string", "number"]
        elif index == 1:
            return ["string", "array"]

def _and(*args):
    return all(args)


def _or(*args):
    return any(args)


def _in(needle, stack):
    return needle in stack


def _is_number(a):
    return isinstance(a, (int, float)) and not isinstance(a, bool)


def _same_type(a, b):
    # Different number types aren't the same type, so bucket all numbers
    if _is_number(a) and _is_number(b):
        return True

    return type(a) == type(b)


def _raise_type_error(operator_str):
    def dec(fn):
        @wraps(fn)
        def inner(a, b):
            if not _same_type(a, b):
                raise TypeError(
                    f"'{operator_str}' not supported between instances of '{type(a).__name__}' and '{type(b).__name__}'"
                )
            return fn(a, b)

        return inner

    return dec


@_raise_type_error("==")
def _equal(a, b):
    return a == b


@_raise_type_error(">")
def _greater(a, b):
    return a > b


@_raise_type_error(">=")
def _greater_or_equal(a, b):
    return a >= b


@_raise_type_error("<")
def _less(a, b):
    return a < b


@_raise_type_error("<=")
def _less_or_equal(a, b):
    return a <= b


@_raise_type_error("!=")
def _not_equal(a, b):
    if not _same_type(a, b):
        raise TypeError(
            f"'!=' not supported between instances of '{type(a)}' and '{type(b)}'"
        )

    return a != b


def _null_(a):
    return a is None


def _not_null(a):
    return a is not None


_operators = {
    "=": _equal,
    "==": _equal,
    "!=": _not_equal,
    ">": _greater,
    ">=": _greater_or_equal,
    "<": _less,
    "<=": _less_or_equal,
    "and": _and,
    "or": _or,
    "null": _null_,
    "!null": _not_null,
    "in": _in,
}


def _get_key(context, key, default=None):
    # Gets the key from the context dictionary
    try:
        for key in str(key).split("."):
            try:
                context = context[key]
            except TypeError:
                context = context[int(key)]
    except (KeyError, TypeError, ValueError):
        return default
    else:
        return context


def get_keys(json_operation):
    operator, *unparsed = json_operation

    keys = []
    if operator == "key":
        keys.append(dict(name=unparsed[0], type=None, index=None))

    subkeys = []
    type_from_val = None
    val = None
    for index, item in enumerate(unparsed):
        if isinstance(item, list):
            results = get_keys(item)
            for result in results:
                if result["index"] is None:
                    result["index"] = index
            subkeys += results
        else:
            new_type_from_val = _get_type_from_val(item)
            if type_from_val and new_type_from_val != type_from_val:
                raise JsonOperationError(
                    f'Operation {json_operation}" has values of different types. `{val}` is of type "{type_from_val}". '
                    f'`{item}` is of type "{new_type_from_val}"'
                )
            type_from_val = new_type_from_val
            val = item

    for key in subkeys:
        if key["type"] is None:
            type_from_operator = _get_type_from_operator(operator, key["index"])
            if type_from_val and _use_type_from_val(operator):
                key["type"] = type_from_val
            elif type_from_operator:
                key["type"] = type_from_operator

            # Check to make sure the types are compatible
            if (
                type_from_operator and type_from_val and type_from_operator != type_from_val and type_from_val not in type_from_operator):
                raise JsonOperationError(
                    f'Operation {json_operation} expects type "{type_from_operator}". But `{val}` is of type "{type_from_val}"'
                )

    return keys + subkeys


def execute(json_operation, context):
    # Stop the recursion, we have reached a literal
    if not isinstance(json_operation, list):
        return json_operation

    operator, *unparsed = json_operation
    values = [execute(val, context) for val in unparsed]

    if operator == "key":
        return _get_key(context, *values)

    if operator not in _operators:
        raise JsonOperationError(f"Invalid operator: {operator}. {json_operation}")

    try:
        return _operators[operator](*values)
    except TypeError as e:
        raise JsonOperationError(f"{e}. {json_operation}")
