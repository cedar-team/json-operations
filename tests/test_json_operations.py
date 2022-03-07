from unittest import TestCase

from parameterized import parameterized

from json_operations import (and_, equal, execute, greater, greater_or_equal,
                             in_, less, less_or_equal, not_equal, or_)


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
        self.assertEqual(equal(a, b), result)

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
        self.assertEqual(not_equal(a, b), result)

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
        self.assertEqual(greater(a, b), result)

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
        self.assertEqual(less(a, b), result)

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
        self.assertEqual(less_or_equal(a, b), result)

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
        self.assertEqual(greater_or_equal(a, b), result)

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
        self.assertEqual(in_(a, b), result)

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
            equal(a, b)

        with self.assertRaises(TypeError):
            not_equal(a, b)

        with self.assertRaises(TypeError):
            less(a, b)

        with self.assertRaises(TypeError):
            greater(a, b)

    def test_and_operator(self):
        self.assertEqual(and_(), True)
        self.assertEqual(and_(False), False)
        self.assertEqual(and_(True), True)
        self.assertEqual(and_(True, False), False)
        self.assertEqual(and_(False, False), False)
        self.assertEqual(and_(True, True), True)
        self.assertEqual(and_(True, True, True), True)
        self.assertEqual(and_(True, False, True), False)

    def test_or_operator(self):
        self.assertEqual(or_(), False)
        self.assertEqual(or_(False), False)
        self.assertEqual(or_(True), True)
        self.assertEqual(or_(True, False), True)
        self.assertEqual(or_(False, False), False)
        self.assertEqual(or_(True, True), True)
        self.assertEqual(or_(True, True, True), True)
        self.assertEqual(or_(True, False, True), True)
        self.assertEqual(or_(False, False, False), False)

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
        ]
    )
    def test_json_function(self, a, b, result):
        self.assertEqual(
            execute(a, b),
            result,
        )
