#!/usr/bin/python
# -*- coding: utf-8 -*-

"""script to automatically write our (unstructured) data to a new, structured format"""
# run in Python 3

##### IMPORTS #####

import re
from xlrd import open_workbook
from names_codings_profiles_NEW import search_coding_manual, search_coding_website, search_profile_manual, search_profile_website
from extract_names_NEW import extract_names, extract_names_whatsapp
from utts_names_to_dict_b import utts_names_to_dict # LH aangepast: underscore

##### REGEXES #####

# time references for the Facebook files:
time_ref_1 = re.compile(r'(\d{1,2}(-|\/|\.)\d{1,2}(-|\/|\.)\d{4} )?\d{1,2}:\d{2}')
time_ref_2 = re.compile(r'((\n)|(\r)|(\\n)|(\\r))\d{1,2} (januari|jan\.|februari|feb\.|maart|maa\.|april|apr\.|mei|mei\.|juni|jun\.|juli|jul\.|augustus|aug\.|september|sep\.|oktober|okt\.|november|nov\.|december|dec\.)( \d{4})?((\n)|(\r)|(\\n)|(\\r))')
time_ref_3 = re.compile(r'((\n)|(\r)|(\\n)|(\\r))(maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag|Vandaag)(( \d{1,2}:\d{2})|(\n)|(\r)|(\\n)|(\\r))')
time_ref_4 = re.compile(r'((\n)|(\r)|(\\n)|(\\r))\d{1,2} (uur|minuten|minuut|dag|dagen) geleden((\n)|(\r)|(\\n)|(\\r))')
time_ref_5 = re.compile(r'\d{1,2}\/\d{1,2}, \d{1,2}:\d{2}(?:am|pm|AM|PM)')

# time references for the WhatsApp files:
timeref_whatsapp = re.compile(r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4},? \d{1,2}\:\d{1,2}(?:\:\d{1,2})?(?:\: | - ))|(\[\d{1,2}\:\d{1,2} \d{1,2}\-\d{1,2}-\d{2,4}\] )')

linebreaks = re.compile(r'(\\r|\\n|\r|\n)+')

letters = re.compile(r'[a-zA-A]+')

# certain lines in the corpora are standard messages (not typed by the chatters) - we do not wish to include them
dont_include_facebook_regex = re.compile(r'((behaald|gescoord) met basketbal.)|((hebt|heeft) (de|je|zijn|haar)( eigen)? bijnaam)|(de ((afbeelding van het gesprek)|chatkleuren|gespreksfoto) gewijzigd.)|(de chatkleuren gewijzigd)|(de emoji ingesteld op)|(Verzonden via Messenger)|(Sent from Messenger)|(Gesprek begonnen)|(Schrijf een reactie)|(het gesprek een naam gegeven)|(een groepsgesprek gestart.)|((heeft|hebt) .+ (toegevoegd|gebeld|gemist).|((Gezien|Bekeken) door))')
#'Groepsgesprek beëindigd' nog toevoegen!
dont_include_whatsapp_regex = re.compile(r'(weggelaten>)|(het onderwerp gewijzigd naar)|(end-to-end encryptie)|(de groepsafbeelding gewijzigd)|((?:hebt|heeft)(?: de)? groep .+ gemaakt)|(heeft u toegevoegd)')

##### DATA INPUT #####

#we create a set with all names
all_names_csv = '/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/data_excels/AF_names.csv'
#all_names_csv = '/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/data_excels/names_af.csv'
all_names_lines = open(all_names_csv, encoding = 'latin-1').readlines()
all_names_list = [item.lower().strip() for item in all_names_lines]
all_names_set = set(all_names_list)


##### FACEBOOK TEXTS TO LIST #####

