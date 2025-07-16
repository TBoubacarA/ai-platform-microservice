from app.core.sanitization import Sanitizer
from app.config import Config

def test_input_sanitization():
    # Test length validation
    long_text = "a" * (Config.MAX_INPUT_LENGTH + 1)
    try:
        Sanitizer.sanitize_input(long_text)
        assert False, "Should have raised exception"
    except ValueError as e:
        assert "exceeds maximum length" in str(e)
    
    # Test blacklist
    try:
        Sanitizer.sanitize_input("This is a malicious text")
        assert False, "Should have raised exception"
    except ValueError as e:
        assert "Forbidden content" in str(e)
    
    # Test HTML stripping
    cleaned = Sanitizer.sanitize_input("<script>alert('xss')</script>")
    assert "<script>" not in cleaned

def test_output_sanitization():
    # Test truncation
    long_text = "a" * (Config.MAX_INPUT_LENGTH * 3)
    cleaned = Sanitizer.sanitize_output(long_text)
    assert len(cleaned) <= Config.MAX_INPUT_LENGTH * 2 + len("... [TRUNCATED]")
    assert "[TRUNCATED]" in cleaned
    
    # Test control characters removal
    text_with_control = "Hello\x00World\x1F"
    cleaned = Sanitizer.sanitize_output(text_with_control)
    assert "\x00" not in cleaned
    assert "\x1F" not in cleaned