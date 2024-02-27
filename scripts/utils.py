import api_handler, constants, config

import sys
import logging
import os.path 
from pathlib import Path
from os import makedirs
import pathlib
from datetime import datetime
import glob
import ntpath
from io import StringIO
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import itertools
import re
import time
from urllib import error
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup 
import ssl
import http
# import certifi


def get_selenium_driver(
	 state_url=None
	,state_proxy=None
	,log=None
):
	options = Options()
	options.add_argument('--disable-notifications')
	options.add_argument('--disable-infobars')
	options.add_argument('--mute-audio')
	options.add_argument('--no-sandbox')
	options.add_argument('--log-level=3')
	options.add_experimental_option('excludeSwitches', ['enable-logging','enable-automation'])
	options.add_argument('--disable-extensions')
	options.add_argument('test-type')
	options.add_argument('user-agent=Mozilla/5.0')
	options.add_argument('--disable-blink-features=AutomationControlled') 
	options.add_experimental_option('useAutomationExtension', False) 
	# comment out the line below to show the browser (use only for debugging)
	options.add_argument('--headless')
	# uncomment the line below to keep the browser window open; use only for debugging
	# options.add_experimental_option('detach', True)
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--ignore-ssl-errors=yes')

	if state_proxy is not None:
		options.add_argument('--proxy-server=%s' % state_proxy);

	service = Service(
		executable_path=ChromeDriverManager().install()
	);
	driver = webdriver.Chrome(
		 service=service
		,options=options
	);   
	driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
	driver.set_window_size(1080, 800)

	# ensure valid session
	if state_url:
		try:
			driver.get(state_url)
			if log:
				log.debug('Current Selenium session is %s', format(driver.session_id))
		except exceptions.InvalidSessionIdException as e:
			if log:
				log.exception(e)
	return driver     


def check_dirs(state):
	# if you don't have logging or data directories locally, this generates them for you
	data_dir = constants.DATA_DIR.replace('XX',state)
	log_dir = constants.LOG_DIR.replace('XX',state)
	dir_ls = [
		data_dir,
		log_dir,
		data_dir + 'Water System Details',
		data_dir + 'Sample Schedules',
		data_dir + 'Chem_Rad Samples',
		data_dir + 'Violations'
	]
	for dir in dir_ls:
		if not os.path.exists(dir):
			os.makedirs(os.path.normpath(dir))


def get_url_param_value(url, param):
	offset = len(param) + 1
	i = url.index(param) + offset
	value = url[i:]
	if '&' in value:
		value = value[:value.index('&')]
	return value.strip()


def get_js_param_value(href):
	i = href.index('(') + 1
	i2 = href.index(',')
	return href[i:i2]


def get_ids_from_href(href):
	wsnumber = get_url_param_value(href, 'wsnumber')
	tinwsys_is_number = get_url_param_value(href, 'tinwsys_is_number')
	tinwsys_st_code = get_url_param_value(href, 'tinwsys_st_code')
	try:
		dwwstate = get_url_param_value(href, 'DWWState')
	except:
		dwwstate = None
	return [wsnumber, tinwsys_is_number, tinwsys_st_code, dwwstate]
	

def get_pretty_time(seconds):
	days = None
	hours = None
	minutes = None

	if seconds > 86400:
		# report in days
		days = int(seconds/86400)
		seconds = seconds%86400
		if seconds > 3600:
			hours = int(seconds/3600)
			seconds = seconds%3600
			if seconds > 60:
				minutes = int(seconds/60)
				seconds = seconds%60
	elif seconds > 3600:
		# report in hours
		hours = int(seconds/3600)
		seconds = seconds%3600
		if seconds > 60:
			minutes = int(seconds/60)
			seconds = seconds%60
	elif seconds > 60:
		# report in minutes
		minutes = int(seconds/60)
		seconds = seconds%60

	seconds = round(seconds)

	time = f'{seconds} seconds'
	if minutes:
		time = f'{minutes} minutes; {time}'
	if hours:
		time = f'{hours} hours; {time}'
	if days:
		time = f'{days} days; {time}'

	return time


