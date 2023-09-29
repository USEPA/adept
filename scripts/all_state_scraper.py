from factories.logger_factory import LoggerFactory
import api_handler, constants, utils
import utils 

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup 
from selenium.webdriver.common.by import By
from os import path, makedirs
from pathlib import Path
import csv
from urllib import error, parse, request
import re
from datetime import timedelta, datetime
import requests 
import argparse


class WebScraper():
	wsn_list = None
	nav_list = None
	dated_reports = None
	report_group_dir = None
	report_file_name = None 
	report_file_path = None
	current_report_url = None
	completed_wsns = None
	table_type = None
	header_index = 1  
	table_title = None 
	driver = None  
	token = None 
	session = None  
	tinwsys_is_number = None 
	tinwsys_st_code = None 
	wsn = None 
	payload = None 

	def __init__(self, 
				 state, 
				 begin_date=None, 
				 end_date=None,
				 wsnumber=None, 
				 num_wsns_to_scrape=None, 
				 report_to_scrape=None, 
				 ignore_logs=False,
				 overwrite_wsn_file=False):
		self.state = state 
		self.state_url = api_handler.get_url(state)
		self.begin_date = utils.get_begin_date(begin_date)
		self.end_date = utils.get_end_date(end_date)
		self.wsnumber = wsnumber
		self.num_wsns_to_scrape = num_wsns_to_scrape
		self.report_to_scrape = report_to_scrape
		self.ignore_logs = ignore_logs
		self.overwrite_wsn_file = overwrite_wsn_file
		self.run_logger = LoggerFactory.build_logger(constants.RUN_LOG.replace('XX', self.state))
		self.wsn_report_logger = LoggerFactory.build_logger(constants.WSN_LOG.replace('XX', self.state), 'wsn')
		self.wsn_report_log = constants.WSN_LOG.replace('XX', self.state) 
		self.wsn_file = constants.WSN_SAVE_LOCATION.replace('XX', self.state) 
		self.rundate_suffix = utils.get_datestamp_suffix()
		self.token_state = self.get_token_state()
		if self.token_state:
			self.driver = self.get_driver()
			self.token = self.get_token()
			self.session = self.get_session()
		elif self.state == 'WY':
			self.driver = self.get_driver()
			self.session = self.get_session()
		self.get_wsn_list()
		self.get_nav_list()
		self.get_dated_reports()

	
	def get_token_state(self):
		if self.state in api_handler.csrf_token_states:
			return True  
		else:
			return False


	def get_driver(self):
		driver = utils.get_selenium_driver(state_url=self.state_url, log=self.run_logger)
		return driver


	def get_token(self):
		html = self.driver.page_source
		token = utils.get_token(html)
		self.run_logger.debug('Session token is %s', token)
		return token


	def get_session(self):
		s = requests.session()
		selenium_user_agent = self.driver.execute_script("return navigator.userAgent;")
		s.headers.update({"User-Agent": selenium_user_agent})
		cookies = ''
		for cookie in self.driver.get_cookies():
			s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
			cookies = cookies + cookie['name'] + '=' + cookie['value'] + '; '
		cookies = cookies[:-2]
		s.headers['Cookie'] = cookies
		return s


	def get_wsns(self):
		try:
			df = pd.read_csv(self.wsn_file, delimiter=',')
			if self.wsnumber and isinstance(self.wsnumber, str):
				df = df[df['wsnumber'] == self.wsnumber]
			elif self.wsnumber and isinstance(self.wsnumber, list):
				df = df[df['wsnumber'].isin(self.wsnumber)]
			elif self.num_wsns_to_scrape:
				df = df.head(self.num_wsns_to_scrape)
			self.wsn_list = [tuple(row) for row in df.values]
		except:
			self.wsn_list = None
		

	def get_wsn_list(self):
		self.get_wsns()
		if self.overwrite_wsn_file or not self.wsn_list:
			self.run_logger.info('Getting WSN list and saving to %s', self.wsn_file)

			first_row = True
			Path(constants.DATA_DIR.replace('XX',self.state)).mkdir(parents=True, exist_ok=True)
			
			with open(self.wsn_file, 'w', newline='') as csvfile:
				writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
				if first_row:
					headers = ['wsnumber', 'tinwsys_is_number', 'tinwsys_st_code', 'dwwstate']
					writer.writerow(headers)
					first_row = False

				if self.state == 'WY':
					html = self.driver.page_source
					soup = BeautifulSoup(html, features='lxml')
					form_action = soup.find('form')['action']
					url = self.state_url + form_action
					# TODO: add '08' as a value
					payload = {'state_code': 'WY'}    
					self.session.post(url, data=payload)
					url = self.state_url + 'JSP/SearchDispatch?number=&name=&county=All&WaterSystemType=All&SourceWaterType=All&PointOfContactType=None&SampleType=null&begin_date=BEGIN_DATE&end_date=END_DATE&action=Search+For+Water+Systems'
					url = url.replace('BEGIN_DATE', self.begin_date).replace('END_DATE', self.end_date)
					response = self.session.get(url)
					html = response.text

					table = utils.get_parent_table_containing_href(html, 'WaterSystemDetail')
					trs = table.find_all('tr')
					for tr in trs:
						td = tr.find('td')
						if td:
							a = td.find('a')
							if a:
								params = utils.get_ids_from_href(a['href'])
								writer.writerow(params)

				elif self.token_state:
					self.driver = utils.load_wsn_search(self.driver)
					url = self.state_url + '?OWASP-CSRFTOKEN=' + self.token
					self.run_logger.debug('url = %s', url)
					data = {'OWASP-CSRFTOKEN': self.token}
					data = parse.urlencode(data).encode()
					req =  request.Request(url, data=data) 
					resp = request.urlopen(req)
					self.driver.find_element(By.NAME, 'action').click()
					self.run_logger.debug('url = %s', self.driver.current_url)                    
					url_text = self.driver.page_source
					anchors = BeautifulSoup(url_text, features='lxml').findAll('a', href=lambda href: href and 'viewData(' in href)
					for a in anchors:
						wsnset = utils.get_wsnset(a['href'])
						ids = [wsnset[2], wsnset[0], wsnset[1]]
						writer.writerow(ids)

				else:
					if self.state == 'NC':
						url = constants.WSN_SEARCH_URL_NC.replace('STATE_URL', self.state_url).replace('BEGIN_DATE', self.begin_date).replace('END_DATE', self.end_date)
					else:
						url = constants.WSN_SEARCH_URL.replace('STATE_URL', self.state_url)
					# self.run_logger.debug(url)
					html = utils.get_html(url)
					table = utils.get_parent_table_containing_href(html, 'WaterSystemDetail')
					trs = table.find_all('tr')
					for tr in trs:
						td = tr.find('td')
						if td:
							a = td.find('a')
							if a:
								params = utils.get_ids_from_href(a['href'])
								writer.writerow(params)
			self.get_wsns()
	

	def load_wyr8(self, url, wyr8='WY'):
		html = self.session.get(self.state_url).text
		soup = BeautifulSoup(html, features='lxml')
		form_action = soup.find('form')['action']
		pre_url = self.state_url + form_action
		payload = {'state_code': wyr8}    
		self.session.post(pre_url, data=payload)
		response = self.session.get(url)
		html = response.text
		return html


	def get_nav_list(self):
		# get a sample wsn
		self.wsn = self.wsn_list[0]

		# get WSN Details html, find the nav menu, and build the report list from it
		if self.token_state:
			payload = self.build_payload()
			html = utils.get_html_post(self.state_url + 'JSP/WaterSystemDetail.jsp', session=self.session, payload=payload)
		else:
			# build WSN Details URL
			url = constants.WSN_DETAILS_URL.replace('TINWSYS_IS_NUMBER', str(self.wsn[1]))
			url = url.replace('WSNUMBER', self.wsn[0])
			url = url.replace('TINWSYS_ST_CODE', self.state)
			url = url.replace('STATE_URL', self.state_url)
			if self.state == 'WY':
				html = self.load_wyr8(url)
			else:
				url = url + '&DWWState=' + str(self.wsn[3])
				html = utils.get_html(url)

		table = utils.get_parent_table_containing_href(html, 'WaterSystemFacilities')
		anchors = table.select(f"a[href*='.jsp']")

		if self.token_state:
			self.nav_list = [self.state_url + 'JSP/WaterSystemDetail.jsp']
		elif self.state == 'WY':
			self.nav_list = [constants.WSN_DETAILS_URL.replace('STATE_URL', self.state_url)]
		else:
			self.nav_list = [constants.WSN_DETAILS_URL.replace('STATE_URL', self.state_url) + '&DWWState=DWWSTATE']
			
		for anchor in anchors:
			if 'WaterSystemDetail' not in anchor['href']: # we added this above b/c not all states have it in the nav list, so don't add it again if they do
				if self.token_state:
					report_url = utils.get_url_from_tag_js(str(anchor))
				else:
					report_url = utils.get_url_from_tag(str(anchor))
					report_url = self.state_url + 'JSP/' + utils.build_report_url_mask(report_url)
					if 'BEGIN_DATE' in report_url:
						# some of the nav links contain begin and end date parameters but the date selection doesn't 
						# exist on the report page and will cause an error if dates are passed, so run a check
						temp_report_url = report_url.replace('TINWSYS_IS_NUMBER', str(self.wsn[1]))
						temp_report_url = temp_report_url.replace('WSNUMBER', self.wsn[0])
						temp_report_url = temp_report_url.replace('TINWSYS_ST_CODE', self.state)
						temp_report_url = temp_report_url.replace('DWWSTATE', self.wsn[2]) 
						temp_report_url = temp_report_url.replace('BEGIN_DATE','')
						temp_report_url = temp_report_url.replace('END_DATE','')
						try:
							html = utils.get_html(temp_report_url)
						except Exception as e:
							self.run_logger.error('Unable to validate %s in order to build navigation list', temp_report_url)
							exit()
						soup = BeautifulSoup(html,'lxml')
						begin_date_selector = soup.find('input', {'name':'begin_date'})
						if not begin_date_selector:
							report_url = report_url.replace('BEGIN_DATE', '').replace('END_DATE', '')
				self.nav_list.append(report_url)

			for url in self.nav_list:
				if 'ReportFormat=WQIR' in url or 'ReportFormat=SR' in url:
					self.nav_list.remove(url)
				for page in api_handler.noscrape_nav_reports:
					if page in url:
						try:
							self.nav_list.remove(url)
						except:
							pass

			if self.report_to_scrape:
				for url in self.nav_list:
					if self.report_to_scrape not in url:
						self.nav_list.remove(url)


	def get_dated_reports(self):
		self.dated_reports = []
		for link in self.nav_list:
			if 'BEGIN_DATE' in link:
				self.dated_reports.append(utils.get_report_group_from_url(link))
			# TODO: this won't work for token states; add code to test each link for token states and look for begin_date element 
				

	def build_current_report_url(self, report_url):
		tinwsys_is_number = str(self.wsn[1])
		tinwsys_st_code = self.wsn[2]
		dwwstate = str(self.wsn[3])
		current_report_url = report_url
		current_report_url = current_report_url.replace('STATE_URL', self.state_url)
		current_report_url = current_report_url.replace('TINWSYS_ST_CODE', tinwsys_st_code)
		current_report_url = current_report_url.replace('TINWSYS_IS_NUMBER', tinwsys_is_number)
		current_report_url = current_report_url.replace('WSNUMBER', self.wsnumber)
		current_report_url = current_report_url.replace('DWWSTATE', dwwstate)
		current_report_url = current_report_url.replace('BEGIN_DATE', self.begin_date)
		current_report_url = current_report_url.replace('END_DATE', self.end_date)
		return current_report_url


	def build_payload(self):
		wsnumber = self.wsn[0]
		tinwsys_is_number = str(self.wsn[1])
		tinwsys_st_code = self.wsn[2]
		dwwstate = str(self.wsn[3])
		payload = {'OWASP-CSRFTOKEN': self.token,
		   'tinwsys_is_number': tinwsys_is_number,
		   'tinwsys_st_code': tinwsys_st_code,
		   'wsnumber': wsnumber,
		   'DWWState': dwwstate,
		   'begin_date': self.begin_date,
		   'end_date': self.end_date,
		   'counter': '0',
		   'history': '0'}    
		return payload


	def look_for_drilldowns(self, table_html, table_title, full_html=None):
		indexes = utils.get_header_and_first_data_indexes(table_html)
		if not indexes:
			return
		header_index = indexes[0]
		first_data_row_index = indexes[1]
		col_headers = utils.get_col_headers(table_html, header_index)

		i = -1
		drilldown_links = []
		drilldown_info = []
		for tr in table_html.find_all('tr'):
			i += 1
			if i < first_data_row_index:
				continue
			j = -1
			for td in tr.find_all('td'):
				j += 1
				try:
					for a in td.find_all('a'):
						link = None 
						if '.jsp' in a['href'] and 'http' not in a['href'] and 'WaterSystemDetail.jsp' not in a['href']:
							# only collect links to .jsp pages; don't follow drilldown to another WSN (e.g. WaterSystemDetail)
							link = self.state_url + 'JSP/' + a['href']
						elif self.token_state and 'javascript:view' in a['href']:
							function_name = utils.get_function_name(a['href'])
							function_def = utils.get_function_definition(function_name, full_html)
							link = self.state_url + 'JSP/' + utils.get_js_action(function_def) 
							# print('function_name = ' + function_name)
							# print('function_def = ' + function_def)
							# print('link = ' + link)

						if link:
							col_header = col_headers[j]
							# some reports have duplicate links in different rows so only add the link to the list if we don't already have it
							if self.token_state or link not in drilldown_links:
								drilldown_links.append(link)
								drilldown_info.append((link, utils.clean_string(a.text), a['href']))
				except:
					pass

		if drilldown_links:
			self.run_logger.info('Found drilldown links, processing now...')
			# print(drilldown_links)

		for link in drilldown_info:
			self.current_report_url = link[0].replace(' ', '%20')
			payload = None 
			if self.token_state:
				payload = self.build_payload()
				params = utils.build_payload_params(link[2], full_html)
				payload = payload | params
				# payload['counter'] = 2
