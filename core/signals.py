import json

from django.db.models.signals import post_save, pre_delete

from core.models import User, Customer, Staff, Admin
from core.services.rabbit_mq_service.main import rabbit_mq_service
from core.services.rabbit_mq_service.consumers import Queues
from serializers import UserSerializer


@post_save(sender=Customer)
def handle_new_customer(sender, instance: Customer, created, *args, **kwargs):
	if created:
		data = UserSerializer(instance.user).data
		data["customer_id"] = instance.id
		payload = dict(
			action="create",
			data_type="user",
			data=json.dumps(data)
		)
		rabbit_mq_service.publish(queues=[Queues.ChatQueue, Queues.CRMQueue, Queues.ReportQueue],
		                          data=payload)


@post_save(sender=Staff)
def handle_new_staff(sender, instance: Staff, created, *args, **kwargs):
	if created:
		data = UserSerializer(instance.user).data
		data["staff_id"] = instance.id
		payload = dict(
			action="create",
			data_type="user",
			data=json.dumps(data)
		)
		rabbit_mq_service.publish(queues=[Queues.ChatQueue, Queues.CRMQueue, Queues.ReportQueue],
		                          data=payload)


@post_save(sender=Admin)
def handle_new_Admin(sender, instance: Admin, created, *args, **kwargs):
	if created:
		data = UserSerializer(instance.user).data
		data["admin_id"] = instance.id
		payload = dict(
			action="create",
			data_type="user",
			data=json.dumps(data)
		)
		rabbit_mq_service.publish(queues=[Queues.ChatQueue, Queues.CRMQueue, Queues.ReportQueue],
		                          data=payload)


@post_save(sender=User)
def handle_user_update(sender, instance: User, created, *args, **kwargs):
	if not created:
		data = UserSerializer(instance).data
		if instance.is_staff:
			data["staff_id"] = instance.staff.id
		elif instance.is_admin:
			data["admin_id"] = instance.admin.id
		elif instance.is_customer:
			data["customer_id"] = instance.customer.id
		payload = dict(
			action="update",
			data_type="user",
			data=json.dumps(data)
		)
		rabbit_mq_service.publish(queues=[Queues.ChatQueue, Queues.CRMQueue, Queues.ReportQueue],
		                          data=payload)


def handle_delete_update(sender, instance: User, created, *args, **kwargs):
	if not created:
		data = UserSerializer(instance).data
		if instance.is_staff:
			data["staff_id"] = instance.staff.id
		elif instance.is_admin:
			data["admin_id"] = instance.admin.id
		elif instance.is_customer:
			data["customer_id"] = instance.customer.id
		payload = dict(
			action="update",
			data_type="user",
			data=json.dumps(data)
		)
		rabbit_mq_service.publish(queues=[Queues.ChatQueue, Queues.CRMQueue, Queues.ReportQueue],
		                          data=payload)


@pre_delete(sender=Customer)
def handle_customer_deletion(sender, instance: Customer, *args, **kwargs):
	data = UserSerializer(instance.user).data
	data["customer_id"] = instance.id
	payload = dict(
		action="delete",
		data_type="user",
		data=json.dumps(data)
	)
	rabbit_mq_service.publish(queues=[Queues.ChatQueue, Queues.CRMQueue, Queues.ReportQueue],
	                          data=payload)


@pre_delete(sender=Staff)
def handle_staff_deletion(sender, instance: Staff, *args, **kwargs):
	data = UserSerializer(instance.user).data
	data["staff_id"] = instance.id
	payload = dict(
		action="delete",
		data_type="user",
		data=json.dumps(data)
	)
	rabbit_mq_service.publish(queues=[Queues.ChatQueue, Queues.CRMQueue, Queues.ReportQueue],
	                          data=payload)


@pre_delete(sender=Admin)
def handle_admin_deletion(sender, instance: Admin, *args, **kwargs):
	data = UserSerializer(instance.user).data
	data["admin_id"] = instance.id
	payload = dict(
		action="delete",
		data_type="user",
		data=json.dumps(data)
	)
	rabbit_mq_service.publish(queues=[Queues.ChatQueue, Queues.CRMQueue, Queues.ReportQueue],
	                          data=payload)
