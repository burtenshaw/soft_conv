""" script to automatically extract names from chat data
(in order to ask for these chatters' profiles, to anonimize them)"""

##### IMPORTS #####

import re


##### REGEXES #####

# regular expressions we will use:
time_ref_1 = re.compile(r'(\d{1,2}(-|\/)\d{1,2}(-|\/)\d{4} )?\d{1,2}:\d{2}')
#time_ref_1a = re.compile(r'(\d{1,2}(-|\/)\d{1,2}((-|\/)\d{4})?)? ?(\d{1,2}:\d{2})') # hour obligatory
#time_ref_1b = re.compile(r'(\d{1,2}(-|\/)\d{1,2}((-|\/)\d{4})?) ?(\d{1,2}:\d{2})?') # date obligatory

# LH probleem met combi 1a en 1b: te ruim! in volgende zin wordt bvb op datum gesplitst: '27-28 moet ik werken'

time_ref_2 = re.compile(r'((\n)|(\r)|(\\n)|(\\r))\d{1,2} (januari|jan\.|februari|feb\.|maart|maa\.|april|apr\.|mei|mei\.|juni|jun\.|juli|jul\.|augustus|aug\.|september|sep\.|oktober|okt\.|november|nov\.|december|dec\.)( \d{4})?((\n)|(\r)|(\\n)|(\\r))')
time_ref_3 = re.compile(r'((\n)|(\r)|(\\n)|(\\r))(maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag|Vandaag)(( \d{1,2}:\d{2})|(\n)|(\r)|(\\n)|(\\r))')
time_ref_4 = re.compile(r'((\n)|(\r)|(\\n)|(\\r))\d{1,2} (uur|minuten|minuut|dag|dagen) geleden((\n)|(\r)|(\\n)|(\\r))')
time_ref_5 = re.compile(r'\d{1,2}\/\d{1,2}, \d{1,2}:\d{2}(?:am|pm|AM|PM)')

linebreaks = re.compile(r'(\\r|\\n|\r|\n)+')

letters = re.compile(r'[a-zA-A]+')


##### NAME EXTRACTION FROM EXCELS #####

def names_from_excels(excel_manually,excel_website):
	"""
	function that extracts the participants' names from our EXCELS

	input:
		- 'excel_manually': a csv file containing the manually typed profiles
		- 'excel_website': a csv file containing the profiles filled in in the website

	output:
		- a list of full names (first + last name) of which we have the corresponding profiles
	"""

	# we open the files
	ex_man = open(excel_manually,'rt', encoding = 'latin-1').read()
	ex_web = open(excel_website, 'rt', encoding = 'latin-1').read()

	# we create a container to store the names
	names = set()

	# we extract the names from the manually typed file
	lines_man = ex_man.split('\n')

	for line in lines_man:
		fields = line.split(';')
		name = fields[1]
		names.add(name.lower())

	# we extract the names from the website file
	lines_web = ex_web.split('\n')
	for line in lines_web:
		fields = line.split(';') 
		first_name = fields[9]
		last_name = fields[10]

		# we concatenate first and last name
		full_name = first_name + ' ' + last_name

		names.add(full_name.lower())

	# we return these names
	return(names)



##### NAME EXTRACTION FUNCTION: FACEBOOK #####