def facebook_2_list(name_raw_corpus):
	"""
	converts a txt Facebook corpus to a list of structured data

	input: 
		- 'name_raw_corpus': name of the txt Facebook corpus

	output:
		- list of utterances, along with the chatter, medium and year, same/mixed-sex conversation, private or group conversation
	"""

	# we open the corpus
	rawcorpus = open(name_raw_corpus,'rt', encoding = 'utf-8').read()
	
	# first, we replace all different kinds of time references by the same indicator
	# (as splitting on a regex pattern containing the OR operator raises problems)
	newcorp = time_ref_5.sub('XDATEX', rawcorpus)
	newcorp = time_ref_3.sub('XDATEX', newcorp)
	newcorp = time_ref_1.sub('XDATEX', newcorp)
	newcorp = time_ref_2.sub('XDATEX', newcorp)
	newcorp = time_ref_4.sub('XDATEX', newcorp)

	# we replace the different kinds of linebreaks by the same indicator
	newcorp = linebreaks.sub('XBREAKX', newcorp)

	# we split the corpus on the dates and store the result
	# result: groups of chat utterances and the chatters' names
	utts_names = newcorp.split('XDATEX')
	# we now split these text strings on the break indicators to get lists of names and utterances
	# we will store them in a new container
	groups_of_utts = []
	for string in utts_names:
		if string != '':
			groups_of_utts.append([item for item in string.split('XBREAKX') if item.strip() != '']) 


	### NAMES ###
	# we use our extract function to extract names from the text
	names_set = extract_names(name_raw_corpus)

	# we will store the utterances in a list
	structured_data = []

	### YEAR ###
	# example filename: "path/2012_Facebook_mixed_private_lisahilte.txt"
	# the year is the same for all utterances in the file, and can be extracted from the filename
	# the first 4 chars of the actual filename (without path) is the year
	parts_path = name_raw_corpus.split('/')
	name_without_path = parts_path[-1]

	parts_name = name_without_path.split('_')

	year = parts_name[0]				# this can be a year (e.g. 2016) or the string 'unknown'
	medium = parts_name[1]				# for the Facebook messages, this will always be 'Facebook'
	conversation_sexes = parts_name[2]	# this will be 'same', 'mixed' or 'unknown'
	conversation_size = parts_name[3]	# this will be 'private', 'group', or 'unknown'


	### UTTS
	for group in groups_of_utts:
		# for each group, we use our function utts_names_to_dict to create a dict with the names as keys and the utts as values
		structured_utts_names_dict = utts_names_to_dict(group,names_set)
		#print(structured_utts_names_dict)
		# if the dict is empty, this group of utts should be checked manually
		# this is sometimes the case for the first lines of a corpus file (where the chatter name in the beginning is missing)
		if not structured_utts_names_dict:
			for utt in group:
				if not utt.lower() in names_set: # LH probleem! 'ontvanger' zit hier niet bij in
					structured_utts_names_dict['unknown'].append(utt)
		# else, the dict is created in the right way

		# we now add all the necessary info to our list of structured data
		for ID in structured_utts_names_dict.keys():
			for utt in structured_utts_names_dict[ID]:
				# we only want to append actual utterances, and no standard Facebook messages
				if ((dont_include_facebook_regex.search(utt) == None) and (utt.lower() not in all_names_set)):
					structured_data.append([utt, ID, medium, year, conversation_sexes, conversation_size])
				elif utt.lower() in all_names_set:
					names_set.add(utt.lower())

	return(structured_data)



##### WHATSAPP TEXTS TO LIST #####

