from os import path, makedirs

from all_state_scraper import WebScraper
import constants, utils


state = 'MO'
wsnumber = None #'AZ0413029'
num_wsns_to_scrape = 1 # None
begin_date = '11/23/2005'
end_date = None # '01/09/2024'
# report_to_scrape = None
report_to_scrape = None
drilldowns = False
ignore_logs = True
overwrite_wsn_file = False
log_level = 'INFO'
if wsnumber:
	state = wsnumber[:2]
if wsnumber and type(num_wsns_to_scrape) is list:
	num_wsns_to_scrape = len(num_wsns_to_scrape)
elif wsnumber:
	num_wsns_to_scrape = 1

# report_url_to_test = 'https://dep.gateway.ky.gov/DWW/JSP/NonTcrSampleResults.jsp?sample_number=IOC2003050202261&collection_date=02-18-2003&tinwsys_is_number=461&tinwsys_st_code=KY&tsasampl_is_number=85034&tsasampl_st_code=KY&history=0&counter=0'
# report_url_to_test = 'https://drinkingwater.dhss.delaware.gov/JSP/NonTcrSampleResults.jsp?sample_number=S1243033&collection_date=11-21-2022&tinwsys_is_number=289&tinwsys_st_code=DE&tsasampl_is_number=416001&tsasampl_st_code=DE&history=0&counter=0'
# report_url_to_test = 'https://ndwis.ndep.nv.gov/DWW/JSP/NonTcrSampleResults.jsp?sample_number=203734&collection_date=11-26-2007&tinwsys_is_number=364528&tinwsys_st_code=NV&tsasampl_is_number=142756&tsasampl_st_code=NV&history=0&counter=0'
# report_url_to_test = 'https://sdwis.waterboards.ca.gov/PDWW/JSP/WaterSystemFacility.jsp?tinwsys_is_number=8536&tinwsys_st_code=CA&tinwsf_is_number=41235&tinwsf_st_code=CA&wsf_id=DST&wsf_name=DISTRIBUTION SYSTEM'
report_url_to_test = None


def do_test(scraper):
	if not report_url_to_test:
		scraper.scrape()
	else:
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

