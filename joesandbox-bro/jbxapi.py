# Joe Sandbox API wrapper.
# REQUIRES: python-requests http://docs.python-requests.org/en/latest/

version = "2.0.0"

import sys
import time
import random
import getpass
import datetime

try:
	import requests
except ImportError:
	print "Error: Please install the Python 'requests' package via pip"
	sys.exit()

try:
	import simplejson as json
except ImportError:
	import json

# API URL.
API_URL  = "https://jbxcloud.joesecurity.org/api/"

# APIKEY, to generate goto user settings - API key
JOE_APIKEY = ""

# https://jbxcloud.joesecurity.org/resources/termsandconditions.pdf
# SET TO TRUE IF AGREE TO TERMS (settings in the web interface do not apply to this configuration)
JOE_TAC  = False


########################################################################################################################
class joe_api:
	"""
	Joe Sandbox API wrapper.
	@see: https://joesandbox.joesecurity.org/index.php/download/Joe%20Sandbox%20WEB%20API.pdf
	"""

	####################################################################################################################
	def __init__ (self, apikey, verify_ssl=True):
		"""
		Initialize the interface to Joe Sandbox API with apikey.
		"""

		self.apikey	   = apikey
		self.verify_ssl = verify_ssl


	####################################################################################################################
	def __API (self, api, params=None, files=None):
		"""
		Robustness wrapper. Tries up to 3 times to dance with the Joe Sandbox API.

		@type  api:		str
		@param api:		API to call.
		@type  params:	 dict
		@param params:	 Optional parameters for API.
		@type  files:	  dict
		@param files:	  Optional dictionary of files for multipart post.

		@rtype:  requests.response.
		@return: Response object.

		@raise Exception: If all attempts failed.
		"""

		# default query parameters.
		default_params = \
		{
			"apikey" : self.apikey
		}

		# interpolate default and supplied API params.
		if params is None:
			params = default_params
		else:
			params.update(default_params)

		# make up to three attempts to dance with the API, use a jittered exponential back-off delay
		for i in xrange(3):
			try:
				return requests.post(API_URL + api, data=params, files=files, verify=self.verify_ssl)

			# 0.4, 1.6, 6.4, 25.6, ...
			except:
				print sys.exc_info()
				time.sleep(random.uniform(0, 4 ** i * 100 / 1000.0))

		raise Exception("exceeded 3 attempts with Joe sandbox API.")


	####################################################################################################################
	def analyses (self):
		"""
		Retrieve a list of analyzed samples.

		@rtype:  list
		@return: List of objects referencing each analyzed file.
		
		Example:
		
		{  
		   "analyses":[  
			  {  
				 "webid":"257605",
				 "md5":"a362758c36bed10fb64823918ed90740",
				 "sha1":"b4bb387abd203338cf01c7bd0fe713fbeef5e381",
				 "sha256":"a1118b689effce96240a82d701c2aa8c2e718512c29edff30412cfa5e8b69c83",
				 "filename":"Delivery-Details.js",
				 "scriptname":"default.jbs",
				 "time":"1491813597",
				 "status":"finished",
				 "reportid":"250843",
				 "comments":" Sample was extracted from sample-248600-a362758c36bed10fb64823918ed90740.zip \/ archive\n",
				 "systems":"w7_1;",
				 "detections":"2;",
				 "tags":"",
				 "errors":";",
				 "runnames":";",
				 "yara":"false;",
				 "numberofruns":2,
				 "mostInterestingRun":0
			  },
			  {  
				 "webid":"257318",
				 "md5":"66f4f1384105ce7ee1636d34f2afb1c9",
				 "sha1":"3f23d152cc7badf728dfd60f6baa5c861a500630",
				 "sha256":"42fbb2437faf68bae5c5877bed4d257e14788ff81f670926e1d4bbe731e7981b",
				 "filename":"mydoc-66f4f1384105ce7ee1636d34f2afb1c9.doc",
				 "scriptname":"defaultwindowsofficecookbook.jbs",
				 "time":"1491738899",
				 "status":"finished",
				 "reportid":"250556",
				 "comments":"",
				 "systems":"w7_1;",
				 "detections":"2;",
				 "tags":"",
				 "errors":";",
				 "runnames":";",
				 "yara":"false;",
				 "numberofruns":2,
				 "mostInterestingRun":0
			  }
		   ]
		}
		
		detections: 2 = malicious, 1 = suspicious, 0 = clean
		
		"""

		# dance with the API.
		response = self.__API("analysis/list")

		return json.loads(response.content)


	####################################################################################################################
	def analyze (self, handle, url, systems="", inet=True, scae=False, dec=False, ssl=False, filter=False, hyper=False, cache_sha256=False, ais=False, vbainstr=False, officepw="", resubmit_dropped=False, comments="", sendoncomplete=False, exporttojbxview=False):
   
		"""
		Submit a file for analysis.

		@type  handle:			   File handle
		@param handle:			  Handle to file to upload for analysis.
		@type  url:				  str
		@param url:				 URL to analyze.
		@type  systems:			  str
		@param systems:			 Comma separated list of systems to run sample on.
		@type  inet:				 bool
		@param inet:				 Raise this flag to allow Internet connectivity for sample.
		@type  scae:				 bool
		@param scae:				 Raise this flag to enable Static Code Analysis Engine.
		@type  dec:				  bool
		@param dec:				  Raise this flag to enable Hybrid Decompilation @see https://www.joesecurity.org/joe-sandbox-dec.
		@type  ssl:				  bool
		@param ssl:				  Raise this flag to enable HTTPS inspection.
		@type  filter:			   bool
		@param filter:			   Raise this flag to enable Joe Sandbox Filter @see https://www.joesecurity.org/joe-sandbox-filter.
		@type  hyper:				bool
		@param hyper:				Raise this flag to enable Hyper Mode. Hyper Mode focus on speed versus deep analysis.
		@type exporttojbxview:	   bool
		@param exporttojbxview	   Raise the flag to enable export of analysis report(s) to Joe Sandbox View.
		@type  cache_sha256:		 bool
		@param cache_sha256:		 Raise this flag to check if an analysis with the same sample exists; if so do not re-analyze.
		@type  ais:				  bool
		@param ais:				  Raise this flag to enable Adaptive Internet Simulation @see https://www.joesecurity.org/joe-sandbox-ais. Only available in Joe Sandbox Cloud and Ultimate.
		@type  vbainstr:			 bool
		@param vbainstr:			 Raise this flag to enable VBA instrumentation.
		@type  officepw:			 string
		@param officepw:			 Sets a password for encrypted Microsoft Office documents.
		@type  resubmit_dropped:	 bool
		@param resubmit_dropped:	 Auto submit dropped non executed PE files.
		@type  comments:			 str
		@param comments:			 Comments to store with sample entry.
		@type  sendoncomplete:		 int
		@param sendoncomplete:		 Send an email on analysis complete.

		@rtype:  dict
		@return: Dictionary of system identifier and associated webids.
		
		Example:
		
		{
			"webid": 257770,
			"webids": [
				257770
			]
		}
		
		"""

		if inet:
			inet = "1"
		else:
			inet = "0"

		if scae:
			scae = "1"
		else:
			scae = "0"
			
		if dec:
			dec = "1"
		else:
			dec = "0"
			
		if ssl:
			ssl = "1"
		else:
			ssl = "0"
			
		if filter:
			filter = "1"
		else:
			filter = "0"
			
		if hyper:
			hyper = "1"
		else:
			hyper = "0"
			
		if exporttojbxview:
			export_to_jbxview = "1"
		else:
			export_to_jbxview = "0"
		
		if cache_sha256:
			cache_sha256 = "1"
		else:
			cache_sha256 = "0"
			
		if ais:
			ais = "1"
		else:
			ais = "0"
			
		if vbainstr:
			vbainstr = "1"
		else:
			vbainstr = "0"
			
		if resubmit_dropped:
			resubmit_dropped = "1"
		else:
			resubmit_dropped = "0"	
			
		if sendoncomplete:
			send_on_complete = "1"
		else:
			send_on_complete = "0"			

		if len(url) != 0:
			type = "url"
		else:
			type = "file"

		# Parameters.
		params = \
		{
			"tandc"	: "1",
			"inet"	 : inet,
			"scae"	 : scae,
			"dec"	  : dec,
			"ssl"	  : ssl,
			"filter"   : filter,
			"hyper"	: hyper,
			"export_to_jbxview": export_to_jbxview,
			"cache_sha256"	: cache_sha256,
			"ais"	  : ais,
			"vbainstr" : vbainstr,
			"officepw" : officepw,
			"resubmit_dropped" : resubmit_dropped,
			"send_on_complete" : send_on_complete,
			"type"		 : type,
			"comments" : comments
		}

		if type == "file":
			files  = { "sample" : handle }
		else:
			files  = {}
			params["url"] = url

		# keep a list of webids per system we send the sample to.
		webids = {}

		if len(systems) == 0:
			params["auto"] = "1"
		else:
		
			for system in systems.split(","):
					
				params[system] = "1"

		# ensure the handle is at offset 0.
		handle.seek(0)

		# set the system and dance with the API.
	
		response	   = self.__API("analysis", params, files)

		#print response

		return json.loads(response.content)


	####################################################################################################################
	def is_available (self):
		"""
		Determine if the Joe Sandbox API servers are alive or in maintenance mode.

		@rtype:  bool
		@return: True if service is available, False otherwise.
		"""

		# dance with the API.
		response = self.__API("server/available")

		try:
			if response.content == "1":
				return True
		except:
			pass

		return False
		
	####################################################################################################################
	def status (self, webid):
		"""
		Checks the status of an analysis.

		@rtype:  dict
		@return: Dictionary of analysis and status. Check for status:finished for finished analysis.
		
		Example:
		
		{  
		   "webid":"257605",
		   "md5":"a362758c36bed10fb64823918ed90740",
		   "sha1":"b4bb387abd203338cf01c7bd0fe713fbeef5e381",
		   "sha256":"a1118b689effce96240a82d701c2aa8c2e718512c29edff30412cfa5e8b69c83",
		   "filename":"Delivery-Details.js",
		   "scriptname":"default.jbs",
		   "time":"1491813597",
		   "status":"finished",
		   "reportid":"250843",
		   "comments":" Sample was extracted from sample-248600-a362758c36bed10fb64823918ed90740.zip \/ ar chive\n",
		   "systems":"w7_1;",
		   "detections":"2;",
		   "errors":";",
		   "runnames":";",
		   "yara":"false;"
		}
		
		detections: 2 = malicious, 1 = suspicious, 0 = clean
		
		"""

		# dance with the API.
		response = self.__API("analysis/check", {"webid" : webid})

		try:
			return json.loads(response.content)
		except:
			None

		return response.content
		
	####################################################################################################################
	def comment (self, webid):
		"""
		Get the comment of an analysis

		@rtype:  str
		@return: Comment
		
		"""

		# dance with the API.
		response = self.__API("analysis/comment", {"webid" : webid})

		return response.content


	####################################################################################################################
	def delete (self, webid):
		"""
		Delete the reports associated with the given webid.

		@type  webid: int
		@param webid: Report ID to delete.

		@rtype:  bool
		@return: True on success, False otherwise.
		"""

		# dance with the API.
		response = self.__API("analysis/delete", {"webid" : webid})

		try:
			if response.content == "1":
				return True
		except:
			pass

		return False


	####################################################################################################################
	def queue_size (self):
		"""
		Determine Joe sandbox queue length.

		@rtype:  int
		@return: Number of submissions in sandbox queue.
		"""

		# dance with the API.
		response = self.__API("queue/size")

		return int(response.content)


	####################################################################################################################
	def report (self, webid, resource="irjsonfixed", run=0):
		"""
		Retrieves the specified report for the analyzed item, referenced by webid. Available resource types include:
		html, xml, json, jsonfixed, lighthtml, lightxml, lightjson, lightjsonfixed, executive, classhtml, classxml, clusterxml, irxml, irjson, irjsonfixed, openioc, maec, misp, graphreports, pdf, openioc, bins (dropped files), unpackpe (unpacked pe files), unpack, ida, pcap, pcapslim, shoots, memstrings, binstrings, memdumps, sample, cookbook and yara.

		@type  webid:		int
		@param webid:		Report ID to draw from.
		@type  resource:	 str
		@param resource:	 Resource type.
		@type  run:			  int
		@param run:			  Index into list of supplied systems to retrieve report from.

		@rtype:  default = json otherwise byte stream
		@return: report data
		"""

		resource = resource.lower()
		params   = \
		{
			"webid" : webid,
			"type"  : resource,
			"run"   : run,
		}

		# dance with the API.
		response = self.__API("analysis/download", params)

		# if resource is JSON, convert to container and return the head reference "analysis".
		if resource.find("json") != -1:
			try:
				return json.loads(response.content)
			except:
				None

		# otherwise, return the raw content.
		return response.content


	####################################################################################################################
	def search (self, query):
		"""
		Searches for analysis.

		@type  query: str, can be an MD5, SHA1, SHA256, filename, cookbook name, comment, URL or report id.
		@param query: Search query.

		@rtype:  list
		@return: List of objects describing available analysis systems. For example see status API.
		
		"""

		# dance with the API.
		response = self.__API("analysis/search", {"q" : query })

		# returns a list, we assign it into a dictionary.
		content = '{"results":' + response.content + '}'

		# parse the JSON into a container and return the result list we just created above.
		return json.loads(content)["results"]


	####################################################################################################################
	def systems (self):
		"""
		Retrieve a list of available systems.

		@rtype:  list
		@return: List of objects describing available analysis systems.
		
		Example: w7,w7x64,W10,W10_Office2016
		
		"""

		# dance with the API.
		response = self.__API("server/systems")

		# returns a list, we assign it into a dictionary.
		content = '{"systems":' + response.content + '}'

		# parse the JSON into a container and return the systems list we just created above.
		return json.loads(content)["systems"]
		
	####################################################################################################################
	def submissionsmonth (self):
		"""
		Determine the remaining submissions available for the current month.

		@rtype:  int
		@return: Number of remaining submissions.
		"""

		# dance with the API.
		response = self.__API("remaininganalysesmonth")

		return int(response.content)
		
	####################################################################################################################
	def submissionsday (self):
		"""
		Determine the remaining submissions available for the current day.

		@rtype:  int
		@return: Number of remaining submissions.
		"""

		# dance with the API.
		response = self.__API("remaininganalysesday")

		return int(response.content)
		
	####################################################################################################################
	def account (self):
		"""
		Determine the account type

		@rtype:  str
		@return: Account type.
		"""

		# dance with the API.
		response = self.__API("account")

		return response.content
		