def extract_names(name_raw_corpus,only_without_profile=False):
	"""
	function that will extract the chatters' names from a corpus, 
	and can filter out the ones for which no profile is yet provided

	input: 
		- 'name_raw_corpus': name of the txt Facebook corpus
		- 'only_without_profile': a boolean variable (default: False) to choose whether or not to only print the names for which no profile is yet provided

	output:
		- list of the chatters' names
	"""

	rawcorpus = open(name_raw_corpus,'rt', encoding = 'utf-8').read()
	
	# first, we replace all different kinds of time references by the same indicator
	# (as splitting on a regex pattern containing the OR operator raises problems)
	newcorp = time_ref_5.sub('XDATEX', rawcorpus)
	#newcorp = time_ref_1b.sub('XDATEX', rawcorpus)
	newcorp = time_ref_3.sub('XDATEX', newcorp)
	newcorp = time_ref_1.sub('XDATEX', newcorp)
	newcorp = time_ref_2.sub('XDATEX', newcorp)
	newcorp = time_ref_4.sub('XDATEX', newcorp)

	# we replace the different kinds of linebreaks by the same indicator
	newcorp = linebreaks.sub('XBREAKX', newcorp)

	# we split the corpus on the dates and store the result
	# result: groups of chat utterances and the chatters' names
	utts_names = newcorp.split('XDATEX')

	# we create a container to store the chatters' names
	names = []

	# we loop over these groups of utterances and names
	for item in utts_names:

		# we split this text group on the line breaks
		# we store the separate elements, except if it is an empty element or does not contain text
		itemlist = [element for element in item.split('XBREAKX') if (element and letters.search(element))]

		# the first element in this list is the name of the chatter, except if the list is empty
		if len(itemlist) != 0:
			name = itemlist[0]
			# we add this name to our set
			names.append(name.lower())

	# if asked, we select only the names for which no profile is provided yet
	if only_without_profile == True:
		with_profile = names_from_excels(excel_manually,excel_website)
		#with_profile2 = names_from_excels(excel_manually,excel_website2)

		for name in names[:]:
			if (name in with_profile): #or (name in with_profile2):
				names.remove(name)

	# we turn the name list into a set (to remove doubles)
	names_set = set(names)
	print(len(names_set))

	# we return the names
	return(names_set)


##### NAME EXTRACTION FUNCTION: WHATSAPP #####

def extract_names_whatsapp(name_raw_corpus,only_without_profile=False):
	"""
	function that will extract the chatters' names from a whatsapp corpus, 
	and can filter out the ones for which no profile is yet provided

	input: 
		- 'name_raw_corpus': name of the txt WhatsApp corpus
		- 'only_without_profile': a boolean variable (default: False) to choose whether or not to only print the names for which no profile is yet provided

	output:
		- list of the chatters' names
	"""
	# we open the corpus
	rawcorpus = open(name_raw_corpus,'rt').read()

	# we create a container to store the chatters' names
	names = []
	
	# we split the text on newline chars, to look at each line separately
	lines = rawcorpus.split('\n')

#24/07/15, 23:15 - Robbe C: Yuu

	# we define the format for WhatsApp time references
	#timeref_whatsapp = re.compile(r'\d{1,2}\/\d{1,2}\/\d{2} \d{1,2}\:\d{1,2}\:\d{1,2}\: ')
	timeref_whatsapp = re.compile(r'\d{1,2}\/\d{1,2}\/\d{2},? \d{1,2}\:\d{1,2}(?:\:\d{1,2})?(?:\: | - )')
	# we delete this ref per line
	for line in lines:
		newline = ''
		if timeref_whatsapp.search(line):
			# we delete the time ref
			newline = timeref_whatsapp.sub('',line)
			# the line now starts with the chatter's name, followed by a colon and the chat utterance
			# we split the line on colons
			parts_line = newline.split(':')
			name = parts_line[0]
			# we add the name to the list
			names.append(name.lower())

	# if asked, we select only the names for which no profile is provided yet
	if only_without_profile == True:
		with_profile = names_from_excels(excel_manually,excel_website)
		#with_profile2 = names_from_excels(excel_manually,excel_website2)

		for name in names[:]:
			if (name in with_profile): #or (name in with_profile2):
				names.remove(name)

	# we turn the name list into a set (to remove doubles)
	names_set = set(names)
	print(len(names_set))

	# we return the names
	return(names_set)


##### TEST #####

# IMPORTANT! always adapt excels to latest files!
excel_manually = '/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/data_excels/2.1_profielcoderingen.csv'
excel_website = '/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/data_excels/2.3_chatmateriaal_website__.csv'


#corp = '/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/sint_jozef_kontich_2/2016_Facebook_rhinojanssens.txt'
#2016_WhatsApp_martaszabelska.txt'
#corp = '/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/2016_Facebook_testsetmetemoji.txt'

#print(extract_names(corp,only_without_profile=False))
#print(extract_names_whatsapp(corp,only_without_profile=True))

