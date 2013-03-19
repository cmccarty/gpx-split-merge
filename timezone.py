# Uses the Google API to find timezone information based on lat/lon
# This is intended to find day splits (midnight) where ever you are in the world

# https://maps.googleapis.com/maps/api/timezone/json?location=37,-122&timestamp=1331161200&sensor=false

"""
Logic

If the timestamps between 2 tracks are close, and the avg speeds are the same, merge them.



"""


import urllib
import json

# ========================================== #


def get_timezone(lat, lon, timestamp):
	url = 'https://maps.googleapis.com/maps/api/timezone/json?location=%f,%f&timestamp=%s&sensor=false' % (lat, lon, timestamp)
	
	response = urllib.urlopen(url).read()
	json_obj = json.loads(response)
	return json_obj
	

# make some test calls
def test():
	lat = 37
	lon = -122
	timestamp = '1331161200'
	
	timezone = get_timezone(lat, lon, timestamp)
	print timezone
	

def main():
	test()
	
	
if __name__ == '__main__':
	main()