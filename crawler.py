# -*- coding: utf-8 -*-
# filename: crawler.py
# Author: Indrajith Indraprastahm
# Lisence: GPL v3:  http://www.gnu.org/licenses/

#--------------------------------------------------------------------------------
# README
#--------------------------------------------------------------------------------
# Install Requirements
# pip install validators beautifulsoup4 lxml

# Python version: Python 3.6.3 :: Anaconda, Inc.



from bs4 import BeautifulSoup, SoupStrainer
import urllib.request
import traceback
import json
import re
import urllib.parse
import validators


class bcolors:          # for colord output, looks pretty.
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


class Spider:

	def __init__(self, root_url, max_links):
		self.root_url = root_url
		self.crawl_result = {} # a dictionary to store the crawl output as key, val pairs.
		self.crawl_set = set()
		self.MAX_CRAWL = max_links
		self.link_count = 0
		self.default_scheme = 'http://'
		self.scheme = self.default_scheme

	def fetch_url(self, url):
		"""
		Reads the content of a url, parse it using Beautifulsoup with lxml parser.
		"""
		try:
			fp = urllib.request.urlopen(url)
			data = fp.read()
		except Exception:
			print(bcolors.FAIL + "Unable to fetch url:" + bcolors.ENDC, url)
			#traceback.print_exc()
			return 
		
		soup = BeautifulSoup(data, 'lxml') #need to have lxml parser installed
		return soup

	def _isvalidurl(self, url):
		"""
		Returns True for a valid url, False for an invalid url.
		"""
		return bool(validators.url(url))

	def save_results(self):
		"""
		Saves results in to a json file
		"""
		with open('out.json','w') as fp:
			json.dump(self.crawl_result, fp, indent=4)

	def _pretty_link(self, url, base_url):
		"""
		Removes any query, params, tag-id reference in the urls. 
		Adds base_url to url if it is a relative link (link to the same domain).
		"""

		u_parse = urllib.parse.urlparse(url)
		base_url = base_url.rstrip('/')
		
		if u_parse.scheme != '':		# protocol in the link (http/https)
			self.scheme = u_parse.scheme

		if u_parse.scheme == u_parse.netloc == '':	# there is no protocol and is not a vaid domain
			if self._isvalidurl(self.default_scheme + u_parse.path): # check validity of the url after adding protocol
				return (self.default_scheme + u_parse.path)	

			if u_parse.path.startswith('/'):
				return base_url + u_parse.path
			else:
				return base_url + '/' + u_parse.path
		
		else:
			return self.scheme + '://' + u_parse.netloc + u_parse.path  # removes query ids params and fragments


	def _crawl(self, url):

		if not self._isvalidurl(url):	
			print(bcolors.FAIL + "Invalid url to crawl:" + bcolors.ENDC, url)
			return

		if url in self.crawl_result.keys():	#checks if the url is already crawled
			print(bcolors.WARNING + "URL already crawled:" + bcolors.ENDC, url )
			return 
		
		print(bcolors.OKGREEN + "Crawling:" + bcolors.ENDC, url)

		soup = self.fetch_url(url) 		

		if soup == None: # failed to fetch
			return 
		
		_links = soup.body.find_all('a') # finds all the links in the body ignores the head.

		self.crawl_result[url] = {}

		# self.crawl_result[url]['content'] = str(soup) # uncoment if we need to preserve the content
		self.crawl_result[url]['urls'] = []

		for link in _links:
			if 'href' not in link.attrs.keys():
				print(bcolors.FAIL + "No href in link:" + bcolors.ENDC, link)
				continue

			pretty_url = self._pretty_link(link['href'].lstrip(), url)

			if self._isvalidurl(pretty_url) != True:	#not a vaid url
				print(bcolors.FAIL + "Invalid url: " + bcolors.ENDC , pretty_url)
				continue

			if pretty_url in self.crawl_result[url]['urls']: # link already added
				continue 

			self.crawl_result[url]['urls'].append(pretty_url)
			self.crawl_set.add(pretty_url)
			print("Link found:", pretty_url)
		
		if self.link_count < self.MAX_CRAWL:
			self.link_count += 1 		#increment counter
			print("Links crawled: ", self.link_count)
		else:
			self.save_results()
			return

			
	def start(self):
		"""
		Start crawling from the root_url. Crawls upto MAX_CRAWL urls.
		After each crawl, urls found are added to the crawl_set, next url to crawl is taken 
		from this set.
		"""

		self._crawl(self.root_url)						# start crawing from the root_url
	
		while len(self.crawl_set):
			if self.link_count >= self.MAX_CRAWL:		#crawled MAX_CRAWL?
				self.save_results()						
				print(bcolors.BOLD + 'Exiting....' + bcolors.ENDC)
				break

			self._crawl(self.crawl_set.pop())			# poping url to crawl from the crawl_set
	

def main():
	root_url = 'http://python.org'	# url on which the crawl starts
	max_links = 5					# Maximum number of urls to crawl
	
	crawler = Spider(root_url, max_links)
	crawler.start()


		
if __name__ == '__main__':
	main()
