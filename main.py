"""main"""
import threading

from helpers.config import ConfigHelper
from helpers.schedule import ScheduleHelper
from helpers.tg import TgHelper
from helpers.utils import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Main logic"""
    # Initialize Telegram helper
    tg_helper = TgHelper()

    # Get yml data
    config_helper = ConfigHelper()

    # Initialize schedule helper and print how many tasks added
    yml_data = config_helper.get_yml_data()
    schedule_helper = ScheduleHelper(yml_data=yml_data, tg_helper=tg_helper)

    # Run the scheduler
    schedule_thread = threading.Thread(target=schedule_helper.run)
    schedule_thread.start()
    logger.info("Scheduler started successfully.")

    # Telegram bot starts polling
    tg_helper.run()


if __name__ == "__main__":
    logger.info("Program Start!")
    main()
