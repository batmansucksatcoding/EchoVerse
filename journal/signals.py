from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from journal.models import JournalEntry
from visualizations.models import MoodVisualization


@receiver(post_save, sender=JournalEntry)
def cleanup_old_blobs_on_new_entry(sender, instance, created, **kwargs):
    """
    Delete older mood blobs when a new journal entry is created.
    Keeps only the most recent blob visualization per user.
    """
    if created:
        user = instance.user
        blobs = MoodVisualization.objects.filter(user=user).order_by('-created_at')

        # Keep only the newest blob
        if blobs.count() > 1:
            for old_blob in blobs[1:]:
                if old_blob.image:
                    old_blob.image.delete(save=False)
                old_blob.delete()


@receiver(post_delete, sender=JournalEntry)
def delete_blobs_on_entry_delete(sender, instance, **kwargs):
    """
    Delete all blobs when all entries for a user are deleted.
    """
    user = instance.user
    if not JournalEntry.objects.filter(user=user).exists():
        # If user has no entries left, delete all blobs
        blobs = MoodVisualization.objects.filter(user=user)
        for blob in blobs:
            if blob.image:
                blob.image.delete(save=False)
            blob.delete()
