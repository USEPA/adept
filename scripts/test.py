import pandas as pd    
import copy

table = """<table border="1" cellspacing="0" width="100%" bgcolor="#FFCC99" style="border-collapse: collapse" bordercolor="#111111" cellpadding="2">
						<tbody><tr>
							<th width="100%" colspan="10" bgcolor="#306192"><font size="4" color="#FFFFFF">Coliform Sample Results
									Distribution System</font></th>
						</tr>
						<tr>
							<th width="6%" bgcolor="#306192"><font color="#FFFFFF">Type/<br>RP
									Loc
							</font></th>
							<th width="9%" bgcolor="#306192"><font color="#FFFFFF">Sample<br>
									No.
							</font></th>
							<th width="5%" bgcolor="#306192"><font color="#FFFFFF">Comp.
									Ind.</font></th>
							<th width="7%" bgcolor="#306192"><font color="#FFFFFF">Date</font></th>
							<th width="8%" bgcolor="#306192"><font color="#FFFFFF">Sample
									Pt.</font></th>
							<th width="12%" bgcolor="#306192"><font color="#FFFFFF">Sample
									Pt.<br>Description
							</font></th>
							<th width="4%" bgcolor="#306192"><font color="#FFFFFF">Lab
									ID</font></th>
							<th width="7%" bgcolor="#306192"><font color="#FFFFFF">CL
									Free</font></th>
							<th width="7%" bgcolor="#306192"><font color="#FFFFFF">CL
									Total</font></th>
							<th width="42%" bgcolor="#306192"><font color="#FFFFFF">Result
									/ Analyte / Method / Mon Period</font></th>

						</tr>

						
						
						<tr>

							

							<td width="6%" bgcolor="#DBDBDB" align="center"><font size="2">  RT    <br> 
							</font> </td>

							<!-- This creates the link to the TCR Field Results for each sample -->
							<td width="9%" bgcolor="#DBDBDB" align="center"><font size="2"> <a href="javascript:viewResult(358541, 'RI')" onmouseover="window.status='Field Results for 2305106-01_SM13'; return true" onclick="window.status='Field Results for 2305106-01_SM13'; return true" onmouseout="window.status=''; return true" title="Field Results"> 2305106-01_SM13
								</a> <br> 
							</font></td>

							<td width="5%" bgcolor="#DBDBDB" align="center"><font size="2">Y</font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2">11-02-2023</font></td>
							<td width="8%" bgcolor="#DBDBDB" align="center"><font size="2">RTOR        </font></td>
							<td width="12%" bgcolor="#DBDBDB"><font size="2">  ROUTINE ORIGINAL 
							</font></td>
							<td width="4%" bgcolor="#DBDBDB" align="center"><font size="2">121       </font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2"> 0.000
</font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2"> </font></td>
							<td width="42%" bgcolor="#DBDBDB" align="center">
								

								<table border="1" cellspacing="0" width="100%" bgcolor="#DBDBDB" style="border-collapse: collapse" cellpadding="2">
									
									

									<tbody><tr>
										

										<td width="4%" bgcolor="#DBDBDB"><font size="2">
												Absent 
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												COLIFORM (TCR)                          (3100)
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												 9223B-PA                       
										</font></td>

										<td width="19%" bgcolor="#DBDBDB"><font size="2">
												 10-01-2023 <br> 12-31-2023 
										</font></td>
										
									</tr>

									
									

									<tr>
										

										<td width="4%" bgcolor="#DBDBDB"><font size="2">
												Absent 
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												E. COLI(3014)
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												 9223B-PA                       
										</font></td>

										<td width="19%" bgcolor="#DBDBDB"><font size="2">
												 10-01-2023 <br> 12-31-2023 
										</font></td>
										
									</tr>

									
									
								</tbody></table>  <font size="1"> 
									                                                                                                                                                                                                         - RESTROOM SINK 
							</font> 
							</td>
						</tr>
						
						<tr>

							

							<td width="6%" bgcolor="#DBDBDB" align="center"><font size="2">  RT    <br> 
							</font> </td>

							<!-- This creates the link to the TCR Field Results for each sample -->
							<td width="9%" bgcolor="#DBDBDB" align="center"><font size="2"> <a href="javascript:viewResult(355125, 'RI')" onmouseover="window.status='Field Results for 2304684-01_SM53'; return true" onclick="window.status='Field Results for 2304684-01_SM53'; return true" onmouseout="window.status=''; return true" title="Field Results"> 2304684-01_SM53
								</a> <br> 
							</font></td>

							<td width="5%" bgcolor="#DBDBDB" align="center"><font size="2">Y</font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2">09-19-2023</font></td>
							<td width="8%" bgcolor="#DBDBDB" align="center"><font size="2">RTOR        </font></td>
							<td width="12%" bgcolor="#DBDBDB"><font size="2">  ROUTINE ORIGINAL 
							</font></td>
							<td width="4%" bgcolor="#DBDBDB" align="center"><font size="2">121       </font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2"> 0.000
</font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2"> </font></td>
							<td width="42%" bgcolor="#DBDBDB" align="center">
								

								<table border="1" cellspacing="0" width="100%" bgcolor="#DBDBDB" style="border-collapse: collapse" cellpadding="2">
									
									

									<tbody><tr>
										

										<td width="4%" bgcolor="#DBDBDB"><font size="2">
												Absent 
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												COLIFORM (TCR)                          (3100)
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												 9223B-PA                       
										</font></td>

										<td width="19%" bgcolor="#DBDBDB"><font size="2">
												 07-01-2023 <br> 09-30-2023 
										</font></td>
										
									</tr>

									
									

									<tr>
										

										<td width="4%" bgcolor="#DBDBDB"><font size="2">
												Absent 
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												E. COLI(3014)
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												 9223B-PA                       
										</font></td>

										<td width="19%" bgcolor="#DBDBDB"><font size="2">
												 07-01-2023 <br> 09-30-2023 
										</font></td>
										
									</tr>

									
									
								</tbody></table>  <font size="1"> 
									                                                                                                                                                                                                         - RESTROOM SINK 
							</font> 
							</td>
						</tr>
						
						<tr>

							

							<td width="6%" bgcolor="#DBDBDB" align="center"><font size="2">  RT    <br> 
							</font> </td>

							<!-- This creates the link to the TCR Field Results for each sample -->
							<td width="9%" bgcolor="#DBDBDB" align="center"><font size="2"> <a href="javascript:viewResult(339608, 'RI')" onmouseover="window.status='Field Results for 2301950-01_SM34'; return true" onclick="window.status='Field Results for 2301950-01_SM34'; return true" onmouseout="window.status=''; return true" title="Field Results"> 2301950-01_SM34
								</a> <br> 
							</font></td>

							<td width="5%" bgcolor="#DBDBDB" align="center"><font size="2">Y</font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2">05-03-2023</font></td>
							<td width="8%" bgcolor="#DBDBDB" align="center"><font size="2">RTOR        </font></td>
							<td width="12%" bgcolor="#DBDBDB"><font size="2">  ROUTINE ORIGINAL 
							</font></td>
							<td width="4%" bgcolor="#DBDBDB" align="center"><font size="2">121       </font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2"> 0.000
</font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2"> </font></td>
							<td width="42%" bgcolor="#DBDBDB" align="center">
								

								<table border="1" cellspacing="0" width="100%" bgcolor="#DBDBDB" style="border-collapse: collapse" cellpadding="2">
									
									

									<tbody><tr>
										

										<td width="4%" bgcolor="#DBDBDB"><font size="2">
												Absent 
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												COLIFORM (TCR)                          (3100)
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												 9223B-PA                       
										</font></td>

										<td width="19%" bgcolor="#DBDBDB"><font size="2">
												 04-01-2023 <br> 06-30-2023 
										</font></td>
										
									</tr>

									
									

									<tr>
										

										<td width="4%" bgcolor="#DBDBDB"><font size="2">
												Absent 
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												E. COLI(3014)
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												 9223B-PA                       
										</font></td>

										<td width="19%" bgcolor="#DBDBDB"><font size="2">
												 04-01-2023 <br> 06-30-2023 
										</font></td>
										
									</tr>

									
									
								</tbody></table>  <font size="1"> 
									                                                                                                                                                                                                         - RESTROOM SINK 
							</font> 
							</td>
						</tr>
						
						<tr>

							

							<td width="6%" bgcolor="#DBDBDB" align="center"><font size="2">  RT    <br> 
							</font> </td>

							<!-- This creates the link to the TCR Field Results for each sample -->
							<td width="9%" bgcolor="#DBDBDB" align="center"><font size="2"> <a href="javascript:viewResult(330023, 'RI')" onmouseover="window.status='Field Results for 2300849-01_SM53'; return true" onclick="window.status='Field Results for 2300849-01_SM53'; return true" onmouseout="window.status=''; return true" title="Field Results"> 2300849-01_SM53
								</a> <br> 
							</font></td>

							<td width="5%" bgcolor="#DBDBDB" align="center"><font size="2">Y</font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2">01-09-2023</font></td>
							<td width="8%" bgcolor="#DBDBDB" align="center"><font size="2">RTOR        </font></td>
							<td width="12%" bgcolor="#DBDBDB"><font size="2">  ROUTINE ORIGINAL 
							</font></td>
							<td width="4%" bgcolor="#DBDBDB" align="center"><font size="2">121       </font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2"> 0.000
</font></td>
							<td width="7%" bgcolor="#DBDBDB" align="center"><font size="2"> </font></td>
							<td width="42%" bgcolor="#DBDBDB" align="center">
								

								<table border="1" cellspacing="0" width="100%" bgcolor="#DBDBDB" style="border-collapse: collapse" cellpadding="2">
									
									

									<tbody><tr>
										

										<td width="4%" bgcolor="#DBDBDB"><font size="2">
												Absent 
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												COLIFORM (TCR)                          (3100)
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												 9223B-PA                       
										</font></td>

										<td width="19%" bgcolor="#DBDBDB"><font size="2">
												 01-01-2023 <br> 03-31-2023 
										</font></td>
										
									</tr>

									
									

									<tr>
										

										<td width="4%" bgcolor="#DBDBDB"><font size="2">
												Absent 
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												E. COLI(3014)
										</font></td>

										<td width="25%" bgcolor="#DBDBDB"><font size="2">
												 9223B-PA                       
										</font></td>

										<td width="19%" bgcolor="#DBDBDB"><font size="2">
												 01-01-2023 <br> 03-31-2023 
										</font></td>
										
									</tr>

									
									
								</tbody></table>  <font size="1"> 
									                                                                                                                                                                                                         - REST ROOM SINK
							</font> 
							</td>
						</tr>
						
					</tbody></table>"""


