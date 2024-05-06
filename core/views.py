from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from core import serializers
from django.contrib.auth import logout, login
from django.db import transaction

from core.helpers.api_utils import SuccessResponse, FailureResponse
from core.helpers.jwt_config import create_refresh_token, create_access_token
from core.models import User, Staff, Customer, Admin
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action


class LoginAPI(APIView):
	permission_classes = [AllowAny, ]
	http_method_names = ("post",)

	# def get_exception_handler(self):

	# def handle_exception(self, exc):
	@swagger_auto_schema(
		operation_summary="logs in a user",
		request_body=serializers.Login
	)
	def post(self, request, *args, **kwargs):
		serializer = serializers.Login(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']
		login(request, user)
		user_data = user.get_user_type_data()
		data = dict()
		data["refresh_token"] = create_refresh_token(user_data)
		data["access_token"] = create_access_token(user_data)
		user_data.update(data)
		return SuccessResponse(message="Login is successful", data=user_data)


class SignupAPI(APIView):
	permission_classes = [AllowAny, ]
	http_method_names = ("post",)

	# def get_exception_handler(self):

	# def handle_exception(self, exc):

	@swagger_auto_schema(
		operation_summary="signs up a new user",
		request_body=serializers.Signup
	)
	@transaction.atomic()
	def post(self, request, *args, **kwargs):
		serializer = serializers.Signup(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.signup()
		data = user.get_user_type_data()
		return SuccessResponse(message="Signup is successful", data=data, status=201)


class ProfileAPI(APIView):
	permission_classes = [IsAuthenticated, ]
	http_method_names = ("patch", "get")

	# def get_exception_handler(self):

	# def handle_exception(self, exc):

	def get(self, request, *args, **kwargs):
		return SuccessResponse(data=request.user.get_user_type_data())

	def patch(self, request, *args, **kwargs):
		serializer_obj = None
		user_type = None
		if request.user.is_admin:
			serializer_obj = serializers.AdminProfile
			user_type = request.user.admin
		elif request.user.is_customer:
			serializer_obj = serializers.CustomerProfile
			user_type = request.user.customer
		elif request.user.is_staff:
			serializer_obj = serializers.StaffProfile
			user_type = request.user.staff
		if serializer_obj and user_type:
			serializer = serializer_obj(data=request.data, instance=user_type, partial=True)
			serializer.is_valid(raise_exception=True)
			user = serializer.save()
			return SuccessResponse(message="Profile updated successfully",
			                       data=user.get_user_type_data())
		return FailureResponse(message="Invalid user type")


class CustomerAPI(ModelViewSet):
	permission_classes = [IsAuthenticated, ]
	http_method_names = ("get",)
	queryset = Customer.objects.all()
	serializer_class = serializers.CustomerProfile


class StaffAPI(ModelViewSet):
	permission_classes = [IsAuthenticated, ]
	http_method_names = ("get",)
	queryset = Staff.objects.all()
	serializer_class = serializers.StaffProfile

	@action(
		methods=["get"],
		detail=False,
		url_name="random",
		url_path="random",
		permission_classes=[IsAuthenticated],
	)
	def random(self, request, *args, **kwargs):
		number = self.request.query_params.get("number", 1)
		queryset = Staff.objects.random_staffs(int(number))
		return SuccessResponse(data=serializers.StaffProfile(queryset, many=True).data)


class AdminAPI(ModelViewSet):
	permission_classes = [IsAuthenticated, ]
	http_method_names = ("get",)
	queryset = Admin.objects.all()
	serializer_class = serializers.AdminProfile
