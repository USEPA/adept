import api_handler, constants, utils
from all_state_scraper import WebScraper

from bs4 import BeautifulSoup 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from urllib import error, parse, request
from urllib.request import urlopen, Request

from requests_html import HTMLSession



def get_recaptcha_token(html):
	soup = BeautifulSoup(html, features='lxml')
	iframe = soup.find('iframe')
	resp = urlopen(iframe['src'])
	soup2 = BeautifulSoup(resp, features='lxml')
	token = soup2.find('input', type='hidden')['value']
	return token

def main(state):
	s = WebScraper(state, num_wsns_to_scrape=1)

	s.session = HTMLSession()
	r = s.session.get(s.state_url)
	r.html.render(sleep=1)
	html = r.html.html
		
	rtoken = get_recaptcha_token(html)
	# print('recaptcha token = ' + rtoken)
	s.token = utils.get_token(html)
	# print('session token = ' + s.token)
	
	script = """document.querySelector("#public").m_bClicked=true; 
	            document.querySelector('#action').setAttribute('value','public');
	            FormSubmit(document.querySelector("#loginform"));
	           // document.querySelector("#loginform").submit();
	         """

	val = r.html.render(script=script)
	print(val)
	print(r.url)
	# print(r.html.html)

	script = 'document.querySelector("#loginform").submit();'
	val = r.html.render(script=script)
	print(val)
	print(r.url)
	exit()


	# url = 'https://dww.kdhe.ks.gov/DWW/Login?OWASP-CSRFTOKEN=' + s.token
	# url = 'https://dww.kdhe.ks.gov/DWW/KSindex.jsp'
	url = 'https://dww.kdhe.ks.gov/DWW/SearchDispatch.jsp'
	print('url = ' + url)
	data = {'OWASP-CSRFTOKEN': s.token, 'captcha': rtoken, 'action': 'public'}
	data = parse.urlencode(data).encode()
	r = s.session.post(url, data=data, allow_redirects=True)
	print(r.url)
	# print(r.html.html)



	# script = """
    #     () => {
    #     	document.querySelector('#action').setAttribute('value','public');
    #     	document.querySelector("#public").m_bClicked=true; 
    #         FormSubmit(document.querySelector("#loginform"));
    #         document.querySelector("#loginform").submit();
    #     }
    # """

	# val = r.html.render(script=script)
	# print(val)
	# # print(r.html.text)

	# url = s.state_url + 'Login?OWASP-CSRFTOKEN=' + s.token
	# print(url)
	# r = s.session.post(url)
	# print(r.html.text)

	# public = r.html.find('#public', first=True)





if __name__ == '__main__':       
	state = 'KS'
	main(state=state)