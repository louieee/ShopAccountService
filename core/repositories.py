from core.exceptions import NotUniqueError
from django.db import models
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError


class UserRepository(models.Manager):

	def create_user(self, first_name: str, last_name: str, email: str, password: str, **extras):
		if self.filter(email=email).exists():
			raise ValidationError("This email address already exists")
		validate_password(password)
		user = self.create(first_name=first_name, last_name=last_name, email=email,  **extras)
		user.set_password(password)
		user.save()
		return user

	def validate_credentials(self, email: str, password: str, return_bool=False):
		user = self.filter(email__iexact=email).first()
		if not user:
			if not return_bool:
				raise ValidationError("You do not have an account with us")
			return False
		if not user.check_password(password):
			if not return_bool:
				raise ValidationError("Incorrect Credentials")
			return False
		if not return_bool:
			return user
		return True


class AdminRepository(models.Manager):

	def create_admin(self, first_name: str, last_name: str, email: str, password: str, **kwargs):
		from core.models import User
		user = User.objects.create_user(first_name, last_name, email, password, is_admin=True, **kwargs)
		return self.create(user=user)


class StaffRepository(models.Manager):
	...

	def create_staff(self, first_name: str, last_name: str, email: str, password: str, **kwargs):
		from core.models import User
		user = User.objects.create_user(first_name, last_name, email, password, is_staff=True, **kwargs)
		return self.create(user=user)

	def random_staffs(self, number: int):
		from random import choices
		ids = choices(self.only("id").values_list("id", flat=True), k=number)
		return self.filter(id__in=ids)


class CustomerRepository(models.Manager):
	def create_customer(self, first_name: str, last_name: str, email: str, password: str, **kwargs):
		from .models import User
		user = User.objects.create_user(first_name, last_name, email, password, is_customer=True, **kwargs)
		return self.create(user=user)
