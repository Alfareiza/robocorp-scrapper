from datetime import date

from robocorp import browser, workitems
from robocorp.tasks import task

from src.parsers import News
from utils.date_utils import get_month_date

from robocorp import log


@task
def web_scraper_news() -> None:
    """
    Automate web scraping for AP news site https://apnews.com
    """
    try:
        item = workitems.inputs.current
        start_date, end_date = get_month_date(item.payload['n_months'])

        obj_news = News('https://apnews.com')
        obj_news.scrap(
            item.payload['category'],
            item.payload['query'],
            item.payload['limite_pages'],
            interval_limit=(start_date, end_date),
        )

        generate_and_export_csv(obj_news)
    except Exception as e:
        log.info(str(e))
    finally:
        browser.context().close()
        browser.browser().close()


def generate_and_export_csv(obj_news):
    """ Generate and export csv in outout folder """

    csv_content = ["Index;Date;Title;Description;ImageFileName;CurrencyInNews;LinkNews"]
    csv_content.extend(
        f"{index};{item.publish_date:%D};{item.title};{item.description};{item.image_name};{item.currency_in_title_or_desc};{item.link}"
        for index, item in enumerate(obj_news.news, 1)
    )

    csv_file = f"output/ap_news_{date.today():%d_%m_%y}.csv"
    log.info(f"### Saving to the CSV file: {csv_file}")
    with open(csv_file, mode="w") as csv:
        csv.writelines([line + "\n" for line in csv_content])
    log.info("### Done!")