def get_wsn_list(wsn_file):
	try:
		df = pd.read_csv(wsn_file, delimiter=',')
		wsn_list = df['wsnumber'].tolist()
	except:
		return []
	return wsn_list


def get_report_list():
	report_list = []
	for report in api_handler.wsn_details_reports:
		report_list.append(report['report'])
	for report in api_handler.sample_schedules_reports:
		report_list.append(report['report'])
	for report in api_handler.coliform_microbial_reports:
		report_list.append(report['report'])
	for report in api_handler.coliform_summary_reports:
		report_list.append(report['report'])
	for report in api_handler.lead_copper_reports:
		report_list.append(report['report'])
	for report in api_handler.chem_rad_subreports:
		report_list.append(report['report'])
	for report in api_handler.chem_rad_reports:
		report_list.append(report['report'])
	for report in api_handler.violations_reports:
		report_list.append(report['report'])
	for report in api_handler.site_visits_reports:
		report_list.append(report['report'])
	for report in api_handler.milestones_reports:
		report_list.append(report['report'])
	return report_list


def get_missing_reports(state):
	wsn_file = constants.WSN_SAVE_LOCATION.replace('XX', state)
	wsn_list = get_wsn_list(wsn_file)
	report_list = get_report_list()

	completed_reports_df = pd.read_csv(constants.WSN_LOG.replace('XX', state), usecols=[0,1], names=['WSN', 'Report'])
	completed_reports_df.drop_duplicates(inplace=True)
	completed_reports_df = completed_reports_df[~completed_reports_df['Report'].str.contains('Violation Detail')]
	completed_reports_df = completed_reports_df[~completed_reports_df['Report'].str.contains('Enforcement Actions')]

	overlap_df = pd.DataFrame(itertools.product(wsn_list, report_list), columns=['WSN', 'Report'])
	missing_reports = pd.concat([overlap_df, completed_reports_df]).drop_duplicates(keep=False)

	return missing_reports

################################################################################
def load_wsn_search(driver, num_tries=0, log=None):
	msg = '1: ' + driver.current_url
	if log:
		log.debug(msg)
	else:
		print(msg)
	try:
		driver.find_element('id','public').click()
		msg = '2: ' + driver.current_url
		if log:
			log.debug(msg)
		else:
			print(msg)
	except exceptions.NoSuchElementException:
		if 'Virginia' in driver.current_url and num_tries <= 3:
			load_wsn_search(driver, num_tries + 1, log)
		elif num_tries > 3:
			msg = 'Unable to find the Public Access button; aborting'
			if log:
				log.exception(msg)
			else:
				print(msg)
		# pass

	if 'SearchDispatch' not in driver.current_url:
		try:
			try:
				driver.find_element('link text', 'Water System Search').click()
			except:
				driver.find_element('link text', 'Search For Water Systems').click()
			msg = '3: ' + driver.current_url
			if log:
				log.debug(msg)
			else:
				print(msg)
		except exceptions.NoSuchElementException:
			if 'Virginia' in driver.current_url and num_tries <= 3:
				load_wsn_search(driver, num_tries + 1, log)
			elif num_tries > 3:
				msg = 'Unable to find the Public Access button; aborting'
				if log:
					log.exception(msg)
				else:
					print(msg)            
	return driver


def get_token(html):
	token = re.search('RecaptchaInitialization.js?(.+?)">', html).group(1)
	token = token.replace('?OWASP-CSRFTOKEN=','')
	return token
	

def get_wsnset(href):
	"""
	Decodes a JSP report link to extract the tinwsys_is_number, tinwsys_st_code, and wsnumber
	"""
	tinwsys_is_number = re.search('javascript:viewData(.+?),', href).group(1).replace('(','')
	tinwsys_st_code = re.search("'(.+?)'", href).group(1)
	wsnumber = re.search(f", '{tinwsys_st_code}', '(.+?)'", href).group(1).strip()
	return (tinwsys_is_number, tinwsys_st_code, wsnumber)


