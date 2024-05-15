from all_state_scraper import WebScraper
import utils

 
state = 'RI'
num_wsns_to_scrape = 1
wsnumber = 'RI1000009'
# wsnumber = None
startdate = '1/1/2023'
enddate = '9/30/2023' 
report = None
drilldowns = True
ignorelogs = False
overwrite_wsn_file = False
log_level = 'INFO'

 
try:        
    if type(wsnumber) is str:
        state = wsnumber[:2]
    elif type(wsnumber) is list:
        state = wsnumber[0][:2]
    elif not wsnumber and not state:
        print("Unable to proceed - please set the 'state' variable")
        exit()
    s = WebScraper(state,
                   num_wsns_to_scrape=num_wsns_to_scrape,
                   wsnumber=wsnumber,
                   begin_date=startdate,
                   end_date=enddate,
                   report_to_scrape=report,
                   drilldowns=drilldowns,
                   ignore_logs=ignorelogs,
                   overwrite_wsn_file=overwrite_wsn_file,
                   log_level=log_level,
                   task_id=1)
except Exception as e:
    utils.handle_scrape_error(state, e)

try:
    s.scrape()
except Exception as e:
    utils.handle_scrape_error(state, e)