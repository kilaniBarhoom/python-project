"""
Form validation utilities
Extracted from Flask routes/auth_routes.py validation logic
"""


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username meets requirements

    Args:
        username: Username to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not username:
        return False, "Username is required"

    username = username.strip()

    if len(username) < 4:
        return False, "Username must be at least 4 characters"

    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password meets requirements

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not password:
        return False, "Password is required"

    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    return True, ""


def validate_passwords_match(password: str, confirm_password: str) -> tuple[bool, str]:
    """
    Validate that passwords match

    Args:
        password: Password
        confirm_password: Confirmation password

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if password != confirm_password:
        return False, "Passwords do not match!"

    return True, ""


def validate_required_fields(**kwargs) -> tuple[bool, str]:
    """
    Validate that all required fields are provided

    Args:
        **kwargs: Dictionary of field_name: value pairs

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    for field_name, value in kwargs.items():
        if not value or (isinstance(value, str) and not value.strip()):
            # Convert field_name from snake_case to Title Case for display
            display_name = field_name.replace('_', ' ').title()
            return False, f"{display_name} is required"

    return True, ""


def validate_signup_form(fullname: str, username: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """
    Validate complete signup form
    Matches validation logic from routes/auth_routes.py lines 68-82

    Args:
        fullname: User's full name
        username: Username
        password: Password
        confirm_password: Password confirmation

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    # Check all fields are provided
    is_valid, message = validate_required_fields(
        fullname=fullname,
        username=username,
        password=password,
        confirm_password=confirm_password
    )
    if not is_valid:
        return False, message

    # Validate username
    is_valid, message = validate_username(username)
    if not is_valid:
        return False, message

    # Validate password
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message

    # Validate passwords match
    is_valid, message = validate_passwords_match(password, confirm_password)
    if not is_valid:
        return False, message

    return True, ""


def validate_login_form(username: str, password: str) -> tuple[bool, str]:
    """
    Validate login form fields are provided

    Args:
        username: Username
        password: Password

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not username or not password:
        return False, "Please fill in all fields"

    return True, ""


def validate_record_form(title: str, description: str) -> tuple[bool, str]:
    """
    Validate record form has required fields

    Args:
        title: Record title
        description: Record description

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    is_valid, message = validate_required_fields(
        title=title,
        description=description
    )
    return is_valid, message


def validate_comment(content: str) -> tuple[bool, str]:
    """
    Validate comment content is not empty

    Args:
        content: Comment content

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not content or not content.strip():
        return False, "Comment cannot be empty"

    return True, ""
