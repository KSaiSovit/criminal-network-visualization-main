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

 Tests for Secure hook """
from unittest.mock import MagicMock
import pytest
from ....conductor.src.hooks.secure_resource import Secure, NotEnoughPrivileges, NotAuthorizedError
from ....storage.builtin_datasets import BuiltinDataset
from ....conductor.src.auth_models import User, Role


@pytest.fixture
def prepared_data():
    """ Prepare user and roles for authentification """
    dataset = BuiltinDataset("", from_file=False)
    role = Role(dataset).add_role("User", 0)
    bigger_role = Role(dataset).add_role("Admin", 1)
    user = User(dataset).store_user("admin", "Pass1234", "User")
    return (dataset, role, user)
'''
- Creates a mocked BuiltinDataset object (dataset) without loading from a file.
- Adds two roles to the dataset:
    - "User" with priority 0.
    - "Admin" with priority 1.
- Creates a user named "admin" with password "Pass1234" and assigns the "User" role to them.
- Returns a tuple containing the prepared data: (dataset, role, user).
'''


@pytest.fixture
def request_mock(prepared_data):
    """ Prepare mock for Request """
    mock = MagicMock()
    mock.context.user = prepared_data[2]
    return mock
'''
Creates a mock request object using MagicMock.
Sets the user attribute in the mock request's context to the user object retrieved from the prepared_data fixture.

- Dependency:
    - This fixture relies on the prepared_data fixture to provide the user object.
'''


def test_secure_should_raise_NotAuthorizedError_if_no_user_in_request_context(request_mock):
    """ Secure should raise NotAuthorizedError when no user found """
    secure_hook = Secure()
    request_mock.context.user = None
    with pytest.raises(NotAuthorizedError):
        secure_hook(request_mock, MagicMock(), MagicMock(), MagicMock())
'''
- Ensures that only authorized users can access functionalities decorated with the Secure decorator.
- Tests if the Secure hook checks for user presence in the request context.

- Test Setup:
    - Creates a Secure object (secure_hook).
    - Sets the user attribute in the request_mock.context to None, simulating an unauthorized user.
- Test Execution:
    - Uses pytest.raises with NotAuthorizedError as the expected exception:
    - Calls the secure_hook function with the mock request, response, and argument objects (not directly relevant in this test).
- Assertion:
    - The assertion is within the with pytest.raises context manager, verifying that the expected NotAuthorizedError is raised during function execution.
'''        

def test_secure_should_raise_NotEnoughPrivileges_if_role_with_higher_rank_required(request_mock):
    """ Secure should raise NotEnoughPrivileges when user role has smaller rank, than the one that needed """
    secure_hook = Secure("Admin")
    with pytest.raises(NotEnoughPrivileges):
        secure_hook(request_mock, MagicMock(), MagicMock(), MagicMock())
'''
- Verifies that the Secure class raises a NotEnoughPrivileges exception when the user's role doesn't meet the required role for a protected function.
- Tests role-based authorization enforced by the Secure hook.

- Test Setup:
    - Creates a Secure object (secure_hook), specifying the required role as "Admin".
    - Leverages the request_mock fixture, which provides a mock request with a user having the "User" role (as set up in the prepared_data fixture).
- Test Execution:
    - Uses pytest.raises with NotEnoughPrivileges as the expected exception:
    - Calls the secure_hook function with the mock request, response, and argument objects (not directly relevant in this test).
- Assertion:
    - The assertion is within the with pytest.raises context manager, verifying that the expected NotEnoughPrivileges is raised during function execution.
'''