def get_report_group_from_url(url):
	"""
	Extracts the report page name from a JSP report link; this code refers to this as the "Report Group Name"
	"""
	if 'JSP' in url:
		result = re.search('JSP/(.*).jsp', url)
	else:
		result = re.search('(.*).jsp', url)
	return result.group(1)
	
	
def get_html(url, session=None, retry_count=0):
	url = url.replace('#','%23').replace(' ','%20')
	html = ''
	if session:
		response = session.get(url)
		return response.text
	else:
		try:
			# context = ssl.create_default_context(cafile=certifi.where())
			context = ssl._create_unverified_context()
			response = urlopen(url, context=context)
		except error.HTTPError:
			try:
				req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
				response = urlopen(req)
			except error.HTTPError:
				raise e
		except (error.URLError, TimeoutError, ConnectionResetError) as e:
			if retry_count == config.MAX_URL_TRIES:
				raise e
			time.sleep(config.TIMEOUT_TIME)
			get_html(url, session=session, retry_count=retry_count + 1)    
		except Exception as e:
			raise e
	try:
		html = response.read()
	except (http.client.IncompleteRead, ValueError) as e:
		if retry_count == config.MAX_URL_TRIES:
			raise e
		get_html(url, session=session, retry_count=retry_count + 1)    
	return html
	
	
def get_html_post(url, session, payload, retry_count=0):
	html = ''
	try:
		response = session.post(url, data=payload)
		html = response.text
	except:
		if retry_count == config.MAX_URL_TRIES:
			raise e 
		time.sleep(config.TIMEOUT_TIME)
	return html


def get_state_report_urls(url_to_check):
	"""
	When passed a state report URL (usually the Water System Details page, but can be any page with report nagivation),
	returns a list of all report URLs from constants.REPORT_URLS that exist in the report navigation for the state_url
	in question. Will NOT add report URLs that exist for a state but are not in constants.REPORT_URLS.
	THIS FUNCTION IS NOT CURRENTLY USED
	"""
	html = get_html(url_to_check)
	soup = BeautifulSoup(html,'lxml')            

	report_urls = []
	for report_url in constants.REPORT_URLS:
		url = report_url.replace('STATE_URL/JSP/','')
		i = url.find('?')
		url = url[:i]
		if soup.find('a', href=re.compile(url)):
			report_urls.append(report_url)
	return report_urls


def get_parent_table_containing_href(html, href_text):
	soup = BeautifulSoup(html,'lxml') 
	a = soup.select_one(f"a[href*='{href_text}']")
	return a.findParent('table')


def get_index(string, substr, direction='forward'):
	i = -1
	if direction == 'forward':
		i = string.find(substr) + len(substr)
	else:
		i = string.find(substr)
	return i


def get_url_from_tag(tag):
	i = get_index(tag, 'href="')
	i2 = get_index(tag, '">', 'backwards')
	return tag[i:i2]


def get_url_from_tag_js(tag):
	search_term = "javascript:viewData('"
	i = get_index(tag, search_term)
	search_term = "')"
	i2 = get_index(tag, search_term, 'backwards')
	return tag[i:i2]


def build_report_url_mask(url):
	i = get_index(url, '.jsp?') 
	i2 = get_index(url, '"', direction='backwards')
	if i2 < 0:
		i2 = len(url)
	url_stem = url[:i]
	param_str = url[i:i2]
	param_list = param_str.split('&amp;')
	new_param_str = ''
	for param in param_list:
		i = param.find('=')
		param_name = param[:i]
		param_value = param[i+1:]
		if param_name.lower() not in ['chem', 'reportformat', 'year', 'counter', 'history']:
			param_value = param_name.upper()
		new_param_str = new_param_str + param_name + '=' + param_value + '&'
	if new_param_str:
		new_param_str = new_param_str[:-1]
	return url_stem + new_param_str


def get_begin_date(begin_date=None):
	if begin_date:
		return begin_date
	else:
		return constants.BEGIN_DATE


def get_end_date(end_date=None):
	if end_date:
		return end_date
	else:
		return constants.END_DATE


