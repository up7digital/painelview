from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from Administracao.models import MidiaPainel

@receiver(post_save, sender=MidiaPainel)
def notify_new_midia(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "painel_group",
            {"type": "painel_update"}
        )
