import os
import logging
from kink import di
from .cogs.admin import Admin
from .cogs.music import Music
from .bot import Bot
from .youtube import Youtube

logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

di['token'] = os.environ.get('TOKEN')
di['data_path'] = os.environ.get('DATA_PATH')

di['youtube'] = Youtube()

di['cogs'] = [Admin, Music]
di['bot'] = Bot
