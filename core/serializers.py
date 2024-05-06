from rest_framework import serializers

from core.models import User, Admin, Staff, Customer


class Login(serializers.Serializer):
	email = serializers.EmailField()
	password = serializers.CharField()

	def validate(self, attrs):
		user = User.objects.validate_credentials(**attrs)
		attrs['user'] = user

		return attrs

class Signup(serializers.ModelSerializer):
	user_type = serializers.ChoiceField(choices=["admin", "staff", "customer"])

	class Meta:
		model = User
		fields = ("first_name", "last_name", "email", "password", "user_type")

	def signup(self):
		create_function_switch = dict(admin=Admin.objects.create_admin,
		                              staff=Staff.objects.create_staff,
		                              customer=Customer.objects.create_customer)
		user_type = self.validated_data.pop('user_type')
		create_function = create_function_switch[user_type]
		custom_user = create_function(**self.validated_data)
		return custom_user.user


class UserProfile(serializers.ModelSerializer):
	user_id = serializers.CharField(source="user.id", read_only=True)
	first_name = serializers.CharField(source="user.first_name")
	last_name = serializers.CharField(source="user.last_name")
	email = serializers.CharField(source="user.email", read_only=True)
	user_type = serializers.SerializerMethodField(read_only=True)

	def get_user_type(self, obj):
		if obj.user.is_admin:
			return "Administrator"
		elif obj.user.is_staff:
			return "Staff"
		elif obj.user.is_customer:
			return "Customer"
		return None


	@staticmethod
	def custom_update(self, instance, validated_data, serializer):
		user_data = validated_data.pop("user")
		instance = super(serializer, self).update(instance, **validated_data)
		User.objects.filter(id=instance.user_id).update(**user_data)
		return instance


class StaffProfile(UserProfile):
	class Meta:
		model = Staff
		exclude = ("user",)

	def update(self, instance, validated_data):
		return self.custom_update(self, instance, validated_data, self.__class__)


class CustomerProfile(UserProfile):
	class Meta:
		model = Customer
		exclude = ("user",)

	def update(self, instance, validated_data):
		return self.custom_update(self, instance, validated_data, self.__class__)


class AdminProfile(UserProfile):
	class Meta:
		model = Admin
		exclude = ("user",)

	def update(self, instance, validated_data):
		return self.custom_update(self, instance, validated_data, self.__class__)
