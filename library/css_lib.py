
import pandas
import logging
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# =============================================================
# CONFIGURE LOGGER
# =============================================================
# set format
ft = "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
logging.basicConfig(format=ft)

# creates a logger
logger = logging.getLogger(__name__)
logger.setLevel(level=10)

# =============================================================
# GLOBAL VARIABLES
# =============================================================
# DRIVER_PATH = "/Users/vdp/Downloads/chromedriver"
DRIVER_PATH = "/usr/bin/chromedriver"
SH_LINK = "https://www.hkexnews.hk/sdw/search/searchsdw.aspx"
INDEX_CODES_LINK = "https://www.hkexnews.hk/sdw/search/stocklist.aspx?sortby=stockcode&shareholdingdate=20220508"
TODAY = datetime.datetime.today()
LIMIT = 3

# Col Headings
COL_MAP = dict()
COL_MAP["Participant ID"] = "id"
COL_MAP["Name of CCASS Participant\n(* for Consenting Investor Participants )"] = "name"
COL_MAP["Address"] = "address"
COL_MAP["Shareholding"] = "shares"
COL_MAP["% of the total number of Issued Shares/ Warrants/ Units"] = "shares_pct"


def __get_driver() -> webdriver.Chrome:
    """
    Helper function to create a chrome driver for selenium to parse the website.
    :return: chrome driver
    """
    option = webdriver.ChromeOptions()
    option.add_argument('headless')

    driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=option)
    return driver


def __get_stock_codes() -> dict:
    """
    Intent of this function is to get all the available stocks in the universe.
    Form a dictionary with {stock_code_1: stock_name_1, stock_code_2: stock_name_2,...}
    Finally cache this dict to access it from anywhere.

    :return: {stock_code_1: stock_name_1, stock_code_2: stock_name_2,...}
    """
    logger.info("__get_stock_codes : start")

    driver = __get_driver()
    driver.get(url=INDEX_CODES_LINK)

    # Get the rows
    rows = driver.find_elements_by_xpath(xpath="//table/tbody/tr")
    len_rows = len(rows)
    logger.debug("number of stocks: {}".format(len_rows))

    # Iterate over the rows
    stock_dict = dict()
    logger.debug("row iteration : start")
    st = time.time()
    for row in rows:
        # get stock code
        st_code = row.find_elements_by_xpath(xpath="./td[1]")[0].text

        # get stock name
        st_name = row.find_elements_by_xpath(xpath="./td[2]/a")[0].text

        # append to the stock dict
        stock_dict[st_code] = st_name
    logger.debug("row iteration : end")
    ed = time.time()
    logger.debug("iteration run time: {}".format(ed - st))

    driver.quit()
    logger.info("__get_stock_codes : end")
    return stock_dict


def __validate_date(dt: str) -> str:
    """
    Helper function that validates whether input date is within the limits of dates acceptable by HKEX website
    i.e. minimum date is one year ago from today and maximum date is today
    :param dt:
    :return:
    """
    logger.info("__validate_date : start")
    try:
        cutoff_dt = datetime.datetime(TODAY.year - 1, TODAY.month, TODAY.day, TODAY.hour, TODAY.minute, TODAY.second,
                                      TODAY.microsecond,
                                      TODAY.tzinfo).strftime("%Y%m%d")
    except ValueError:
        cutoff_dt = datetime.datetime(TODAY.year - 1, TODAY.month, TODAY.day - 1, TODAY.hour, TODAY.minute,
                                      TODAY.second, TODAY.microsecond,
                                      TODAY.tzinfo).strftime("%Y%m%d")

    if int(dt) < int(cutoff_dt):
        raise ValueError("Date cannot be less than one year from today, i.e. ({})".format(cutoff_dt))

    if int(dt) >= int(TODAY.strftime("%Y%m%d")):
        raise ValueError("Date cannot be greater than today")

    logger.info("__validate_date : end")
    return dt


