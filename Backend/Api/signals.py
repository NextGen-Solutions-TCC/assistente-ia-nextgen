from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Usuario


@receiver(post_delete, sender=Usuario)
def apagar_user_ao_apagar_usuario(sender, instance, **kwargs):
    """
    Usuario.user tem on_delete=CASCADE (apagar o User apaga o Usuario),
    mas o inverso não acontece sozinho: apagar o Usuario pelo admin ou
    pela API deixava o User (auth_user) órfão, com o mesmo e-mail,
    bloqueando novos cadastros por "e-mail já cadastrado".
    Aqui garantimos que apagar o Usuario também apaga o User.
    """
    User.objects.filter(pk=instance.user_id).delete()
