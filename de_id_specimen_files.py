'''
    author@esilgard April 2016
    replace patient identifiers in specimen tsv files
    with unique de-identified id
'''
import os

# directories for input and output files
input_file_dir = 'input_file_directory'
output_file_dir = 'output_file_directory'

# first line expected to be a header line,
# mapping Caisis and/ids or MRNs to a predefined alternate id
patient_id_mapping_file = input_file_dir + os.path.sep + 'mrn_id_key.txt'

# speicmen input and output files expected to be tab delimited, deidentifiable data
# with only the zeroth element of each line being an identifiable patient id
specimen_input_file = input_file_dir + os.path.sep + 'input_file_name'
specimen_output_file = output_file_dir + os.path.sep + 'output_file_name'

mrn_to_de_id = dict((x.split('\t')[1].strip(), x.split('\t')[0]) \
            for x in open(patient_id_mapping_file, 'r').readlines()[1:])


with open (specimen_output_file,'w') as out:
    line_index = 0
    for lines in open(specimen_input_file, 'r').readlines():
        if line_index == 0:
            out.write(lines)
        else:
            l = lines.split('\t')
            ## replace mrn at beginning of line with de-id patient identifier
            out.write(mrn_to_de_id[l[0]]+'\t')
            ## write out the rest of the data per line
            out.write('\t'.join(l[1:]))
    
        line_index += 1
