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

 Test file helpers """
import pytest
from unittest.mock import MagicMock, patch
from ....conductor.src.helpers.file_helpers import save_file, FileExistsError, CHUNK_SIZE


def test_save_file_should_copy_file_into_file_on_disc():
    """ save_file should read passed file and write it into new file if file does not exists """
    file_mock = MagicMock()
    file_mock.read.return_value = None
    filepath = "/tmp/files/file.json"
    with patch("sna.conductor.src.helpers.file_helpers.isfile") as file_checker:
        file_checker.return_value = False
        with patch("sna.conductor.src.helpers.file_helpers.open") as open_mock:
                save_file(file_mock, filepath)
                file_mock.read.assert_called_once_with(CHUNK_SIZE)


def test_save_file_should_raise_FileExistsError_if_file_on_given_path_exists():
    """ save_file should raise FileExistsError if isfile returns True """
    file_mock = MagicMock()
    filepath = "/tmp/files/file.json"
    with patch("sna.conductor.src.helpers.file_helpers.isfile") as file_checker:
        file_checker.return_value = True
        with pytest.raises(FileExistsError):
            save_file(file_mock, filepath)


'''
- Imports:
    - pytest: This imports the pytest library for writing unit tests.
    - MagicMock and patch: These functions from unittest.mock are used to create mock objects and temporarily patch functions during testing.
- Test Functions:
    - test_save_file_should_copy_file_into_file_on_disc():
        - Tests if save_file successfully reads from a provided file and writes it to a new file on disk if it doesn't already exist.
        - Mock Setup:
            - file_mock: Uses MagicMock to create a mock object representing the input file.
            - isfile (patched): Uses patch to temporarily replace the isfile function with a mock that returns False (file doesn't exist).
            - open (patched): Uses patch to temporarily replace the open function with a mock that opens the output file for writing.
        - Test Logic:
            - Calls save_file with file_mock and the target filepath.
            - Asserts that file_mock.read was called once with CHUNK_SIZE to read the input file chunks.
    - test_save_file_should_raise_FileExistsError_if_file_on_given_path_exists():
        - Tests if save_file raises a FileExistsError when the destination file already exists.
        - Mock Setup:
            - file_mock: Similar to the previous test.
            - isfile (patched): Uses patch to temporarily replace isfile with a mock that returns True (file exists).
        - Test Logic:
            - Calls save_file with file_mock and the target filepath.
            - Uses pytest.raises to expect a FileExistsError exception.

The tests use mocks to isolate and test the save_file function's behavior.
patch is used to mock external dependencies (isfile and open) for controlled testing.
Specific assertions are made to verify expected behavior (file_mock.read calls).
'''
