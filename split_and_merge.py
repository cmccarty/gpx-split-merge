import gpxpy.parser as parser
from datetime import *
import os
import re

import gpxpy
import gpxpy.gpx

from optparse import OptionParser
from GpxMerger import *

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
	gpx = gpxpy.gpx.GPX()
	for t in tracks:
		gpx.tracks.append(t)
		
	xml = gpx.to_xml()
	
	# save output gpx file
	if output_file:
		
		directory = '/'.join(output_file.split('/')[0:-1])
		print directory
		if not os.path.exists(directory):
		    os.makedirs(directory)
		
		
		f = open(output_file, 'w+')
		f.write(xml)
		f.close()
		print 'Wrote to file: %s' % output_file
	

# split out tracks and show stats to find breaks
def split_and_merge_by_date(file_path, merge_names=None, merge_file=None):
	# Splits a larger GPX file and merges tracks together by the same day.  Tries to account for timezones as well.
	
	print file_path

	
	print 'parsing %s...' % file_path
	gpx = open(file_path, 'r')
	gpx_parser = parser.GPXParser(gpx)
	gpx_parser.parse()
	gpx.close()

	# parse
	gpx = gpx_parser.get_gpx()
	print 'File parsed.'
	
	track_names = [t.name for t in gpx.tracks]
	start_times = [t.segments[0].points[0].time for t in gpx.tracks]
	
	# time_format = '%Y-%m-%d %H-%i-%s'
	
	
	# loop through tracks
	for track in gpx.tracks:
		original_2d = track.length_2d()
		original_3d = track.length_3d()
		print '%s, %f, %f' % (track.name, original_2d, original_3d)
		
		# first point
		first_point = track.segments[0].points[0]
		last_point = track.segments[-1].points[-1]
		print '\t(%f, %f, ele=%d) @ %s' % (first_point.latitude, first_point.longitude, first_point.elevation, first_point.time)
		duration = last_point.time - first_point.time
		avg_speed = get_avg_speed(track)
		
		#datetime.strptime(last_point.time, format) - datetime.strptime(first_point.time, format)
		print '\t%s seconds, %s meters, speed=%f' % (duration, original_2d, avg_speed)
		print ''
		
		
	if merge_names and merge_file:	
		print 'Merge the tracks: %s to %s' % (str(merge_names), merge_file)	
		merge_tracks([t for t in gpx.tracks if t.name in merge_names], merge_file)
	
	
# convert merged_names option input string to a list	
def separate_names(option, opt, value, parser):

	# Value is a range, include all values between
	if re.search(':', value):
		(start, end) = value.split(':')
		names = [str(i) for i in range(int(start), int(end)+1)]
			
	# value is a list
	else:
		names = value.split(",")
		
	parser.values.merge_names = names


def debugMerge():
	print '[Debug] running Merger tests...'
	
	merger = GPXMerger()
	merger.debug = False
	
	print merger
	
	filePaths = []
	
	base_dir = '/Users/cmccarty/Documents/gps/2014-05-22 Grand Canyon'
	outfile_name = 'merged.gpx'
	
	file_names = ['Track-2014-05-23 11 23 00.gpx', 'Track-2014-05-23 21 47 24.gpx', 'Track-2014-05-26 08 53 03.gpx', 'Track-2014-05-26 08 53 34.gpx', 'Track-2014-05-28 09 38 12.gpx', 'Track-2014-05-29 21 51 59.gpx', 'Track-2014-06-01 13 30 09.gpx']
	
	#file_names = ['Track-2014-05-23 21 47 24.gpx']
	

	
	for f in file_names:
		path = '%s/%s' % (base_dir, f)
		print 'Adding %s...' % path
		filePaths.append(path)
	
	
	merger.addFilePaths(filePaths, True)
	print merger
	
	outfile = '%s/%s' % (base_dir, outfile_name)
	print 'Saving to %s...' % outfile
	merger.mergeTracksToFile(outfile)


	
# ========================================= #
def main(options=None):
	#debugMerge()
	#return
	
	if options:
		file_path = options.input_file
		merge_names = options.merge_names
		merge_file = options.output_file
	
		split_and_merge_by_date(file_path, merge_names, merge_file)
		
		
if __name__ == '__main__':
	# Options from command line
	option_parser = OptionParser()
	option_parser.add_option("-i", "--input", dest="input_file", help="Input GPX file", type="string")
	option_parser.add_option("-o", "--output", dest="output_file", help="Merged output file", type="string")
	option_parser.add_option('--names', dest="merge_names", help="list of names to merge (comma separated)", type="string", action="callback", callback=separate_names)
	(options, args) = option_parser.parse_args()
	
	main(options)
	
	
