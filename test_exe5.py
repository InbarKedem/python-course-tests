import unittest

from unittest.mock import patch
import io


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

        # p9 = 2x^3 - 2x^2 + 5 => [2, -2, 0, 5]
        p9 = Polynomial([2, -2, 0, 5])
        # p10 = 2x^3 - 2x^2 - 5 => [2, -2, 0, -5]
        p10 = Polynomial([2, -2, 0, -5])
        # p9 + p10 => (2+2)x^3 + (-2-2)x^2 + (5-5) => 4x^3 + -4x^2 + 0
        # which should simplify to [4, -4, 0, 0], i.e. 4x^3 - 4x^2
        sum_9_10 = p9 + p10
        self.assertEqual(
            sum_9_10.coefficients, [4, -4, 0, 0],
            "Expected 4x^3 - 4x^2 after adding p9 and p10."
        )

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

        # p11 = 5x^3 - x + 2 => [5, 0, -1, 2]
        p11 = Polynomial([5, 0, -1, 2])
        # p12 = 2x^3 - x + 7 => [2, 0, -1, 7]
        p12 = Polynomial([2, 0, -1, 7])
        # p11 - p12 => (5-2)x^3 + (0-0)x^2 + (-1 - -1)x + (2 - 7)
        #           => 3x^3 + 0x^2 + 0x - 5 => [3, 0, 0, -5]
        diff_11_12 = p11 - p12
        self.assertEqual(
            diff_11_12.coefficients, [3, 0, 0, -5],
            "Expected 3x^3 - 5 after subtracting p12 from p11."
        )

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

        # Now compare polynomials with same degree but different leading coefficients:
        # p17 = 2x^3 + 1 => [2, 0, 0, 1]
        p17 = Polynomial([2, 0, 0, 1])
        # p18 = -3x^3 + 10 => [-3, 0, 0, 10]
        p18 = Polynomial([-3, 0, 0, 10])
        # Both are degree 3, but leading coefficients differ: 2 vs -3 => p17 > p18
        self.assertTrue(
            p17.__gt__(p18),
            "p17 should be greater because 2 (leading coeff) > -3 for the same degree."
        )
        self.assertFalse(
            p18.__gt__(p17),
            "p18 is not greater than p17 because -3 < 2 at the leading term."
        )

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


class TestMinibar(unittest.TestCase):

    # ----------- Setup method ----------- #
    def setUp(self):
        # General test minibars
        self.minibar = Minibar({'Coke': 10, 'Water': 5}, {'Chips': 3, 'Cookies': 2})
        self.drinks1 = {'Coke': 3, 'BEER': 5, 'WaTeR': 10}
        self.snacks1 = {'M&M': 10, 'Cake': 40, 'cookies': 23}
        self.minibar1 = Minibar(self.drinks1, self.snacks1)
        self.minibar2 = Minibar({}, {})
        self.minibar3 = Minibar({'Coke': 3, 'BEER': 5, 'WaTeR': 10}, {'M&M': 10, 'Cake': 40, 'cookies': 23})

        # Minibars for __repr__ tests
        self.minibar4 = Minibar({'Coke': 1, 'WATER': 3}, {'M&M': 10, 'cake': 30})
        self.minibar5 = Minibar({'Water': 1}, {'M&M': 10})
        self.minibar6 = Minibar({}, {})
        self.minibar7 = Minibar({'Juice': 2}, {})
        self.minibar8 = Minibar({}, {'Chips': 15})

    # ----------- Tests for Initialization ----------- #
    def test_initialization(self):
        """Tests initialization of minibar attributes."""
        self.assertEqual(self.minibar.drinks, {'Coke': 10, 'Water': 5})
        self.assertEqual(self.minibar.snacks, {'Chips': 3, 'Cookies': 2})
        self.assertEqual(self.minibar.bill, 0)

    # ----------- Tests for Eat ----------- #
    def test_eat_existing_snack(self):
        """Tests eating an existing snack and reducing its price from the bill."""
        self.minibar3.eat('M&M')
        self.assertEqual(self.minibar3.bill, 10)
        self.assertNotIn('M&M', self.minibar3.snacks)

    @patch('builtins.print')  # Mock the print function
    def test_eat_non_existing_snack(self, mock_print):
        """Tests eating a snack that does not exist and checks the printed message."""
        self.minibar3.eat('Kinder Bueno')
        self.assertEqual(self.minibar3.bill, 0)
        self.assertEqual(self.minibar3.snacks, {'M&M': 10, 'Cake': 40, 'cookies': 23})
        mock_print.assert_called_once_with("The snack kinder bueno was not found.")

    def test_eat_case_insensitive(self):
        """Tests eating a snack with lowercase input while the dictionary has mixed case."""
        self.minibar3.eat('m&m')
        self.assertEqual(self.minibar3.bill, 10)
        self.assertNotIn('M&M', self.minibar3.snacks)

    # ----------- Tests for Drink ----------- #
    def test_drink_existing_drink_lowercase(self):
        """Tests drinking an existing drink with lowercase input."""
        self.minibar3.drink('water')
        self.assertEqual(self.minibar3.bill, 21)
        self.assertEqual(self.minibar3.drinks['WaTeR'], 9)
        self.assertIn('WaTeR', self.minibar3.drinks)

    @patch('builtins.print')  # Mock the print function
    def test_drink_non_existing_drink(self, mock_print):
        """Tests drinking a drink that does not exist and checks the printed message."""
        self.minibar3.drink('Soda')
        self.assertEqual(self.minibar3.bill, 0)
        self.assertEqual(self.minibar3.drinks, {'Coke': 3, 'BEER': 5, 'WaTeR': 10})
        mock_print.assert_called_once_with("The drink soda was not found.")

    def test_drink_case_insensitive(self):
        """Tests drinking a drink with different letter cases."""
        self.minibar3.drink('WaTeR')
        self.assertEqual(self.minibar3.bill, 21)
        self.assertEqual(self.minibar3.drinks['WaTeR'], 9)
        self.assertIn('WaTeR', self.minibar3.drinks)

    def test_drink_removes_empty_drink(self):
        """Tests that a drink is removed when its quantity reaches 0."""
        self.minibar3.drink('Coke')
        self.minibar3.drink('Coke')
        self.minibar3.drink('Coke')
        self.assertEqual(self.minibar3.bill, 63)
        self.assertNotIn('Coke', self.minibar3.drinks)

    @patch('builtins.print')  # Mock the print function
    def test_drink_empty_drinks(self, mock_print):
        """Tests drinking when the drinks dictionary is empty."""
        minibar = Minibar({}, {})
        minibar.drink('Coke')
        self.assertEqual(minibar.bill, 0)
        self.assertEqual(minibar.drinks, {})
        mock_print.assert_called_once_with("The drink coke was not found.")

    # ----------- Tests for __repr__ ----------- #
    def test_repr_with_full_minibar(self):
        """Tests __repr__ with drinks and snacks available, and no bill."""
        expected_output = "Drinks: Coke (1), WATER (3)\nSnacks: M&M (10), cake (30)\nNo bill yet"
        self.assertEqual(repr(self.minibar4), expected_output)

    def test_repr_with_empty_minibar(self):
        """Tests __repr__ with no drinks and no snacks."""
        expected_output = "No drinks left\nNo snacks left\nNo bill yet"
        self.assertEqual(repr(self.minibar6), expected_output)

    def test_repr_with_no_snacks(self):
        """Tests __repr__ with drinks available but no snacks."""
        expected_output = "Drinks: Juice (2)\nNo snacks left\nNo bill yet"
        self.assertEqual(repr(self.minibar7), expected_output)

    def test_repr_with_no_drinks(self):
        """Tests __repr__ with snacks available but no drinks."""
        expected_output = "No drinks left\nSnacks: Chips (15)\nNo bill yet"
        self.assertEqual(repr(self.minibar8), expected_output)

    def test_repr_with_bill_and_no_drinks_snacks(self):
        """Tests __repr__ when no drinks and no snacks are left, and there is a bill."""
        self.minibar5.drink('water')
        self.minibar5.eat('M&M')
        expected_output = "No drinks left\nNo snacks left\nBill: 31"
        self.assertEqual(repr(self.minibar5), expected_output)

    def test_repr_with_bill_and_items_left(self):
        """Tests __repr__ when drinks and snacks are available, and there is a bill."""
        self.minibar4.drink('Coke')
        expected_output = "Drinks: WATER (3)\nSnacks: M&M (10), cake (30)\nBill: 21"
        self.assertEqual(repr(self.minibar4), expected_output)

    def test_repr_no_trailing_newline(self):
        """Tests that the __repr__ output does not end with a newline character (\n)."""
        output = repr(self.minibar4)  # Use an example minibar with drinks and snacks
        self.assertFalse(output.endswith('\n'), "Output should not end with a newline.")

    # ----------- Tests for class Room ----------- #


