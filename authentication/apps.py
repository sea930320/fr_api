from django.apps import AppConfig


class AuthenticationAppConfig(AppConfig):
    name = 'authentication'
    label = 'authentication'
    verbose_name = 'Authentication'

    # def ready(self):
    #     import authentication.signals