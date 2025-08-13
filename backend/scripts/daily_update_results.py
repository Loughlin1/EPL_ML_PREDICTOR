import logging
from app.core.config import settings
from app.db.database import get_session
from app.services.web_scraping.fixtures.fixtures_scraper import scrape_and_save_fixtures
from app.services.web_scraping.fixtures.shooting_stats_scraper import scrape_and_save_shooting_stats

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting fixtures and shooting stats scraping")
    scrape_and_save_fixtures(settings.CURRENT_SEASON)
    scrape_and_save_shooting_stats([settings.CURRENT_SEASON])
    logger.info("Finished fixtures and shooting stats scraping")


if __name__ == "__main__":
    main()
