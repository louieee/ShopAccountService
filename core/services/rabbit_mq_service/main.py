from core.services.rabbit_mq_service.consumers import Exchange, AccountConsumer
from core.services.rabbit_mq_service.rabbit_mq import RabbitMQService

rabbit_mq_service = RabbitMQService(
        exchange=Exchange,
        consumers=[
            AccountConsumer
        ]
    )