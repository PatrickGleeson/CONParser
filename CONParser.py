# CONParser.py
# Python module to import Crooked Object Notation files 

from collections import *

class CONParser:
	
	def __init__(self):
		
	
	def getLines(self, fileName):
		try:
			theFile = open(fileName, 'r+')
		lines = theFile.read().splitlines() # read the whole thing in, then split it up per line (because readlines() keeps the \n on the end of the line, yes really)
		theFile.close()
		return lines


	# preception() is a recursive algoritm to load in the structure
	# the structure consists of nested OrderedDict objects where each key is '+' or '-' then the name of object type then (if needed) a "defaultKey"  
	# a + indicates that the object will require another recursion
	# a - indicates that the object will not require another recursion (and instead be loaded from one line)
	# the defaultKey distinguishes between two keys that would otherwise be identical AND is used as the a key for that element if the data section doesn't provide it's own key
	def preception(self, fileLines, currentLevel):
		
		currentTabs = '\t' * currentLevel

		result = OrderedDict()
		while fileLines[0].startswith(currentTabs+'+') or fileLines[0].startswith(currentTabs+'-'):
			key=fileLines[0][currentLevel:]
			fileLines.pop(0)
			result[key] = self.preception(fileLines,currentLevel+1)
		
		return result
	
	def inception(self, fileLines, currentLevel, structure, currentBranch):
		currentTabs = "\t"*currentLevel

		# Create an object with the information provided by the currentBranch element in the top level of the structure
		
		# Annoyingly, keys() returns an object that can't be indexed so cast it as a list first
		# Then take the currentBranch element of that list
		# Save it as branchKey
		branchKey = list(structure.keys())[currentBranch]

		# THEN split branchKey by tabs at most 2 times (results in a list of at most 3 pieces)
		# Zip that list with a list of named keys and cast it as a dictionary
		# Save that dictionary as branch
		branch = dict(zip(['recurse', 'type', 'defaultKey'], branchKey.split('\t', 2)))

		# Then create the type of object specified
		# exec() is used despite its SEVERE security issues as nothing else is feasible (afaik)
		result = eval(branch['type'] + "()")


		# The while loop below will populate this object
		
		# Since we can't tamper with the structure as it's passed by reference, create a quick int to store the number of the leaf being worked on
		leaf = 0

		# While there are still branches on this level to process and the indentation is correct and there's still lines left
		while leaf+1 <= len(structure[branchKey]) and fileLines and fileLines[0].startswith(currentTabs):
			# Only the 0th branch of the 0th element is dealt with in each iteration of the while loop
			# Check if it's populated here or if WE NEED TO GO DEEPER
			# To do this *deep breath*
			# Get the keys of the 0th element
			# Cast them as a list
			# Take the leaf-th element of that list (which is a string)
			# Split it by tabs into at most 2 times (results in a list of at most 3 pieces)
			# Zip that list with a list of named keys and cast it as a dictionary
			# Save that dictionary as peek
			peek = dict(zip(['recurse', 'type', 'defaultKey'], list(structure[branchKey].keys())[leaf].split('\t', 2)))
			value = fileLines[0][currentLevel:]
			
			# Check if peek is supposed to be loaded recursively
			if peek['recurse'] == '+' :
				#WE NEED TO GO DEEPER
				fileLines.pop(0)
				if isinstance(result, MutableMapping):
					# Then the value is the key for the rest of it
					result[value] = self.inception(fileLines, currentLevel+1, structure[branchKey], leaf)
				else:
					# Then the value is irrelevant and vanishes into the ether
					result.append(self.inception(fileLines, currentLevel+1, structure[branchKey], leaf))
			else: # It's a single value object i.e. string, int, etc.
				#Floating around on the ceiling
				if isinstance(result, MutableMapping):
					# Split based on tab character, but at most one split (therefore tabs in the data won't mess things up)
					value = value.split('\t', 1)
					if len(value) > 1:
						exec("result[value[0]] = " + peek['type'] + "(value[1])")
					else: #Use the default key
						exec("result[peek['defaultKey']] = " + peek['type'] + "(value[0])")

				else:
					exec("result.append(" + peek['type'] + "(value))")
				fileLines.pop(0)
			
			# If there's other elements on the top level, then the 0th element gets removed and the next iteration works with the following element
			# Otherwise, just keep using the same element
			if leaf+1 < len(structure[branchKey]): # If this isn't the last branch
				leaf = leaf+1
		# end while
		# Riding the skip
		return result

	#getComplex(): gets a complex structure from a file
		# file is structured with tabs, 0 tabs for 0th level keys, 1 tab for 1st level keys, etc.
		# the last level will have the appropriate number of tabs, and if keyed, the key & the value will be separated with a tab

	def getComplex(self, filePath):
		fileLines = self.getLines(filePath)
		# Load up the file structure from the file
		structure = self.preception(fileLines, 0)
		return self.inception(fileLines, 0, structure, 0)


	def writeComplex(self, filePath, data):
		# First read in the structure
		originalLines = self.getLines(filePath)
		remainingLines = self.getLines(filePath) # Gotta be some way to copy originalLines
		structure = self.preception(remainingLines, 0)
		
		# Then write the structure anew
		outFile = open(filePath, "w")
		for i in range(0, len(originalLines)-len(remainingLines)):
			outFile.write(originalLines[i]+'\n')
		
		# We need to go deeper
		tempKey = list(structure.keys())[0]
		self.outception(outFile, data, structure[tempKey], 0, 0, 0)
		
		# And close the file
		outFile.close()
		
	def outception(self, outFile, data, structure, currentLevel, currentDataBranch, currentStructureBranch):
		
		currentTabs = "\t"*currentLevel
		
		while currentDataBranch < len(data):
			if isinstance(data, MutableMapping):
				dataBranchKey = list(data.keys())[currentDataBranch]
			else:
				dataBranchKey = currentDataBranch
			structureBranchKey = list(structure.keys())[currentStructureBranch]
			structureBranch =  dict(zip(['recurse', 'type', 'defaultKey'], structureBranchKey.split('\t', 2)))
			
			print("structure branch: " + str(structureBranch))
			print("data branch key: " + str(dataBranchKey))
			
			if structureBranch['recurse'] == '+':
				outFile.write(currentTabs + str(dataBranchKey) + '\n')
				self.outception(outFile, data[dataBranchKey], structure[structureBranchKey], currentLevel+1, 0, 0)
			else:
				if isinstance(data, MutableMapping):
					outFile.write(currentTabs + str(dataBranchKey) + '\t'+ data[dataBranchKey] + '\n')
				else:
					outFile.write(currentTabs + data[dataBranchKey] + '\n')
			
			currentDataBranch+=1
			if currentStructureBranch+1 < len(structure):
				currentStructureBranch = currentStructureBranch + 1
		
