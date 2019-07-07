from django.apps import AppConfig


class TaskConfig(AppConfig):
    name = 'task'

    def ready(self):
        """
        On django runtime, load up the following code.
        """
        pass
