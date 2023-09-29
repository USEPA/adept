from config import BASE_DIR, REPORT_BEGIN_DATE, REPORT_END_DATE
import datetime

REPORT_BGCOLORS = ['306192','d3c1ab']

DATA_DIR = BASE_DIR + 'data/XX/'
LOG_DIR = BASE_DIR + 'log/XX/'

RUN_LOG = LOG_DIR + 'XX_run_log.log'
WSN_LOG = LOG_DIR + 'XX_wsn_report_log.csv'

WSN_SAVE_LOCATION = DATA_DIR + 'XX_WSNs.csv'

BEGIN_DATE = REPORT_BEGIN_DATE
BEGIN_DATE_URL_STR = REPORT_BEGIN_DATE.replace('/','%2F')

TODAY_DATE = datetime.datetime.now().strftime('%m/%d/%Y')
TODAY_DATE_URL_STR = TODAY_DATE.replace('/','%2F')

if REPORT_END_DATE:
    END_DATE = REPORT_END_DATE
else:
    END_DATE = TODAY_DATE
END_DATE_URL_STR = END_DATE.replace('/','%2F')

WSN_DETAILS_URL = 'STATE_URL/JSP/WaterSystemDetail.jsp?tinwsys_is_number=TINWSYS_IS_NUMBER&tinwsys_st_code=TINWSYS_ST_CODE&wsnumber=WSNUMBER'
WSN_SEARCH_URL = 'STATE_URL/JSP/SearchDispatch?number=&name=&county=All&WaterSystemType=All&SourceWaterType=All&PointOfContactType=None&action=Search+For+Water+Systems'
WSN_SEARCH_URL_NC = 'STATE_URL/JSP/SearchDispatch?number=&name=&companyname=&WaterSystemStatusCode=A&county=All&WaterSystemType=All&SourceWaterType=All&PointOfContactType=None&SampleType=null&begin_date=BEGIN_DATE&end_date=END_DATE&action=Search+For+Water+Systems'