"""
=================================== LICENSE ==================================
Copyright (c) 2021, Consortium Board ROXANNE
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

Neither the name of the ROXANNE nor the
names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY CONSORTIUM BOARD ROXANNE ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL CONSORTIUM BOARD TENCOMPETENCE BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
==============================================================================

 Tests for validate_schema decorator """
import pytest
from unittest.mock import MagicMock, Mock
from falcon import Request
from ....conductor.src.helpers.validate_schema import validate_schema, InputMachingError, OutputMatchingError

@pytest.fixture
def request_mock():
    request = MagicMock()
    request.media = {
        "key": "val"
    }
    del request.context.form
    return request
'''
- This fixture creates a mock object representing an HTTP request using MagicMock. It sets up specific attributes to be used in tests:
    - request.media: A dictionary with a key-value pair ("key": "val"). This likely represents data received in the request body.
    - del request.context.form: This line intentionally removes the form attribute from the mock request's context attribute. Its exact purpose is unclear without more context.
'''

def test_validate_schema_should_validate_dictonary_data_in_request_media(request_mock):
    """ validate_schema should decorate request handler with function, that will walidate Request.media agains given schema """
    schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"}
        },
        "required": ["key"]
    }
    @validate_schema(schema)
    def func(self, req, resp):
        assert req.media == {"key": "val"}
    func(MagicMock(), request_mock, MagicMock())
'''
- Tests if the validate_schema decorator ensures the request data (in req.media) conforms to the provided schema before calling the decorated function.
- Test Setup:
    - Defines a schema dictionary representing the expected data structure.
    - Uses a decorator syntax to apply validate_schema with the schema to a mock function func.
    - Creates mock objects for request and response (not used in the assertion).
- Test Execution:
    - Calls the decorated func with the mock objects, simulating a request.
- Assertion:
    - Asserts that req.media (the request data) within the decorated function matches the expected dictionary ({"key": "val"}). This implies successful validation using the provided schema.
'''

def test_validate_schema_should_raise_InputMachingError_if_schema_not_matched(request_mock):
    """ validate_schema should decorate request handler with function, that raises InputMachingError if Request.media does not match schema """
    schema = {
        "type": "object",
        "properties": {
            "key": {"type": "number"},
            "field": {"type": "number"}
        }
    }
    @validate_schema(schema)
    def func(self, req, resp):
        pass
    with pytest.raises(InputMachingError):
        func(MagicMock(), request_mock, MagicMock())
'''
- Verifies that the validate_schema decorator raises an InputMachingError exception when the request data (req.media) does not conform to the provided schema.
- Test Setup:
    - Defines a more restrictive schema requiring two numeric properties (key and field).
    - Applies the validate_schema decorator to a mock function func with the stricter schema.
    - Creates mock objects for request and response.
- Test Execution:
    - Uses pytest.raises with InputMachingError as the expected exception:
    - Calls the decorated func with the mock objects.
- Assertion:
    - The assertion is within the with pytest.raises context manager, verifying that the expected InputMachingError is raised during function execution.
'''

def test_validate_schema_should_validate_dictonary_data_in_response_media(request_mock):
    """ validate_schema should decorate request handler with function, that will walidate Request.media agains given schema """
    schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "field": {"type": "number"}
        }
    }
    out_schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"}
        },
        "required": ["key"]
    }
    response_mock = MagicMock()
    @validate_schema(schema, out_schema)
    def func(self, req, resp):
        resp.media = req.media
    func(MagicMock(), request_mock, response_mock)
    assert response_mock.media == request_mock.media
'''
- Tests if the validate_schema decorator, when provided with an additional out_schema, validates the data assigned to resp.media (the response data) before sending the response.
- Test Setup:
    - Defines two schemas:
        - schema: Used for request data validation (as seen in previous tests).
        - out_schema: Used for response data validation.
        - Creates a mock object for the response (response_mock).
        - Applies validate_schema with both schemas to a mock function func.
- Test Execution:
    - Calls the decorated func, which sets resp.media to the request data.
- Assertion:
    - Asserts that response_mock.media (the response data) remains unchanged, implying successful validation against the out_schema.
'''

def test_validate_schema_should_raise_OutputMatchingError_if_output_schema_not_matched(request_mock):
    """ validate_schema should decorate request handler with function, that raises OutputMatchingError if Response.media does not match schema """
    schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"}
        }
    }
    out_schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "field": {"type": "number"}
        },
        "required": ["key", "field"]
    }
    out_mock = MagicMock()
    out_mock.stream = None
    @validate_schema(schema, out_schema)
    def func(self, req, resp):
        resp.media = req.media
    with pytest.raises(OutputMatchingError):
        func(MagicMock(), request_mock, out_mock)
'''
- Tests if the validate_schema decorator raises an OutputMatchingError exception when the response data (resp.media) does not conform to the provided out_schema.
- Test Setup:
    - Defines two schemas:
        - schema: Used for request data validation (not directly relevant in this test).
        - out_schema: Requires a key and field property, both strings.
    - Creates a mock object for the response (out_mock).
    - Sets out_mock.stream to None, likely to avoid potential side effects during validation.
    - Applies validate_schema with both schemas to a mock function func.
- Test Execution:
    - Uses pytest.raises with OutputMatchingError as the expected exception:
    - Calls the decorated func, which sets resp.media to the request data that doesn't match out_schema.
- Assertion:
    - The assertion is within the with pytest.raises context manager, verifying that the expected OutputMatchingError is raised during function execution.
'''
