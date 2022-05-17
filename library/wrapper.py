from library import css_lib
import logging
import traceback
import sys

# =============================================================
# CONFIGURE LOGGER
# =============================================================
# set format
ft = "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
logging.basicConfig(format=ft)

# creates a logger
logger = logging.getLogger(__name__)
logger.setLevel(level=10)


def get_investor_details(stock_code, start_date, end_date):
    logger.info("get_investor_details : start")

    if not isinstance(stock_code, str):
        stock_code = str(stock_code)

    if not isinstance(start_date, str):
        start_date = str(start_date)

    if not isinstance(end_date, str):
        end_date = str(end_date)

    out = dict()
    out["data"] = None
    out["code"] = 0
    out["error"] = list()

    try:
        out["data"] = css_lib.get_investor_details(stock_code=stock_code, start_date=start_date, end_date=end_date)
    except Exception as err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb = traceback.TracebackException(exc_type, exc_value, exc_traceback)

        out["code"] += 1
        out["error"] = [''.join(tb.format_exception_only())]

    logger.info("get_investor_details : end")
    return out


def find_transactions(stock_code, start_date, end_date, threshold):
    logger.info("find_transactions : start")

    if not isinstance(stock_code, str):
        stock_code = str(stock_code)

    if not isinstance(start_date, str):
        start_date = str(start_date)

    if not isinstance(end_date, str):
        end_date = str(end_date)

    if not isinstance(threshold, float):
        threshold = float(threshold)

    out = dict()
    out["data"] = None
    out["code"] = 0
    out["error"] = list()

    try:
        out["data"] = css_lib.find_transactions(stock_code=stock_code, start_date=start_date, end_date=end_date,
                                                threshold=threshold)
    except Exception as err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb = traceback.TracebackException(exc_type, exc_value, exc_traceback)

        out["code"] += 1
        out["error"] = [''.join(tb.format_exception_only())]

    logger.info("find_transactions : end")
    return out


def do():
    # GET_STOCK_CODES = __get_stock_codes()
    # print(GET_STOCK_CODES)

    # get_investor_details_for_date(stock_code="00001", dt="20210513")
    # get_investor_details("05000", "20220103", "20220103")
    # __validate_date("20210413")

    find_transactions("00700", "20220103", "20220105", 0.009)
    pass

# do()