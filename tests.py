"""Tests for kwbar."""

import contextlib
import io
import itertools
import random
import re
import sys
import unittest
import warnings

from kwbar import WIDTH


def strip_ansi(string: str) -> str:
    """Remove ANSI escape sequences from a string."""
    return re.sub(r"\x1b[^m]*m", "", string)


def is_ascii(string: str) -> bool:
    """Return True if the line is ASCII."""
    return all(ord(c) < 128 for c in string)


class TestTests(unittest.TestCase):
    """Test the test utility functions."""

    def test_strip_ansi(self):
        """Test strip_ansi function."""
        self.assertEqual(strip_ansi("\x1b[31mHello\x1b[0m"), "Hello")

    def test_is_ascii(self):
        """Test is_ascii function."""
        self.assertTrue(is_ascii("Hello"))
        self.assertFalse(is_ascii("こんにちは"))


class TestKwbar(unittest.TestCase):
    """Test cases for kwbar."""

    kwbar = None

    @classmethod
    def setUp(cls):
        """Set up the test case."""
        import kwbar as _kwbar

        cls.kwbar = _kwbar

    @classmethod
    def tearDown(cls):
        """Tear down the test case."""
        sys.modules.pop("kwbar", None)
        cls.kwbar = None

    def test_kwbar_empty_input(self):
        """Test that kwbar raises an exception with empty input."""
        # Arrange
        self.setUp()
        kwbar = self.kwbar
        # Act & Assert
        with self.assertRaises(ValueError):
            kwbar.kwbar()

    def test_fuzz_fixed_width_no_warnings(self):
        """Test that kwbar does not overrun or raise warnings with a fixed width."""
        # Arrange
        self.setUp()
        kwbar = self.kwbar
        kwbar.WIDTH = 24
        kwbar.TRUNCATE = 4
        for _ in range(10_000):
            data = {
                str(float(v)): v for v in (random.randint(0, 10_000) for _ in range(5))
            }
            out = io.StringIO()
            with warnings.catch_warnings(record=True) as w, contextlib.redirect_stdout(
                out
            ):
                # Act
                kwbar.kwbar(**data)
            # Assert
            self.assertEqual(len(w), 0, "warnings.warn was called")
            for line in out.getvalue().splitlines():
                line = strip_ansi(line)
                self.assertLessEqual(len(line), kwbar.WIDTH)
        self.tearDown()

    def test_warns_over_width(self):
        """Test that kwbar warns when the output overflows."""
        # Arrange
        self.setUp()
        kwbar = self.kwbar
        kwbar.WIDTH = 19
        kwbar.TRUNCATE = 4
        out = io.StringIO()
        with warnings.catch_warnings(record=True) as w, contextlib.redirect_stdout(out):
            # Act
            kwbar.kwbar(one=1, two=2, pi=3.14)
        # Assert
        self.assertGreaterEqual(len(w), 1, "warnings.warn was not called")
        self.assertIn("overflow", str(w[0].message))
        self.tearDown()

    def test_ascii_mode(self):
        """Test that kwbar only outputs ASCII after ascii() is called."""
        # Arrange
        kwbar = self.kwbar
        kwbar.WIDTH = 40
        kwbar.TRUNCATE = 4
        kwbar.ascii()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            # Act
            kwbar.kwbar(one=1, two=2, pi=3.14)
        for line in out.getvalue().splitlines():
            # Assert
            self.assertTrue(is_ascii(line))
        self.tearDown()

    def test_hotdog_mode(self):
        """Test that kwbar uses hotdog mode when requested."""
        # Arrange
        self.setUp()
        kwbar = self.kwbar
        kwbar.WIDTH = 40
        kwbar.TRUNCATE = 4
        kwbar.hotdog()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            # Act
            kwbar.kwbar(one=1, two=2, pi=3.14)
        # Assert
        self.assertTrue("🌭" in out.getvalue())
        self.tearDown()

    def test_partial_hotdogs(self):
        """Test that hotdogs counts and rounding are correct.

        Hotdog mode shows to the nearest 1/8th of a hotdog:
        - 1/8 = 0.125 [0.0000, 0.1875) A nibble
        - 1/4 = 0.250 [0.1875, 0.3125) A generous bite
        - 3/8 = 0.375 [0.3125, 0.4375) More than a bite
        - 1/2 = 0.500 [0.4375, 0.5625) A fair share
        - 5/8 = 0.625 [0.5625, 0.6875) A little more than half a dog
        - 3/4 = 0.750 [0.6875, 0.8125) A good portion
        - 7/8 = 0.875 [0.8125, 0.9375) Nearly a whole hotdog
        - 🌭  = 1.000 [0.9375, 1.0000] Close enough
        """
        # Arrange
        self.setUp()
        kwbar = self.kwbar
        kwbar.WIDTH = 23
        kwbar.TRUNCATE = 10
        # This will make the max bar width of 12 dogs
        kwbar.hotdog()
        kwbar.SHOW_VALS = False
        kwbar.BEFORE = True
        out = io.StringIO()
        with warnings.catch_warnings(record=True) as w, contextlib.redirect_stdout(out):
            # Act
            kwbar.kwbar(
                dozen=12,
                half=6,
                pie=3.1,
                quarter=0.1875,
                abomination=0.31251,  # 5/8 is not a useful fraction
                nearly=0.9374999999999999,
                kinda=0.9375,
            )
        # Assert
        # No warnings should be raised
        self.assertEqual(len(w), 0, "warnings.warn was called")
        # Check that there are a dozen dogs in line 0
        self.assertEqual(out.getvalue().splitlines()[0].count("🌭"), 12)
        # Verify that half a dozen is indeed 6 hotdogs
        self.assertEqual(out.getvalue().splitlines()[1].count("🌭"), 6)
        # Assert that a pie is about 3 and 1/8 hotdogs
        self.assertTrue(out.getvalue().splitlines()[2].endswith("🌭🌭🌭⅛"))
        # Assert that 0.1876 is shown as 1/4 hotdog
        self.assertTrue(out.getvalue().splitlines()[3].endswith("¼"))
        # Assert that 0.31251 is shown as 3/8 hotdog
        self.assertTrue(out.getvalue().splitlines()[4].endswith("⅜"))
        # Assert that 0.9374999999999999 is shown as 7/8 hotdog
        self.assertTrue(out.getvalue().splitlines()[5].endswith("⅞"))
        # Assert that 0.9375 is shown as 1 hotdog
        self.assertTrue(out.getvalue().splitlines()[6].endswith("🌭"))
        self.tearDown()

    def test_ascii_outside_no_vals(self):
        """Test correct bar lengths when no values are shown (OUTSIDE = True)."""
        self.setUp()
        kwbar = self.kwbar
        kwbar.ascii()
        kwbar.TRUNCATE = 10
        kwbar.WIDTH = kwbar.TRUNCATE + 12 + 1
        kwbar.SHOW_VALS = True
        kwbar.BEFORE = False
        out = io.StringIO()
        with warnings.catch_warnings(record=True) as w, contextlib.redirect_stdout(out):
            # Act
            kwbar.kwbar(
                dozen=12,
                half=6,
                pie=3.1,
                two=2,
                near_nil=0.1,
                near_one=0.9375,
            )
        # Assert
        # A warnings should be raised
        self.assertEqual(len(w), 1, "warnings.warn was not called")
        # Check that line 0 has 12 chars after the last space
        self.assertEqual(len(out.getvalue().splitlines()[0].split()[-1]), 12)
        self.tearDown()

    def test_ascii_outside_values(self):
        """Test correct bar lengths when values are shown outside (before) bars."""
        self.setUp()
        kwbar = self.kwbar
        kwbar.ascii()
        kwbar.WIDTH = 33
        kwbar.TRUNCATE = 10
        kwbar.SHOW_VALS = True
        kwbar.BEFORE = True
        out = io.StringIO()
        with warnings.catch_warnings(record=True) as w, contextlib.redirect_stdout(out):
            # Act
            kwbar.kwbar(
                dozen=12,
                half=6,
                pie=3.1,
                two=2,
                near_nil=0.1,
                near_one=0.9375,
            )
        # Assert
        # No warnings should be raised
        self.assertEqual(len(w), 0, "warnings.warn was called")
        # Check that there are a dozen Xs in line 0
        self.assertEqual(out.getvalue().splitlines()[0].count("X"), 12)
        # Verify that half a dozen is indeed 6 Xs
        self.assertEqual(out.getvalue().splitlines()[1].count("X"), 6)
        # Assert that a pie is about 3 XXXs
        self.assertEqual(out.getvalue().splitlines()[2].count("X"), 3)
        # Assert that two is shown as 2 Xs
        self.assertEqual(out.getvalue().splitlines()[3].count("X"), 2)
        # Assert that near zero showns no X
        self.assertEqual(out.getvalue().splitlines()[4].count("X"), 0)
        # Assert that near one shows 1 X
        self.assertEqual(out.getvalue().splitlines()[5].count("X"), 1)
        self.tearDown()

    def test_fuzz_outside_has_no_effect_when_show_vals_false(self):
        """Test that OUTSIDE makes no difference when SHOW_VALS is False."""
        self.setUp()
        kwbar = self.kwbar
        kwbar.ascii()
        kwbar.WIDTH = 25
        kwbar.SHOW_VALS = False

        # Generate random data
        random.seed(0)
        for _ in range(100):
            data = {str(v): v for v in (random.randint(0, 10_000) for _ in range(5))}
            outside_out = io.StringIO()
            inside_out = io.StringIO()

            # Set OUTSIDE
            kwbar.BEFORE = True
            with warnings.catch_warnings(
                record=True
            ) as outside_w, contextlib.redirect_stdout(outside_out):
                # Act
                kwbar.kwbar(**data)

            # Unset OUTSIDE
            kwbar.BEFORE = False
            with warnings.catch_warnings(
                record=True
            ) as inside_w, contextlib.redirect_stdout(inside_out):
                # Act
                kwbar.kwbar(**data)

            # Assert
            # No warnings should be raised
            self.assertEqual(len(outside_w), 0, "warnings.warn was called")
            self.assertEqual(len(inside_w), 0, "warnings.warn was called")

            # Assert that the output is the same
            self.assertEqual(outside_out.getvalue(), inside_out.getvalue())

        self.tearDown()

    def test_fixed_width(self):
        """Test the a fixed width output functions as expected."""
        # Arrange
        self.setUp()
        kwbar = self.kwbar
        WIDTHS = (23, 24, 32, 40, 48, 64, 72, 80)
        TRUNCATES = range(1, 11)
        data = {
            "one": 1,
            "half": 0.5,
        }
        for width, truncate in itertools.product(WIDTHS, TRUNCATES):
            kwbar.WIDTH = width
            kwbar.TRUNCATE = truncate
            # Sanity check
            should_fit = (kwbar.WIDTH - kwbar.TRUNCATE - kwbar.SF - 17) >= 0
            # Act
            out = io.StringIO()
            with warnings.catch_warnings(record=True) as w, contextlib.redirect_stdout(
                out
            ):
                kwbar.kwbar(**data)
            # Assert
            self.assertEqual(len(w), not should_fit, "warnings.warn was called")
        self.tearDown()

    def test_fuzz_fix_width_outside(self):
        """Ensure that width is fixed when OUTSIDE = True and TRUNCATE > 1."""
        # Arrange
        self.setUp()
        kwbar = self.kwbar
        kwbar.BEFORE = True
        WIDTHS = (23, 24, 32, 40, 48, 64, 72, 80)
        TRUNCATES = range(1, 11)
        random.seed(0)
        for _ in range(100):
            for width, truncate in itertools.product(WIDTHS, TRUNCATES):
                data = {
                    str(x): x for x in (random.randint(0, 10_000) for _ in range(5))
                }
                kwbar.WIDTH = width
                kwbar.TRUNCATE = truncate
                # Act
                out = io.StringIO()
                with warnings.catch_warnings(
                    record=True
                ) as w, contextlib.redirect_stdout(out):
                    kwbar.kwbar(**data)
                # Assert
                self.assertEqual(len(w), 0, "warnings.warn was called")
                max_line_len = max(len(line) for line in strip_ansi(out.getvalue()))
                self.assertLessEqual(max_line_len, width)


if __name__ == "__main__":
    unittest.main()
