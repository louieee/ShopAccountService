from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from core.repositories import UserRepository, AdminRepository, CustomerRepository, StaffRepository


# Create your models here.

class User(AbstractBaseUser):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.EmailField(max_length=100)
	is_admin = models.BooleanField(db_default=False)
	is_staff = models.BooleanField(db_default=False)
	is_customer = models.BooleanField(db_default=False)

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
