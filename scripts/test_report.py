from os import path, makedirs

from all_state_scraper import WebScraper
import constants, utils


state = 'NC'						# Required. If wnumber is set and is not associated with the state variable, the state variable will be overwritten with the state the wsnumber is part of.
wsnumber = 'NC0392045'				# Optional; can be a string (single WSN) or Python list of WSNs. 
num_wsns_to_scrape = 1 				# Optional; will scrape entire state if None and wsnumber is None. 
begin_date = None        			# Optional; sampling report date range to begin with. mm/dd/yyyy format. If None, will default to 01/01/1980.
end_date = None 					# Optional; sampling report date range to end with. mm/dd/yyyy format. If None, will default to the current date.
report_to_scrape = None				# Optional. Set to the name of the JSP page. For example, set to "SampleSchedules" to run only the /DWW/JSP/SampleSchedules.jsp report. If None, will scrape all reports. 		
drilldowns = True					# Defaults to True if not set. If False, will NOT drill down to subreports if links are found in a report table. 			
ignore_logs = True                  # Defaults to False if not set. If True, will scrape all data found whether or not it was previously scraped according to the log files.
overwrite_wsn_file = False			# Defaults to True if not set. If False, will re-use an existing wsns.csv file instead of creating a new one at the beginning of a scrape.
log_level = 'INFO'					# Defaults to "INFO" if not set. Most commonly, the other value you may wish to set it to is "DEBUG", which writes extra information to the logs and console.


report_url_to_test = None			# Optional; must be a valid link to a specific report page. IF SET, ALL OTHER VARIABLES ABOVE WILL BE IGNORED.
# report_url_to_test = 'http://dww.adem.alabama.gov/DWW/JSP/SampleSchedules.jsp?tinwsys_is_number=458&tinwsys_st_code=AL&counter=0'
# report_url_to_test = 'https://ndwis.ndep.nv.gov/DWW/JSP/SampleSchedules.jsp?tinwsys_is_number=295819&tinwsys_st_code=NV&counter=0'
# report_url_to_test = 'https://sdwisdww.mt.gov/DWW/JSP/SampleSchedules.jsp?tinwsys_is_number=1285&tinwsys_st_code=MT&counter=0'
# report_url_to_test = 'https://sdwis.waterboards.ca.gov/PDWW/JSP/NextSamplingDue.jsp?tinwsys_is_number=7630&tinwsys_st_code=CA'

# report_url_to_test = 'https://dep.gateway.ky.gov/DWW/JSP/NonTcrSampleResults.jsp?sample_number=IOC2003050202261&collection_date=02-18-2003&tinwsys_is_number=461&tinwsys_st_code=KY&tsasampl_is_number=85034&tsasampl_st_code=KY&history=0&counter=0'
# report_url_to_test = 'https://drinkingwater.dhss.delaware.gov/JSP/NonTcrSampleResults.jsp?sample_number=S1243033&collection_date=11-21-2022&tinwsys_is_number=289&tinwsys_st_code=DE&tsasampl_is_number=416001&tsasampl_st_code=DE&history=0&counter=0'
# report_url_to_test = 'https://ndwis.ndep.nv.gov/DWW/JSP/NonTcrSampleResults.jsp?sample_number=203734&collection_date=11-26-2007&tinwsys_is_number=364528&tinwsys_st_code=NV&tsasampl_is_number=142756&tsasampl_st_code=NV&history=0&counter=0'
# report_url_to_test = 'https://sdwis.waterboards.ca.gov/PDWW/JSP/WaterSystemFacility.jsp?tinwsys_is_number=8536&tinwsys_st_code=CA&tinwsf_is_number=41235&tinwsf_st_code=CA&wsf_id=DST&wsf_name=DISTRIBUTION SYSTEM'


if wsnumber:
	state = wsnumber[:2]
if wsnumber and type(num_wsns_to_scrape) is list:
	num_wsns_to_scrape = len(num_wsns_to_scrape)
elif wsnumber:
	num_wsns_to_scrape = 1


def get_state_from_url(url):
	i = url.find('.gov') - 2
	return url[i:i+2].upper()


def do_test(scraper):
	if not report_url_to_test:
		scraper.scrape()
	else:
		scraper.state = get_state_from_url(report_url_to_test)
		scraper.wsnumber = None 
		scraper.num_wsns_to_scrape = None
		scraper.begin_date = None 
		scraper.end_date = None 

		report_group_name = utils.get_report_group_from_url(report_url_to_test)
		scraper.report_group_dir = constants.DATA_DIR.replace('XX', scraper.state) + report_group_name
		if not path.exists(scraper.report_group_dir):
			makedirs(path.normpath(scraper.report_group_dir))
			scraper.run_logger.info('Created directory %s', scraper.report_group_dir)    

		scraper.current_report_url = report_url_to_test
		scraper.write_table_data()

		utils.endtime_files(scraper.state)
		scraper.run_logger.info('Files renamed to include scrape end date.')
		scraper.delete_dirs()


if __name__ == '__main__':     
	s = WebScraper(state=state,
				   num_wsns_to_scrape=num_wsns_to_scrape, 
				   wsnumber=wsnumber, 
				   begin_date=begin_date, 
				   end_date=end_date, 
				   report_to_scrape=report_to_scrape,
				   drilldowns=drilldowns,
				   ignore_logs=ignore_logs,
				   overwrite_wsn_file=overwrite_wsn_file,
				   log_level=log_level)
	do_test(s)