/				# print(payload)

			join_column = {col_header: link[1]}
			if 'NonTcrSampleResults' in self.current_report_url:
				# add the unique identifier of the sample to the table because there are some cases where the Sample No. in the HTML table is not unique
				if self.token_state:
					join_column['tsasampl_is_number'] = utils.get_js_param_value(link[2])
				else:
					join_column['tsasampl_is_number'] = utils.get_url_param_value(self.current_report_url, 'tsasampl_is_number')

			self.run_logger.info('Working on %s %s', col_header, link[1])
			self.write_table_data(join_column=join_column, parent_table_title=table_title, payload=payload, parent_html=full_html)


	def write_table_data(self, join_column=None, parent_table_title=None, payload=None, parent_html=None):
		self.run_logger.info('Report URL is %s', self.current_report_url)
		# print(join_column)

		try:
			if payload:
				html = utils.get_html_post(self.current_report_url, self.session, payload)
			elif self.state == 'WY':
				html = self.load_wyr8(self.current_report_url)
				# print(html)
			else:
				html = utils.get_html(self.current_report_url)
		except Exception as e:
			self.run_logger.error('Unable to open %s for WSN %s: %s', self.current_report_url, self.wsnumber, e)
			return False

		soup = BeautifulSoup(html,'lxml')
		try:
			page_title = soup.find('title').text
		except:
			page_title = None
		# self.run_logger.debug('page_title = %s', page_title)

		# loop through nested tables to get down to report tables
		table_index = -1 # we will need the index of each table so start a counter
		for table in soup.find_all('table'):
			table_index += 1
			# print('table_index = ' + str(table_index))

			if 'Violation Detail' in page_title and 'Violation No.' in utils.clean_string(table.find('td').text):
				# "Standard" states (non-TX-like) have Violation Detail table without a title, 
				# so identify it here because it will get ruled out later
				self.table_title = 'Violation Detail'
				self.table_type = 'columns'
				self.header_index = 0
			elif not utils.test_table(table):
				continue # not a report table, go to next one
			else:
				self.table_title = utils.get_table_title(soup, table_index)
				self.table_type = utils.get_table_type(table, self.table_title)
				self.header_index = utils.get_table_header_index(table, self.table_title)
			
			# if parent_html:
			# 	print(table)
			# 	print('table_title = ' + self.table_title)
			# 	print('table_index = ' + str(table_index))
			# 	print('table type = ' + self.table_type)
			# 	print('header_index = ' + str(self.header_index))
			# 	print('-------------------------------------------------------------------------------------------------------------------------------------')

			if (((self.table_title == 'Water System Detail Information' or self.table_title == 'Water System Details') 
				 and 'WaterSystemDetail.jsp' not in self.current_report_url) or 
			   ((self.table_title == 'Water System Facilities' or self.table_title == 'Water System Facility Detail') 
				 and 'WaterSystemFacilities.jsp' not in self.current_report_url)):
				# We only want to collect the Water System Detail Information from the WasterSystemDetails page
				# and Water System Facilities from the WaterSystemFacilities page
				continue

			if parent_table_title and self.table_title == parent_table_title:
				# When drilling down, it's possible for the table title to be the same as the 
				# parent page table title (e.g. Compliance Schedules), meaning they would write to the 
				# same CSV file, so make a new table title 
				self.table_title = self.table_title + ' Detail'			
				self.run_logger.debug('Table title is a repeat, changing to ' + self.table_title)	

			self.run_logger.info(f'Working on {self.wsnumber}: {self.table_title} . . .')
			self.report_file_name = self.state + '_' + self.table_title + self.rundate_suffix + '.csv'
			self.report_file_path = self.report_group_dir + '/' + self.report_file_name

			try:
				if self.table_type == 'rows':
					report_table = utils.get_table_df(table, header=self.header_index)
					if 'NonTcrSamples.jsp' in self.current_report_url:
						# sometimes in this report there are multiple rows with the same sample number that link to 
						# different sample results, so add a column containing the unique sample identifier from the URL
						report_table['tsasampl_is_number'] = utils.get_unique_sample_ids_from_url(table, self.token_state)
				else:
					report_table = utils.get_table_df(table)
			except (ValueError, IndexError):
				# sometimes a legitimate report table is just a table title with no headings (or data),
				# which will throw an error; in that case, skip and go to next table
				continue

			if self.table_type == 'columns':
				report_table.dropna(how='all', axis='columns', inplace=True)
				header_indexes = []
				for i in range(len(report_table.columns)):
					if (i % 2) == 0:
						header_indexes.append(i)
				headers = report_table.iloc[:,header_indexes[0]].to_list()
				for i in header_indexes[1:]:
					headers.extend(report_table.iloc[:,i].to_list())
				headers = [h for h in headers if not(pd.isnull(h)) == True]    
				headers = [h.replace(' :', '') for h in headers]
				headers = [h.replace(':', '') for h in headers]

				working_report_table = pd.DataFrame(columns=headers)
				new_row = report_table.iloc[:,header_indexes[0]+1].to_list() 
				for i in header_indexes[1:]:
					new_row.extend(report_table.iloc[:,i+1].to_list())
					try:
						working_report_table.loc[len(working_report_table.index)] = new_row
					except ValueError:
						if np.isnan(new_row[len(new_row)-1]):
							# if there is an uneven number of rows, there will be one too many items in the list
							new_row.pop()
							try:
								working_report_table.loc[len(working_report_table.index)] = new_row
							except:
								pass
						else:
							# no data in header at this location so do nothing
							pass
				if 'Water System No.' not in working_report_table.columns:
					working_report_table.insert(0, 'Water System No.', self.wsnumber)
				if join_column:
					for col_header, value in join_column.items():
						try:
							working_report_table.insert(1, col_header, value)
						except ValueError:
							# column already exists in the drill-down table so just move on 
							pass 
				if join_column:
					for k in join_column.keys():
						join_col_name = k
					working_report_table = working_report_table.melt(id_vars=['Water System No.', join_col_name], value_vars=headers, var_name='Type', value_name='Value')
				else:
					working_report_table = working_report_table.melt(id_vars=['Water System No.'], value_vars=headers, var_name='Type', value_name='Value')
				report_table = working_report_table
			else:
				report_table = report_table.loc[:, ~report_table.columns.str.contains('^Unnamed')]
				if 'Water System No.' not in report_table.columns:
					report_table.insert(0, 'Water System No.', self.wsnumber)
				if join_column:
					# print('join_column = ' + str(join_column))
					for col_header, value in join_column.items():
						try:
							report_table.insert(1, col_header, value)
						except ValueError:
							# column already exists in the drill-down table so just move on 
							pass 

			rpath = Path(self.report_file_path)
			
			if not rpath.is_file():
				with open (self.report_file_path, 'a', newline='', encoding='utf-8') as write_file:
					writer = csv.writer(write_file, quoting=csv.QUOTE_MINIMAL)
					writer.writerow(list(report_table.columns))
			
			report_table.to_csv(self.report_file_path, mode='a', encoding='utf-8', index=False,  header=False)       
			self.run_logger.info('Wrote %s data to %s', self.table_title, self.report_file_path)

			if self.token_state and not parent_html:
				full_html = html
			elif self.token_state and parent_html:
				full_html = parent_html
			else:
				full_html = None
			if self.table_title not in api_handler.nondrilldown_reports:
				self.look_for_drilldowns(table, table_title=self.table_title, full_html=full_html)

		return True


	def scrape_wsn(self):
		self.run_logger.info('Working on %s', self.wsnumber)

		for report_url in self.nav_list:
			# get the report group name, which is the subfolder to save to
			report_group_name = utils.get_report_group_from_url(report_url)

			if not self.ignore_logs:
				df = utils.get_completed_report_for_wsn(self.wsnumber, report_group_name, self.completed_wsns)	
			else:
				df = pd.DataFrame()

			if len(df) > 0:
				if report_group_name in self.dated_reports:
					report_end_date = datetime.strptime(constants.END_DATE, '%m/%d/%Y')
					new_date = df.iloc[0]['End Date'] + timedelta(days=1)
					if report_end_date > new_date:
						# We have some data for this WSN/report but the last scraped report date is older 
						# than our current report end date, so replace the begin date with the last scraped date.
						self.begin_date = new_date.strftime('%m/%d/%Y')
						self.run_logger.info('Setting report begin date to %s', self.begin_date)
					else:
						# This report has date ranges but this WSN is scraped up to date to go to next report
						continue
				else:
					# This report doesn't have date ranges and we've already scraped this it for this WSN 
					# so go to the next report
					continue

			# self.report_group_dir = constants.DATA_DIR.replace('XX', self.state) + report_group_name
			self.report_group_dir = utils.get_report_dir(self.state, self.rundate_suffix, report_group_name)
			payload = None
			if self.token_state:
				payload = self.build_payload()
				if 'WaterSystemDetail' in report_url:
					self.current_report_url = report_url
				else:
					self.current_report_url = self.state_url + 'JSP/' + report_url
			else:
				# build the report URL
				self.current_report_url = self.build_current_report_url(report_url)
			# scrape the tables
			self.run_logger.debug('Working on %s report group', report_group_name)
			scraped = self.write_table_data(payload=payload)
			# log the report
			if scraped:
				self.wsn_report_logger.info('%s, %s, %s, %s', self.wsnumber, report_group_name, self.begin_date, self.end_date)


	def make_dirs(self):
		for report_url in self.nav_list:
			# report_group_dir = constants.DATA_DIR.replace('XX', self.state) + utils.get_report_group_from_url(report_url)
			report_group_dir = utils.get_report_dir(self.state, self.rundate_suffix, utils.get_report_group_from_url(report_url))
			if not path.exists(report_group_dir):
				makedirs(path.normpath(report_group_dir))
				self.run_logger.info('Created directory %s', report_group_dir)    


	def scrape(self):
		self.completed_wsns = utils.get_completed_wsn_reports(self.wsn_report_log)

		self.make_dirs()

		for wsn in self.wsn_list:
			self.wsnumber = wsn[0]
			self.wsn = wsn
			self.scrape_wsn()

		self.run_logger.info('Scrape complete')
		self.wsn_report_logger.info('%s, %s, %s, %s', 'All', 'All', self.begin_date, self.end_date)

		utils.endtime_files(self.state, self.rundate_suffix)
		self.run_logger.info('Files renamed to include scrape end date.')

		try:
			self.driver.close()
		except AttributeError:
			pass