import utils
from bs4 import BeautifulSoup

soup = BeautifulSoup(table, features='lxml')

header = utils.get_table_header_index(soup)
table_title = utils.get_table_title(soup, 0)
report_table = utils.get_table_df(table, header=header)

if len(report_table) > 1 and 'Coliform' in table_title:
	nested_table_columns = utils.get_nested_table_column_indexes(soup, header)
	column_headers = utils.get_column_headers(soup, header, nested_table_columns)
	column_headers.insert(0, 'Water System No.')
	if 'Coliform' in table_title:
		column_headers.append('Sample Pt Description Detail')
	# print(column_headers)
	working_report_table = pd.DataFrame(columns=column_headers)

	rows = soup.find('tbody').find_all('tr', recursive=False)
	rows = rows[header+1:3] 

	for row in rows:
		base_report_row = ['WSN'] # TODO: change to the WSN		
		row_copy = copy.copy(row)
		for td in row_copy.find_all('td', recursive=False):
			try:
				td.find('table').decompose()
			except:
				pass
			base_report_row.append(utils.clean_string(td.text))
		# print(base_report_row)

		subtable = row.find('table').find('tbody')
		for td in subtable.select('tr td:nth-of-type(2)'): # TODO: this extraneous empty table cell might not exist in all reports
			td.decompose()
		subtrs = subtable.find_all('tr', recursive=False)
		num_subtable_rows = len(subtrs)
		# print('num_subtable_rows = ' + str(num_subtable_rows))

		for n in range(0, num_subtable_rows):
			subreport_row = base_report_row[0: nested_table_columns[0]+1] # TODO: this will only work if there is a single subtable per row

			for td in subtrs[n].find_all('td'):
				subreport_row.append(utils.clean_string(td.text))

			subreport_row.append(base_report_row[len(base_report_row)-1])
			# print(subreport_row)
			working_report_table.loc[len(working_report_table.index)] = subreport_row

	print(working_report_table)


	








# import api_handler, constants, utils
# from all_state_scraper import WebScraper	



# def main(state):
# 	s = WebScraper(state, num_wsns_to_scrape=1)
# 	s.get_wsn_list()
# 	print(s.wsn_list)

# 	s.get_nav_list()
# 	print(s.nav_list)
	
# 	s.get_dated_reports()
# 	print(s.dated_reports)

# 

# if __name__ == '__main__':       
# 	state = 'MO'
# 	main(state=state)	

	