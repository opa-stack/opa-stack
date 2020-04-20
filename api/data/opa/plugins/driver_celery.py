from celery import Celery

from opa import Driver, Hook, Setup, HookDefinition, call_hook
from opa.utils import host_exists


class celery_setup_definition(HookDefinition):
    name = 'driver.celery.setup'


class celery_setup(Hook):
    name = 'driver.celery.setup'
    order = -1

    def run(self, celery_app):
        return celery_app


class CeleryDriver(Driver):
    name = 'celery'

    def connect(self):
        if not host_exists(self.opts.BACKEND_URL, 'database-url'):
            return None

        if not host_exists(self.opts.BROKER_URL, 'database-url'):
            return None

        celery_app = Celery(
            "tasks", backend=self.opts.BACKEND_URL, broker=self.opts.BROKER_URL,
        )

        celery_app.autodiscover_tasks(self.pm.store['task_candidates'])
        celery_app = call_hook('driver.celery.setup', celery_app=celery_app)

        self.instance = celery_app
