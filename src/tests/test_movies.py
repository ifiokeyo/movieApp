from flask import template_rendered

from .base import BaseTestCase
from ..app.models.models import db
from contextlib import contextmanager


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class MoviesTestCase(BaseTestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

    render_templates = False

    def test_get_movies_successfully(self):
        app = self.create_app()
        with captured_templates(app) as templates:
            res = self.client.get('/movies')
            assert res.status_code == 200
            assert len(templates) == 1
            template, context = templates[0]
            assert template.name == 'movies.html'
            assert len(context['movies']) > 10

        # self.assert_template_used('movies.html')