def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('--state', help='Required. Two-character state code to scrape. Must be a JSP state listed in api_handler.py.')
	parser.add_argument('--num', nargs='?',  help="Optional. Number of Water Systems to scrape. If passed, the first n WSNs found on the state's Water System Search page will be scraped. If neither this argument nor --wsnumber are passed, all WSNs will be scraped.")
	parser.add_argument('--wsnumber', nargs='?', help='Optional. A string containing a single Water System Number or multiple Water System Numbers separated by commas to scrape. No validiation is performed to ensure a valid WSN has been passed.')
	parser.add_argument('--startdate', nargs='?',  help='Optional. The start date to use for reports with filterable date ranges. Defaults to 01/01/1980. Use format MM/DD/YYYY.')
	parser.add_argument('--enddate', nargs='?',  help='Optional. The end date to use for reports with filterable date ranges. Defaults to the current date. Use format MM/DD/YYYY.')
	parser.add_argument('--report', nargs='?', help='Optional. Typically used for development/debugging only. The report group from the report URL to restrict scrape to a single report. (Example: NonTcrSample can be used to restrict scrape to Other Chemical Samples only.) No validiation is performed to ensure entry is a valid report.')
	parser.add_argument('--ignorelogs', nargs='?', help='Optional. Typically used for development/debugging only. Pass Y or True to scrape all data even for WSNs that have already been logged as scraped.')
	parser.add_argument('--overwrite_wsn_file', nargs='?', help="Optional. Typically used for development/debugging only. Pass Y or True to download a new WSN list, overwriting an existing one if it exists")
	args = parser.parse_args()

	try:
		state = args.state.upper() 
	except AttributeError:
		print('Please enter a state using argument --state and passing the 2-character state code')
		exit()
	num_wsns_to_scrape = args.num
	wsnumber = utils.parse_wsnumber(args.wsnumber)
	startdate = args.startdate
	enddate = args.enddate
	report = args.report
	ignorelogs = args.ignorelogs
	overwrite_wsn_file = args.overwrite_wsn_file
	ok = True

	if not utils.check_valid_state(state):
		print('Invalid state: ' + state)
		utils.display_valid_states()
		print()
		ok = False

	if num_wsns_to_scrape and not utils.check_valid_number(num_wsns_to_scrape):
		print('Invalid number: ' + num_wsns_to_scrape)
		print('Please enter an integer for number of Water Systems to scrape')
		ok = False
	elif num_wsns_to_scrape:
		num_wsns_to_scrape = int(num_wsns_to_scrape)

	if startdate and not utils.check_valid_date(startdate):
		print('Invalid start date: ' + startdate)
		print('Please enter dates using format MM/DD/YYYY')
		ok = False

	if enddate and not utils.check_valid_date(enddate):
		print('Invalid end date: ' + enddate)
		print('Please enter dates using format MM/DD/YYYY')
		ok = False

	if ignorelogs and ignorelogs.upper() not in ['Y','YES','TRUE']:
		print('Unknown value for ignorelogs: ' + ignorelogs)
		print('Accepted values are: Y, Yes, or True')
		ok = False

	if overwrite_wsn_file and overwrite_wsn_file.upper() not in ['Y','YES','TRUE']:
		print('Unknown value for overwrite_wsn_file: ' + overwrite_wsn_file)
		print('Accepted values are: Y, Yes, or True')
		ok = False
	if not ok:
		exit()

	print('Beginning scrape for ' + state)
	if wsnumber:
		print('Scraping ' + str(len(wsnumber)) + ' Water Systems: ' + str(wsnumber))
	elif num_wsns_to_scrape:
		print('Scraping ' + str(num_wsns_to_scrape) + ' Water Systems')

	print('Date range for sampling reports is ' + utils.get_begin_date(startdate) + ' to ' + utils.get_end_date(enddate))

	if report:
		print('Output restricted to reports containing ' + report + ' in the URL')

	if ignorelogs:
		print('Ignoring the logs and scraping all data even if previously logged as scraped')

	if overwrite_wsn_file:
		print('Overwriting WSN list if it already exists')

	try:	
		s = WebScraper(state, 
					   num_wsns_to_scrape=num_wsns_to_scrape, 
					   wsnumber=wsnumber, 
					   begin_date=startdate, 
					   end_date=enddate, 
					   report_to_scrape=report, 
					   ignore_logs=ignorelogs,
					   overwrite_wsn_file=overwrite_wsn_file)
	except Exception as e:
		utils.handle_scrape_error(state, e)

	try:
		s.scrape()
	except Exception as e:
		utils.handle_scrape_error(state, e)



if __name__ == '__main__':       
	get_arguments()
