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

 Interface implementation for conductor """
import requests
from pathlib import Path
from enum import Enum
from yarl import URL
from requests_toolbelt import MultipartEncoder
from .interfaces import Connector, DataManager


class Method(Enum):
    """ HTTP request types """
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4
'''
The class Method is an enumeration that defines the different HTTP request types. It inherits from the Enum class, which provides a way to define a set of named constants. 

The Method enum can be used to represent the type of HTTP request that is being made.
'''


class ConductorConnector(Connector):
    """ Connector for conductor api """

    def __init__(self, host, port, username, password, scheme="http", **params):
        super().__init__(params)
        self._api_url = URL.build(scheme=scheme, host=host, port=port)
        self._username = username
        self._password = password
        self._request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self._file_headers = {
            "Accept": "application/json"
        }
        self._login()

    def _login(self):
        """ Login to conductor and save token """
        response = requests.post(
            self._api_url.join(URL("/login")),
            headers=self._request_headers,
            json={"username": self._username, "password": self._password}
        )
        if response.status_code >= 300:
            raise RuntimeError(
                f"Cannot authenticate user by username {self._username} and password {self._password}, response: {response.text}")
        token = response.json().get("access_token")
        if not token:
            raise RuntimeError("Couldn't find 'access_token' field in response: " + response.text)
        self._request_headers["Authorization"] = "Bearer " + token
        self._file_headers["Authorization"] = "Bearer " + token

    def request(self, url: URL, method: Method, payload=None, stream=False):
        """ Make http request that sends and recieves json """
        result = None
        if method is Method.GET:
            result = requests.get(
                self._api_url.join(url),
                headers=self._request_headers,
                stream=stream
            )
        if method is Method.POST:
            result = requests.post(
                self._api_url.join(url),
                headers=self._request_headers,
                json=payload,
                stream=stream
            )
        if method is Method.PUT:
            result = requests.put(
                self._api_url.join(url),
                headers=self._request_headers,
                json=payload,
                stream=stream
            )
        if method is Method.DELETE:
            result = requests.delete(
                self._api_url.join(url),
                headers=self._request_headers,
                json=payload,
                stream=stream
            )
        return result

    def request_multipart(self, url: URL, method: Method, payload: dict, stream=False):
        """ Send or receive file from server """
        result = None
        form_data = MultipartEncoder(fields=payload)
        self._file_headers["Content-Type"] = form_data.content_type
        if method is Method.POST:
            result = requests.post(
                self._api_url.join(url),
                headers=self._file_headers,
                data=form_data,
                stream=stream
            )
        if method is Method.PUT:
            result = requests.put(
                self._api_url.join(url),
                headers=self._file_headers,
                data=form_data,
                stream=stream
            )
        if method is Method.DELETE:
            result = requests.delete(
                self._api_url.join(url),
                headers=self._file_headers,
                data=form_data,
                stream=stream
            )
        return result
'''
Acts as a connector to make authorized HTTP requests to the Conductor API.
Handles authentication, request headers, and file uploads/downloads.

Initialization:
- Inherits from a base Connector class (not shown).
- Stores host, port, username, password, and scheme (defaulting to "http").
- Builds the API URL using URL.build.
- Sets up request and file headers for JSON data.
- Performs initial login to obtain an access token.

Login:
- Sends a POST request to /login with credentials.
- Extracts and stores the access token from the response.
- Adds the token to Authorization header for subsequent requests.

Request:
- Takes URL, method, payload (optional), and stream (optional) as arguments.
- Uses requests library to make appropriate HTTP requests (GET, POST, PUT, DELETE) based on the method.
- Adds authentication token to headers.
- Handles JSON payload and streaming options.

RequestMultipart:
- Similar to request, but for sending/receiving files.
- Uses MultipartEncoder to prepare multipart form data.
- Sets appropriate Content-Type header.

This class provides a convenient way to interact with the Conductor API.
Authentication and header management are handled internally.
File uploads/downloads are also supported.
'''


class ConductorDataManager(DataManager):
    """ Implementation of DataManager for conductor api """

    def __init__(self, connector, **params):
        super().__init__(connector, params)

    def run_script(self, script: str, stream=False):
        """ Send script to the database and return response """
        response = self.connector.request(
            URL("/query/run"),
            Method.POST,
            {"script": script},
            stream
        )
        if stream:
            return response.iter_lines()
        else:
            return response.text

    def _send_multipart_request(self, name, path, mimetype):
        """ Stream multipart request """
        file_payload = {
            "network": (name, open(path, "rb"), mimetype)
        }
        response = self.connector.request_multipart(
            URL("/query/upload"),
            Method.POST,
            file_payload
        )
        return response

    def upload_file(self, filepath: str):
        """ Upload file to the database """
        filepath = Path(filepath)
        file_name = filepath.name
        extension = filepath.suffixes[0]
        abspath = filepath.resolve()
        if extension == ".xml":
            return self._send_multipart_request(file_name, abspath, "application/xml")
        if extension == ".json":
            return self._send_multipart_request(file_name, abspath, "application/json")
        else:
            raise RuntimeError("Only xml and json files are supported")
'''
Provides methods for executing scripts and uploading files to the Conductor database.

Initialization:
- Inherits from a base DataManager class (not shown).
- Stores the provided connector object for API communication.

Run Script:
- Takes a script string and an optional stream argument.
- Sends a POST request to /query/run with the script in the payload.
- Uses the connector to make the request and handle authentication.
- Returns the response text if not streaming, otherwise returns an iterator for line-by-line processing.

_send_multipart_request:
- Internal helper function for sending multipart requests (used for file uploads).
- Prepares a dictionary with file information (name, path, mimetype).
- Uses the connector to make a POST request to /query/upload with the multipart data.
- Returns the response from the API.

Upload File:
- Takes a filepath string as input.
- Validates the file extension to support only XML and JSON.
- Uses the _send_multipart_request helper to upload the file with appropriate content type.

This class offers convenient methods for script execution and file upload through the Conductor API.
The code is well-structured and uses the provided connector for API interactions.
'''