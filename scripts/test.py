from bs4 import BeautifulSoup
import pandas as pd
import utils

current_report_url = 'https://azsdwis.azdeq.gov/DWW_EXT/JSP/TcrSampleResults.jsp?tinwsys_is_number=2004&tinwsys_st_code=AZ&begin_date=12/01/2023&end_date=01/09/2024&counter=0'
header_index = None

html = utils.get_html(current_report_url)
soup = BeautifulSoup(html,'lxml')

table_index = -1
for table in soup.find_all('table'):
	table_index += 1

	if not utils.test_table(table):
		continue # not a report table, go to next one
	else:
		table_title = utils.get_table_title(soup, table_index)
		header_index = utils.get_table_header_index(table, table_title)


	if (((table_title == 'Water System Detail Information' or table_title == 'Water System Details') 
		 and 'WaterSystemDetail.jsp' not in current_report_url) or 
	   ((table_title == 'Water System Facilities' or table_title == 'Water System Facility Detail') 
		 and 'WaterSystemFacilities.jsp' not in current_report_url)):
		continue	

	# print(table)
	nested_table_columns = utils.get_nested_table_column_indexes(table, header_index)
	# print(nested_table_columns)

	if len(nested_table_columns) > 0 and ('Coliform' in table_title or 'TCR' in table_title or 'Long Term 2' in table_title): # TX-like states have nested tables in the coliform sample report
		column_headers = utils.get_column_headers(table, header_index, nested_table_columns)
		column_headers.insert(0, 'Water System No.')
		column_headers.append('Sample Pt Description Detail')
		working_report_table = pd.DataFrame(columns=column_headers)

		print(column_headers)