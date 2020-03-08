from threading import Thread
import schedule

from .app import create_flask_app
from .app.models.models import Person, Movie

from .job import run_schedule, delete_cache


schedule.every(1).minutes.do(delete_cache)
t = Thread(target=run_schedule)
t.start()

app = create_flask_app()


@app.shell_context_processor
def make_shell_context():
    return {'Person': Person, 'Movie': Movie}
