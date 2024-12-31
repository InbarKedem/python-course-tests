import unittest


class TestPolynomial(unittest.TestCase):
    def test_polynomial_repr(self):
        p1 = Polynomial([3, 2, 1])
        p2 = Polynomial([1, 2])
        p3 = Polynomial([2, 0, 6])
        p4 = Polynomial([0, 0, 0])  # 0
        p5 = Polynomial([1, -2])  # x + -2
        p6 = Polynomial([2, 0, 6, 0])  # 2x^3 + 6x
        p7 = Polynomial([2, 0, -1, 0])  # 2x^3 + -x
        p8 = Polynomial([0])  # 0
        self.assertEqual(repr(p1), "3x^2 + 2x + 1")
        self.assertEqual(repr(p2), "x + 2")
        self.assertEqual(repr(p3), "2x^2 + 6")
        self.assertEqual(repr(p4), "0")
        self.assertEqual(repr(p5), "x + -2")
        self.assertEqual(repr(p6), "2x^3 + 6x")
        self.assertEqual(repr(p7), "2x^3 + -x")
        self.assertEqual(repr(p8), "0")

    def test_add(self):
        # p1 = 3x^2 + 2x + 1
        p1 = Polynomial([3, 2, 1])
        # p2 = x + 2
        p2 = Polynomial([1, 2])
        # p3 = 2x^2 + 6
        p3 = Polynomial([2, 0, 6])
        # p4 = 0 (the zero polynomial)
        p4 = Polynomial([0])

        # 1) p1 + p2 = 3x^2 + 3x + 3
        res_12 = p1 + p2
        self.assertEqual(str(res_12), "3x^2 + 3x + 3")
        self.assertIsInstance(res_12, Polynomial)

        # 2) p1 + p1 = 6x^2 + 4x + 2
        res_11 = p1 + p1
        self.assertEqual(str(res_11), "6x^2 + 4x + 2")
        self.assertIsInstance(res_11, Polynomial)

        # 3) p1 + p3 = (3+2)x^2 + (2+0)x + (1+6) = 5x^2 + 2x + 7
        res_13 = p1 + p3
        self.assertEqual(str(res_13), "5x^2 + 2x + 7")
        self.assertIsInstance(res_13, Polynomial)

        # 4) p1 + p4 = p1 (adding zero changes nothing)
        res_14 = p1 + p4
        self.assertEqual(str(res_14), "3x^2 + 2x + 1")
        self.assertIsInstance(res_14, Polynomial)

        """
        Test that after an addition resulting polynomial has no unwanted leading zeros.
        """
        # p1 = x^2 + 1 => [1, 0, 1]
        p5 = Polynomial([1, 0, 1])
        # p2 = -x^2 + 5 => [-1, 0, 5]
        p6 = Polynomial([-1, 0, 5])
        # Sum => (x^2 + 1) + (-x^2 + 5) => 6 (just a constant)
        # Internally, that might be [0, 0, 6] but after verify_zero => [6].
        result = p5 + p6
        self.assertEqual(result.coefficients, [6],
                         "Adding p1 + p2 should yield the constant polynomial [6].")

    def test_sub(self):
        p1 = Polynomial([1, 2, 3])  # x^2 + 2x + 3
        p2 = Polynomial([1, 2, 0])  # x^2 + 2

        # p1 - p1 => 0
        result1 = p1 - p1
        # Compare by string (repr) or by internal coefficients:
        self.assertEqual(str(result1), "0", "p1 - p1 should be the zero polynomial")
        # Also check the type:
        self.assertIsInstance(result1, Polynomial, "p1 - p1 should return a Polynomial object")

        # p1 - p2 => 3
        result2 = p1 - p2
        self.assertEqual(str(result2), "3", "p1 - p2 should be the constant polynomial 3")
        self.assertIsInstance(result2, Polynomial, "p1 - p2 should return a Polynomial object")

        # p3 = 3x^2 + 2x + 1 => [3,2,1]
        p3 = Polynomial([3, 2, 1])
        # p4 = 3x^2 + 2x + 1 => [3,2,1]
        p4 = Polynomial([3, 2, 1])
        # p3 - p4 => 0
        result = p3 - p4
        self.assertEqual(result.coefficients, [0],
                         "Subtracting identical polynomials should yield [0].")

    def test_mul(self):
        """
        Tests for the __mul__ (multiplication) operator.
        We assume p1 * p2 yields a new Polynomial whose coefficients
        reflect the product of the two.
        """
        # p1 = x + 2  => [1, 2]
        p1 = Polynomial([1, 2])
        # p2 = 2x + 1 => [2, 1]
        p2 = Polynomial([2, 1])
        # (x+2)(2x+1) = 2x^2 + (1+4)x + 2 = 2x^2 + 5x + 2
        product_12 = p1 * p2
        self.assertEqual(str(product_12), "2x^2 + 5x + 2",
                         "Multiplication failed for (x+2)*(2x+1).")
        self.assertIsInstance(product_12, Polynomial)

        # Multiply by 0 polynomial => result is 0
        # p3 = 0 => [0]
        p3 = Polynomial([0])
        product_13 = p1 * p3
        self.assertEqual(str(product_13), "0",
                         "Multiplication by zero polynomial should be 0.")
        self.assertIsInstance(product_13, Polynomial)

        # Another example:
        # p4 = x^2 + 1 => [1, 0, 1]
        p4 = Polynomial([1, 0, 1])
        # p2 * p4 = (2x+1)(x^2 + 1) = 2x^3 + 2x + x^2 + 1 => 2x^3 + x^2 + 2x + 1
        product_24 = p2 * p4
        self.assertEqual(str(product_24), "2x^3 + x^2 + 2x + 1",
                         "Multiplication mismatch for (2x+1)*(x^2+1).")
        self.assertIsInstance(product_24, Polynomial)

        p5 = Polynomial([1, 2])
        # p6 = 0 => [0]
        p6 = Polynomial([0])
        # p5 * p6 => 0 => [0]
        result = p5 * p6
        self.assertEqual(result.coefficients, [0],
                         "Multiplying by zero polynomial should yield [0].")
        # self.assertEqual(str(result), "0")

    def test_gt(self):
        """
        Tests for the __gt__ (greater than) operator.
        We'll compare the 'leading power' first, then leading coefficients if needed.
        """
        # p1 = x^2 + 2 => [1, 0, 2], highest power 2
        p1 = Polynomial([1, 0, 2])
        # p2 = x + 2 => [1, 2], highest power 1
        p2 = Polynomial([1, 2])
        # p3 = x^2 + 3 => [1, 0, 3], also highest power 2
        p3 = Polynomial([1, 0, 3])

        # Compare highest power: p1 > p2 => True (2 > 1)
        self.assertTrue(p1 > p2, "p1 should be greater than p2 because p1 has degree 2 vs degree 1.")

        # Opposite check: p2 > p1 => False
        self.assertFalse(p2 > p1, "p2 should not be greater than p1.")

        # Compare same power (degree 2) but different coefficients:
        # p3 = x^2 + 3 vs p1 = x^2 + 2
        # They share the same leading coefficient (1 for x^2), so the next difference is in constant term: 3 vs 2
        self.assertTrue(p3 > p1, "p3 should be greater than p1, since both are x^2 polynomials but 3 > 2.")

        # If polynomials are identical, p1 > p1 => False
        self.assertFalse(p1 > p1, "A polynomial should not be greater than itself.")

    def test_verify_zero(self):
        """
        Test the verify_zero function directly via the constructor
        (since typically you might call self.verify_zero() in __init__).
        """
        # Example 1: Leading zeros => [0, 0, 3, 5] should become [3, 5]
        p1 = Polynomial([0, 0, 3, 5])
        self.assertEqual(p1.coefficients, [3, 5],
                         "Leading zeros should be trimmed to [3, 5].")
        # Optionally check str representation, e.g. 3x + 5
        # self.assertEqual(str(p1), "3x + 5")

        # Example 2: All zeros => [0,0,0] should become [0]
        p2 = Polynomial([0, 0, 0])
        self.assertEqual(p2.coefficients, [0],
                         "All-zero polynomial should become [0].")
        # self.assertEqual(str(p2), "0")


