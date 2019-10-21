#!/usr/bin/python
# -*- coding: utf-8 -*-


"""script to write the final corpus in the correct format"""
# run in Python 3


##### IMPORTS #####

from writecorpus_NEW_b import facebook_2_list, whatsapp_2_list, excel_2_list, write_corpus
from os import listdir

##### PROFILE AND CODING FILES #####
manual_codings_csv = 	'/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/data_excels/AF_profielcoderingen.csv'
manual_profiles_csv = 	'/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/data_excels/AF_profielen.csv'
website_forms_csv = 	'/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/data_excels/AF_website.csv'
names_csv = 			'/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/data_excels/AF_names.csv'



##### TEST FILES: INPUT DATA #####

# FINAL GTI DUFFEL

gti_duffel = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/gti_duffel"

 

# NEW KOSH HERENTALS
kosh_herentals = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/kosh_herentals"


# NEW KTA DA VINCI
kta_da_vinci_edegem = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/kta_da_vinci_edegem" 


# NEW KTA DEN BIEZERD
kta_denbiezerd_niel = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/kta_denbiezerd_niel" 

# NEW OLVE EDEGEM
olve_edegem = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/olve_edegem" 


# NEW OLVI BOOM
olvi_boom = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/olvi_boom"

# NEW OLVI BOOM 2
olvi_boom_2 = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/olvi_boom_2"


# NEW ONAFHANKELIJK
onafhankelijk = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/onafhankelijk"


# NEW PIVA
piva = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/piva_antwerpen"


# NEW SINT JOZEF ESSEN
sji_essen = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/sint_jozef_essen"


# NEW SINT JOZEF KONTICH
sji_kontich = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/sint_jozef_kontich"

# NEW SINT JOZEF KONTICH
sji_kontich_2 = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/sint_jozef_kontich_2"

# NEW SINT JOZEF KONTICH
sji_kontich_3 = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/sint_jozef_kontich_3"

# NEW SINT NORBERTUS ANTWERPEN
snor_antwerpen = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/sint_norbertus_antwerpen"


# NEW SINT NORBERTUS DUFFEL
snor_duffel = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/sint_norbertus_duffel"

# NEW SINT NORBERTUS DUFFEL
snor_duffel_2 = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/sint_norbertus_duffel_2"


# NEW SINT RITA KONTICH
rita = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/sint_rita_kontich"



# NEW SINT URSULA LIER

ursula = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/sint_ursula_lier" 



# NEW VTI KONTICH
vti = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/vti_kontich" 


# NEW EXCELCORPUS
excelcorpus = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/excelcorpus" 

# MINI EXCEL
mini = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/FINAL_VERSIONS/mini" 


# TESTIE
testie = "/Users/lisahilte/Documents/doctoraat/corpora/verzameling_scholen/code_dataverwerking/write_new_corpus/test_mapje"


##### TEST RUNS #####

#### TEST RUN FUNCTION

def write_corpus_per_folder(school_folder = "", name_outputfile = ""):
	"""
	function to write the corpora in a list of corpora to one large corpus
	- input: 
		- the pathname of the school folder
		- the name of the desired outputfile
	- output: the corpora are written to a large file
	"""

	# we read in the filenames inside the folder
	list_files = [item for item in listdir(school_folder) if (item.endswith('.txt') or item.endswith('.xlsx'))]

	for filename in list_files:

		corpus_path = school_folder + "/" + filename

		# we check if the file is a Facebook, WhatsApp or Excel file
		if 'Facebook' in corpus_path:
			# we first convert the corpus file to a list of the chat utterances with meta-information
			listie = facebook_2_list(corpus_path)
			# we convert each item to utf-8
			for item in listie:
				item_ = [element.encode('utf-8') for element in item]
				# we print each item to check if nothing goes wrong
				print(item_)


		elif 'WhatsApp' in corpus_path:
			# we convert the corpus file to a list of the chat utterances with meta-information
			listie = whatsapp_2_list(corpus_path)
			for item in listie:
				# we convert each item to utf-8
				item_ = [element.encode('utf-8') for element in item]
				# we print each item
				print(item_)


		elif corpus_path.endswith('xlsx'):	# Excel file
			# we convert the corpus file to a list of the chat utterances with meta-information
			listie = excel_2_list(corpus_path)
			for item in listie:
				# we convert each item to utf-8
				item_ = [str(element).encode('utf-8') for element in item]
				# and print each item
				print(item_)

		# now we write the obtained list to the larger corpus file
		write_corpus(listie,name_outputfile,manual_codings_csv,manual_profiles_csv,website_forms_csv)


	return None

###write_corpus_per_folder(school_folder = mini, name_outputfile = 'output/mini.txt')
###write_corpus_per_folder(school_folder = gti_duffel, name_outputfile = 'output/gti.txt')
###write_corpus_per_folder(school_folder = kosh_herentals, name_outputfile = 'output/kosh.txt')
###write_corpus_per_folder(school_folder = kta_da_vinci_edegem, name_outputfile = 'output/davinci.txt')
###write_corpus_per_folder(school_folder = kta_denbiezerd_niel, name_outputfile = 'output/denbiezerd.txt')
###write_corpus_per_folder(school_folder = olve_edegem, name_outputfile = 'output/olve.txt')
###write_corpus_per_folder(school_folder = olvi_boom, name_outputfile = 'output/olvi.txt')
###write_corpus_per_folder(school_folder = olvi_boom_2, name_outputfile = 'output/olvi2.txt')
###write_corpus_per_folder(school_folder = onafhankelijk, name_outputfile = 'output/onafhankelijk.txt')
###write_corpus_per_folder(school_folder = piva, name_outputfile = 'output/piva.txt')
###write_corpus_per_folder(school_folder = sji_essen, name_outputfile = 'output/sji_essen.txt')
###write_corpus_per_folder(school_folder = sji_kontich, name_outputfile = 'output/sji.txt')
###write_corpus_per_folder(school_folder = sji_kontich_2, name_outputfile = 'output/sji2.txt')
###write_corpus_per_folder(school_folder = sji_kontich_3, name_outputfile = 'output/sji3.txt')
###write_corpus_per_folder(school_folder = snor_antwerpen, name_outputfile = 'output/snor_antwerpen.txt')
###write_corpus_per_folder(school_folder = snor_duffel, name_outputfile = 'output/snor.txt')
###write_corpus_per_folder(school_folder = snor_duffel_2, name_outputfile = 'output/snor2.txt')
###write_corpus_per_folder(school_folder = rita, name_outputfile = 'output/rita.txt')
###write_corpus_per_folder(school_folder = ursula, name_outputfile = 'output/ursula.txt')
###write_corpus_per_folder(school_folder = vti, name_outputfile = 'output/vti.txt')
###write_corpus_per_folder(school_folder = excelcorpus, name_outputfile = 'output/excelcorpus.txt')