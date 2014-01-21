"""
Class to work with GPX files that have some overlap, to create a single GPX file with all the merged track (and waypoint data).

The goal is to merge many files that I dump while traveling and pull the data using LoadMyTracks.  There is often overlap since it pulls everything currently on the device, and I want an easy way to create a single file from it all.
"""

# ================================================= #
# Imports
import gpxpy.parser as parser
import gpxpy
import gpxpy.gpx
#from gpxpy import mod_gpx

# ================================================= #

class GPXMerger:
	gpxFilePaths = None
	gpxData = None
	debug = None
	
	
	
	# Constructor
	def __init__(self):
		self.gpxFilePaths = []
		self.gpxData = {}
	

	# print out representation
	def __str__(self):
		s = '[GPXMerger class]\n'
		s += 'Found %s files added:\n' % len(self.gpxFilePaths)
	
		for filePath in self.gpxFilePaths:
			s += '\t%s' % filePath
			
			# if the file has been parsed already, print the number of tracks
			if self.gpxData.get(filePath):
				s += ' (%d tracks)' % len(self.gpxData[filePath].tracks)
			
			
			s += '\n'
		
		return s
		
	
	# add a file path to merge
	def addFilePath(self, filePath, pullData=False):
		if not filePath: return None
		if self.debug: print 'Adding file: %s' % filePath
		
		if pullData:
			self.pullGPXData(filePath)
		else:
			self.gpxFilePaths.append(filePath)
		
	# add a list of file paths to merge
	def addFilePaths(self, filePaths, pullData=False):
		for filePath in filePaths:
			self.addFilePath(filePath, pullData)	
		
		
		
	def getGpxForFile(self, filePath):
		gpx = open(filePath, 'r')
		gpx_parser = parser.GPXParser(gpx)
		gpx_parser.parse()
		gpx.close()

		# parse
		gpx = gpx_parser.get_gpx()
		return gpx
			
		
	# read the file and set the gpx object in the dictionary
	def pullGPXData(self, filePath):
		if self.debug: print 'Pulling Data for %s' % filePath
		# add the file path if not already in the list
		if filePath not in self.gpxFilePaths:
			self.gpxFilePaths.append(filePath)
			#self.addFilePath(filePath)
			
		# parse the file, pull the data
		gpx = self.getGpxForFile(filePath)
		
		# set data in dictionary for quick lookup
		self.gpxData[filePath] = gpx
		
	
	# megers the tracks from all gpx files added
	def getMergedTracks(self):
		
		# very basic approach for now, just look at the track names.
		# Future: hash track
		mergedTracks = []
		mergedTrackKeys = []
		for filePath in self.gpxData:
			
			# add all tracks for this file
			for track in self.gpxData[filePath].tracks:
				key = track.name
				if key not in mergedTrackKeys: # no need to add if already there
					mergedTracks.append(track)
					mergedTrackKeys.append(key)
					
		
		if self.debug: print 'Total unique tracks: %d' % len(mergedTracks)
		return mergedTracks


	# sort the tracks based on the start time. This is a naive implementation, it can probably be done with a better comparison function but I'm on an airplane and don't have access to any documentation so I'm just hacking it together.
	def sortTracksByTime(self, tracks):
		sortedTracks = []
		
		# create list of track dictionaries w/ start point
		for track in tracks:
			firstTrkpt = track.segments[0].points[0]
			startTime = firstTrkpt.time
			
			sortedTracks.append({'startTime': startTime, 'track':track})
			
	
		# sort based on start time
		sortedTracks = sorted(sortedTracks, key=lambda k: k['startTime']) 
		
		# pull the tracks back out
		sortedTracks = [track['track'] for track in sortedTracks]
		
			
		return sortedTracks
	
	# merge tracks
	def mergeTracksToFile(self, outputFile):
		if not outputFile: 
			print 'No output file set'
			return False
			
		# create a merged file
		
		
		# save the file
		gpx = mod_gpx.GPX()
		tracks = self.getMergedTracks()
		tracks = self.sortTracksByTime(tracks)
		
		for t in tracks:
			gpx.tracks.append(t)

		xml = gpx.to_xml()

		# save output gpx file
		
		f = open(outputFile, 'w+')
		f.write(xml)
		f.close()
		print 'Merged GPX file saved at: %s' % outputFile	
		
		
	def addFilesInDirectory(self, dir):
		return
		