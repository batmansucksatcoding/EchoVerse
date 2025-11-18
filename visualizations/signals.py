from django.apps import apps
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete)
def delete_blob_image(sender, instance, **kwargs):
    """Delete image file from storage when MoodVisualization is deleted."""
    MoodVisualization = apps.get_model('journal', 'MoodVisualization')
    if sender == MoodVisualization and instance.image:
        instance.image.delete(save=False)

