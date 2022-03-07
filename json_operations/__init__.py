from functools import wraps
from typing import List, Sequence, Union


class OperationError(Exception):
    pass


def get_json_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema",
        "definitions": {
            "operationOrLiteral": {
                "oneOf": [
                    {"$def": "#/definitions/operation"},
                    {"type": ["string", "number", "boolean", "null"]},
                ]
            },
            "operation": {
                "oneOf": [
                    {
                        "type": "array",
                        "prefixItems": [
                            {"enum": ["=", "==", "!=", ">", ">=", "<", "<=", "in"]},
                            {
                                "def": "#/definitions/operationOrLiteral",
                            },
                            {
                                "def": "#/definitions/operationOrLiteral",
                            },
                        ],
                    },
                    {
                        "type": "array",
                        "prefixItems": [
                            {"enum": ["null", "!null", "key"]},
                            {
                                "def": "#/definitions/operationOrLiteral",
                            },
                        ],
                    },
                    {
                        "type": "array",
                        "prefixItems": [
                            {"enum": ["and", "or"]},
                        ],
                        "items": {
                            "def": "#/definitions/operationOrLiteral",
                        },
                    },
                ],
            },
        },
        "$def": "#/definitions/operation",
    }


def and_(*args):
    return all(args)


def or_(*args):
    return any(args)


def in_(needle, stack):
    return needle in stack


def is_number(a):
    return isinstance(a, (int, float)) and not isinstance(a, bool)


def same_type(a, b):
    # Different number types aren't the same type, so bucket all numbers
    if is_number(a) and is_number(b):
        return True

    return type(a) == type(b)


def raise_type_error(operator_str):
    def dec(fn):
        @wraps(fn)
        def inner(a, b):
            if not same_type(a, b):
                raise TypeError(
                    f"'{operator_str}' not supported between instances of '{type(a).__name__}' and '{type(b).__name__}'"
                )
            return fn(a, b)

        return inner

    return dec


@raise_type_error("==")
def equal(a, b):
    return a == b


@raise_type_error(">")
def greater(a, b):
    return a > b


@raise_type_error(">=")
def greater_or_equal(a, b):
    return a >= b


@raise_type_error("<")
def less(a, b):
    return a < b


@raise_type_error("<=")
def less_or_equal(a, b):
    return a <= b


@raise_type_error("!=")
def not_equal(a, b):
    if not same_type(a, b):
        raise TypeError(
            f"'!=' not supported between instances of '{type(a)}' and '{type(b)}'"
        )

    return a != b


def null_(a):
    return a is None


def not_null(a):
    return a is not None


operators = {
    "=": equal,
    "==": equal,
    "!=": not_equal,
    ">": greater,
    ">=": greater_or_equal,
    "<": less,
    "<=": less_or_equal,
    "and": and_,
    "or": or_,
    "null": null_,
    "!null": not_null,
    "in": in_,
}


def get_key(context, key, default=None):
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


def execute(json_operation, context):
    # Stop the recursion, we have reached a literal
    if not isinstance(json_operation, list):
        return json_operation

    operator, *unparsed = json_operation
    values = [execute(val, context) for val in unparsed]

    if operator == "key":
        return get_key(context, *values)

    if operator not in operators:
        raise OperationError(f"Invalid operator: {operator}. {json_operation}")

    try:
        return operators[operator](*values)
    except TypeError as e:
        raise OperationError(f"{e}. {json_operation}")
