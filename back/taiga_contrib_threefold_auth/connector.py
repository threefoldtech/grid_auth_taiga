# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


import requests
import json

from collections import namedtuple

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import nacl
import nacl.signing
from nacl.public import Box
import base64

from taiga.base.connectors.exceptions import ConnectorBaseException


class ThreeFoldApiError(ConnectorBaseException):
    pass


######################################################
## Data
######################################################

APP_SECRET = getattr(settings, "THREEFOLD_API_APP_SECRET", None)
URL = getattr(settings, "THREEFOLD_URL", "https://login.threefold.me")
OPENKYC_URL = getattr(settings, "THREEFOLD_OPENKYC_URL", "https://openkyc.threefold.me/verification/verify-sei") 


HEADERS = {"Content-Type": "application/json"}

AuthInfo = namedtuple("AuthInfo", ["access_token"])
User = namedtuple("User", ["id", "username", "full_name", "bio", "email"])


######################################################
## utils
######################################################

def _get(url:str, headers:dict) -> dict:
    """
    Make a GET call.
    """
    response = requests.get(url, headers=headers)
    is_json = "application/json" in response.headers["Content-Type"]
    data = response.json() if is_json else {}

    if response.status_code != 200 or "error" in data:
        raise ThreeFoldApiError({"status_code": response.status_code,
                                  "error": data.get("error", "")})
    return data


def _post(url:str, params:dict, headers:dict) -> dict:
    """
    Make a POST call.
    """
    response = requests.post(url, json=params, headers=headers)
    is_json = "application/json" in response.headers["Content-Type"]
    data = response.json() if is_json else {}
    if response.status_code != 200 or "error" in data:
        raise ThreeFoldApiError({"status_code": response.status_code,
                                  "error": data.get("error", "")})
    return data

def removesuffix(text, suffix):
    # for python 3.8 and older as str.removesuffix is python 3.9+ only
    if suffix and text.endswith(suffix):
        return text[:-len(suffix)]
    return text
######################################################
## Simple calls
######################################################

def tf_login(signedAttempt:str, state:str):
    if not signedAttempt or not state:
        raise ThreeFoldApiError({"error_message": _("Login with threefold account is disabled. Contact "
                                                     "with the sysadmins. Maybe they're snoozing in a "
                                                     "secret hideout of the data center.")})
    # check signedAttempt data format
    signedData, username = check_signed_attempt(signedAttempt)

    # get user public key
    user_verify_key = get_user_verify_key(username)

    # verify data
    verifiedData = verify_signed_data(signedData, user_verify_key, username)
    
    # verify state
    verify_state(state, verifiedData["signedState"])
    

    # decrypt ciphertext
    app_signing_key = nacl.signing.SigningKey(APP_SECRET, encoder=nacl.encoding.Base64Encoder)

    decrypted_data = decrypt_cyphertext(verifiedData, user_verify_key, app_signing_key)
    
    # get user email data
    email, sei = get_user_email_data(decrypted_data)

    # verify user email
    _post(OPENKYC_URL, params={"signedEmailIdentifier": sei}, headers=HEADERS)

    # return user info
    username_no_suffix = removesuffix(username, ".3bot")
    return User(id=username,
                username=username_no_suffix,
                email=email,
                full_name=username_no_suffix,
                bio="")

def check_signed_attempt(signedAttempt:str):
    """
    Check if the signedAttempt is valid.
    """
    try:
        data = json.loads(signedAttempt)
        signedData = data["signedAttempt"]
        username = data['doubleName']
    except json.JSONDecodeError:
        raise ThreeFoldApiError({"error_message": _("invalid signedAttempt format.")})
    return signedData, username

def get_user_verify_key(username:str):
    data = _get(f"{URL}/api/users/{username}", HEADERS)
    if "publicKey" in data:
        return nacl.signing.VerifyKey(data["publicKey"], encoder=nacl.encoding.Base64Encoder)
    raise ThreeFoldApiError({"error_message": _("Error getting user pub key.")})

def verify_signed_data(signed_data, user_pub_key, username):
    verifiedData = user_pub_key.verify(base64.b64decode(signed_data)).decode()
    data = json.loads(verifiedData)
    if "doubleName" not in data or "signedState" not in data:
        raise ThreeFoldApiError({"error_message": _("Decrypted data missing required info.")})
    
    if data["doubleName"] != username:
        raise ThreeFoldApiError({"error_message": _("username mismatch!.")})
    return data

def verify_state(state:str, signedState):
    if signedState != state:
        raise ThreeFoldApiError({"error_message": _("Invalid state. not matching one in user session")})

def decrypt_cyphertext(verifiedData:dict, user_verify_key:nacl.signing.VerifyKey, app_signing_key:nacl.signing.SigningKey):
    nonce = base64.b64decode(verifiedData["data"]["nonce"])
    ciphertext = base64.b64decode(verifiedData["data"]["ciphertext"])
    try:
        box = Box(app_signing_key.to_curve25519_private_key(), user_verify_key.to_curve25519_public_key())
        decrypted = box.decrypt(ciphertext, nonce)
    except nacl.exceptions.CryptoError:
        raise ThreeFoldApiError({"error_message": _("Error decrypting data")})
    return decrypted

def get_user_email_data(decrypted_data:str):
    try:
        result = json.loads(decrypted_data)
    except json.JSONDecodeError:
        raise ThreeFoldApiError({"error_message": _("3bot login returned faulty data")})
    
    if "email" not in result:
        raise ThreeFoldApiError({"error_message": _("can't retrive user email")})

    return result["email"]["email"], result["email"]["sei"]

######################################################
## Convined calls
######################################################

def me(signedAttempt:str, state:str, redirectUri:str) -> tuple:
    """
    Connect to a threefold account and get all personal info (profile and the primary email).
    """
    user = tf_login(signedAttempt, state)

    return user.email, user

