from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Value, Func, F
from django.db.models.functions import Lower, Concat

from core.repositories import UserRepository, AdminRepository, CustomerRepository, StaffRepository


# Create your models here.

class GenderChoice(models.TextChoices):
	Male = ("Male", "Male")
	Female = ("Female", "Female")


class User(AbstractBaseUser):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.EmailField(max_length=100)
	is_admin = models.BooleanField(db_default=False)
	is_staff = models.BooleanField(db_default=False)
	is_customer = models.BooleanField(db_default=False)
	gender = models.CharField(choices=GenderChoice, default=GenderChoice.Male, max_length=10)
	date_of_birth = models.DateField(default=None, null=True)
	display_name = models.GeneratedField(expression=Lower(
		Concat(
			Value('@'),
			Func(F('first_name'), function='LEFT', template='%(function)s(%(expressions)s, 1)'),
			F('last_name')
		)
	), editable=False, output_field=models.CharField(max_length=255), db_persist=True)
	profile_pic = models.ImageField(default=None, null=True)

	@property
	def get_profile_pic(self):
		return f"http://localhost:8000{self.profile_pic.url}"

	USERNAME_FIELD = "email"

	class Meta:
		db_table = "User"

	def get_user_type_data(self):
		from core import serializers
		if self.is_customer:
			return serializers.CustomerProfile(self.customer).data
		elif self.is_staff:
			return serializers.StaffProfile(self.customer).data
		elif self.is_admin:
			return serializers.AdminProfile(self.admin).data
		return dict()

	@property
	def get_username(self):
		return f"@{self.first_name[0]}{self.last_name}".lower()

	objects = UserRepository()


class Admin(models.Model):
	user = models.OneToOneField("core.User", on_delete=models.CASCADE)

	class Meta:
		db_table = "Admin"

	objects = AdminRepository()


class Staff(models.Model):
	user = models.OneToOneField("core.User", on_delete=models.CASCADE)

	class Meta:
		db_table = "Staff"

	objects = StaffRepository()


class Customer(models.Model):
	user = models.OneToOneField("core.User", on_delete=models.CASCADE)

	class Meta:
		db_table = "Customer"

	objects = CustomerRepository()