def completed_report_log_to_df(wsn_report_log):
	try:
		df = pd.read_csv(wsn_report_log, usecols=[0,1,3], names=['WSN', 'Report', 'End Date'], converters={0: str.strip,1: str.strip})
	except (pd.errors.EmptyDataError, FileNotFoundError):   
		return pd.DataFrame({'WSN': [], 'Report': [], 'End Date': []})
	except Exception as e:
		print('Unexpected error trying to import ' + wsn_report_log + ' into a dataframe')
		exit()

	df = df.astype({'WSN': 'string[pyarrow]', 'Report': 'string[pyarrow]'})    
	# convert End Date column to date format
	df['End Date'] = pd.to_datetime(df['End Date'])
	# eliminate any rows where the End Date is older than required end date
	# df = df.loc[df['End Date'] >= constants.END_DATE]

	return df


def get_completed_wsn_reports(wsn_report_log):
	df = completed_report_log_to_df(wsn_report_log)
	# group by WSN/Report and get max End Date
	df = df.sort_values('End Date', ascending=False).drop_duplicates(['WSN','Report'])
	return df        


def get_completed_report_for_wsn(wsnumber, report, df):
	df = df[df['WSN'] == wsnumber]
	df = df[df['Report'] == report]
	return df


def clean_string(string):
	string = string.replace('/','_')
	string = string.replace('\n',' ')
	string = string.replace('\r',' ')
	string = string.replace('\t',' ')
	string = string.replace('  ',' ').replace('  ',' ').replace('  ',' ')
	string = string.strip()
	return string


def get_table_title(soup, table_index):
	table = soup.find_all('table')[table_index]

	# California nests its Water System Details and Water System Facility Detail tables in a child table which 
	# breaks this function so get those out of the way first
	td = table.find('td') 
	try:
		if 'Water System No.' in clean_string(td.text):
			return 'Water System Details'
		elif 'State Asgn ID No.' in clean_string(td.text):
			return 'Water System Facility Detail'
	except:
		pass

	if table.find('caption'):
		return clean_string(table.find('caption').text)

	try:
		# header rows with the colspan attribute contain a title and data we want for TX-like states
		th = table.find(['th','td'], colspan=True)
		table_title = th.text
	except AttributeError:
		date_form = soup.find('form', {'name': 'dateForm'})
		dt_buttons = soup.find('div', {'class': 'dt-buttons'})
		toggler = soup.find('p', {'class': 'toggler'}) # CA has a "click to show/hide" section on some report. When present, the table title is above the water system details
		p = None
		if date_form or dt_buttons or toggler:
			# on pages where there is a date range selector, the report title is at the top of the page
			water_detail = soup.find(text=re.compile('Water System No'))
			if water_detail:
				p = water_detail.find_previous('p')
			else:
				p = table.find_previous('p')

		if p:
			table_title = p.get_text()
		else:
			# We're not in a TX-like state so look for table title outside of table itself
			tr = soup.select('table')[table_index].find_previous('tr')
			if tr.find('table') == table:
				# there are multiple report tables in this row and this is first one, so go up to the previous row and get the first p tag
				try:
					table_title = tr.find_previous('tr').find('p').text
				except Exception as e:
					return None
			else:
				try:
					# there is only one report table per row, OR this is the second table in a row of two report tables, so just get the previous p tag  
					table_title = table.find_previous('p').text
				except Exception as e:
					return None

	return clean_string(table_title)


def test_table(soup, parent=False):
	# make sure there is more than one row
	try:
		trs = soup.find_all('tr')
		if len(trs) < 2:
			return False
	except:
		return False

	if soup.has_attr('class') and 'detailTable' in soup['class']:
		return True

	try:
		td = soup.find(['td','th']) # get first th or td, which will be the header row
	except AttributeError:
		return False

	try: # if there is an anchor tag in the table header, it's the navigation bar so skip it
		if td.find('a'):
			return False
	except:
		pass 

	try:
		if ('Water System No.' in clean_string(td.text) # It's the Water System Details table
			or 'State Asgn ID No' in clean_string(td.text)): # it's the Water System Facility Detail table 
			# California nests its Water System Details and Water System Facility Detail tables in a child table; use only the nested table
			if soup.find('table'):
				return False
			return True
	except:
		pass

	try: 
		bgcolor = td.get('bgcolor').replace('#','').lower()
	except:
		return False 

	if bgcolor in constants.REPORT_BGCOLORS: # assumes all report tables have a header cell that is on of the background colors coded in constants.py
		if not parent: # don't recursively do this check
			parent_table = soup.find_parent('table')
			if test_table(parent_table, parent=True):
				return False
	else:
		return False

	return True