def __get_dates(start_date: str, end_date: str) -> list:
    """
    Helper function to get all the calender dates between start and end dates.
    :param start_date:
    :param end_date:
    :return:
    """
    logger.info("__get_dates : start")

    if start_date > end_date:
        raise ValueError("start_date {} > end_date {}, please check and try again!".format(start_date, end_date))

    start_date = datetime.datetime.strptime(start_date, "%Y%m%d")
    end_date = datetime.datetime.strptime(end_date, "%Y%m%d")
    dates = [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    dates = [x.strftime("%Y%m%d") for x in dates]
    logger.debug("number of days : {}".format(len(dates)))

    logger.info("__get_dates : end")
    return dates


def ___get_investor_details_for_date(stock_code: str, date: str, count: int = 10) -> dict:
    """
    Helper function that gets participants data for a specific stock code and given date
    :param stock_code:
    :param dt: date in yyyymmdd format (9, May, 2022 = 20220509)
    :return:
    """
    logger.info("___get_investor_details_for_date : start")

    driver = __get_driver()
    driver.get(url=SH_LINK)

    # set the date
    logger.debug("*"*60)
    logger.debug("Parsing website for date : {}, stock_code : {}".format(date, stock_code))
    logger.debug("*"*60)

    date = __validate_date(date)
    yr = date[:4]
    mt = str(int(date[4:6]))
    dy = str(int(date[6:]))
    driver.find_element_by_id(id_="txtShareholdingDate").click()

    # select year
    if yr == "2022":
        driver.find_element_by_xpath(xpath="//*[@id='date-picker']/div[1]/b[1]/ul/li[1]/button").click()
    elif yr == "2021":
        driver.find_element_by_xpath(xpath="//*[@id='date-picker']/div[1]/b[1]/ul/li[2]/button").click()
    else:
        raise ValueError("Date cannot be greater than today or less than a year ago")

    # select month
    driver.find_element_by_xpath(xpath="//*[@id='date-picker']/div[1]/b[2]/ul/li[" + mt + "]/button").click()

    # select date
    dt = driver.find_element_by_xpath(xpath="//*[@id='date-picker']/div[1]/b[3]/ul/li[" + dy + "]/button")
    action = ActionChains(driver)
    action.double_click(dt).perform()

    # enter the stock code and hit enter
    st_code = driver.find_element_by_id(id_="txtStockCode")
    st_code.send_keys(stock_code)
    st_code.send_keys(Keys.ENTER)

    # extract column names
    col_headings = driver.find_elements_by_xpath(
        xpath="//*[@id='pnlResultNormal']/div[2]/div/div[2]/table/thead/tr[1]/th")
    col_headings = [i.text for i in col_headings]
    len_cols = len(col_headings)
    # logger.debug("column headings : {}".format(col_headings))

    # extract top n participants
    row_xpath = "//*[@id='pnlResultNormal']/div[2]/div/div[2]/table/tbody"
    rows = list()

    for i in range(count):
        row = list()

        for j in range(len_cols):
            dt = driver.find_element_by_xpath(xpath=row_xpath + "/tr[" + str(i + 1) + "]/td[" + str(j + 1) + "]").text
            row.append(dt)
        rows.append(row)

    logger.debug("len(rows) : {}".format(len(rows)))
    driver.quit()
    logger.debug("Parsing for date : {} done!".format(date))

    # creating output dict
    out = dict()
    out["columns"] = col_headings
    out["rows"] = rows

    logger.info("___get_investor_details_for_date : end")
    return out


def ___get_investor_details_for_date_range(stock_code: str, start_date: str, end_date: str,
                                           count: int = 10) -> pandas.DataFrame:
    """
    Helper function to retrieve participant details for a date range. This inturn calls helper function that gets data
    for a single day and aggregates it.
    :param stock_code:
    :param start_date:
    :param end_date:
    :param count:
    :return:
    """
    logger.info("___get_investor_details_for_date_range : start")

    dates = __get_dates(start_date=start_date, end_date=end_date)

    df = pandas.DataFrame()
    for date in dates:
        inv_data = ___get_investor_details_for_date(stock_code=stock_code, date=date, count=count)
        inv_df = pandas.DataFrame(columns=inv_data["columns"], data=inv_data["rows"])
        inv_df["date"] = date
        df = pandas.concat([df, inv_df], axis=0)

    df.rename(columns=COL_MAP, inplace=True)
    cols_order = ["date"] + list(COL_MAP.values())
    df = df[cols_order]
    logger.debug("df.shape : {}".format(df.shape))

    logger.info("___get_investor_details_for_date_range : end")
    return df


def get_investor_details(stock_code: str, start_date: str, end_date: str, count: int = 10) -> dict:
    """
    Get top 10 participants' details for a given stock
    :param stock_code:
    :param start_date:
    :param end_date:
    :param count:
    :return:
    """
    logger.info("="*80)
    logger.info("get_investor_details : start")
    logger.info("="*80)

    df = ___get_investor_details_for_date_range(stock_code=stock_code, start_date=start_date, end_date=end_date,
                                                count=count)
    table_data = df.to_dict(orient="split")

    # plot data
    plot_data = dict()
    plot_data["date"] = end_date
    plot_data["stock_code"] = stock_code

    plot_df = df[df["date"] == end_date]
    plot_data["columns"] = list(plot_df.columns)
    plot_data["names"] = plot_df["name"].tolist()
    plot_data["shares_pct"] = plot_df["shares_pct"].tolist()
    plot_data["shares_pct"] = [float(i[:-1]) for i in plot_data["shares_pct"]]

    out = dict()
    out["table"] = table_data
    out["plot"] = plot_data
    logger.info("get_investor_details : end")
    return out


def find_transactions(stock_code: str, start_date: str, end_date: str, threshold: float) -> dict:
    """
    Identify the possible transactions based on change of shares held each day by a participant
    Criteria: shares exchanged between parties should be at least 30% of (max shares) between the parties
    :param stock_code:
    :param start_date:
    :param end_date:
    :param threshold:
    :return:
    """
    logger.info("="*80)
    logger.info("find_transactions : start")
    logger.info("="*80)

    if start_date == end_date:
        logger.debug(
            "start_date {} is same as end_date {}, resetting start_date to previous day".format(start_date, end_date))
        st = datetime.datetime.strptime(start_date, "%Y%m%d")
        start_date = (st - datetime.timedelta(1)).strftime("%Y%m%d")
        logger.debug("start_date reset from {} to {}".format(end_date, start_date))

    df = pandas.DataFrame(
        ___get_investor_details_for_date_range(stock_code=stock_code, start_date=start_date, end_date=end_date,
                                               count=20))

    # Prepare the data frame for finding transactions
    sorted_df = df.groupby(by=["id"]).apply(lambda x: x.sort_values(["date"])).reset_index(drop=True)
    sorted_df["float_holdings"] = sorted_df["shares_pct"].apply(lambda x: float(x[:-1]))
    sorted_df["sh_change_pct"] = sorted_df.groupby(["id"])["float_holdings"].diff()
    sorted_df["mark_threshold"] = sorted_df["sh_change_pct"].apply(lambda x: 1 if abs(x) > threshold else 0)

    filt_df = sorted_df.copy()
    filt_df = filt_df[filt_df["mark_threshold"] == 1]
    filt_df = filt_df.sort_values(["date", "sh_change_pct"])

    temp_df = filt_df[["date", "id", "name", "shares", "shares_pct", "sh_change_pct"]]
    buys_df = temp_df[temp_df["sh_change_pct"] > 0]
    sells_df = temp_df[temp_df["sh_change_pct"] < 0]
    buys = buys_df.to_dict("records")
    sells = sells_df.to_dict("records")

    # get list of transactions based on criteria
    # trans_list = [[date, buy_id, sell_id]]
    trans_list = list()
    for buy in buys:
        b_pid = buy["id"]
        dt = buy["date"]
        for sell in sells:
            if dt == sell["date"]:
                s_pid = sell["id"]
                bd = buy["sh_change_pct"]
                sd = abs(sell["sh_change_pct"])
                mx = max(bd, sd)
                mn = min(bd, sd)
                if mn / mx >= 0.3:
                    trans_list.append([dt, b_pid, s_pid])

    # rename columns
    out_df = pandas.DataFrame(
        columns=["date", "b_id", "b_name", "b_shares", "b_shares_pct", "b_sh_change_pct", "s_id", "s_name", "s_shares",
                 "s_shares_pct", "s_sh_change_pct"])
    buys_df.rename(
        columns={"date": "date", "id": "b_id", "name": "b_name", "shares": "b_shares", "shares_pct": "b_shares_pct",
                 "sh_change_pct": "b_sh_change_pct"}, inplace=True)
    sells_df.rename(
        columns={"date": "date", "id": "s_id", "name": "s_name", "shares": "s_shares", "shares_pct": "s_shares_pct",
                 "sh_change_pct": "s_sh_change_pct"}, inplace=True)

    for exch in trans_list:
        dt = exch[0]
        bid = exch[1]
        sid = exch[2]
        b_df = (buys_df[(buys_df["date"] == dt) & (buys_df["b_id"] == bid)]).reset_index(drop=True)
        s_df = (sells_df[(sells_df["date"] == dt) & (sells_df["s_id"] == sid)]).reset_index(drop=True)
        s_df.drop(columns=["date"], inplace=True)
        row_df = pandas.concat([b_df, s_df], axis=1)
        out_df = pandas.concat([out_df, row_df], axis=0)

    out_df["b_sh_change_pct"] = out_df["b_sh_change_pct"].astype("float").round(2)
    out_df["s_sh_change_pct"] = out_df["s_sh_change_pct"].astype("float").round(2)
    logger.debug("out_df.shape (i.e. number of transactions): {}".format(out_df.shape))

    out = out_df.to_dict(orient="split")
    logger.info("find_transactions : end")
    return out


def do():
    # GET_STOCK_CODES = __get_stock_codes()
    # print(GET_STOCK_CODES)

    # get_investor_details_for_date(stock_code="00001", dt="20210513")
    print(get_investor_details("00001", "20220103", "20220103"))
    # __validate_date("20210413")

    # find_transactions("00001", "20220104", "20220104", 0.009)
    pass

# do()
