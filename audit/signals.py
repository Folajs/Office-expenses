from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import AuditLog
from users.models import User
from users.models import Department


@receiver(post_save, sender=User)
@receiver(post_save, sender=Department)
def log_save(sender, instance, created, **kwargs):
    user = getattr(instance, "created_by", None)
    if not user:
        return

    action = "create" if created else "update"

    AuditLog.objects.create(
        user=user,
        role=user.role,
        action=action,
        target_model=sender.__name__,
        target_id=instance.id,
    )


@receiver(post_delete, sender=User)
@receiver(post_delete, sender=Department)
def log_delete(sender, instance, **kwargs):
    user = getattr(instance, "created_by", None)
    if not user:
        return

    AuditLog.objects.create(
        user=user,
        role=user.role,
        action="delete",
        target_model=sender.__name__,
        target_id=instance.id,
    )
