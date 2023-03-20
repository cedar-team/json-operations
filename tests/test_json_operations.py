from unittest import TestCase

from parameterized import parameterized

from json_operations import (
    NEVER_MATCH,
    _and,
    _between,
    _equal,
    _greater,
    _greater_or_equal,
    _in,
    _intersection,
    _less,
    _less_or_equal,
    _not_equal,
    _not_in,
    _or,
    execute,
    execute_debug,
    get_keys,
)


class TestJsonOperations(TestCase):
    @parameterized.expand(
        [
            (1, 1, True),
            (1, 1.01, False),
            ("a", "a", True),
            ("a", "b", False),
            (None, None, True),
            (0, 0, True),
            (False, False, True),
            (True, True, True),
            (True, False, False),
        ]
    )
    def test_equal_operator(self, a, b, result):
        self.assertEqual(_equal(a, b), result)

    @parameterized.expand(
        [
            (1, 1, False),
            (1, 1.01, True),
            ("a", "a", False),
            ("a", "b", True),
            (None, None, False),
            (0, 0, False),
            (False, False, False),
            (True, True, False),
            (True, False, True),
        ]
    )
    def test_not_equal_operator(self, a, b, result):
        self.assertEqual(_not_equal(a, b), result)

    @parameterized.expand(
        [
            (0, 0, False),
            (1, 1, False),
            (1, 1.01, False),
            (1.01, 1, True),
            ("a", "a", False),
            ("ab", "b", False),
            ("a", "ab", False),
            (False, False, False),
            (True, True, False),
            (True, False, True),
            (False, True, False),
        ]
    )
    def test_greater_operator(self, a, b, result):
        self.assertEqual(_greater(a, b), result)

    @parameterized.expand(
        [
            (0, 0, False),
            (1, 1, False),
            (1, 1.01, True),
            (1.01, 1, False),
            ("a", "a", False),
            ("ab", "b", True),
            ("a", "ab", True),
            (False, False, False),
            (True, True, False),
            (True, False, False),
            (False, True, True),
        ]
    )
    def test_less_operator(self, a, b, result):
        self.assertEqual(_less(a, b), result)

    @parameterized.expand(
        [
            (0, 0, True),
            (1, 1, True),
            (1, 1.01, True),
            (1.01, 1, False),
            ("a", "a", True),
            ("ab", "b", True),
            ("a", "ab", True),
            ("ab", "a", False),
            (False, False, True),
            (True, True, True),
            (True, False, False),
            (False, True, True),
        ]
    )
    def test_less_or_equal_operator(self, a, b, result):
        self.assertEqual(_less_or_equal(a, b), result)

    @parameterized.expand(
        [
            (0, 0, True),
            (1, 1, True),
            (1, 1.01, False),
            (1.01, 1, True),
            ("a", "a", True),
            ("ab", "b", False),
            ("a", "ab", False),
            ("ab", "a", True),
            (False, False, True),
            (True, True, True),
            (True, False, True),
            (False, True, False),
        ]
    )
    def test_greater_or_equal_operator(self, a, b, result):
        self.assertEqual(_greater_or_equal(a, b), result)

    @parameterized.expand(
        [
            ("a", ["a", "b"], True),
            ("ab", ["a", "b"], False),
            ("c", ["a", "b"], False),
            ("b", "abc", True),
            ("d", "abc", False),
            ("bc", "abcd", True),
            ("", "", True),
            ("", "a", True),
            ("", [""], True),
            ("", ["a"], False),
        ]
    )
    def test_in_operator(self, a, b, result):
        self.assertEqual(_in(a, b), result)

    @parameterized.expand(
        [
            ("a", ["a", "b"], False),
            ("ab", ["a", "b"], True),
            ("c", ["a", "b"], True),
            ("b", "abc", False),
            ("d", "abc", True),
            ("bc", "abcd", False),
            ("", "", False),
            ("", "a", False),
            ("", [""], False),
            ("", ["a"], True),
        ]
    )
    def test_not_in_operator(self, a, b, result):
        self.assertEqual(_not_in(a, b), result)

    @parameterized.expand(
        [
            (2, 1, 3, True),
            (1, 1, 3, True),
            (3, 1, 3, True),
            (0.99, 1, 3, False),
            (3.01, 1, 3, False),
            (0, 1, 3, False),
            (0, -1, 1, True),
            (-2, -3, -1, True),
            (1.15, 1.1, 1.2, True),
        ]
    )
    def test_between_operator(self, val, low, high, result):
        self.assertEqual(_between(val, [low, high]), result)

    @parameterized.expand(
        [
            ([], [], False),
            ([0], [0], True),
            ([1, 0], [0, 2], True),
            ([1, 2, 3], [3], True),
            ([1, "2", 3], ["2"], True),
            ([1], ["1"], False),
            ([], [0], False),
            ([0], [], False),
        ]
    )
    def test_intersection_operator(self, a, b, result):
        self.assertEqual(_intersection(a, b), result)

    @parameterized.expand(
        [
            (2, [1, "a"]),
            (2, ["a", 1]),
            ("hello", [1, 2]),
            (1, [1]),
            (1, []),
        ]
    )
    def test_between_operator(self, val, vals):
        with self.assertRaises(TypeError):
            _between(val, vals)

    @parameterized.expand(
        [
            (1, "1"),
            (0, None),
            (0, False),
            (False, None),
        ]
    )
    def test_operator_error(self, a, b):
        with self.assertRaises(TypeError):
            _equal(a, b)

        with self.assertRaises(TypeError):
            _not_equal(a, b)

        with self.assertRaises(TypeError):
            _less(a, b)

        with self.assertRaises(TypeError):
            _greater(a, b)

    def test_and_operator(self):
        self.assertEqual(_and(), True)
        self.assertEqual(_and(False), False)
        self.assertEqual(_and(True), True)
        self.assertEqual(_and(True, False), False)
        self.assertEqual(_and(False, False), False)
        self.assertEqual(_and(True, True), True)
        self.assertEqual(_and(True, True, True), True)
        self.assertEqual(_and(True, False, True), False)

    def test_or_operator(self):
        self.assertEqual(_or(), False)
        self.assertEqual(_or(False), False)
        self.assertEqual(_or(True), True)
        self.assertEqual(_or(True, False), True)
        self.assertEqual(_or(False, False), False)
        self.assertEqual(_or(True, True), True)
        self.assertEqual(_or(True, True, True), True)
        self.assertEqual(_or(True, False, True), True)
        self.assertEqual(_or(False, False, False), False)

    @parameterized.expand(
        [
            # 100.01 != 100
            (
                [
                    "==",
                    ["key", "customer_balance"],
                    100,
                ],
                dict(
                    customer_balance=100.01,
                ),
                False,
            ),
            (
                [
                    "in",
                    ["key", "division"],
                    ["something", "my_division"],
                ],
                dict(
                    division="my_division",
                ),
                True,
            ),
            (
                [
                    "in",
                    ["key", "division"],
                    ["something", "not_my_division"],
                ],
                dict(
                    division="my_division",
                ),
                False,
            ),
            (
                [
                    "==",
                    ["key", "customer_balance"],
                    100,
                ],
                dict(
                    customer_balance=100,
                ),
                True,
            ),
            (
                [
                    "&",
                    ["key", "ids"],
                    [2],
                ],
                dict(
                    ids=[3],
                ),
                False,
            ),
            (
                [
                    "&",
                    ["key", "ids"],
                    [2],
                ],
                dict(
                    ids=[1, 2],
                ),
                True,
            ),
            (
                [
                    "in",
                    "b",
                    ["key", "items"],
                ],
                dict(
                    items=["a", "b", "c"],
                ),
                True,
            ),
            (
                [
                    "and",
                    [">", ["key", "customer_balance"], 100],
                    [">", ["key", "age"], 50],
                ],
                dict(customer_balance=101, age=51),
                True,
            ),
            (
                [
                    "or",
                    [
                        "and",
                        [">", ["key", "customer_balance"], 100],
                        ["<", ["key", "age"], 99],
                    ],
                    [
                        "and",
                        ["==", ["key", "type"], "magic"],
                        ["!=", ["key", "name"], "something"],
                    ],
                ],
                dict(customer_balance=20, age=98, type="magic", name="not_something"),
                True,
            ),
            # Balance greater than 100, but age not less than 30
            (
                [
                    "and",
                    [">", ["key", "customer_balance"], 100],
                    ["<", ["key", "age"], 30],
                ],
                dict(customer_balance=101, age=30),
                False,
            ),
            (
                [
                    "and",
                    ["btw", ["key", "customer_balance"], [100, 200]],
                ],
                dict(customer_balance=101),
                True,
            ),
        ]
    )
    def test_json_function(self, a, b, result):
        self.assertEqual(
            execute(a, b),
            result,
        )

    @parameterized.expand(
        [
            (
                [
                    "==",
                    ["key", "customer_balance"],
                    100,
                ],
                [dict(name="customer_balance", type="number", index=0)],
            ),
            (
                [
                    "==",
                    ["key", "customer_balance"],
                    True,
                ],
                [dict(name="customer_balance", type="boolean", index=0)],
            ),
            (
                [
                    "==",
                    ["key", "customer_something"],
                    ["key", "customer_another"],
                ],
                [
                    dict(
                        name="customer_something",
                        type=["number", "string", "boolean"],
                        index=0,
                    ),
                    dict(
                        name="customer_another",
                        type=["number", "string", "boolean"],
                        index=1,
                    ),
                ],
            ),
            (
                [
                    "==",
                    100,
                    ["key", "customer_balance"],
                ],
                [dict(name="customer_balance", type="number", index=1)],
            ),
            (
                [
                    "==",
                    ["key", "customer_name"],
                    "hello",
                ],
                [dict(name="customer_name", type="string", index=0)],
            ),
            (
                [
                    ">",
                    100,
                    ["key", "customer_balance"],
                ],
                [dict(name="customer_balance", type="number", index=1)],
            ),
            (
                [
                    ">",
                    ["key", "customer_payment_plan"],
                    ["key", "customer_balance"],
                ],
                [
                    dict(name="customer_payment_plan", type="number", index=0),
                    dict(name="customer_balance", type="number", index=1),
                ],
            ),
            (
                [
                    "in",
                    "hello",
                    ["key", "customer_types"],
                ],
                [
                    dict(name="customer_types", type=["string", "array"], index=1),
                ],
            ),
            (
                [
                    "in",
                    ["key", "customer_type"],
                    "hello,",
                ],
                [
                    dict(
                        name="customer_type",
                        type=["string", "number", "boolean"],
                        index=0,
                    ),
                ],
            ),
            (
                [
                    "in",
                    ["key", "customer_type"],
                    "hello,",
                ],
                [
                    dict(
                        name="customer_type",
                        type=["string", "number", "boolean"],
                        index=0,
                    ),
                ],
            ),
            (
                [
                    "and",
                    [
                        "==",
                        "hello",
                        ["key", "customer_name"],
                    ],
                    [
                        "==",
                        ["key", "customer_balance"],
                        100,
                    ],
                ],
                [
                    dict(name="customer_name", type="string", index=1),
                    dict(name="customer_balance", type="number", index=0),
                ],
            ),
            (
                [
                    "or",
                    [
                        "or",
                        [
                            ">",
                            ["key", "key1"],
                            100,
                        ],
                        [
                            "<=",
                            ["key", "key2"],
                            100,
                        ],
                        [
                            "==",
                            ["key", "key3"],
                            "test",
                        ],
                    ],
                    [
                        "and",
                        [
                            "in",
                            ["key", "key4"],
                            ["key", "key5"],
                        ],
                        [
                            "null",
                            ["key", "key6"],
                        ],
                        [
                            "!null",
                            ["key", "key7"],
                        ],
                        ["btw", ["key", "key8"], [1, 3]],
                    ],
                ],
                [
                    dict(name="key1", type="number", index=0),
                    dict(name="key2", type="number", index=0),
                    dict(name="key3", type="string", index=0),
                    dict(name="key4", type=["string", "number", "boolean"], index=0),
                    dict(name="key5", type=["string", "array"], index=1),
                    dict(name="key6", type=None, index=0),
                    dict(name="key7", type=None, index=0),
                    dict(name="key8", type="number", index=0),
                ],
            ),
        ]
    )
    def test_get_keys(self, a, result):
        self.assertEqual(
            get_keys(a),
            result,
        )

    @parameterized.expand(
        [
            # 100.01 != 100
            (
                [
                    "==",
                    ["key", "customer_balance"],
                    100,
                ],
                dict(
                    customer_balance=100.01,
                ),
                {"": False},
            ),
            (
                [
                    "in",
                    ["key", "division"],
                    ["something", "my_division"],
                ],
                dict(
                    division="my_division",
                ),
                {"": True},
            ),
            (
                [
                    "in",
                    ["key", "division"],
                    ["something", "not_my_division"],
                ],
                dict(
                    division="my_division",
                ),
                {"": False},
            ),
            (
                [
                    "==",
                    ["key", "customer_balance"],
                    100,
                ],
                dict(
                    customer_balance=100,
                ),
                {"": True},
            ),
            (
                [
                    "in",
                    "b",
                    ["key", "items"],
                ],
                dict(
                    items=["a", "b", "c"],
                ),
                {"": True},
            ),
            (
                [
                    "and",
                    [">", ["key", "customer_balance"], 100],
                    [">", ["key", "age"], 50],
                ],
                dict(customer_balance=101, age=51),
                {"0": True, "1": True, "": True},
            ),
            (
                [
                    "or",
                    [
                        "and",
                        [">", ["key", "customer_balance"], 100],
                        ["<", ["key", "age"], 99],
                    ],
                    [
                        "and",
                        ["==", ["key", "type"], "magic"],
                        ["!=", ["key", "name"], "something"],
                    ],
                ],
                dict(customer_balance=20, age=98, type="magic", name="not_something"),
                {
                    "0.0": False,
                    "0.1": True,
                    "0": False,
                    "1.0": True,
                    "1.1": True,
                    "1": True,
                    "": True,
                },
            ),
            # Balance greater than 100, but age not less than 30
            (
                [
                    "and",
                    [">", ["key", "customer_balance"], 100],
                    ["<", ["key", "age"], 30],
                ],
                dict(customer_balance=101, age=30),
                {"0": True, "1": False, "": False},
            ),
        ]
    )
    def test_execute_debug_function(self, a, b, result):
        self.assertEqual(
            execute_debug(a, b),
            result,
        )

    @parameterized.expand(
        [
            # 100.01 != 100
            (
                [
                    "==",
                    ["key", "customer_balance"],
                    100,
                ],
                dict(
                    customer_balance=NEVER_MATCH,
                ),
                False,
            ),
            (
                [
                    "in",
                    ["key", "division"],
                    ["something", "my_division"],
                ],
                dict(
                    division=NEVER_MATCH,
                ),
                False,
            ),
            (
                [
                    "nin",
                    ["key", "division"],
                    ["something", "my_division"],
                ],
                dict(
                    division=NEVER_MATCH,
                ),
                False,
            ),
            (
                [">", ["key", "customer_balance"], 100],
                dict(customer_balance=NEVER_MATCH),
                False,
            ),
            (
                ["<", ["key", "customer_balance"], 100],
                dict(customer_balance=NEVER_MATCH),
                False,
            ),
            (
                ["<=", ["key", "customer_balance"], 100],
                dict(customer_balance=NEVER_MATCH),
                False,
            ),
            (
                [">=", ["key", "customer_balance"], 100],
                dict(customer_balance=NEVER_MATCH),
                False,
            ),
            (
                ["==", ["key", "has_insurance"], True],
                dict(has_insurance=NEVER_MATCH),
                False,
            ),
            (
                ["==", ["key", "has_insurance"], False],
                dict(has_insurance=NEVER_MATCH),
                False,
            ),
            (
                ["!=", ["key", "has_insurance"], True],
                dict(has_insurance=NEVER_MATCH),
                False,
            ),
            (
                ["!=", ["key", "has_insurance"], False],
                dict(has_insurance=NEVER_MATCH),
                False,
            ),
            (
                ["!=", ["key", "has_insurance"], False],
                dict(has_insurance=NEVER_MATCH),
                False,
            ),
            (
                ["null", ["key", "has_insurance"]],
                dict(has_insurance=NEVER_MATCH),
                False,
            ),
            (
                ["!null", ["key", "has_insurance"]],
                dict(has_insurance=NEVER_MATCH),
                False,
            ),
            (
                ["btw", ["key", "customer_balance"], [10, 20]],
                dict(customer_balance=NEVER_MATCH),
                False,
            ),
        ]
    )
    def test_never_match(self, a, b, result):
        self.assertEqual(
            execute(a, b),
            result,
        )