def get_table_type(soup, table_title=None):
	if table_title in ('Water System Details', 'Water System Detail Information', 'Water System Facility', 'Chemical Sample Detail Information'):
		return 'columns'
	else:
		try:    
			tr = soup.find_all('tr')[-1]
			try:
				b = tr.find('td').find('b')
				if b:
					return 'columns'
			except:
				return 'rows'
		except:
			return 'rows'
	return 'rows'


def get_table_header_index(soup, table_title=None):
	tr = soup.find('tr')
	if tr.text in ('Water System Detail Information', 'Water System Facility', 'Chemical Sample Detail Information'):
		return 0

	trs = soup.find_all('tr')
	if trs:
		try:
			if trs[1].find('th'):
				return 1
			if trs[0].find('th'):
				return 0
		except:
			pass 

		try:
			if trs[1].find('td').find('b'):
				return 1
			if trs[0].find('td').find('b'):
				return 0
		except:
			pass
				
	tr = soup.find('tr')
	if tr:
		tds = tr.find_all('td')
		try:
			td = tds[1]
			if td.find('b'):
			   return 1
			else:
				return 0
		except:
			return 0
	return 0


def get_header_and_first_data_indexes(soup):
	i = -1
	header_row = None
	trs = soup.find_all('tr')
	for tr in trs:
		i += 1
		th = tr.find_all('th')
		if th:
			header_row = i
			continue 
		else:
			try:
				th = tr.find('td').find('b')
				if th:
					header_row = i
					continue
			except:
				pass 
		
		if not header_row:
			# TODO: this avoids an error if checking a by-columns table for drilldowns but is unknown to work if the by-columns table contains drilldowns we want
			return (0, 0)
		return (header_row, i)  


def get_col_headers(soup, header_index):
	col_headers = []
	tr = soup.find_all('tr')[header_index]
	ths = tr.find_all('th')
	if not ths:
		ths = tr.find_all('b')

	for th in ths:
		col_header = clean_string(th.get_text())
		col_headers.append(col_header)

	return col_headers


def get_valid_states():
	state_list = []
	for state in api_handler.state_urls():
		for k in state.keys():
			state_list.append(k)
	return state_list   


def check_valid_state(state):
	if state in get_valid_states():
		return True
	return False


def check_valid_number(n):
	if not n:
		return True 
	try:
		n = int(n)
		return True   
	except:
		return False

	
def check_valid_date(date_str):
	try:
		datetime.strptime(date_str,'%m/%d/%Y')
	except ValueError:
		return False
	return True


def display_valid_states():
	valid_states = ''
	for state in get_valid_states():
		valid_states = valid_states + state + ', ' 
	valid_states = valid_states[:-2]
	print('Valid states are: ' + valid_states)


def parse_wsnumber(wsn_string):
	if not wsn_string:
		return None
	wsn_string = wsn_string.replace(' ','')
	wsn_list = wsn_string.split(',')
	return wsn_list


def get_function_name(href):
	i = get_index(href, 'javascript:')
	i2 = get_index(href, '(', 'backwards')
	return href[i:i2]


def get_function_definition(function_name, html):
	function = None
	soup = BeautifulSoup(html, 'lxml')
	js = soup.head.find_all('script')

	for j in js:
		if 'function view' in j.text:
			functions = re.split(r'function ', j.text, flags=re.DOTALL)

	for f in functions:
		if function_name in f:
			return f


