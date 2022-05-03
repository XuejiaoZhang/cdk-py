import logging
import sys

logging.basicConfig(stream = sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

bash_command="test logger"
logger.info(f"Bash command: {bash_command}")
print(f"Bash command: {bash_command}")