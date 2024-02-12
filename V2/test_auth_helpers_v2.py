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

 Test authorization helpers """
import jwt
import pytest
from datetime import datetime, timedelta
from ....conductor.src.helpers.auth_helpers import create_token, read_token, ALGORITHM, InvalidTokenError, TokenExpiredError
from ....conductor.src.config import config


def test_create_token_should_create_token_with_given_claims():
    """ passed claims into create_token should be in token """
    claim_name = "user_id"
    claims = {
        claim_name: 123
    }
    token = create_token(claims)
    decoded_claims = jwt.decode(token, config["JWT_SECRET_KEY"], algorithms=[ALGORITHM])
    assert claim_name in decoded_claims
    assert claims[claim_name] == decoded_claims[claim_name]
'''
This function verifies that the create_token function correctly includes the specified claims in the generated JSON Web Token (JWT).

Steps:
- Test Function Definition:
    - def test_create_token_should_create_token_with_given_claims(): Defines the test function with a descriptive name.
- Test Case Setup:
    - claim_name = "user_id": Sets the name of the claim to be tested (presumably related to user identification).
    - claims = {"user_id": 123}: Creates a dictionary of claims, containing the user_id with a value of 123.
- Token Generation:
    - token = create_token(claims): Calls the create_token function (not provided in the snippet) with the defined claims, expecting it to return the generated JWT.
- Claim Verification:
    - decoded_claims = jwt.decode(token, config["JWT_SECRET_KEY"], algorithms=[ALGORITHM]): Decodes the JWT using the jwt library, providing the secret key from the config dictionary and specifying the allowed algorithm.
    - assert claim_name in decoded_claims: Asserts that the claim_name is present in the decoded claims (meaning it was included in the token).
    - assert claims[claim_name] == decoded_claims[claim_name]: Asserts that the value of the claim_name in the decoded claims matches the value in the original claims dictionary, ensuring consistent data.
'''


def test_create_token_should_add_issue_date_to_token():
    """ create_token should create iat claim """
    token = create_token({})
    decoded_claims = jwt.decode(token, config["JWT_SECRET_KEY"], algorithms=[ALGORITHM])
    assert "iat" in decoded_claims
'''
to verify that the create_token function includes the "iat" (issued at) claim in the generated JSON Web Token (JWT).

Steps:
- Test Function Definition:
    - def test_create_token_should_add_issue_date_to_token(): Defines the test function with a descriptive name.
- Test Case Setup:
    - token = create_token({}): Calls the create_token function (not provided) with an empty dictionary as claims, assuming it generates a token regardless of claims.
- Claim Verification:
    - decoded_claims = jwt.decode(token, config["JWT_SECRET_KEY"], algorithms=[ALGORITHM]): Decodes the JWT using the jwt library, providing the secret key from the config dictionary and specifying the allowed algorithm.
    - assert "iat" in decoded_claims: Asserts that the key "iat" (issued at) exists in the decoded claims, ensuring the claim is present in the token.
'''


def test_create_token_should_add_expiration_date_to_token():
    """ create_token should add exp claim """
    token = create_token({})
    decoded_claims = jwt.decode(token, config["JWT_SECRET_KEY"], algorithms=[ALGORITHM])
    assert "exp" in decoded_claims
'''
to verify that the create_token function includes the "exp" (expiration time) claim in the generated JSON Web Token (JWT).

Steps:
- Test Function Definition:
    - def test_create_token_should_add_expiration_date_to_token(): Defines the test function with a descriptive name.
- Test Case Setup:
    - token = create_token({}): Calls the create_token function (not provided) with an empty dictionary as claims, assuming it generates a token regardless of claims.
- Claim Verification:
    - decoded_claims = jwt.decode(token, config["JWT_SECRET_KEY"], algorithms=[ALGORITHM]): Decodes the JWT using the jwt library, providing the secret key from the config dictionary and specifying the allowed algorithm.
    - assert "exp" in decoded_claims: Asserts that the key "exp" (expiration time) exists in the decoded claims, ensuring the claim is present in the token.
'''


def test_read_token_should_decode_token_and_return_dictionary_of_claims():
    """ read_token should return decoded claims """
    payload = {
        "user_id": 123
    }
    token = jwt.encode(payload, config["JWT_SECRET_KEY"], algorithm=ALGORITHM)
    decoded_claims = read_token(token)
    assert payload == decoded_claims
'''
This test function verifies that the read_token function correctly decodes a given JSON Web Token (JWT) and returns its payload as a dictionary of claims.

Steps:
- Test Function Definition:
    - def test_read_token_should_decode_token_and_return_dictionary_of_claims(): Defines the function with a descriptive name.
- Payload Setup:
    - payload = {"user_id": 123}: Creates a dictionary representing the claims to be included in the token.
- Token Creation:
    - token = jwt.encode(payload, config["JWT_SECRET_KEY"], algorithm=ALGORITHM): Generates a JWT using the jwt library, the payload, the secret key from the config dictionary, and the specified algorithm.
- Claim Decoding:
    - decoded_claims = read_token(token): Calls the read_token function (not provided) with the generated token, expecting it to return the decoded claims.
- Claim Verification:
    - assert payload == decoded_claims: Asserts that the original payload matches the decoded claims, ensuring accurate decoding.
'''


def test_read_token_should_raise_TokenExpiredError_if_token_expired():
    """ read_token should raise TokenExpiredError when exp > iat """
    payload = {
        "user_id": 123,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() - timedelta(minutes=10)
    }
    token = jwt.encode(payload, config["JWT_SECRET_KEY"], algorithm=ALGORITHM)
    with pytest.raises(TokenExpiredError):
        decoded_claims = read_token(token)
'''
To verify that the read_token function correctly raises a TokenExpiredError when it encounters an expired JWT.

Steps:
- Test Function Definition:
    - def test_read_token_should_raise_TokenExpiredError_if_token_expired(): Defines the function with a descriptive name.
- Payload Setup:
    - payload: Creates a dictionary representing the claims to be included in the token.
    - user_id: Sets the user ID claim.
    - iat: Sets the "issued at" timestamp to the current time.
    - exp: Sets the "expiration time" timestamp to 10 minutes before the current time.
- Token Creation:
    - token: Encodes the payload into a JWT using the jwt library, the secret key from the config dictionary, and the specified algorithm.
- Expected Exception:
    - with pytest.raises(TokenExpiredError): Wraps the subsequent code in a context manager expecting a TokenExpiredError to be raised.
- Token Decoding:
    - decoded_claims = read_token(token): Attempts to call the read_token function (not provided) with the generated token. The context manager ensures this raises the expected exception.
'''


def test_read_token_should_raise_InvalidTokenError_if_token_improperly_signed():
    """ read_token should raise InvalidTokenError when different properties used during encoding """
    payload = {
        "user_id": 123,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    token = jwt.encode(payload, "", algorithm=ALGORITHM)
    with pytest.raises(InvalidTokenError):
        decoded_claims = read_token(token)
'''
To verify that the read_token function raises an InvalidTokenError when it encounters a JWT signed with a different secret key than the one used for decoding.

Steps:
- Test Function Definition:
    - def test_read_token_should_raise_InvalidTokenError_if_token_improperly_signed(): Defines the function with a descriptive name.
- Payload Setup:
    - payload: Creates a dictionary representing the claims to be included in the token.
    - user_id: Sets the user ID claim.
    - iat: Sets the "issued at" timestamp to the current time.
    - exp: Sets the "expiration time" timestamp to 10 minutes in the future.
- Token Creation with Wrong Secret:
    - token: Encodes the payload into a JWT using the jwt library, but with an empty string instead of the actual secret key, and the specified algorithm. This creates a token signed with an incorrect key.
- Expected Exception:
    - with pytest.raises(InvalidTokenError): Wraps the subsequent code in a context manager expecting an InvalidTokenError to be raised.
- Token Decoding:
    - decoded_claims = read_token(token): Attempts to call the read_token function (not provided) with the generated token. The context manager ensures this raises the expected exception.
'''


def test_read_token_should_raise_InvalidTokenError_if_token_doesnt_have_required_claims():
    """ read_token should raise InvalidTokenError if required claim not found """
    payload = {
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    token = jwt.encode(payload, config["JWT_SECRET_KEY"], algorithm=ALGORITHM)
    with pytest.raises(InvalidTokenError):
        read_token(token, ["user_id"])
'''
This test funxtion verifies that the read_token function raises an InvalidTokenError when it encounters a JWT missing a required claim.

Steps:
- Test Function Definition:
    - def test_read_token_should_raise_InvalidTokenError_if_token_doesnt_have_required_claims(): Defines the function with a descriptive name.
- Payload Setup:
    - payload: Creates a dictionary representing the claims to be included in the token. It only includes iat and exp claims, without the required user_id claim.
- Token Creation:
    - token: Encodes the payload into a JWT using the jwt library, the secret key from the config dictionary, and the specified algorithm.
- Expected Exception:
    - with pytest.raises(InvalidTokenError): Wraps the subsequent code in a context manager expecting an InvalidTokenError to be raised.
- Token Decoding with Required Claims:
    - read_token(token, ["user_id"]): Attempts to call the read_token function (not provided) with the generated token and a list of required claims, including "user_id". Since the token doesn't have this claim, the context manager ensures the expected exception is raised.
'''
