""" Helpers for the task resources """
import pytest
from pathlib import Path
from falcon import HTTP_202
from ....conductor.src.helpers.task_helpers import get_bool_field, generate_response, save_form_file
from ....conductor.src.exceptions import FormValidationError
from unittest.mock import MagicMock, patch


def test_get_bool_field_should_return_true_if_form_value_is_string_with_true():
    """ get_bool_field should return True if field value is 'true' """
    form_field = MagicMock()
    form_field.value = "true"
    form = {"field": form_field}
    assert get_bool_field(form, "field")
'''
- Verifies that the get_bool_field function returns True when the specified field in a form has the value "true" (as a string).
- Test Setup:
    - Creates a mock object form_field using MagicMock() to represent a form field.
    - Sets the value attribute of the mock field to "true".
    - Creates a dictionary form to represent a form, containing the mock field with the key "field".
- Test Execution:
    - Calls the get_bool_field function with the form and the field name "field".
    - Asserts that the function returns True.
'''


def test_get_bool_field_should_return_false_if_form_value_is_string_with_false():
    """ get_bool_field should return False if field value is 'false' """
    form_field = MagicMock()
    form_field.value = "false"
    form = {"field": form_field}
    assert not get_bool_field(form, "field")
'''
- Tests if get_bool_field returns False when the specified field value is the string "false".
- Test Setup:
    - Creates a mock form field (form_field) with the value "false".
    - Defines a form dictionary (form) containing the field.
- Test Execution:
    - Calls get_bool_field with the form and field name.
    - Uses not before the assertion to check if the returned value is indeed False.
'''


def test_get_bool_field_should_raise_FormValidationError_if_field_is_not_boolean():
    """
    get_bool_field should raise FormValidationError if
    form fields value is neither 'true' or 'false'
    """
    form_field = MagicMock()
    form_field.value = "random"
    form = {"wrong": form_field}
    with pytest.raises(FormValidationError):
        get_bool_field(form, "field")
'''
- Verifies that get_bool_field raises a FormValidationError if the value of the specified form field is not one of the strings "true" or "false".
- Test Setup:
    - Creates a mock form field (form_field) with the value "random".
    - Defines a form dictionary (form) containing the field with the key "wrong" (not "field").
- Test Execution:
    - Uses pytest.raises with FormValidationError as the expected exception:
    - Calls get_bool_field with the form and field name "field".
    - The assertion within the context manager is not explicitly shown, but it verifies that the expected exception is raised.
'''


def test_get_bool_field_should_return_default_when_set_and_value_is_not_boolean():
    """
    get_bool_field should return the default value if default is set and value is not a boolean
    """
    form_field = MagicMock()
    form_field.value = "pepe"
    default = True
    form = {"field": form_field}
    assert default == get_bool_field(form, "field", default)
'''
- Verifies that get_bool_field returns the provided default value when the form field's value is not a valid boolean string ("true" or "false") and a default value is specified.
- Test Setup:
    - Creates a mock form field with a non-boolean value ("pepe").
    - Sets a default value (default) to True.
    - Creates a form dictionary containing the field.
- Test Execution:
    - Calls get_bool_field with the form, field name, and default value.
    - Asserts that the returned value matches the provided default.
'''


def test_generate_response_should_set_http_code_to_202_and_set_operation_location_header():
    """
    generate_response should set the http response code to 202 accepted and
    set the Operation-Location header to the address of the operation results
    """
    response_mock = MagicMock()
    task_id = "some-task-id"
    generate_response(response_mock, task_id)
    assert response_mock.status == HTTP_202
    response_mock.append_header.assert_called_once_with("Operation-Location", "/v1.0/operations/" + str(task_id))
'''
- Tests if generate_response sets the HTTP status code to 202 ("Accepted") and adds the "Operation-Location" header with the specified format using the provided task ID.
- Test Setup:
    - Creates a mock object (response_mock) representing the HTTP response.
    - Defines a task_id string to be used during header construction.
- Test Execution:
    - Calling generate_response:
        - Calls generate_response with the response_mock and task_id.
    - Verifying HTTP Status Code:
        - Asserts that the response_mock.status attribute (representing the HTTP code) is equal to HTTP_202.
    - Verifying Header Addition:
        - Uses response_mock.append_header.assert_called_once_with to check if the append_header method was called once with the expected arguments:
            - First argument: "Operation-Location" (header name)
            - Second argument: Formatted URL using the task_id (e.g., "/v1.0/operations/some-task-id")
'''


def test_save_form_file_should_save_file_in_user_directory_and_return_filepath():
    """
    save_form_file should sanitize the filename, add it to the user directory, save the file
    and return the filepath
    """
    form_field = MagicMock()
    form_field.filename = "path/to/file.json"
    file_mock = MagicMock()
    form_field.file = file_mock
    user_folder = Path("/some/user/path/")
    form = {"file": form_field}
    with patch("sna.conductor.src.helpers.task_helpers.save_file") as save_mock:
        save_form_file(form, user_folder, "file")
        save_args = save_mock.call_args[0]
        assert save_args[0] is file_mock
        assert str(user_folder / "path_to_file.json") == save_args[1]
'''
- Verifies that the save_form_file function performs the following:
- Sanitizes the filename (removes path separators).
- Saves the file in the specified user directory.
- Returns the correct filepath.

- Test Setup:
    - Creates mock objects:
        - form_field: Represents a form field with a filename and file object.
        - file_mock: Represents the file to be saved.
        - user_folder: A Path object for the user's directory.
    - Constructs a form dictionary containing the mock field.
- Test Execution:
    - Patches the save_file function with a mock (save_mock) to isolate save_form_file's behavior.
    - Calls save_form_file with the form, user folder, and field name.
- Assertions:
    - Checks if save_mock was called with the expected arguments:
        - save_args[0] (file object) should be the file_mock.
        - save_args[1] (filepath) should be the sanitized filename joined with the user folder path.
'''


def test_save_form_file_should_raise_FormValidationError_if_field_not_found():
    """
    save_form_file_should raise FormValidationError if the field is not found
    on the form
    """
    user_folder = Path("/some/user/path/")
    form = {}
    with pytest.raises(FormValidationError):
        save_form_file(form, user_folder, "file")
'''
- Test Setup:
    - Creates a user_folder path object representing the user's directory.
    - Constructs an empty form dictionary (no "file" field).
- Test Execution:
    - Uses pytest.raises with FormValidationError as the expected exception:
    - Calls save_form_file with the empty form, user folder, and field name "file".
- Assertion:
    - The actual assertion is not explicitly shown in the code, but within the with pytest.raises context manager, it verifies that the expected FormValidationError exception is raised during function execution.
'''
