#!/usr/bin/python
# -*- coding: utf-8 -*-

"""script to automatically read in names, codings and profiles from the manually created excel and the website excel"""


##### SEARCH NAME IN MANUAL CODINGS #####
def search_coding_manual(name,manual_codings_csv):
	"""
	function to search the correct manual coding for a name

	input: 
	- name: a text string containing the chatter's name
	- manual_codings_csv: a csv-file containing manual codings, i.e. the participants' names and unique IDs

	output: 
	- the name's corresponding coding
	"""

	# per default, we say the ID is not found. if it is found later on, we change this
	ID = None

	# we open the manual codings file
	codings_file = open(manual_codings_csv,'rt', encoding = 'latin-1').read()

	# we split the data on newline characters to split the profile information per person
	codings_names = codings_file.split("\n")

	# we look for the correct coding
	for item in codings_names:
		fields = item.split(';')
		if len(fields)>1:
			# if the line contains more than one field, it holds an ID and a name
			field_ID = fields[0]
			field_name = fields[1]
			# we search for the name in the coding file
			if name.lower() == field_name.lower():
				# we do not take whitespace into account for the ID
				if (field_ID[0] == '\n') or (field_ID[0] == '\r'):
					field_ID = field_ID[1:]
				ID = field_ID
				break
	# we return the correct ID for the name
	return(ID)



##### SEARCH NAME IN WEBSITE CODINGS #####
def search_coding_website(name,website_forms_csv):
	"""
	function to search the correct coding for a name

	input: 
	- name: a text string containing the chatter's name
	- website_forms_csv: a csv-file containing the website forms

	output: 
	- the name's corresponding coding
	"""

	# per default, we say the ID is not found. if it is found later on, we change this
	ID = None

	# we open the manual codings file
	codings_file = open(website_forms_csv,'rt', encoding = 'latin-1').read()

	# we split the data on newline characters to split the profile information per person
	codings_names = codings_file.split("\n")

	# we look for the correct coding
	for item in codings_names:
		fields = item.split(';')
		# if the length of the line is valid, the fields contain the necessary info
		if len(fields)>=23:
			field_ID = fields[0]
			field_first_name = fields[9]
			field_last_name = fields[10]
			field_name = str(field_first_name)+' '+str(field_last_name)
			# we search for the name
			if name.lower() == field_name.lower():
				# we strip away whitespace for the ID
				if (field_ID[0] == '\n') or (field_ID[0] == '\r'):
					field_ID = field_ID[1:]
				ID = 'website '+str(field_ID)
				break

	return(ID)


##### SEARCH PROFILE IN MANUAL EXCEL #####
def search_profile_manual(coding,profiles_manual_csv):
	"""
	function to search the correct profile for a coding

	input: 
	- coding: a text string containing the chatter's coding
	- profiles_manual_csv: a csv-file containing the manual profiles

	output: 
	- a dict containing the coding's corresponding profile
	"""

	# we open the csv-file
	profiles_file = open(profiles_manual_csv,'rt').read()

	# we split the data on newline characters to split the profile information per person
	profiles = profiles_file.split("\n")

	# we fill a dictionary with the relevant information
	profile_dic = {}

	# we look for the correct profile
	for profile in profiles:
		# we split each person's profile information per field
		fields = profile.split(';')
		# we look for the correct unique coding
		field_ID = fields[0]
		# we strip away whitespace in the ID
		if (field_ID[0] == '\n') or (field_ID[0] == '\r'):
			field_ID = field_ID[1:]
		if str(field_ID) == str(coding):
			# if we found the correct profile, we fill in the dictionary
			profile_dic['Gender'] = fields[1]
			profile_dic['Age info'] = fields[2]
			profile_dic['Region'] = fields[3]
			profile_dic['Education'] = fields[4]
			profile_dic['Home languages'] = fields[5]
			profile_dic['Profession parents'] = fields[6]
			profile_dic['Social class parents'] = fields[7]
			profile_dic['Consent'] = fields[8]
			profile_dic['Consent parents'] = fields[9]
			profile_dic['School'] = fields[10]
			profile_dic['In gesprek'] = fields[11]


			# we also create a field 'full year': the year in which the chatter was born
			# we first check if the chatter filled in his actual age or his birth year
			# birth years are always written in full format (4 digits), whereas an age is written with 2 digits
			if len(profile_dic['Age info']) == 2:
				actual_age = profile_dic['Age info']
				# we calculate the birth year
				full_year = 2016 - int(actual_age)
			elif len(profile_dic['Age info']) == 4:
				full_year = profile_dic['Age info']
			else:
				full_year = 'unknown'

			# we add the birth year to the profile
			profile_dic['Birth year'] = full_year

			break

	return(profile_dic)



##### SEARCH PROFILE IN WEBSITE EXCEL #####
def search_profile_website(coding,website_forms_csv):
	"""
	function to search the correct profile for a coding

	input: 
	- coding: a text string containing the chatter's coding
	- website_forms_csv: a csv-file containing the website forms

	output: 
	- a dict containing the coding's corresponding profile
	"""

	# we open the csv-file
	profiles_file = open(website_forms_csv,'rt', encoding = 'latin-1').read()

	# we split the data on newline characters to split the profile information per person
	profiles = profiles_file.split("\n")

	# we fill a dictionary with the relevant information
	profile_dic = {}

	# we look for the correct profile
	for profile in profiles:

		# we split each person's profile information per field
		fields = profile.split(';')
		if ((len(fields) == 23) or (len(fields) == 24)): # two possibilities: with chat material included (24) or excluded (23) 
			# we look for the correct unique coding
			field_ID = fields[0]
			# we strip away whitespace from the ID
			if (field_ID[0] == '\n') or (field_ID[0] == '\r'):
				field_ID = field_ID[1:]
			# if we find the correct profile, we fill in the dictionary
			if (str(field_ID) == str(coding)) or ('website '+str(field_ID) == str(coding)):
				profile_dic['Gender'] = fields[15][0] # we only take the first letter: M or V
				profile_dic['Birthday'] = fields[14]
				profile_dic['Region'] = fields[17]
				profile_dic['Education'] = fields[16]
				profile_dic['Home languages'] = fields[18]
				profile_dic['Profession parents'] = fields[19]
				profile_dic['Social class parents'] = fields[23]
				profile_dic['Consent'] = fields[21]
				profile_dic['Consent parents'] = fields[22]
				profile_dic['School'] = fields[11]
				profile_dic['In gesprek'] = ''

				# we also create a field 'full year': the year in which the chatter was born
				short_year = profile_dic['Birthday'][-2:]
				# we decide if the year is in the 20th or 21st century
				if short_year[0] != str(0): # important to add 'str' (otherwise, the 0 is not recognized as such)
					full_year = '19'+short_year
				else:
					full_year = '20'+short_year

				profile_dic['Birth year'] = full_year

				break

	return(profile_dic)