def whatsapp_2_list(name_raw_corpus):
	"""
	converts a txt WhatsApp corpus to a list of structured data

	input: 
		- 'name_raw_corpus': name of the txt WhatsApp corpus

	output:
		- list of utterances, along with the chatter, medium, year, conversation sexes and conversation size
	"""

	# we will store the utterances in a list
	utts_names_list = []

	# we open the corpus
	rawcorpus = open(name_raw_corpus,'rt', encoding = 'utf-8').read()

	# some metadata can be extracted from the filename
	# example of a filename: 'path/2015_WhatsApp_same_private_lisahilte.txt'
	parts_path = name_raw_corpus.split('/')
	name_without_path = parts_path[-1]
	parts_name = name_without_path.split('_')

	year = parts_name[0]				# this can be a year (e.g. 2016) or the string 'unknown'
	medium = parts_name[1]				# for the WhatsApp messages, this will always be 'WhatsApp'
	conversation_sexes = parts_name[2]	# this will be 'same', 'mixed' or 'unknown'
	conversation_size = parts_name[3]	# this will be 'private', 'group', or 'unknown'


	# in WhatsApp, every line contains one utterance (by one chatter)
	# we replace the different kinds of linebreaks by the same indicator
	# we split the text on newline chars, to look at each line separately
	newcorp = linebreaks.sub('XBREAKX', rawcorpus)
	lines = newcorp.split('XBREAKX')

	# we delete the time reference in every line
	for line in lines:
		# if the line just says that media were left out (or similar messages), we do not take it into account
		if dont_include_whatsapp_regex.search(line) == None:
			newline = ''
			if timeref_whatsapp.search(line):
				#print(line)
				# we delete the time ref
				newline = timeref_whatsapp.sub('',line)
				# the line now starts with the chatter's name, followed by a colon and the chat utterance
				# we split the line on colons
				parts_line = newline.split(':')
				ID = parts_line[0]
				utt = parts_line[1:]
				# if utt contains something (which is not the case for sentences like 'chatter X changed the emoticons')
				if utt:
					# then we replace the utterance by the string itself (no more list), without the first char, which is a space
					utt = utt[0][1:]
					# we also replace tabs and newlines by spaces, to avoid trouble later on
					utt = utt.replace('\t', ' ').replace('\n', ' ') ## LH toegevoegd
				else:
					print(parts_line)

				# we add the information to the list
				utts_names_list.append([utt, ID, medium, year, conversation_sexes, conversation_size])

	# we return this list
	return(utts_names_list)


##### EXCEL CORPUS TO LIST #####

def excel_2_list(name_raw_corpus):
	"""
	converts an Excel corpus to a list of structured data

	input: 
		- 'name_raw_corpus': name of the Excel corpus (format: .xlsx)

	output:
		- list of utterances, along with the chatter, medium, year, conversation sexes and conversation size
	"""

	# we will store the utterances in a list
	utts_names_list = []

	# we open the corpus
	workbook = open_workbook(name_raw_corpus)
	# we only have one worksheet in the file
	worksheet = workbook.sheet_by_index(0)

	# every row contains one utterance + its metadata
	offset = 0	# change to 1 not to include the header
	rows = []
	for i, row in enumerate(range(worksheet.nrows)):
		if i <= offset:  # (Optionally) skip headers
			continue
		r = []
		for j, col in enumerate(range(worksheet.ncols)):
			r.append(worksheet.cell_value(i, j))

		# we will need to slightly adjust some fields in r
		# we will save the adjusted fields to 'new_r'
		new_r = []
		for field in r:
			if type(field) == float:
				field = int(field)
			elif type(field) == str:
				field = field.replace('\n',' ')
				field = field.replace('\t',' ')
				field = field.strip() # LH toevoeging
			new_r.append(field)


		rows.append(new_r)

    # rows now includes all rows
    # each row is a list, containing multiple fields
    # order: utterance (position 0), chatter ID (pos 1), medium (pos 2), year (pos 3), conversation sexes (pos 4), conversation size (pos 5)

	# we return this list
	return(rows)




##### LISTS TO CSV #####

coding_regex = re.compile(r'^(website )?\d+$')

