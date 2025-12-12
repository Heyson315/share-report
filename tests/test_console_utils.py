"""Tests for console utilities module."""
import io
import sys
from contextlib import redirect_stdout

from src.core.console_utils import print_header


def test_print_header_default():
    """Test print_header with default parameters."""
    output = io.StringIO()
    with redirect_stdout(output):
        print_header("Test Header")
    
    result = output.getvalue()
    assert "=" * 80 in result
    assert "Test Header" in result
    # Should have 3 lines: newline + equals + title + equals + newline
    assert result.count("\n") >= 3


def test_print_header_custom_width():
    """Test print_header with custom width."""
    output = io.StringIO()
    with redirect_stdout(output):
        print_header("Test", width=40)
    
    result = output.getvalue()
    assert "=" * 40 in result
    assert "Test" in result


def test_print_header_custom_char():
    """Test print_header with custom character."""
    output = io.StringIO()
    with redirect_stdout(output):
        print_header("Test", char="-")
    
    result = output.getvalue()
    assert "-" * 80 in result
    assert "=" not in result
    assert "Test" in result


def test_print_header_returns_none():
    """Test that print_header returns None."""
    result = print_header("Test")
    assert result is None
