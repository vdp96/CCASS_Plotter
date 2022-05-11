from library import plotter
import logging

# =============================================================
# CONFIGURE LOGGER
# =============================================================
# set format
ft = "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
logging.basicConfig(format=ft)

# creates a logger
logger = logging.getLogger(__name__)
logger.setLevel(level=10)


def get_investor_details(*args, **kwargs):
    logger.info("get_investor_details : start")

    stock_code = kwargs.get("stock_code")
    start_date = kwargs.get("start_date")
    end_date = kwargs.get("end_date")

    out = plotter.get_investor_details(stock_code=stock_code, start_date=start_date, end_date=end_date)

    logger.info("get_investor_details : end")
    return out


def find_transactions(*args, **kwargs):
    logger.info("find_transactions : start")

    stock_code = kwargs.get("stock_code")
    start_date = kwargs.get("start_date")
    end_date = kwargs.get("end_date")
    threshold = kwargs.get("threshold")

    out = plotter.find_transactions(stock_code=stock_code, start_date=start_date, end_date=end_date, threshold=threshold)

    logger.info("find_transactions : end")
    return out