# def test_hotel():
#     m1 = Minibar({'Coke': 10, 'Lemonade': 1}, {'Bamba': 8, 'Mars': 12})
#     m2 = Minibar({'Beer': 10, 'Lemonade': 4}, {'m&m': 6})
#     rooms = [Room(m2, 514, [], 5, True),
#              Room(m2, 210, ["Ronen", "Shir"], 6, True),
#              Room(m1, 102, ["Liat"], 7, False),
#              Room(m2, 223, [], 6, True)]
#     h = Hotel("Dan", rooms)
#     test_sep = '\n------------------'
#     print('PRINT m1:\n', m1, test_sep, sep="")
#     print('PRINT m2:\n', m2, test_sep, sep="")
#     print('PRINT h:\n', h, test_sep, sep="")
#     liat_room = h.send_cleaner('Liat')
#     print('CALL: h.send_cleaner("Liat")\n', liat_room, test_sep, sep="")
#     print('CALL: liat_room.eat("bamba")\n', liat_room.minibar.eat("bamba"), test_sep, sep="")
#     print('PRINT liat_room.minibar:\n', liat_room.minibar, test_sep, sep="")
#     print('CALL: liat_room.drink("lemonade")\n', liat_room.minibar.drink("lemonade"), test_sep, sep="")
#     print('PRINT liat_room.minibar:\n', liat_room.minibar, test_sep, sep="")
#     print('CALL: h.upgrade("Liat")\n', h.upgrade("Liat"), test_sep, sep="")
#
#     print('CALL: h.check_out("Ronen")\n', h.check_out("Ronen"), test_sep, sep="")
#     print('CALL: h.check_out("Ronen")\n', h.check_out("Ronen"), test_sep, sep="")
#     print('CALL: h.check_in(["Alice", "Wonder"], True)\n',
#           h.check_in(["Alice", "Wonder"], True), test_sep, sep="")
#     print('CALL: h.check_in(["Alex"], True)\n', h.check_in(["Alex"], True), test_sep,
#           sep="")
#     print('PRINT h:\n', h, test_sep, sep="")
#     print('CALL: h.check_in(["Oded", "Shani"], False)\n',
#           h.check_in(["Oded", "Shani"], False), test_sep, sep="")
#     print('CALL: h.check_in(["Oded", "Shani"], False)\n',
#           h.check_in(["Oded", "Shani"], False), test_sep, sep="")
#     print('CALL: h.check_out("Liat")\n', h.check_out("Liat"), test_sep, sep="")
#     print('CALL: h.check_out("Liat")\n', h.check_out("Liat"), test_sep, sep="")
#     print('PRINT h:\n', h, test_sep, sep="")


if __name__ == "__main__":
    unittest.main()
