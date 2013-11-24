import logging

from werewolf.application.service import GameMaster, ResidentManager, Messenger

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console_log = logging.StreamHandler()
console_log.setLevel(logging.INFO)
console_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

logger.addHandler(console_log)
