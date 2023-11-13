"""Tests for kwbar."""

import contextlib
import io
import random
import re
import sys
import unittest
import warnings


def strip_ansi(string: str) -> str:
    """Remove ANSI escape sequences from a string."""
    return re.sub(r"\x1b[^m]*m", "", string)


def is_ascii(string: str) -> bool:
    """Return True if the line is ASCII."""
    return all(ord(c) < 128 for c in string)


class TestKWBar(unittest.TestCase):
    kwbar = None

    @classmethod
    def setUp(cls):
        """Import kwbar."""
        import kwbar as _kwbar

        cls.kwbar = _kwbar

    @classmethod
    def tearDown(cls):
        """Delete kwbar."""
        sys.modules.pop("kwbar", None)
        cls.kwbar = None

    def test_fuzz_fixed_width_no_warnings(self):
        """Test that kwbar does not overrun or raise warnings with a fixed width."""
        # Arrange
        self.setUp()
        kwbar = self.kwbar
        kwbar.WIDTH = 23
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
        """Test that kwbar warns when the width runs over."""
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


if __name__ == "__main__":
    unittest.main()
