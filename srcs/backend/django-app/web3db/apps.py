from django.apps import AppConfig
import logging
import sys

logger = logging.getLogger(__name__)

class Web3DbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web3db'

    count=0

    def ready(self):
        pass
