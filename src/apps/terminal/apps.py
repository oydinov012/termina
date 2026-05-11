from django.apps import AppConfig


class TerminalConfig(AppConfig):
    name = 'apps.terminal'

    def ready(self):
        import apps.terminal.signals
