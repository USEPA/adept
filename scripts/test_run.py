from all_state_scraper import WebScraper
import utils

 
state = 'NC'                        # Required. If wnumber is set and is not associated with the state variable, the state variable will be overwritten with the state the wsnumber is part of.
num_wsns_to_scrape = 1              # Optional; will scrape entire state if None and wsnumber is None. 
wsnumber = None                     # Optional; can be a string (single WSN) or Python list of WSNs. 
begin_date = None                   # Optional; sampling report date range to begin with. mm/dd/yyyy format. If None, will default to 01/01/1980.
end_date = None                     # Optional; sampling report date range to end with. mm/dd/yyyy format. If None, will default to the current date.
report_to_scrape = None             # Optional. Set to the name of the JSP page. For example, set to "SampleSchedules" to run only the /DWW/JSP/SampleSchedules.jsp report. If None, will scrape all reports.       
drilldowns = True                   # Defaults to True if not set. If False, will NOT drill down to subreports if links are found in a report table.            
ignore_logs = True                  # Defaults to False if not set. If True, will scrape all data found whether or not it was previously scraped according to the log files.
overwrite_wsn_file = False          # Defaults to True if not set. If False, will re-use an existing wsns.csv file instead of creating a new one at the beginning of a scrape.
log_level = 'INFO'                  # Defaults to "INFO" if not set. Most commonly, the other value you may wish to set it to is "DEBUG", which writes extra information to the logs and console.


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
                   begin_date=begin_date,
                   end_date=end_date,
                   report_to_scrape=report_to_scrape,
                   drilldowns=drilldowns,
                   ignore_logs=ignore_logs,
                   overwrite_wsn_file=overwrite_wsn_file,
                   log_level=log_level,
                   task_id=1)
except Exception as e:
    utils.handle_scrape_error(state, e)

try:
    s.scrape()
except Exception as e:
    utils.handle_scrape_error(state, e)