from celery import shared_task


@shared_task(time_limit=300)
def do_container_eval_cc(*args, **kwargs):
    pass