########################################################################################################################

def prettyprint(msg):
	print json.dumps(msg, indent=4, sort_keys=True)

if __name__ == "__main__":

	def USAGE ():
		msg = "%s: <analyses | analyze <filepath> | available | status <id> | delete <id> | queue | report <id> | search <term> | systems>"
		print "Joe Sandbox Web API implementation v" + version
		print msg % sys.argv[0]
		sys.exit(1)

	if len(sys.argv) == 2:
		cmd = sys.argv.pop().lower()
		arg = None

	elif len(sys.argv) == 3:
		arg = sys.argv.pop().lower()
		cmd = sys.argv.pop().lower()

	else:
		USAGE()

	if JOE_APIKEY:
		apikey = JOE_APIKEY
	else:
		apikey = getpass.getpass("Joe Sandbox APIKEY: ")

	if JOE_TAC:
		tac = "yes"
	else:
		tac = raw_input("Do you agree to the terms and conditions (yes/no)? ")
		
	if tac.lower() != "yes":
		sys.exit(1)
		
	# instantiate Joe Sandbox API interface.
	joe = joe_api(apikey)

	if "analyses" in cmd:
		for a in joe.analyses():
			i = 0
			for d in a["detections"].split(";"):
				if len(d) == 0: continue

				d = int(d)
				if d >= 2: d = "malicious"
				elif d >= 1: d = "suspicious"
				elif d <= -1: d = "unknown"
				else: d = "clean"
				
				# Time, WebID, status, system name, filename, detection
				
				print datetime.datetime.fromtimestamp(int(a["time"])).strftime('%Y-%m-%d %H:%M:%S'), a["webid"], a["status"], a["systems"].split(";")[i], a["filename"], d
				
				i += 1

	elif "analyze" in cmd:		
		if arg is None:
			USAGE()
		else:
			with open(arg, "rb") as handle:
				prettyprint(joe.analyze(handle, ""))

	elif "available" in cmd:
		print joe.is_available()

	elif "delete" in cmd:
		if arg is None:
			USAGE()
		else:
			print joe.delete(arg)
			
	elif "status" in cmd:
		if arg is None:
			USAGE()
		else:
			prettyprint(joe.status(arg))

	elif "queue" in cmd:
		print joe.queue_size()

	elif "report" in cmd:
		if arg is None:
			USAGE()
		else:
			prettyprint(joe.report(arg))

	elif "search" in cmd:
		if arg is None:
			USAGE()
		else:
			prettyprint(joe.search(arg))

	elif "system" in cmd:
		prettyprint(joe.systems())
	else:
		USAGE()