def write_corpus(list_of_chatlists,name_outputfile,manual_codings_csv,manual_profiles_csv,website_forms_csv):
	"""
	function to write a list of chat utterances + info to a txt file (format: tab delimited text)

	input:
		- 'list_of_chatlists': list of smaller lists, containing chat utterances + info
		- 'name_outputfile': a name for the outputfile
		- the csv datasheets containing (both manual and website) codings and profiles

	output:
		- a 'tab delimited text'-file containing the chat utterances + info
	"""

	with open(name_outputfile, "ab") as output: ## LH 'ab': append mode, + binary mode (not text mode: crashes!)

		for listy in list_of_chatlists:
			utterance = listy[0]
			ID = listy[1]
			medium = listy[2]
			year = listy[3]
			conversation_sexes = listy[4]
			conversation_size = listy[5]


			# if the type of the ID is a float, we change this to int
			if type(ID) == float:
				ID = int(ID)

			ID = str(ID)

			# we do the same for the year
			if type(year) == float:
				year = int(year)

			# we look up the chatter's profile
			# first we need to replace the ID by the coding, if it is still a name
			# however, the excel lists already contain the codings instead of names
			# we check this
			if coding_regex.match(ID):
				# in this case, the ID already is a coding
				coding = ID
				# we check if it is a manual or website coding
				if coding.startswith('website '):
					# we look up the profile among the website profiles (we exclude 'website ' from the coding)
					profile = search_profile_website(coding[8:],website_forms_csv)
				else:
					# else, we look up the profile among the manual profiles
					profile = search_profile_manual(coding,manual_profiles_csv)
			# else, the ID is not yet a coding but a name, and we have to look up the coding first before we can search for the profile
			else:
				# we first look in the website forms
				if search_coding_website(ID,website_forms_csv) != None:
					# if we find the name in the website forms, we can fill in the coding and the profile
					coding = search_coding_website(ID,website_forms_csv)
					profile = search_profile_website(coding,website_forms_csv)
				# if necessary, we continue by checking the manual files
				elif search_coding_manual(ID,manual_codings_csv) != None:
					# if we find the name in the manual files, we can fill in the coding and the profile
					coding = search_coding_manual(ID,manual_codings_csv)
					profile = search_profile_manual(coding,manual_profiles_csv)
				# else, we cannot find the coding nor the profile
				else: 
					coding = None
					profile = None


			# we also add the actual age of the chatters (i.e. at the time of the particular chat conversation)
			if (profile != None):
				if len(profile) != 0:
					if ((profile['Birth year'] != 'unknown') and (year != 'unknown')):
						profile['Actual age (at the time)'] = str(int(year)-int(profile['Birth year']))
					else:
						profile['Actual age (at the time)'] = 'unknown'


			# if we have found a coding and profile, we can write this info to a txt file
			# we print a message if the coding cannot be found or if the profile is empty
			if ((coding == None) or (profile == None) or (len(profile) == 0)):
				listy_ = [str(element).encode('utf-8') for element in listy]
				print('coding not found OR empty profile for: '+str(listy_))

				# we write these utterances to the corpus, but all metadata are unknown
				# we start by writing a new line
				output.write('\n'.encode('utf-8'))
				# we first write the utterance info: utterance, coding, medium, year, conversation sexes and conversation size
				output.write(utterance.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write(medium.encode('utf-8')+'\t'.encode('utf-8'))
				output.write((str(year)).encode('utf-8')+'\t'.encode('utf-8'))
				output.write(conversation_sexes.encode('utf-8')+'\t'.encode('utf-8'))
				output.write(conversation_size.encode('utf-8')+'\t'.encode('utf-8'))
				# then we add the profile info
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\t'.encode('utf-8'))
				output.write('unknown'.encode('utf-8')+'\n'.encode('utf-8'))


			else:
				# we start by writing a new line
				output.write('\n'.encode('utf-8'))
				# we first write the utterance info: utterance, coding, medium, year, conversation sexes and conversation size
				output.write(str(utterance).encode('utf-8')+'\t'.encode('utf-8'))
				output.write(coding.encode('utf-8')+'\t'.encode('utf-8'))
				output.write(medium.encode('utf-8')+'\t'.encode('utf-8'))
				output.write((str(year)).encode('utf-8')+'\t'.encode('utf-8'))
				output.write(conversation_sexes.encode('utf-8')+'\t'.encode('utf-8'))
				output.write(conversation_size.encode('utf-8')+'\t'.encode('utf-8'))
				# then we add the profile info
				output.write(profile['Gender'].encode('utf-8')+'\t'.encode('utf-8'))
				output.write(profile['Actual age (at the time)'].encode('utf-8')+'\t'.encode('utf-8'))
				output.write(profile['Region'].encode('utf-8')+'\t'.encode('utf-8'))
				output.write(profile['Education'].encode('utf-8')+'\t'.encode('utf-8'))
				output.write(profile['Home languages'].encode('utf-8')+'\t'.encode('utf-8'))
				output.write(profile['Profession parents'].encode('utf-8')+'\t'.encode('utf-8'))
				output.write(profile['Social class parents'].encode('utf-8')+'\t'.encode('utf-8'))
				output.write(profile['Consent'].encode('utf-8')+'\t'.encode('utf-8'))
				output.write(profile['Consent parents'].encode('utf-8')+'\t'.encode('utf-8'))
				output.write(profile['School'].encode('utf-8')+'\t'.encode('utf-8'))
				output.write(profile['In gesprek'].encode('utf-8')+'\n'.encode('utf-8'))

		output.close()

	return(None)