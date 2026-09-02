from celery import shared_task
from django.utils import timezone

from social.models import Post


@shared_task
def publish_post(post_pk: str) -> None:
    try:
        post = Post.objects.get(pk=post_pk)
    except Post.DoesNotExist:
        return

    if post.scheduled_at is None:
        return

    if post.scheduled_at > timezone.now():
        return

    if post.status != Post.Status.SCHEDULED:
        return

    post.status = Post.Status.PUBLISHED
    post.published_at = timezone.now()
    post.save(update_fields=["status", "published_at"])
