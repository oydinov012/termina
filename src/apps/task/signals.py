# apps/task/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.task.models import Task

@receiver(post_save, sender=Task)
def task_status_notification(sender, instance, created, **kwargs):
    """
    Task holati o'zgarganda (completed yoki failed) ishga tushib,
    foydalanuvchiga yoki tizimga xabar beruvchi signal.
    """
    # created == True bo'lsa, demak task endigina yaratildi (status="in_progress").
    # Bizga esa faqat task Celery tomonidan yangilangandagi (update) holati kerak!
    if not created:
        
        # 1. Topshiriq muvaffaqiyatli bajarilsa
        if instance.status == "completed":
            print(f"🎉 SIGNAL: Foydalanuvchi '{instance.user.username}' '{instance.title}' topshirig'ini muvaffaqiyatli bajardi!")
            print(f"Foydalanuvchiga {instance.xp} XP qo'shildi.")
            
            # TODO: Bu yerda Notification modeliga yozish yoki WebSocket (Channels) orqali frontedga xabar yuborish mumkin
            # Notification.objects.create(user=instance.user, message=f"Tabriklaymiz! {instance.title} topshirig'ini bajardingiz.")

        # 2. Topshiriq xato bajarilsa
        elif instance.status == "failed":
            print(f"❌ SIGNAL: Foydalanuvchi '{instance.user.username}' '{instance.title}' topshirig'ida xato qildi.")
            print(f"Joriy urinishlar soni: {instance.attempt_count}")
            
            # TODO: Xatolik haqida bildirishnoma yuborish logikasi