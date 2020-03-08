import functools
import os
import logging
import time

import redis
import schedule

redis_db = redis.from_url(os.environ.get('REDIS_URL'))


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                logging.error(traceback.format_exc())

                if cancel_on_failure:
                    return schedule.CancelJob

        return wrapper

    return catch_exceptions_decorator


# Job to clear cache
@catch_exceptions(cancel_on_failure=True)
def delete_cache():
    redis_db.delete("movies")
    logging.info("Cache cleared")


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)
