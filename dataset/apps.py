from django.apps import AppConfig


class DatasetAppConfig(AppConfig):
    name = 'dataset'
    label = 'dataset'
    verbose_name = 'Dataset'

    def ready(self):
        import dataset.signals