def get_js_params(function_def):
	cnt = function_def.count('getElementById')
	param_dict = {}
	for i in range(0, cnt):
		idx =  get_index(function_def, 'getElementById("')
		function_def = function_def[idx:]
		idx = get_index(function_def, '"', 'backwards')       
		param_name = function_def[:idx]

		idx = get_index(function_def, param_name + '").value = ')
		idx2 = get_index(function_def, ';', 'backwards')
		param_dict[param_name] = function_def[idx:idx2]
	return param_dict


def get_js_action(function_def):
	i = get_index(function_def, 'action = "')
	i2 = get_index(function_def, '.jsp', 'backwards')
	return function_def[i:i2] + '.jsp'


def get_first_js_key(function_def):
	i = get_index(function_def, 'getElementById("')
	frag = function_def[i:]
	i2 = frag.find('"')
	return frag[:i2]


def get_js_param_order(function_def):
	i = get_index(function_def, '(')
	i2 = get_index(function_def, ')', 'backwards')
	param_str = function_def[i:i2]
	params = param_str.split(', ')
	return params


def get_js_param_values(href):
	i = get_index(href, '(')
	i2 = get_index(href, ')', 'backwards')
	return href[i:i2].split(', ')


def sort_payload_params(param_dict, param_values, param_order):
	new_param_dict = {}
	i = 0
	for p in param_order:
		for k, v in param_dict.items():
			if v == p:
				new_param_dict[k] = param_values[i].replace("'","")
		i += 1
	return new_param_dict


def build_payload_params(href, html):
	try:
		function_name = get_function_name(href) 
		function_def = get_function_definition(function_name, html)
		action = get_js_action(function_def)
		param_order = get_js_param_order(function_def)
		param_dict = get_js_params(function_def)
		param_values = get_js_param_values(href)
		params = sort_payload_params(param_dict, param_values, param_order)
		params['url'] = action
		return params
	except Exception as e:
		return None


def get_table_df(table, header=None):
	skiprows = None
	try:
		df = pd.read_html(StringIO(str(table)), header=header)[0]
	except (ValueError, IndexError):
		header = 0
		skiprows = 1
		df = pd.read_html(StringIO(str(table)), skiprows=skiprows, header=header)[0]
	converters = {i:str for i in range(len(df.columns))}
	df = pd.read_html(StringIO(str(table)), skiprows=skiprows, header=header, converters=converters)[0]
	return df


def get_datestamp_suffix():
	return '_' + datetime.today().strftime('%Y%m%d')


def get_timestamp_suffix():
	return '_' + datetime.today().strftime('%Y%m%d%H%M%S')


def is_ended(filename):
	if len(re.findall(r'\d{8}_\d{14}', filename)) > 0:
		return True 
	return False


def endtime_files(state,dzslug):
	endtime_suffix = get_timestamp_suffix()
	report_dir = constants.DATA_DIR.replace('XX', state)
	for full_path in glob.glob(report_dir + '**/*.tmp', recursive=True):
		file_name = ntpath.basename(full_path)
		if not is_ended(file_name):
			directory = ntpath.split(full_path)[0] + '/'
			new_file_name = file_name.replace('.tmp','') + endtime_suffix + '.csv'
			os.rename(full_path, directory + new_file_name)        


def handle_scrape_error(state, error, task_id=None):
	from factories.logger_factory import LoggerFactory
	print('Scraper encountered an error; please see the run log')
	if task_id:
		print('Task ID:' + str(task_id))
	endtime_files(state, get_datestamp_suffix())
	run_logger = LoggerFactory.build_logger(constants.RUN_LOG.replace('XX', state))
	run_logger.exception('Error attempting to scrape %s: %s', state, error)
	run_logger.info('Task ID: %s', task_id)
	exit()
	

def get_unique_sample_ids_from_url(table, token_state=False):
	sample_ids = []
	for tr in table.findAll('tr'):
		trs = tr.findAll('td')
		for each in trs:
			try:
				link = each.find('a')['href']
				if token_state:
					sample_id = get_js_param_value(link)
				else:
					sample_id = get_url_param_value(link, 'tsasampl_is_number')
				sample_ids.append(sample_id)
			except:
				pass
	return sample_ids


