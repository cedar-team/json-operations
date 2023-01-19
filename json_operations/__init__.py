from functools import wraps
from typing import Dict, List, Sequence, Union

# This is a value that will never match any operator. It is useful when evaluating multiple
# rule sets and want to ignore rule sets targeting a specific field
NEVER_MATCH = object()


class JsonOperationError(Exception):
    pass


def get_json_schema() -> Dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema",
        "definitions": {
            "operationOrLiteral": {
                "anyOf": [
                    {"$def": "#"},
                    {"type": ["string", "number", "boolean", "null", "array"]},
                ]
            },
        },
        "oneOf": [
            {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": [
                    {
                        "enum": [
                            "=",
                            "==",
                            "!=",
                            ">",
                            ">=",
                            "<",
                            "<=",
                            "in",
                            "nin",
                            "!in",
                            "btw",
                        ]
                    },
                    {
                        "$def": "#/definitions/operationOrLiteral",
                    },
                    {
                        "$def": "#/definitions/operationOrLiteral",
                    },
                ],
                "additionalItems": False,
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
                "additionalItems": False,
            },
            {
                "type": "array",
                "minItems": 2,
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
    elif isinstance(val, bool):
        return "boolean"


def _use_type_from_val(operator):
    return operator in {">", "<", ">=", "<=", "=", "==", "!="}


def _get_type_from_operator(operator, index):
    if operator in {">", "<", ">=", "<=", "btw"}:
        return "number"
    elif operator in {"=", "==", "!="}:
        return ["number", "string", "boolean"]
    elif operator in {"in", "nin", "!in"}:
        if index == 0:
            return ["string", "number", "boolean"]
        elif index == 1:
            return ["string", "array"]


def _and(*args):
    return all(args)


def _or(*args):
    return any(args)


def _in(needle, stack):
    return needle in stack


def _not_in(needle, stack):
    # "not in" operator
    return needle not in stack


def _is_number(a):
    return isinstance(a, (int, float)) and not isinstance(a, bool)


def _same_type(*args):
    # Different number types aren't the same type, so bucket all numbers
    if all(_is_number(arg) for arg in args):
        return True

    # Check if all types are the same
    return len({type(arg) for arg in args}) == 1


def _raise_type_error(operator_str):
    def dec(fn):
        @wraps(fn)
        def inner(*args):
            if not _same_type(*args):
                error_type_msg = " and ".join(type(arg).__name__ for arg in args)
                raise TypeError(
                    f"'{operator_str}' not supported between instances of {error_type_msg}"
                )
            return fn(*args)

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


def _between(val, range):
    if not isinstance(range, list):
        raise TypeError("btw list is not a list")
    if len(range) != 2 or not _is_number(range[0]) or not _is_number(range[1]):
        raise TypeError("btw list must have to number type items")
    if not _is_number(val):
        raise TypeError(f"btw cannot be used with type {type(val)}")

    return range[0] <= val <= range[1]


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
    "nin": _not_in,
    "!in": _not_in,
    "btw": _between,
}

_nesting_operators = {"and", "or"}


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


def _execute_operation(operation: str, values):
    if NEVER_MATCH in values:
        return False

    return _operators[operation](*values)


def get_keys(json_operation: List) -> List[Dict]:
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
                type_from_operator
                and type_from_val
                and type_from_operator != type_from_val
                and type_from_val not in type_from_operator
            ):
                raise JsonOperationError(
                    f'Operation {json_operation} expects type "{type_from_operator}". But `{val}` is of type "{type_from_val}"'
                )

    return keys + subkeys


def _execute_base(json_operation: List, context, handler, prefix=""):
    # Stop the recursion, we have reached a literal
    if not isinstance(json_operation, list):
        return json_operation

    operator, *unparsed = json_operation
    if operator in _nesting_operators:
        values = [
            _execute_base(
                val,
                context,
                handler,
                prefix=".".join([prefix, str(index)]) if prefix else str(index),
            )
            for index, val in enumerate(unparsed)
        ]
    else:
        values = []
        for val in unparsed:
            # Check if it's a key operation
            if isinstance(val, list) and 2 >= len(val) <= 3 and val[0] == "key":
                values.append(_get_key(context, *val[1:]))
            else:
                values.append(val)

    if operator == "key":
        return _get_key(context, *values)

    if operator not in _operators:
        raise JsonOperationError(f"Invalid operator: {operator}. {json_operation}")

    try:
        return handler(_execute_operation(operator, values), prefix)
    except TypeError as e:
        raise JsonOperationError(f"{e}. {json_operation}")


def _boolean_handler(value, prefix):
    return value


def execute(json_operation: List, context) -> bool:
    return _execute_base(
        json_operation=json_operation, context=context, handler=_boolean_handler
    )


def execute_debug(json_operation: List, context) -> bool:
    results = []

    def _debug_handler(value, prefix):
        nonlocal results
        results.append((prefix, value))
        return value

    _execute_base(
        json_operation=json_operation, context=context, handler=_debug_handler
    )

    return dict(results)
