'''
    author@esilgard April 2016
    "sweep" through output directory files
    searching for potential PHI and print out warning statements
'''
import os, re

# general directory for output files
file_dir = 'H:\DataExtracts\OncoscapeLungHoughton-4229\Output'

## common names or potential phi (assume first line is a header/column description)
first_names = set([x.strip() for x in open('resources' + os.path.sep + 'First_Names.txt', 'r').readlines()[1:]])
last_names = set([x.strip() for x in open('resources' + os.path.sep + 'Last_Names.txt', 'r').readlines()[1:]])
potential_phi_keywords = set([x.strip() for x in open('resources' + os.path.sep + 'PHI_Keywords.txt', 'r').readlines()[1:]])

print 'sweeping output files for potential PHI: mrns, path numbers, ',\
      len(first_names), 'first names, ', len(last_names), 'last names, ',\
      len(potential_phi_keywords), 'PHI indicator keywords'

for path, directory, files in os.walk(file_dir):
    
    for f in files:
        text = open(path + os.path.sep + f, 'r').read()
        alpha_words = set(re.split('[\W]', text))

        ## PHI patterns
        mrn = re.search('[UH][0-9]{7}', text)        
        pathnum = re.search('[A-B][\-][\-\d]{2,11}', text)
        if mrn:
            print 'WARNING. Potential MRN found in ' + path + f + ' at ' + str(mrn.start())                 
        if pathnum:
            print 'WARNING. Potential accession number found in ' + path + f + ' at ' + str(pathnum.start())
                    
        if first_names.intersection(alpha_words):
            print 'WARNING. Potential first name(s) found in ' + path + f + ' -- ' + ','.join(first_names.intersection(alpha_words))
            
        if last_names.intersection(alpha_words):
            print 'WARNING. Potential last name(s) found in ' + path + f + ' -- ' + ','.join(last_names.intersection(alpha_words))
    
        if potential_phi_keywords.intersection(alpha_words):
            print 'WARNING. Potential PHI indicator keyword found in ' + path + f + ' -- ' + ','.join(potential_phi_keywords.intersection(alpha_words))
    