class TestRoom(unittest.TestCase):

    # ----------- Setup method ----------- #
    def setUp(self):
        """Initializes a minibar for testing."""
        self.minibar = Minibar({'Coke': 10, 'Water': 5}, {'Chips': 3, 'Cookies': 2})
        self.empty_minibar = Minibar({}, {})  # Empty minibar for edge cases

        # Create rooms
        self.r1 = Room(self.minibar, 223, ["Dana", "Ron"], 5, False)
        self.r2 = Room(self.minibar, 257, ["Omer"], 10, False)
        self.r_better = Room(self.minibar, 630, [], 4, True)

    # ----------- Tests for type errors ----------- #

    def test_type_error_clean_level(self):
        """Tests type error for clean_level that is not an integer."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], "clean", True, 0.5)
            mock_print.assert_called_once_with("type error")

    def test_type_error_is_suite(self):
        """Tests type error for is_suite that is not a boolean."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], 5, "yes", 0.5)
            mock_print.assert_called_once_with("type error")

    def test_type_error_satisfaction(self):
        """Tests type error for satisfaction that is not a float or int."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], 5, True, "high")
            mock_print.assert_called_once_with("type error")

    def test_type_error_guests_not_list(self):
        """Tests type error for guests when input is not a list."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, "Dana", 5, True, 0.5)
            mock_print.assert_called_once_with("type error")

    def test_type_error_guests_invalid_element(self):
        """Tests type error for guests when elements are not strings."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana", 123], 5, True, 0.5)
            mock_print.assert_called_once_with("type error")

    # ----------- Tests for value errors ----------- #

    def test_value_error_number_length(self):
        """Tests value error for number that does not have 3 digits and all other types are correct."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 10, ["Dana"], 5, True, 0.5)
            mock_print.assert_called_once_with("value error")

    def test_value_error_number_floor_starts_with_zero(self):
        """Tests value error for number has more than 3 digits and all other types are correct."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 1041, ["Dana"], 5, True, 0.5)  # Invalid floor starting with 0
            mock_print.assert_called_once_with("value error")

    def test_value_error_number_room_invalid(self):
        """Tests value error for number with invalid room number and all other types are correct."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 150, ["Dana"], 5, True, 0.5)
            mock_print.assert_called_once_with("value error")

    def test_value_error_satisfaction_below_0(self):
        """Tests value error for satisfaction below 0."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], 5, True, -0.1)
            mock_print.assert_called_once_with("value error")

    def test_value_error_satisfaction_above_1(self):
        """Tests value error for satisfaction above 1."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], 5, True, 1.1)
            mock_print.assert_called_once_with("value error")

    def test_value_error_satisfaction_above_1_2(self):
        """Tests value error for satisfaction above 1 and an int."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], 5, True, 2)
            mock_print.assert_called_once_with("value error")

    # ----------- Combined tests for multiple errors ----------- #

    def test_multiple_type_errors_once(self):
        """Tests that multiple type errors print only once."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana", 123], "clean", "yes", "high")
            mock_print.assert_called_once_with("type error")

    def test_multiple_value_errors_once(self):
        """Tests that multiple value errors print only once."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 10, ["Dana"], 5, True, 1.5)
            mock_print.assert_called_once_with("value error")

    # ----------- Additional Tests ----------- #

    def test_valid_input(self):
        """Tests valid input where no errors should be printed."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana", "Ron"], 5, True, 0.5)
            mock_print.assert_not_called()

    def test_edge_case_lowest_floor(self):
        """Tests the lowest valid floor (1)."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], 5, True, 0.5)
            mock_print.assert_not_called()

    def test_edge_case_highest_floor(self):
        """Tests the highest valid floor (9)."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 940, ["Dana"], 5, True, 0.5)
            mock_print.assert_not_called()

    def test_edge_case_satisfaction_zero(self):
        """Tests satisfaction at the lower edge (0.0)."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], 5, True, 0.0)
            mock_print.assert_not_called()

    def test_edge_case_satisfaction_one(self):
        """Tests satisfaction at the upper edge (1.0)."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], 5, True, 1.0)
            mock_print.assert_not_called()

    def test_value_error_valid_floor_invalid_room(self):
        """Tests value error for valid floor but invalid room number."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 141, ["Dana"], 5, True, 0.5)
            mock_print.assert_called_once_with("value error")

    def test_type_error_and_value_error_only_type_printed(self):
        """Tests both type and value errors but only type error is printed."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 999, ["Dana", 123], "dirty", "no", 1.5)  # Both errors
            mock_print.assert_called_once_with("type error")

    def test_type_error_clean_level_and_value_error_number(self):
        """Tests type error for clean_level and value error for number, only type error printed."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 1041, ["Dana"], "clean", True, 0.5)  # Invalid length and clean level
            mock_print.assert_called_once_with("type error")

    # ----------- Additional Tests for Type Errors ----------- #

    def test_type_error_guests_and_clean_level(self):
        """Tests type errors for guests and clean_level together."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, "Dana", "clean", True, 0.5)
            mock_print.assert_called_once_with("type error")

    def test_type_error_clean_level_and_is_suite(self):
        """Tests type errors for clean_level and is_suite together."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], "clean", "yes", 0.5)
            mock_print.assert_called_once_with("type error")

    def test_type_error_all_except_number(self):
        """Tests type errors for all fields except number."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, "Dana", "clean", "yes", "high")
            mock_print.assert_called_once_with("type error")

    def test_type_error_invalid_minibar_and_clean_level(self):
        """Tests type errors for minibar (not Minibar object) and clean_level."""
        with patch('builtins.print') as mock_print:
            Room({}, 101, ["Dana"], "clean", True, 0.5)
            mock_print.assert_called_once_with("type error")

    def test_type_error_guests_and_satisfaction(self):
        """Tests type errors for guests and satisfaction together."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, 123, 5, True, "high")
            mock_print.assert_called_once_with("type error")

    # ----------- Additional Tests for Value Errors ----------- #

    def test_value_error_number_and_satisfaction(self):
        """Tests value errors for invalid number and satisfaction together."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 999, ["Dana"], 5, True, 1.5)
            mock_print.assert_called_once_with("value error")

    def test_value_error_floor_and_room_number(self):
        """Tests value errors for invalid floor and invalid room number together."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 150, ["Dana"], 5, True, 0.5)
            mock_print.assert_called_once_with("value error")

    def test_value_error_satisfaction_and_number_length(self):
        """Tests value errors for satisfaction and number length together."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 10, ["Dana"], 5, True, 1.5)
            mock_print.assert_called_once_with("value error")

    def test_value_error_satisfaction_and_room_invalid(self):
        """Tests value errors for satisfaction and invalid room number together."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 141, ["Dana"], 5, True, -0.1)
            mock_print.assert_called_once_with("value error")

    # ----------- Additional Tests for Mixed Errors ----------- #

    def test_type_and_value_errors_guests_and_room(self):
        """Tests type error for guests and value error for room number."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 999, ["Dana", 123], 5, True, 0.5)
            mock_print.assert_called_once_with("type error")

    def test_type_and_value_errors_clean_and_satisfaction(self):
        """Tests type error for clean_level and value error for satisfaction."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 101, ["Dana"], "clean", True, 1.5)
            mock_print.assert_called_once_with("type error")

    def test_type_and_value_errors_is_suite_and_room(self):
        """Tests type error for is_suite and value error for room number."""
        with patch('builtins.print') as mock_print:
            Room(self.minibar, 141, ["Dana"], 5, "yes", 0.5)
            mock_print.assert_called_once_with("type error")

    def test_type_and_value_errors_minibar_and_satisfaction(self):
        """Tests type error for minibar and value error for satisfaction."""
        with patch('builtins.print') as mock_print:
            Room({}, 101, ["Dana"], 5, True, 1.5)  # Invalid minibar and satisfaction
            mock_print.assert_called_once_with("value error")

    # ----------- Tests for __repr__ ----------- #

    def test_repr_empty_all(self):
        """Tests repr when there are no drinks, no snacks, and no guests."""
        room = Room(self.empty_minibar, 101, [], 6, True)
        expected_output = ('Room number: 101\n'
                           'Guests: empty\n'
                           'Clean level: 6\n'
                           'Is suite: True\n'
                           'Satisfaction: 0.5\n'
                           'Minibar:\n'
                           'No drinks left\n'
                           'No snacks left\n'
                           'No bill yet')
        self.assertEqual(repr(room), expected_output)

    def test_repr_empty_guests(self):
        """Tests repr when there are no guests."""
        room = Room(self.minibar, 101, [], 6, True)
        expected_output = ('Room number: 101\n'
                           'Guests: empty\n'
                           'Clean level: 6\n'
                           'Is suite: True\n'
                           'Satisfaction: 0.5\n'
                           'Minibar:\n'
                           'Drinks: Coke (10), Water (5)\n'
                           'Snacks: Chips (3), Cookies (2)\n'
                           'No bill yet')
        self.assertEqual(repr(room), expected_output)

    def test_repr_empty_minibar(self):
        """Tests repr when the minibar has no drinks or snacks."""
        room = Room(self.empty_minibar, 101, ["Shir", "Ronen"], 6, True)
        expected_output = ('Room number: 101\n'
                           'Guests: ronen, shir\n'
                           'Clean level: 6\n'
                           'Is suite: True\n'
                           'Satisfaction: 0.5\n'
                           'Minibar:\n'
                           'No drinks left\n'
                           'No snacks left\n'
                           'No bill yet')
        self.assertEqual(repr(room), expected_output)

    def test_repr_with_bill(self):
        """Tests repr when there is a bill in the minibar."""
        self.minibar.drink('Coke')  # Reduces coke quantity by 1 and adds 21 to the bill
        room = Room(self.minibar, 101, ["Shir", "Ronen"], 6, True)
        expected_output = ('Room number: 101\n'
                           'Guests: ronen, shir\n'
                           'Clean level: 6\n'
                           'Is suite: True\n'
                           'Satisfaction: 0.5\n'
                           'Minibar:\n'
                           'Drinks: Coke (9), Water (5)\n'
                           'Snacks: Chips (3), Cookies (2)\n'
                           'Bill: 21')
        self.assertEqual(repr(room), expected_output)

    def test_repr_no_drinks(self):
        """Tests repr with snacks available but no drinks."""
        empty_drinks_minibar = Minibar({}, {'Chips': 3, 'Cookies': 2})
        room = Room(empty_drinks_minibar, 101, ["Shir", "Ronen"], 6, True)
        expected_output = ('Room number: 101\n'
                           'Guests: ronen, shir\n'
                           'Clean level: 6\n'
                           'Is suite: True\n'
                           'Satisfaction: 0.5\n'
                           'Minibar:\n'
                           'No drinks left\n'
                           'Snacks: Chips (3), Cookies (2)\n'
                           'No bill yet')
        self.assertEqual(repr(room), expected_output)

    def test_repr_no_snacks(self):
        """Tests repr with drinks available but no snacks."""
        empty_snacks_minibar = Minibar({'Coke': 10, 'Water': 5}, {})
        room = Room(empty_snacks_minibar, 101, ["Shir", "Ronen"], 6, True)
        expected_output = ('Room number: 101\n'
                           'Guests: ronen, shir\n'
                           'Clean level: 6\n'
                           'Is suite: True\n'
                           'Satisfaction: 0.5\n'
                           'Minibar:\n'
                           'Drinks: Coke (10), Water (5)\n'
                           'No snacks left\n'
                           'No bill yet')
        self.assertEqual(repr(room), expected_output)

    # ----------- Tests for is_occupied ----------- #

    def test_is_occupied_invalid_is_suite(self):
        """Tests is_occupied when is_suite is not boolean."""
        room = Room(self.minibar, 101, ["Guest1"], 6, "not_a_boolean")
        self.assertTrue(room.is_occupied())

    def test_is_occupied_multiple_invalid_params_with_guests(self):
        """Tests is_occupied with multiple invalid parameters and guests."""
        room = Room(self.minibar, 941, ["Guest1"], "invalid", "not_a_boolean")
        self.assertTrue(room.is_occupied())

    def test_is_occupied_multiple_invalid_params_no_guests(self):
        """Tests is_occupied with multiple invalid parameters and no guests."""
        room = Room(self.empty_minibar, 456, [], "invalid", "not_a_boolean")  # השתמשתי ב-empty_minibar
        self.assertFalse(room.is_occupied())

    def test_is_occupied_empty_string_guest(self):
        """Tests is_occupied with empty string guest."""
        room = Room(self.minibar, 101, [""], 6, True)
        self.assertTrue(room.is_occupied())

    def test_is_occupied_none_guest(self):
        """Tests is_occupied with None as guest."""
        room = Room(self.minibar, 101, [None], 6, True)
        self.assertTrue(room.is_occupied())

    def test_is_occupied_space_guest(self):
        """Tests is_occupied with space as guest."""
        room = Room(self.minibar, 101, [" "], 6, True)
        self.assertTrue(room.is_occupied())

    def test_is_occupied_empty_list(self):
        """Tests is_occupied with empty guests list."""
        room = Room(self.empty_minibar, 101, [], 6, True)  # השתמשתי ב-empty_minibar
        self.assertFalse(room.is_occupied())

    # ----------- Tests for clean ----------- #

    def test_clean_with_non_numeric_room_number(self):
        """Tests clean when minibar is not class minibar."""
        room = Room("101", 101, ["Dana"], 1, True, 0.5)
        initial_clean_level = room.clean_level
        room.clean()
        self.assertEqual(room.clean_level, initial_clean_level + 2)

    def test_clean_with_satisfaction_level_2(self):
        """Tests clean when satisfaction level is 2."""
        room = Room(self.minibar, 101, ["Dana"], 5, True, 2)
        initial_clean_level = room.clean_level
        room.clean()
        self.assertEqual(room.clean_level, initial_clean_level + 2)

    def test_clean_with_guest_list_as_dict(self):
        """Tests clean when guest list is a dictionary."""
        room = Room(101, 101, {"Dana": 30, "Avi": 25}, 1, False, 0.5)
        initial_clean_level = room.clean_level
        room.clean()
        self.assertEqual(room.clean_level, initial_clean_level + 1)

    # ----------- Tests for check-in ----------- #

    def test_check_in_occupied_room_invalid_suite(self):
        """Ensure check-in fails for occupied room even if is_suite is invalid."""
        room = Room(self.minibar, 101, ["Eve"], 5, "invalid", 0.5)
        with patch('builtins.print') as mock_print:
            room.check_in(["Alice"])
            # Exact check for printed output
            mock_print.assert_called_once_with("Cannot check-in new guests to an occupied room.")
        # Ensure the original guests remain unchanged
        self.assertEqual(room.guests, ["eve"])  # 'Eve' is converted to lowercase

    def test_check_in_with_invalid_room_number(self):
        """Ensure check-in works even if room number is invalid."""
        room = Room(self.minibar, 9999, [], 5, False, 0.5)
        room.check_in(["Bob"])
        # Expect lowercase conversion
        self.assertEqual(room.guests, ["bob"])  # 'Bob' is converted to lowercase
        self.assertEqual(room.satisfaction, 0.5)
        self.assertEqual(self.minibar.bill, 0)

    def test_minibar_bill_before_and_after_check_in(self):
        """Check minibar bill before and after successful check-in."""
        # Ensure the bill starts with a value greater than 0
        self.assertEqual(self.minibar.bill, 0)
        room = Room(self.minibar, 101, [], 5, False, 0.5)
        room.check_in(["Charlie", "Dana"])
        # Ensure the bill resets to 0 after check-in
        self.assertEqual(self.minibar.bill, 0)

    def test_check_in_reset_satisfaction_and_minibar_invalid_suite(self):
        """Ensure satisfaction and minibar reset even if is_suite is invalid."""
        room = Room(self.minibar, 101, [], 5, 123, 0.9)
        room.check_in(["Frank"])
        # Expect lowercase conversion for names
        self.assertEqual(room.guests, ["frank"])  # 'Frank' is converted to lowercase
        self.assertEqual(room.satisfaction, 0.5)
        self.assertEqual(self.minibar.bill, 0)

    # ----------- Tests for check-out ----------- #

    def test_check_out_with_occupied_room(self):
        """Ensure check-out works correctly for an occupied room."""
        # Create a room with guests
        room = Room(self.minibar, 101, ["Alice", "Bob"], 5, False, 0.5)
        room.check_out()
        # Verify that the guests list is now empty
        self.assertEqual(room.guests, [])

    def test_check_out_with_empty_room(self):
        """Ensure check-out prints error message for an empty room."""
        # Create an empty room (no guests)
        room = Room(self.minibar, 101, [], 5, False, 0.5)
        with patch('builtins.print') as mock_print:
            room.check_out()
            # Exact match check for printed output
            mock_print.assert_called_once_with("Cannot check-out an empty room.")
        # Verify that the guests list is still empty
        self.assertEqual(room.guests, [])

    def test_check_out_with_invalid_minibar(self):
        """Ensure check-out works correctly even if minibar is an invalid type (int)."""
        # Create a room with invalid minibar (int instead of object)
        room = Room(1234, 101, ["Alice"], "clean", {"key": "value"}, {"satisfaction"})
        room.check_out()
        # Verify that the guests list is now empty
        self.assertEqual(room.guests, [])

    def test_check_out_with_invalid_is_suite(self):
        """Ensure check-out works correctly even if is_suite is an invalid type (dict)."""
        # Create a room with invalid is_suite (dict instead of bool)
        room = Room(self.minibar, 101, ["Bob"], "clean", {"key": "value"}, {"satisfaction"})
        room.check_out()
        # Verify that the guests list is now empty
        self.assertEqual(room.guests, [])

    def test_check_out_with_invalid_satisfaction(self):
        """Ensure check-out works correctly even if satisfaction is an invalid type (set)."""
        # Create a room with invalid satisfaction (set instead of float)
        room = Room(self.minibar, 101, ["Charlie"], "clean", False, {"satisfaction"})
        room.check_out()
        # Verify that the guests list is now empty
        self.assertEqual(room.guests, [])

    def test_check_out_with_invalid_clean_level(self):
        """Ensure check-out works correctly even if clean_level is an invalid type (string)."""
        # Create a room with invalid clean_level (string instead of int)
        room = Room(self.minibar, 101, ["Dana"], "clean", False, 0.5)
        room.check_out()
        # Verify that the guests list is now empty
        self.assertEqual(room.guests, [])

    # ----------- Tests for move_to ----------- #

    def test_move_to_successful_transfer(self):
        """Ensure successful transfer when other room is empty and better."""
        room1 = Room(self.minibar, 101, ["Alice", "Bob"], 5, False, 0.5)
        room2 = Room(self.empty_minibar, 201, [], 6, True, 0.7)  # Better room (suite)

        # Simulate minibar bill for room1
        room1.minibar.bill = 50

        room1.move_to(room2)

        # Verify guests transferred
        self.assertEqual(room2.guests, ["alice", "bob"])  # Converted to lowercase
        self.assertEqual(room1.guests, [])  # Emptied

        # Verify minibar bill transferred
        self.assertEqual(room2.minibar.bill, 50)

        # Verify satisfaction improved since room2 is better
        self.assertEqual(room2.satisfaction, min(1.0, 0.5 + 0.1))

    def test_move_to_empty_self_room(self):
        """Ensure error message when moving guests from an empty room."""
        room1 = Room(self.minibar, 101, [], 5, False, 0.5)
        room2 = Room(self.empty_minibar, 201, [], 6, True, 0.7)

        with patch('builtins.print') as mock_print:
            room1.move_to(room2)
            mock_print.assert_called_once_with("Cannot move guests from an empty room")

        # Ensure no guests were transferred
        self.assertEqual(room1.guests, [])
        self.assertEqual(room2.guests, [])

    def test_move_to_occupied_other_room(self):
        """Ensure error message when moving guests to an occupied room."""
        room1 = Room(self.minibar, 101, ["Alice", "Bob"], 5, False, 0.5)
        room2 = Room(self.empty_minibar, 201, ["Charlie"], 6, True, 0.7)  # Already occupied

        with patch('builtins.print') as mock_print:
            room1.move_to(room2)
            mock_print.assert_called_once_with("Cannot move guests into an occupied room")

        # Ensure no changes were made to either room
        self.assertEqual(room1.guests, ["alice", "bob"])  # Original guests remain
        self.assertEqual(room2.guests, ["charlie"])  # No changes to other

    def test_move_to_transfer_when_rooms_are_equal(self):
        """Ensure transfer when rooms are equal and satisfaction is copied."""
        room1 = Room(self.minibar, 101, ["Alice"], 5, False, 0.5)
        room2 = Room(self.empty_minibar, 102, [], 5, False, 0.7)

        room1.minibar.bill = 30

        room1.move_to(room2)

        # Verify guests transferred
        self.assertEqual(room2.guests, ["alice"])
        self.assertEqual(room1.guests, [])

        # Verify minibar bill transferred
        self.assertEqual(room2.minibar.bill, 30)

        # Satisfaction copied (rooms are equal)
        self.assertEqual(room2.satisfaction, 0.5)

    def test_move_to_transfer_when_other_is_worse(self):
        """Ensure transfer when other room is worse and satisfaction is copied."""
        room1 = Room(self.minibar, 301, ["Alice"], 7, False, 0.9)
        room2 = Room(self.empty_minibar, 202, [], 5, False, 0.6)

        room1.minibar.bill = 40

        room1.move_to(room2)

        # Verify guests transferred
        self.assertEqual(room2.guests, ["alice"])
        self.assertEqual(room1.guests, [])

        # Verify minibar bill transferred
        self.assertEqual(room2.minibar.bill, 40)

        # Satisfaction copied (other room is worse)
        self.assertEqual(room2.satisfaction, 0.9)

    # ----------- Tests based on pdf ----------- #
    def test_first_image_operations(self):
        """Tests room operations based on the first image."""

        # Test better_than method
        self.assertTrue(self.r_better.better_than(self.r1))

        # Test check_in and clean
        self.r_better.check_in(["Amir"])
        self.r_better.clean()
        self.assertEqual(self.r_better.clean_level, 6)

        # Test check-in failure for an occupied room
        with patch('builtins.print') as mock_print:
            self.r1.check_in(["Avi", "Hadar"])
            mock_print.assert_called_once_with("Cannot check-in new guests to an occupied room.")

        # Test is_occupied
        self.assertTrue(self.r1.is_occupied())

        # Test check_out
        self.assertIsNone(self.r1.check_out())
        self.assertFalse(self.r1.is_occupied())

        # Test satisfaction after move_to
        self.r_better.move_to(self.r1)
        self.assertEqual(self.r1.satisfaction, 0.5)

    def test_second_image_operations(self):
        """Tests room operations based on the second image."""

        # Test initial satisfaction
        self.assertEqual(self.r1.satisfaction, 0.5)

        # Test guests
        self.assertEqual(self.r1.guests, ["dana", "ron"])  # Lowercase check

        # Move guests to r_better
        self.r1.move_to(self.r_better)

        # Test r1 is no longer occupied
        self.assertFalse(self.r1.is_occupied())

        # Test satisfaction increase when moved to a better room
        self.assertEqual(self.r_better.satisfaction, 0.6)

        # Test guests in r_better
        self.assertEqual(self.r_better.guests, ["dana", "ron"])  # Lowercase check


class TestHotel(unittest.TestCase):

    def setUp(self):
        """Setup common minibars for testing."""
        # Create minibars for the test cases
        self.minibar = Minibar({'Coke': 10, 'Water': 5}, {'Chips': 3, 'Cookies': 2})
        self.empty_minibar = Minibar({}, {})  # Empty minibar for edge cases

        # Create rooms
        self.suite_room = Room(self.minibar, 101, [], 5, True)  # Empty suite
        self.regular_room = Room(self.minibar, 102, [], 5, False)  # Empty regular room
        self.occupied_suite = Room(self.minibar, 103, ["Alice"], 5, True)  # Occupied suite
        self.occupied_regular = Room(self.minibar, 104, ["Bob"], 5, False)  # Occupied regular room
        self.better_suite = Room(self.minibar, 105, [], 8, True)  # Better empty suite
        self.better_regular = Room(self.minibar, 106, [], 7, False)  # Better empty regular room
        self.better_regular_bill = Room(Minibar({'Water': 3}, {'Nuts': 2}), 107, [], 6, False)
        self.worst_regular_bill = Room(Minibar({'Juice': 3}, {'Cookies': 5}), 108, ["Eve"], 4, False)
        self.better_suite_bill = Room(Minibar({'Water': 2}, {'Nuts': 4}), 109, [], 9, True)

        # Create Princess Hotel
        self.princess_hotel = Hotel("Princess Hotel", [self.suite_room, self.regular_room,
                                                       self.occupied_suite, self.occupied_regular,
                                                       self.better_suite, self.better_regular])

    # ----------- Tests repr ----------- #

    # 1. Test for an empty hotel (no rooms)
    def test_empty_hotel(self):
        """Test repr for an empty hotel (no rooms)."""
        hotel = Hotel("EmptyHotel", [])
        self.assertEqual(repr(hotel), "EmptyHotel Hotel has: 0/0 occupied rooms.")

    # 2. Test for a hotel where all rooms are empty
    def test_all_rooms_empty(self):
        """Test repr for a hotel where all rooms are empty."""
        rooms = [
            Room(self.minibar, 101, [], 5, False),
            Room(self.minibar, 102, [], 7, True),
            Room(self.minibar, 103, [], 6, False)
        ]
        hotel = Hotel("EmptyRoomsHotel", rooms)
        self.assertEqual(repr(hotel), "EmptyRoomsHotel Hotel has: 0/3 occupied rooms.")

    # 3. Test for a hotel where all rooms are occupied
    def test_all_rooms_occupied(self):
        """Test repr for a hotel where all rooms are occupied."""
        rooms = [
            Room(self.minibar, 101, ["Alice"], 5, False),
            Room(self.minibar, 102, ["Bob", "Charlie"], 7, True),
            Room(self.minibar, 103, ["Dana"], 6, False)
        ]
        hotel = Hotel("FullHotel", rooms)
        self.assertEqual(repr(hotel), "FullHotel Hotel has: 3/3 occupied rooms.")

    # 4. Test for a hotel with an equal number of occupied and empty rooms
    def test_half_rooms_occupied(self):
        """Test repr for a hotel with equal numbers of occupied and empty rooms."""
        rooms = [
            Room(self.minibar, 101, ["Alice"], 5, False),  # Occupied
            Room(self.minibar, 102, [], 7, True),  # Empty
            Room(self.minibar, 103, ["Dana"], 6, False),  # Occupied
            Room(self.minibar, 104, [], 4, False)  # Empty
        ]
        hotel = Hotel("HalfFullHotel", rooms)
        self.assertEqual(repr(hotel), "HalfFullHotel Hotel has: 2/4 occupied rooms.")

    # 5. Test for a hotel with a single occupied room
    def test_one_room_occupied(self):
        """Test repr for a hotel with one occupied room."""
        rooms = [
            Room(self.minibar, 101, ["Alice"], 5, False),  # Occupied
            Room(self.minibar, 102, [], 7, True),  # Empty
            Room(self.minibar, 103, [], 6, False)  # Empty
        ]
        hotel = Hotel("OneOccupiedHotel", rooms)
        self.assertEqual(repr(hotel), "OneOccupiedHotel Hotel has: 1/3 occupied rooms.")

    # 6. Test for a hotel with a single empty room
    def test_one_room_empty(self):
        """Test repr for a hotel with one empty room."""
        rooms = [
            Room(self.minibar, 101, ["Alice"], 5, False),  # Occupied
            Room(self.minibar, 102, ["Bob"], 7, True),  # Occupied
            Room(self.minibar, 103, [], 6, False)  # Empty
        ]
        hotel = Hotel("OneEmptyHotel", rooms)
        self.assertEqual(repr(hotel), "OneEmptyHotel Hotel has: 2/3 occupied rooms.")

    # 7. Test for a hotel with a single room that has multiple guests
    def test_single_room_multiple_guests(self):
        """Test repr for a hotel with a single room occupied by multiple guests."""
        rooms = [
            Room(self.minibar, 101, ["Alice", "Bob", "Charlie"], 5, False)
        ]
        hotel = Hotel("SingleRoomMultipleGuests", rooms)
        self.assertEqual(repr(hotel), "SingleRoomMultipleGuests Hotel has: 1/1 occupied rooms.")

    # 8. Test for a hotel with rooms containing invalid or edge-case values
    def test_rooms_with_invalid_values(self):
        """Test repr for a hotel with rooms containing invalid values (edge cases)."""
        rooms = [
            Room(self.minibar, 101, [], "clean", False),  # Invalid clean level as string
            Room(self.minibar, 102, [], 5, "not_bool"),  # Invalid suite status as string
            Room(self.minibar, 103, [], 5, False)  # Valid empty room
        ]
        hotel = Hotel("InvalidValuesHotel", rooms)
        self.assertEqual(repr(hotel), "InvalidValuesHotel Hotel has: 0/3 occupied rooms.")

    # 9. Test for a hotel with duplicated room numbers
    def test_duplicated_room_numbers(self):
        """Test repr for a hotel with duplicated room numbers."""
        rooms = [
            Room(self.minibar, 101, ["Alice"], 5, False),
            Room(self.minibar, 101, [], 7, True)  # Duplicate room number
        ]
        hotel = Hotel("DuplicateRoomsHotel", rooms)
        self.assertEqual(repr(hotel), "DuplicateRoomsHotel Hotel has: 1/2 occupied rooms.")

    # 10. Test for a hotel with a room having an extremely high number of guests
    def test_room_with_high_guest_count(self):
        """Test repr for a hotel with a room containing a large number of guests."""
        guests = ["Guest" + str(i) for i in range(100)]  # 100 guests
        rooms = [
            Room(self.minibar, 101, guests, 5, False)
        ]
        hotel = Hotel("HighGuestCountHotel", rooms)
        self.assertEqual(repr(hotel), "HighGuestCountHotel Hotel has: 1/1 occupied rooms.")

    # 11. Test for a hotel with all rooms having different conditions
    def test_varied_room_conditions(self):
        """Test repr for a hotel with rooms having varied conditions."""
        rooms = [
            Room(self.minibar, 101, ["Alice"], 5, False),  # Occupied
            Room(self.minibar, 102, [], 6, True),  # Empty suite
            Room(self.minibar, 103, ["Bob"], 7, False),  # Occupied
            Room(self.minibar, 104, [], 4, False),  # Empty
            Room(self.minibar, 105, ["Charlie"], 8, True)  # Occupied suite
        ]
        hotel = Hotel("VariedConditionsHotel", rooms)
        self.assertEqual(repr(hotel), "VariedConditionsHotel Hotel has: 3/5 occupied rooms.")

    # 12. Test for a hotel with rooms having mixed guest types (strings, numbers, empty)
    def test_mixed_guest_types(self):
        """Test repr for a hotel with mixed types of guests."""
        rooms = [
            Room(self.minibar, 101, ["Alice", 123, "Charlie"], 5, False),  # Mixed types
            Room(self.minibar, 102, [], 7, True),  # Empty
            Room(self.minibar, 103, ["Bob"], 6, False)  # Occupied
        ]
        hotel = Hotel("MixedGuestTypesHotel", rooms)
        self.assertEqual(repr(hotel), "MixedGuestTypesHotel Hotel has: 2/3 occupied rooms.")

    # 13. Test for a hotel where all rooms have no minibar
    def test_rooms_with_no_minibar(self):
        """Test repr for a hotel where all rooms have no minibar."""
        rooms = [
            Room(None, 101, ["Alice"], 5, False),  # No minibar
            Room(None, 102, [], 7, True),  # No minibar
            Room(None, 103, ["Bob"], 6, False)  # No minibar
        ]
        hotel = Hotel("NoMinibarHotel", rooms)
        self.assertEqual(repr(hotel), "NoMinibarHotel Hotel has: 2/3 occupied rooms.")

    # ----------- Tests check_in ----------- #

    # 1. Test check-in to an available suite
    def test_check_in_to_available_suite(self):
        """Test checking into an available suite."""
        guests = ["Charlie", "Dana"]
        assigned_room = self.princess_hotel.check_in(guests, True)
        self.assertEqual(assigned_room, self.better_suite)  # Correct suite is assigned
        self.assertEqual(assigned_room.guests, ["charlie", "dana"])  # Guests checked in (lowercase)

    # 2. Test check-in to an available regular room
    def test_check_in_to_available_regular_room(self):
        """Test checking into an available regular room."""
        guests = ["Eve"]
        assigned_room = self.princess_hotel.check_in(guests, False)
        self.assertEqual(assigned_room, self.better_regular)  # Correct regular room is assigned
        self.assertEqual(assigned_room.guests, ["eve"])  # Guest checked in (lowercase)

    # 3. Test check-in when no suites are available
    def test_check_in_no_available_suites(self):
        """Test check-in to a suite when all suites are occupied."""
        guests = ["Frank"]

        # Occupy all suites, including better ones
        self.suite_room.check_in(["Existing Guests"])  # Room 101
        self.better_suite.check_in(["Better Guests"])  # Room 105

        # Attempt to check-in when no suites are available
        assigned_room = self.princess_hotel.check_in(guests, True)

        # Assert - No suite should be assigned
        self.assertIsNone(assigned_room)  # No suite should be assigned

    # 4. Test check-in when no regular rooms are available
    def test_check_in_no_available_regular_rooms(self):
        """Test check-in to a regular room when all regular rooms are occupied."""
        guests = ["Grace"]

        # Occupy all regular rooms, including better ones
        self.regular_room.check_in(["Existing Guests"])  # Room 102
        self.better_regular.check_in(["Other Guests"])  # Room 106

        # Attempt to check-in when all regular rooms are occupied
        assigned_room = self.princess_hotel.check_in(guests, False)

        # Assert - No room should be assigned
        self.assertIsNone(assigned_room)  # No available regular rooms

    # 5. Test check-in to a small room with long names
    def test_check_in_large_names(self):
        """Test check-in with guests having long names."""
        guests = ["AlexanderTheGreat", "Cleopatra"]
        assigned_room = self.princess_hotel.check_in(guests, False)
        self.assertEqual(assigned_room, self.better_regular)  # Should assign the room correctly
        self.assertEqual(assigned_room.guests, ["alexanderthegreat", "cleopatra"])  # Names checked in (lowercase)

    # 6. Test check-in with spaces in guest names
    def test_check_in_names_with_spaces(self):
        """Test check-in with guest names containing spaces."""
        guests = ["John Smith", "Jane Doe"]
        assigned_room = self.princess_hotel.check_in(guests, False)
        self.assertEqual(assigned_room, self.better_regular)  # Should assign the room
        self.assertEqual(assigned_room.guests, ["john smith", "jane doe"])  # Names checked in (lowercase)

    # ----------- Tests check_out ----------- #

    # 1. Test case-sensitive check-out (guest name exactly matches)
    def test_check_out_case_sensitive_match(self):
        """Test check-out with exact case-sensitive match."""
        room = self.princess_hotel.check_out("Alice")  # Case matches
        self.assertEqual(room.number, 103)  # Correct room
        self.assertEqual(room.guests, [])  # All guests removed
        self.assertFalse(room.is_occupied())  # Room should be unoccupied

    # 2. Test case-insensitive check-out (same name, different case)
    def test_check_out_case_insensitive_match(self):
        """Test check-out with case-insensitive name match."""
        room = self.princess_hotel.check_out("ALICE")  # Different case
        self.assertEqual(room.number, 103)  # Correct room
        self.assertEqual(room.guests, [])  # All guests removed
        self.assertFalse(room.is_occupied())  # Room should be unoccupied

    # 3. Test check-out removes all guests (not just the given guest)
    def test_check_out_removes_all_guests(self):
        """Test check-out removes all guests from the room, not just the specified one."""
        # Act - Try to check out 'Bob'
        room = self.princess_hotel.check_out("Bob")  # Bob is in room 103

        # Assert - Room 103 should be cleared
        self.assertEqual(room.number, 104)  # Bob and Alice should be removed
        self.assertEqual(room.guests, [])  # All guests should be cleared
        self.assertFalse(room.is_occupied())  # Room should now be unoccupied

    # 4. Test check-out for single guest
    def test_check_out_single_guest(self):
        """Test check-out for a room with a single guest."""
        room = self.princess_hotel.check_out("         B o b")  # Bob is in room 104
        self.assertEqual(room.number, 104)  # Room 104 should be cleared
        self.assertEqual(room.guests, [])  # Room should be empty
        self.assertFalse(room.is_occupied())  # Room should be unoccupied

    # 5. Test check-out when no guests match
    def test_check_out_no_match(self):
        """Test check-out when no guest matches."""
        room = self.princess_hotel.check_out("David")  # Guest does not exist
        self.assertIsNone(room)  # Should return None

    # 6. Test check-out with case-sensitive mismatch
    def test_check_out_case_sensitive_mismatch(self):
        """Test check-out with a case-sensitive mismatch."""
        room = self.princess_hotel.check_out("alice")  # Lowercase mismatch
        self.assertEqual(room.number, 103)  # Should match due to case-insensitivity
        self.assertEqual(room.guests, [])  # All guests should be removed
        self.assertFalse(room.is_occupied())  # Room should be unoccupied

    # 7. Test check-out when all rooms are empty
    def test_check_out_all_empty(self):
        """Test check-out when all rooms are already empty."""
        # Empty all rooms first
        self.princess_hotel.check_out("Alice")
        self.princess_hotel.check_out("Bob")
        self.princess_hotel.check_out("Charlie")

        # Try to check out a guest who doesn't exist
        room = self.princess_hotel.check_out("David")
        self.assertIsNone(room)  # Should return None since no guests are left

    # 8. Test check-out when guest name contains spaces
    def test_check_out_with_spaces(self):
        """Test check-out when guest name contains spaces."""
        room = self.princess_hotel.check_out(" Bob ")  # Includes leading/trailing spaces
        self.assertEqual(room.number, 104)  # Bob should be in room 103
        self.assertEqual(room.guests, [])  # All guests should be cleared
        self.assertFalse(room.is_occupied())  # Room should be unoccupied

    # 9. Test check-out with empty string as input
    def test_check_out_empty_string(self):
        """Test check-out with an empty string."""
        room = self.princess_hotel.check_out("")  # Empty string
        self.assertIsNone(room)  # Should return None

    # ----------- Tests for upgrade method -----------#

    # 1. Upgrade guest to the first better suite
    def test_upgrade_to_first_better_suite(self):
        """Test upgrading a guest to the first better suite in the list."""
        room = self.princess_hotel.upgrade("Alice")  # Alice is in Room 103
        self.assertEqual(room.number, 105)  # Moves to the first better suite (105)
        self.assertEqual(room.guests, ["alice"])
        self.assertEqual(room.satisfaction, 0.6)  # Satisfaction +0.1
        self.assertEqual(self.occupied_suite.guests, [])  # Old room empty

    # 3. No upgrade when no better rooms are available
    def test_no_upgrade_available(self):
        """Test no upgrade when no better room is available."""
        # Fill all better rooms
        self.better_suite.check_in(["Eve"])
        self.better_regular.check_in(["Dan"])
        room = self.princess_hotel.upgrade("Alice")
        self.assertIsNone(room)  # No upgrade possible

    # 4. Guest not found in any room
    def test_upgrade_guest_not_found(self):
        """Test upgrade when guest is not found."""
        room = self.princess_hotel.upgrade("David")
        self.assertIsNone(room)  # No upgrade if guest not found

    # 5. Case-insensitive guest matching
    def test_upgrade_case_insensitive(self):
        """Test upgrade with case-insensitive guest name matching."""
        room = self.princess_hotel.upgrade("ALICE")  # Case-insensitive match
        self.assertEqual(room.number, 105)  # Moves to first better suite

    # 6. Spaces in guest names
    # def test_upgrade_with_spaces(self):
    #    """Test upgrade with guest name containing extra spaces."""
    #    room = self.princess_hotel.upgrade("    B o   b  ")  # Normalized input
    #    self.assertEqual(room.number, 106)  # Moves to first better regular room

    # 7. Already in the best room
    def test_upgrade_already_best_room(self):
        """Test no upgrade if guest is already in the best room."""
        self.better_suite.check_in(["Zoe"])  # Zoe already in the best suite
        room = self.princess_hotel.upgrade("Zoe")
        self.assertIsNone(room)  # Already in best room

    # 9. Satisfaction transfer during upgrade
    def test_upgrade_satisfaction_transfer(self):
        """Test that satisfaction is transferred or updated during upgrade."""
        self.occupied_suite.satisfaction = 0.8
        room = self.princess_hotel.upgrade("Alice")
        self.assertEqual(room.satisfaction, 0.9)  # Satisfaction improves

    # 10. No upgrade when the guest is not in any room
    def test_upgrade_guest_not_in_room(self):
        """Test no upgrade when the guest is not assigned to any room."""
        room = self.princess_hotel.upgrade("UnknownGuest")
        self.assertIsNone(room)

    # ----------- Tests for send_cleaner() method -----------#

    # 1. Test cleaning a room where the guest exists
    def test_send_cleaner_successful(self):
        """Test cleaning a room successfully where the guest exists."""
        # Act - Send cleaner to Bob's room
        room = self.princess_hotel.send_cleaner("Bob")

        # Assert - Room should be cleaned and returned
        self.assertEqual(room.number, 104)  # Bob is in Room 104
        self.assertEqual(room.clean_level, 6)  # Regular room clean level increases by 1

    # 2. Test cleaning a suite where the guest exists
    def test_send_cleaner_suite_successful(self):
        """Test cleaning a suite successfully where the guest exists."""
        # Act - Send cleaner to Alice's room (suite)
        room = self.princess_hotel.send_cleaner("Alice")

        # Assert - Room should be cleaned and returned
        self.assertEqual(room.number, 103)  # Alice is in Room 103
        self.assertEqual(room.clean_level, 7)  # Suite clean level increases by 2

    # 3. Test sending a cleaner for a guest not in the hotel
    def test_send_cleaner_guest_not_found(self):
        """Test sending a cleaner for a guest who is not in the hotel."""
        # Act - Attempt to clean a non-existent guest
        room = self.princess_hotel.send_cleaner("Charlie")

        # Assert - No room should be found
        self.assertIsNone(room)  # Charlie does not exist

    # 4. Test case-insensitive guest lookup
    def test_send_cleaner_case_insensitive(self):
        """Test case-insensitive guest lookup for cleaning."""
        # Act - Send cleaner using uppercase guest name
        room = self.princess_hotel.send_cleaner("BOB")

        # Assert - Cleaner still finds Bob in Room 104
        self.assertEqual(room.number, 104)  # Bob's room
        self.assertEqual(room.clean_level, 6)  # Clean level increases

    # 5. Test sending a cleaner with leading/trailing spaces
    def test_send_cleaner_with_spaces(self):
        """Test sending a cleaner with spaces in the guest name."""
        # Act - Send cleaner with spaced guest name
        room = self.princess_hotel.send_cleaner("  Bob   ")

        # Assert - Cleaner should still clean Bob's room
        self.assertEqual(room.number, 104)  # Bob's room
        self.assertEqual(room.clean_level, 6)  # Clean level increases

    # 6. Test cleaning for a guest with multiple guests in the same room
    def test_send_cleaner_multiple_guests(self):
        """Test cleaning a room with multiple guests."""
        # Arrange - Add multiple guests to the same room
        self.occupied_regular.guests = ["Bob", "Tom"]

        # Act - Send cleaner for one guest
        room = self.princess_hotel.send_cleaner("Tom")

        # Assert - Room should still be cleaned
        self.assertEqual(room.number, 104)  # Room with Bob and Tom
        self.assertEqual(room.clean_level, 6)  # Clean level increases


class TestPolynomial(unittest.TestCase):

    # ----------- Tests __repr__ ----------- #

    def test_example(self):
        ret_val = Polynomial([1, -2])
        answer = 'x + -2'
        self.assertEqual(str(ret_val), answer)

    # 1. Test basic polynomial
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_basic_polynomial(self, mock_stdout):
        print(Polynomial([1, -2]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, 'x + -2')

    # 2. Test zero polynomial
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_zero_polynomial(self, mock_stdout):
        print(Polynomial([0, 0, 0]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, '0')

    # 3. Test polynomial with negative coefficients
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_negative_coefficients(self, mock_stdout):
        print(Polynomial([-3, -2, -1, -4]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, '-3x^3 + -2x^2 + -x + -4')

    # 4. Test polynomial with mixed coefficients
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_mixed_coefficients(self, mock_stdout):
        print(Polynomial([-3, -2, 1, -4]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, '-3x^3 + -2x^2 + x + -4')

    # 5. Test polynomial with all coefficients equal to 1
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_all_ones(self, mock_stdout):
        print(Polynomial([1, 1, 1, 1]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, 'x^3 + x^2 + x + 1')

    # 6. Test polynomial with all coefficients equal to 2
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_all_twos(self, mock_stdout):
        print(Polynomial([2, 2, 2, 2, 2, 2]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, '2x^5 + 2x^4 + 2x^3 + 2x^2 + 2x + 2')

    # 7. Test polynomial with leading zero coefficients
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_large_constant(self, mock_stdout):
        print(Polynomial([1, 0, 0, 0, 5000]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, 'x^4 + 5000')

    # 8. Test polynomial with negative terms and large constant
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_large_and_negative(self, mock_stdout):
        print(Polynomial([1, -1, -5, -20, 5000]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, 'x^4 + -x^3 + -5x^2 + -20x + 5000')

    # 9. Test polynomial with negative, positive and 0 terms.
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_very_long_polynomial(self, mock_stdout):
        # Create a very long polynomial without leading zero
        coefficients = [5, -5, 3, 0, 0, -2, 0, 7, -8, 0, 1, 0, 0, 4, 0, -1, 6, 0, 0, -3]
        print(Polynomial(coefficients))
        output = mock_stdout.getvalue().strip()

        # Expected output
        expected_output = (
            '5x^19 + -5x^18 + 3x^17 + -2x^14 + 7x^12 + -8x^11 + x^9 + 4x^6 + -x^4 + 6x^3 + -3'
        )
        self.assertEqual(output, expected_output)

    # 10. Test a single term with high degree
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_single_high_degree_term(self, mock_stdout):
        print(Polynomial([1] + [0] * 99 + [-1]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, 'x^100 + -1')

    # 11. Test polynomial with zeros and mixed signs
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_zeros_and_mixed_signs(self, mock_stdout):
        print(Polynomial([0, -5, 0, 3, 0, -1]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, '-5x^4 + 3x^2 + -1')

    # 12. Test a polynomial with all zeros except one at the end
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_trailing_constant(self, mock_stdout):
        print(Polynomial([0, 0, 0, 0, 10]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, '10')

    # 13. Test a polynomial with alternating zeros and non-zeros
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_alternating_zeros(self, mock_stdout):
        print(Polynomial([1, 0, -1, 0, 1]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, 'x^4 + -x^2 + 1')

    # 14. Test polynomial with only one variable with coefficient -1
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_negative_one_variable(self, mock_stdout):
        print(Polynomial([-1, 0]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, '-x')

    # 15. Test a polynomial with zeros in between coefficients
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_zeros_in_middle(self, mock_stdout):
        print(Polynomial([3, 0, 0, -1]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, '3x^3 + -1')

    # 16. Test polynomial with all negative coefficients
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_all_negative_coefficients(self, mock_stdout):
        print(Polynomial([-3, -2, -1]))
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, '-3x^2 + -2x + -1')

    # ----------- Tests __add__ ----------- #

    # 1. Different lengths
    def test_01_add_different_lengths(self):
        """Test adding polynomials of different lengths"""
        p1 = Polynomial([1, -2])
        p2 = Polynomial([1, 0, 0, 0, 5000])
        result = p1 + p2
        self.assertEqual(str(result), "x^4 + x + 4998")

    # 2. Negative coefficients
    def test_02_add_negative_coefficients(self):
        """Test adding polynomials with negative coefficients"""
        p1 = Polynomial([-3, -2, -1, -4])
        p2 = Polynomial([-3, -2, 1, -4])
        result = p1 + p2
        self.assertEqual(str(result), "-6x^3 + -4x^2 + -8")

    # 3. Zero polynomials
    def test_03_add_zero_polynomials(self):
        """Test adding two zero polynomials"""
        p1 = Polynomial([0, 0, 0])
        p2 = Polynomial([0, 0])
        result = p1 + p2
        self.assertEqual(str(result), "0")

    # 4. Adding with zero polynomial
    def test_04_add_with_zero_polynomial(self):
        """Test adding a polynomial with a zero polynomial"""
        p1 = Polynomial([1, -1, -5, -20, 5000])
        p2 = Polynomial([0])
        result = p1 + p2
        self.assertEqual(str(result), "x^4 + -x^3 + -5x^2 + -20x + 5000")

    # 5. Identical polynomials
    def test_05_add_identical_polynomials(self):
        """Test adding identical polynomials"""
        p1 = Polynomial([2, 2, 2])
        result = p1 + p1
        self.assertEqual(str(result), "4x^2 + 4x + 4")

    # 6. Opposite signs polynomials
    def test_06_add_opposite_sign_polynomials(self):
        """Test adding polynomials that cancel each other out"""
        p1 = Polynomial([3, -5, 7])
        p2 = Polynomial([-3, 5, -7])
        result = p1 + p2
        self.assertEqual(str(result), "0")

    # 7. One zero, one non-zero polynomial
    def test_07_add_zero_and_nonzero_polynomial(self):
        """Test adding a zero polynomial and a non-zero polynomial"""
        p1 = Polynomial([0])
        p2 = Polynomial([4, 3, 2, 1])
        result = p1 + p2
        self.assertEqual(str(result), "4x^3 + 3x^2 + 2x + 1")

    # 8. Large coefficients
    def test_08_add_large_coefficients(self):
        """Test adding polynomials with large coefficients"""
        p1 = Polynomial([10 ** 6, -10 ** 6])
        p2 = Polynomial([-10 ** 6, 10 ** 6])
        result = p1 + p2
        self.assertEqual(str(result), "0")

    # 9. Single coefficient polynomials
    def test_09_add_single_coefficients(self):
        """Test adding single coefficient polynomials"""
        p1 = Polynomial([5])
        p2 = Polynomial([3])
        result = p1 + p2
        self.assertEqual(str(result), "8")

    # 10. Sparse polynomials
    def test_10_add_sparse_polynomials(self):
        """Test adding sparse polynomials"""
        p1 = Polynomial([1, 0, 0, 0, 5000])
        p2 = Polynomial([0, 0, 0, 0, 1])
        result = p1 + p2
        self.assertEqual(str(result), "x^4 + 5001")

    # ----------- Tests for __sub__ ----------- #
    # 1. Different lengths
    def test_01_subtract_different_lengths(self):
        """Test subtracting polynomials of different lengths"""
        p1 = Polynomial([1, -2])
        p2 = Polynomial([1, 0, 0, 0, 5000])
        result = p1 - p2
        self.assertEqual(str(result), "-x^4 + x + -5002")

    # 2. Negative coefficients
    def test_02_subtract_negative_coefficients(self):
        """Test subtracting polynomials with negative coefficients"""
        p1 = Polynomial([-3, -2, -1, -4])
        p2 = Polynomial([-3, -2, 1, -4])
        result = p1 - p2
        self.assertEqual(str(result), "-2x")

    # 3. Zero polynomials
    def test_03_subtract_zero_polynomials(self):
        """Test subtracting two zero polynomials"""
        p1 = Polynomial([0, 0, 0])
        p2 = Polynomial([0, 0])
        result = p1 - p2
        self.assertEqual(str(result), "0")

    # 4. Subtracting with zero polynomial
    def test_04_subtract_with_zero_polynomial(self):
        """Test subtracting a polynomial with a zero polynomial"""
        p1 = Polynomial([1, -1, -5, -20, 5000])
        p2 = Polynomial([0])
        result = p1 - p2
        self.assertEqual(str(result), "x^4 + -x^3 + -5x^2 + -20x + 5000")

    # 5. Identical polynomials
    def test_05_subtract_identical_polynomials(self):
        """Test subtracting identical polynomials"""
        p1 = Polynomial([2, 2, 2])
        result = p1 - p1
        self.assertEqual(str(result), "0")

    # 6. Opposite signs polynomials
    def test_06_subtract_opposite_sign_polynomials(self):
        """Test subtracting polynomials with opposite signs"""
        p1 = Polynomial([3, -5, 7])
        p2 = Polynomial([-3, 5, -7])
        result = p1 - p2
        self.assertEqual(str(result), "6x^2 + -10x + 14")

    # 7. One zero, one non-zero polynomial
    def test_07_subtract_zero_and_nonzero_polynomial(self):
        """Test subtracting a zero polynomial and a non-zero polynomial"""
        p1 = Polynomial([0])
        p2 = Polynomial([4, 3, 2, 1])
        result = p1 - p2
        self.assertEqual(str(result), "-4x^3 + -3x^2 + -2x + -1")

    # 8. Large coefficients
    def test_08_subtract_large_coefficients(self):
        """Test subtracting polynomials with large coefficients"""
        p1 = Polynomial([5, -5])
        p2 = Polynomial([-5, 5])
        result = p1 - p2
        self.assertEqual(str(result), "10x + -10")

    # 9. Single coefficient polynomials
    def test_09_subtract_single_coefficients(self):
        """Test subtracting single coefficient polynomials"""
        p1 = Polynomial([5])
        p2 = Polynomial([3])
        result = p1 - p2
        self.assertEqual(str(result), "2")

    # 10. Sparse polynomials
    def test_10_subtract_sparse_polynomials(self):
        """Test subtracting sparse polynomials"""
        p1 = Polynomial([1, 0, 0, 0, 5000])
        p2 = Polynomial([0, 0, 0, 0, 1])
        result = p1 - p2
        self.assertEqual(str(result), "x^4 + 4999")

    # 11. equal polynomials

    def test_equal_polynomials(self):
        """Test subtracting sparse polynomials"""
        p1 = Polynomial([1, 0, -9, 0, 5000])
        p2 = Polynomial([1, 0, -9, 0, 5000])
        result = p1 - p2
        self.assertEqual(str(result), "0")

    # ----------- Tests for __gt__ ----------- #
    # 1. Higher degree
    def test_01_higher_degree(self):
        """Test if a polynomial with a higher degree is considered greater."""
        p1 = Polynomial([1, 2, 3])  # Degree 2
        p2 = Polynomial([4, 5])  # Degree 1
        self.assertTrue(p1 > p2)

    # 2. Lower degree
    def test_02_lower_degree(self):
        """Test if a polynomial with a lower degree is considered smaller."""
        p1 = Polynomial([4, 5])  # Degree 1
        p2 = Polynomial([1, 2, 3])  # Degree 2
        self.assertFalse(p1 > p2)

    # 3. Equal degree, higher coefficient
    def test_03_equal_degree_higher_coefficient(self):
        """Test if a polynomial with a higher leading coefficient is greater when degrees are equal."""
        p1 = Polynomial([3, 2, 1])  # Leading coefficient 3
        p2 = Polynomial([2, 2, 1])  # Leading coefficient 2
        self.assertTrue(p1 > p2)

    # 4. Equal degree, lower coefficient
    def test_04_equal_degree_lower_coefficient(self):
        """Test if a polynomial with a lower leading coefficient is considered smaller when degrees are equal."""
        p1 = Polynomial([2, 2, 1])  # Leading coefficient 2
        p2 = Polynomial([3, 2, 1])  # Leading coefficient 3
        self.assertFalse(p1 > p2)

    # 5. Identical polynomials
    def test_05_identical_polynomials(self):
        """Test if two identical polynomials are considered equal and return False."""
        p1 = Polynomial([1, 2, 3])
        p2 = Polynomial([1, 2, 3])
        self.assertFalse(p1 > p2)

    # 6. Polynomials with internal zeros
    def test_07_polynomials_with_internal_zeros(self):
        """Test polynomials with internal zeros."""
        p1 = Polynomial([3, 0, 1])  # Degree 2, leading coefficient 3
        p2 = Polynomial([3, 0, 0])  # Degree 2, leading coefficient 3
        self.assertTrue(p1 > p2)

    # 7. Polynomials with negative coefficients
    def test_08_polynomials_with_negative_coefficients(self):
        """Test if polynomials with negative coefficients are compared correctly."""
        p1 = Polynomial([-1, -2, -3])
        p2 = Polynomial([-4, -5, -6])
        self.assertTrue(p1 > p2)

    # 8. Zero and empty polynomials
    def test_09_zero_and_empty_polynomials(self):
        """Test if a zero or empty polynomial is considered smaller than any other polynomial."""
        p1 = Polynomial([0])
        p2 = Polynomial([1])
        self.assertFalse(p1 > p2)

    # 9. Last coefficient check
    def test_10_last_coefficient_check(self):
        """Test if the last coefficient matters when degrees are equal."""
        p1 = Polynomial([1, 0, 0, 5])  # Last coefficient 5
        p2 = Polynomial([1, 0, 0, 4])  # Last coefficient 4
        self.assertTrue(p1 > p2)

    # ----------- Tests for __mul__ ----------- #

    # 1. Multiplying two polynomials of different lengths
    def test_01_multiply_different_lengths(self):
        """Test multiplying polynomials of different lengths"""
        p1 = Polynomial([1, -2])
        p2 = Polynomial([1, 0, 0, 0, 5000])
        result = p1 * p2
        self.assertEqual(str(result), "x^5 + -2x^4 + 5000x + -10000")

    # 2. Multiplying polynomials with negative coefficients
    def test_02_multiply_negative_coefficients(self):
        """Test multiplying polynomials with negative coefficients"""
        p1 = Polynomial([-3, -2, -1])
        p2 = Polynomial([-1, 2])
        result = p1 * p2
        self.assertEqual(str(result), "3x^3 + -4x^2 + -3x + -2")

    # 3. Multiplying by a zero polynomial
    def test_03_multiply_by_zero_polynomial(self):
        """Test multiplying any polynomial by a zero polynomial"""
        p1 = Polynomial([1, -1, -5, -20, 5000])
        p2 = Polynomial([0])
        result = p1 * p2
        self.assertEqual(str(result), "0")

    # 4. Multiplying two zero polynomials
    def test_04_multiply_two_zero_polynomials(self):
        """Test multiplying two zero polynomials"""
        p1 = Polynomial([0, 0, 0])
        p2 = Polynomial([0, 0])
        result = p1 * p2
        self.assertEqual(str(result), "0")

    # 5. Multiplying by a single coefficient (scalar)
    def test_05_multiply_by_scalar(self):
        """Test multiplying by a single coefficient"""
        p1 = Polynomial([3])
        p2 = Polynomial([5])
        result = p1 * p2
        self.assertEqual(str(result), "15")

    # 6. Multiplying sparse polynomials
    def test_06_multiply_sparse_polynomials(self):
        """Test multiplying sparse polynomials"""
        p1 = Polynomial([1, 0, 0, 0, 5000])
        p2 = Polynomial([0, 0, 0, 0, 1])
        result = p1 * p2
        self.assertEqual(str(result), "x^4 + 5000")

    # 7. Multiplying identical polynomials
    def test_07_multiply_identical_polynomials(self):
        """Test multiplying identical polynomials"""
        p1 = Polynomial([1, 1])
        result = p1 * p1
        self.assertEqual(str(result), "x^2 + 2x + 1")

    # 8. Multiplying polynomials with large coefficients
    def test_08_multiply_large_coefficients(self):
        """Test multiplying polynomials with large coefficients"""
        p1 = Polynomial([10, -10])
        p2 = Polynomial([-10, 10])
        result = p1 * p2
        self.assertEqual(str(result), "-100x^2 + 200x + -100")

    # 9. Multiplying a polynomial by 1
    def test_09_multiply_by_one(self):
        """Test multiplying a polynomial by 1"""
        p1 = Polynomial([3, -2, 1])
        p2 = Polynomial([1])
        result = p1 * p2
        self.assertEqual(str(result), "3x^2 + -2x + 1")

    # 10. Multiplying a polynomial by -1
    def test_10_multiply_by_negative_one(self):
        """Test multiplying a polynomial by -1"""
        p1 = Polynomial([3, -2, 1])
        p2 = Polynomial([-1])
        result = p1 * p2
        self.assertEqual(str(result), "-3x^2 + 2x + -1")

    # ----------- Tests for verify_zero() ----------- #
    # 1. Test removing leading zeros
    def test_01_leading_zeros(self):
        """Test removing leading zeros from coefficients"""
        coefficients = [0, 0, 3, 5]
        result = Polynomial.verify_zero(Polynomial(coefficients))
        self.assertEqual(result, [3, 5])

    # 2. Test zero polynomial with multiple zeros
    def test_02_zero_polynomial(self):
        """Test a polynomial consisting only of zeros"""
        coefficients = [0, 0, 0, 0]
        result = Polynomial.verify_zero(Polynomial(coefficients))
        self.assertEqual(result, [0])

    # 3. Test polynomial with no leading zeros
    def test_03_no_leading_zeros(self):
        """Test a polynomial that already has no leading zeros"""
        coefficients = [3, 5, 0]
        result = Polynomial.verify_zero(Polynomial(coefficients))
        self.assertEqual(result, [3, 5, 0])

    # 4. Test single zero polynomial
    def test_04_single_zero(self):
        """Test a single zero coefficient"""
        coefficients = [0]
        result = Polynomial.verify_zero(Polynomial(coefficients))
        self.assertEqual(result, [0])

    # 5. Test polynomial with negative coefficients
    def test_05_negative_coefficients(self):
        """Test removing leading zeros with negative coefficients"""
        coefficients = [0, 0, -3, -5]
        result = Polynomial.verify_zero(Polynomial(coefficients))
        self.assertEqual(result, [-3, -5])

    # 6. Test polynomial with mixed coefficients
    def test_06_mixed_coefficients(self):
        """Test removing leading zeros with mixed coefficients"""
        coefficients = [0, 0, -3, 0, 5]
        result = Polynomial.verify_zero(Polynomial(coefficients))
        self.assertEqual(result, [-3, 0, 5])

    # 7. Test already valid polynomial
    def test_07_valid_polynomial(self):
        """Test a polynomial that does not require changes"""
        coefficients = [1, -2, 3]
        result = Polynomial.verify_zero(Polynomial(coefficients))
        self.assertEqual(result, [1, -2, 3])

    # 8. Test empty polynomial
    def test_08_empty_polynomial(self):
        """Test an empty polynomial"""
        coefficients = []
        result = Polynomial.verify_zero(Polynomial(coefficients))
        self.assertEqual(result, [0])

    # ----------- Tests for verify_zero() ----------- #
    # 1. Test evaluation with positive x
    def test_01_positive_x(self):
        """Test calculating polynomial value with positive x"""
        p = Polynomial([2, 3, 4])  # Represents 2x^2 + 3x + 4
        result = p.calc(2)  # 2(2^2) + 3(2) + 4 = 18
        self.assertEqual(result, 18)

    # 2. Test evaluation with negative x
    def test_02_negative_x(self):
        """Test calculating polynomial value with negative x"""
        p = Polynomial([1, -3, 2])  # Represents x^2 - 3x + 2
        result = p.calc(-1)  # (-1)^2 - 3(-1) + 2 = 6
        self.assertEqual(result, 6)

    # 3. Test evaluation with x = 0
    def test_03_zero_x(self):
        """Test calculating polynomial value with x = 0"""
        p = Polynomial([5, -4, 3])  # Represents 5x^2 - 4x + 3
        result = p.calc(0)  # 5(0^2) - 4(0) + 3 = 3
        self.assertEqual(result, 3)

    # 4. Test evaluation with zero polynomial
    def test_04_zero_polynomial(self):
        """Test calculating value of a zero polynomial"""
        p = Polynomial([0])  # Zero polynomial
        result = p.calc(10)  # Always 0, regardless of x
        self.assertEqual(result, 0)

    # 5. Test evaluation with a constant polynomial
    def test_05_constant_polynomial(self):
        """Test calculating value of a constant polynomial"""
        p = Polynomial([7])  # Represents 7
        result = p.calc(100)  # Always 7, regardless of x
        self.assertEqual(result, 7)

    # 6. Test evaluation with a linear polynomial
    def test_06_linear_polynomial(self):
        """Test calculating value of a linear polynomial"""
        p = Polynomial([3, -2])  # Represents 3x - 2
        result = p.calc(5)  # 3(5) - 2 = 13
        self.assertEqual(result, 13)

    # 7. Test evaluation with large coefficients
    def test_07_large_coefficients(self):
        """Test calculating value of polynomial with large coefficients"""
        p = Polynomial([10 ** 6, -10 ** 5, 10 ** 4])  # 10^6 x^2 - 10^5 x + 10^4
        result = p.calc(1)  # 10^6(1^2) - 10^5(1) + 10^4 = 910000
        self.assertEqual(result, 910000)

    # 8. Test evaluation with fractional x
    def test_08_fractional_x(self):
        """Test calculating polynomial value with fractional x"""
        p = Polynomial([2, -3, 1])  # Represents 2x^2 - 3x + 1
        result = p.calc(0.5)  # 2(0.5^2) - 3(0.5) + 1 = 0.5 - 1.5 + 1 = 0
        self.assertAlmostEqual(result, 0)

    # 9. Test evaluation with negative coefficients
    def test_09_negative_coefficients(self):
        """Test calculating polynomial value with negative coefficients"""
        p = Polynomial([-3, -2, -1])  # Represents -3x^2 - 2x - 1
        result = p.calc(2)  # -3(2^2) - 2(2) - 1 = -17
        self.assertEqual(result, -17)

    # 10. Test evaluation with a sparse polynomial
    def test_10_sparse_polynomial(self):
        """Test calculating value of a sparse polynomial"""
        p = Polynomial([1, 0, 0, 0, 5000])  # x^4 + 5000
        result = p.calc(2)  # (2^4) + 5000 = 16 + 5000 = 5016
        self.assertEqual(result, 5016)


if __name__ == "__main__":
    unittest.main()