def get_report_counts(state):
	"""
	Used for development and debugging; not currently called by other scripts.
	Returns total number of WSNs for a state with a breakdown of how many WSNs 
	have been scraped for each report. 
	"""
	state = state.upper()
	constants.WSN_SAVE_LOCATION.replace('XX',state)
	wsn_file = constants.WSN_SAVE_LOCATION.replace('XX',state)
	try:
		df = pd.read_csv(wsn_file, delimiter=',')
	except FileNotFoundError:
		print('No data found for ' + state)
		exit()
	df.drop_duplicates(inplace=True)
	print(f'There are {df.shape[0]} WSNs in {state}')
	print('   ')
	report_file = constants.WSN_LOG.replace('XX',state)
	df = pd.read_csv(report_file, delimiter=',', usecols=[0,1], names=['WSN', 'Report'], converters={0: str.strip,1: str.strip})
	if len(df) == 0:
		print('No reports have been scraped yet for ' + state)
		exit()
	df.drop_duplicates(inplace=True)
	print(df.groupby('Report').count())    


def test_url(url):
	try:
		req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
		context = ssl._create_unverified_context()
		r = urlopen(req, context=context)
	except Exception as e:
		return e
	if 'gecsws' in r.geturl():
		return 'dwv'
	elif r.geturl() != url:
		return 'redirect'
	else:
		return 0


def get_new_url(url):
	req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
	context = ssl._create_unverified_context()
	r = urlopen(req, context=context)
	return r.geturl()


def get_nested_table_column_indexes(soup, header_index):
	nested_table_columns = []
	rows = soup.find_all('tr', recursive=False)
	if not rows:
		rows = soup.find_all('tr', recursive=True)
	i = -1
	try:
		for td in rows[header_index+1].find_all('td', recursive=False):
			i += 1
			try:
				if td.find('table'):
					nested_table_columns.append(i)              
			except:
				continue
	except:
		pass
	return nested_table_columns


def get_nested_table_column_headers(soup, header_index, nested_table_columns):
	column_headers = []
	rows = soup.find_all('tr', recursive=False)
	i = 0
	for td in rows[header_index].find_all(['td','th'], recursive=False):
		if i in nested_table_columns:
			nested_list = td.text.split('/')  # !!!this delimiter is specific to the Coliform sample report for Texas-like states
			for c in nested_list:
				column_headers.append(c)
		i += 1
	column_headers = [clean_string(x) for x in column_headers]
	return column_headers


def get_column_headers(soup, header_index, nested_table_columns=[]):
	column_headers = []
	rows = soup.find_all('tr', recursive=False)
	if not rows:
		rows = soup.find_all('tr', recursive=True)
	i = 0
	for td in rows[header_index].find_all(['td','th'], recursive=False):
		if i in nested_table_columns:
			nested_list = td.text.split('/')  # !!!this delimiter is specific to the Coliform sample report for Texas-like states
			for c in nested_list:
				column_headers.append(c)
		else:
			column_headers.append(td.text)    
		i += 1
	column_headers = [clean_string(x) for x in column_headers]
	return column_headers


def get_num_table_cells(soup):
	tds = soup.find('tr').find_all('td')
	return(len(tds))


def pretty_print_soup(soup, save_to_file=False):
	try:
		pretty = soup.prettify()
		print(pretty)
		with open('temp.html', 'w') as f:
			f.write(pretty)
	except:
		print('EMPTY SOUP')


def pretty_print_df(df):
	pd.set_option('display.max_columns', None)
	pd.set_option('display.max_rows', None)
	print(df)
	print(f'Dataframe contains {len(df)} rows.')


def find_report_tables(url):
	html = get_html(report_url)
	soup = BeautifulSoup(html, 'lxml') 
	table_index = -1 
	for table in soup.find_all('table'):
		table_index += 1
		print('table_index = ' + str(table_index))
		pretty_print_soup(table)
		print(test_table(table))
		print('-----------------------------------------------------------------------------------------------------------------------------------------------------')
