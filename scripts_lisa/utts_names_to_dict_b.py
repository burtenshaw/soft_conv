### IMPORTS #####

from collections import defaultdict as dd 

l = ['lisa hilte','haha	hihi','hehe','thomas pinna','thomas pinna','hihi', 'hallo \n blabla','lisa hilte']
lis = ['blqblq','lisa hilte']
n = set(['lisa hilte','thomas pinna'])

def utts_names_to_dict(group_of_utts_and_names,names):
	"""
	function to convert an unstructured group of utterances mixed with names into a structured dictionary (who wrote what)
	input:
		- group_of_utts_and_names: list of utterances mixed with names
		- names: set of the chatters' names
	output:
		- a dictionary with the chatters' names as keys and what they wrote as values

	"""
	# we create a defaultdict to store the info in. the values will be lists of utterances
	structured_dic = dd(list)

	# we loop over all items in the list, by their indices
	index = 0
	# we do not want to exceed the length of the list
	while index < len(group_of_utts_and_names):
		#print('nu bezig met '+str(l[index]))
		if group_of_utts_and_names[index].lower() in names: # lowercase! because the names we use will always be lowercased
			name_lower = group_of_utts_and_names[index].lower()
			# if an element of the list is a name, we want it as key in the dictionary
			# we now want to loop over the next items in the list
			a = 1
			while a < (len(group_of_utts_and_names)-index):
				utt = group_of_utts_and_names[index+a]
				utt_lower = group_of_utts_and_names[index+a].lower()
				if utt_lower not in names:
					utt = utt.replace('\t', ' ').replace('\n', ' ')
					# if the next item is no name, we add it to the chatter's list of utts
					if utt.strip() != '':
						structured_dic[name_lower].append(utt)
				else:
					#if it is, we leave this while loop
					break
				a += 1
		index += 1

	# we return the dict
	return(structured_dic)

### TEST ###
#print(utts_names_to_dict(l,n))