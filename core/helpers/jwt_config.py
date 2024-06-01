# main.py
import logging
from datetime import datetime, timedelta
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import authentication

from AccountService import settings
from core.models import User
from jose import jwt

# JWT Configuration
ALGORITHM = settings.SIMPLE_JWT["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
REFRESH_TOKEN_EXPIRE_MINUTES = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
JWT_SECRET = settings.SECRET_KEY
JWT_ISSUER = settings.SIMPLE_JWT["ISSUER"]


# Function to create JWT token

def create_access_token(user: dict, expires_delta: int = None) -> str:
	if expires_delta is not None:
		expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)
	else:
		expires_delta = datetime.utcnow() + ACCESS_TOKEN_EXPIRE_MINUTES

	to_encode = {"exp": expires_delta, "user": user, "iss": JWT_ISSUER}
	encoded_jwt = jwt.encode(to_encode, JWT_SECRET, ALGORITHM)
	return encoded_jwt


def create_refresh_token(user: dict, expires_delta: int = None) -> str:
	if expires_delta is not None:
		expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)
	else:
		expires_delta = datetime.utcnow() + REFRESH_TOKEN_EXPIRE_MINUTES

	to_encode = {"exp": expires_delta, "user": user, "iss": JWT_ISSUER, "name": user["user_id"]}
	encoded_jwt = jwt.encode(to_encode, JWT_SECRET, ALGORITHM)
	return encoded_jwt


# Function to decode JWT token
def decode_access_token(token: str):
	try:
		payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])

		if datetime.utcnow().__ge__(datetime.fromtimestamp(payload['exp'])):
			raise AuthenticationFailed("Expired Access Token")
		if payload["iss"] != JWT_ISSUER:
			raise AuthenticationFailed("Invalid Access Token")
		return payload['user']
	except Exception as e:
		logging.critical(e)
		raise AuthenticationFailed(e)


def validate_refresh_token(token: str):
	try:
		payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
		if datetime.utcnow().__ge__(datetime.fromtimestamp(payload['exp'])):
			raise AuthenticationFailed("Expired refresh token")
		if payload["iss"] != JWT_ISSUER:
			raise AuthenticationFailed("Invalid Refresh Token")
		return payload['user']
	except Exception as e:
		raise AuthenticationFailed(e)


def refresh_access_token(refresh_token: str):
	user = validate_refresh_token(refresh_token)
	return create_access_token(user)


class JWTAuthentication(authentication.BaseAuthentication):

	def authenticate(self, request):
		auth_header = request.META.get('HTTP_AUTHORIZATION')
		if not auth_header:
			return None

		try:
			prefix, token = auth_header.split(' ')
			if prefix.lower() != 'bearer':
				raise AuthenticationFailed('Invalid authentication header')

			payload = decode_access_token(token)
			user_id = payload['user_id']
		except (jwt.JWTError, jwt.ExpiredSignatureError, ValueError, KeyError):
			raise AuthenticationFailed('Invalid token')

		user = User.objects.get(pk=user_id)
		if not user:
			raise AuthenticationFailed('User not found')

		return user, None  # Return user object and None (no additional credentials)
