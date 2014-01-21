# This script adds a number of seconds to each of the points in a track, and creates a new track file


import gpxpy.parser as parser
import datetime

from optparse import OptionParser
from GpxMerger import *

import gpxpy
import gpxpy.gpx

# ========================================= #

"""
Goals:
	- Pull data directly from a garmin that I can plug into a computer, iphone, or ipad.
	- With that data, pull individual tracks out, and also create some "summary tracks" for each day (take timezones into account)
	- Optionally, geotag my photos (ideally the raw data, but also jpegs and potentially ones on Flickr as well)
		- specify a directory and gpx file, or have a large collection of all my geodata on the web (mongo) and pull from that to find the best possible position.
		
		
	Steps: 
		1) parse in GPX file, loop through points
		2) function to look for closest point given a time and list of points (interpolate=True/False), offset=#
"""

# ========================================= #


# converts meters per second to km per hour
def ms_to_kmh(mps):
	return mps / 1000 * 3600
	

# returns the average speed for a track
# Improvement: only calculate moving time within tracksegs
def get_avg_speed(track):
	# use mean
	first_point = track.segments[0].points[0]
	last_point = track.segments[-1].points[-1]
	seconds = (last_point.time - first_point.time).seconds
	meters = track.length_2d()
	speed = ms_to_kmh(meters / seconds)
	return speed 
	

# Merge tracks together, and save in the output file
def merge_tracks(tracks, output_file=None):
	gpx = mod_gpx.GPX()
	for t in tracks:
		gpx.tracks.append(t)
		
	xml = gpx.to_xml()
	
	# save output gpx file
	if output_file:
		f = open(output_file, 'w+')
		f.write(xml)
		f.close()
		print 'Wrote to file: %s' % output_file
	

# split out tracks and show stats to find breaks
def adjustTimestamps(inputPath, outputPath, seconds):
	print 'adjustTimestamps(%s, %s, %i)' % (inputPath, outputPath, seconds)
	
	# Splits a larger GPX file and merges tracks together by the same day.  Tries to account for timezones as well.
	print 'parsing %s...' % inputPath
	gpx = open(inputPath, 'r')
	gpx_parser = parser.GPXParser(gpx)
	gpx_parser.parse()
	gpx.close()

	# parse
	gpx = gpx_parser.get_gpx()
	print 'File parsed.'


	"""
	# save output gpx file
	if output_file:
		
	"""
	
	# loop through tracks
	for track in gpx.tracks:
		
		# loop through segments
		for segment in track.segments:
			
			# loop through points
			for point in segment.points:
				newTime = point.time + datetime.timedelta(0, seconds)
				#print '%s --> %s' % (point.time, newTime)
				
				point.time = newTime
		
	
	
	
	# save file
	xml = gpx.to_xml()
	f = open(outputPath, 'w+')
	f.write(xml)
	f.close()
	print 'Wrote to file: %s' % outputPath
	
	
# convert merged_names option input string to a list	
def separate_names(option, opt, value, parser):
	parser.values.merge_names = value.split(",")




	
# ========================================= #
def main(options=None):
	
	if options:
		inputFile = options.input_file
		outputFile = options.output_file
		numSeconds = options.seconds
	
		adjustTimestamps(inputFile, outputFile, numSeconds)
	

		
if __name__ == '__main__':
	# Last checked I needed to add -269 to sync up the minutes/seconds
	
	
	
	# Options from command line
	option_parser = OptionParser()
	option_parser.add_option("-i", "--input", dest="input_file", help="Input GPX file", type="string")
	option_parser.add_option("-o", "--output", dest="output_file", help="Merged output file", type="string")
	option_parser.add_option('-s', '--seconds', dest="seconds", help="Number of seconds to add (or remove)", type="int")
	(options, args) = option_parser.parse_args()
	
	main(options)
	
	
