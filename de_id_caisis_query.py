'''
    author@esilgard April 2016
    query caisis for clinical data based on the metadata.json file
    in order to pair with a given list of MRNs
    de-identify PHI (shift dates and hash keys) and output each table of clinical data to file
'''

import pyodbc, json, hashlib
import datetime
import random

# general directory for output files
output_file_dir = 'output_file_dir'
input_file_dir = 'input_file_dir'
disease_group = 'head_neck'

# first line expected to be a header line, mapping caisis ids or MRNs to a deidentified id
patient_id_mapping_file = input_file_dir + os.path.sep + 'patient_id_key_file'
# metadata file dictates which tables and fields should be queried and where joins on foreign keys are necessary
metadata = json.load(open(input_file_dir + os.path.sep + disease_group + os.path.sep + 'metadata.json', 'r'))

## output files for logging
# store the hashes of foreign and primary keys for QA if necessary
output_de_id_key_mapping_file = input_file_dir  + os.path.sep + 'PHI_hashed_keys_mapping.txt'
# store the date offsets for each patient for QA if necessary
output_date_offset_file = input_file_dir + os.path.sep + 'PHI_date_offsets_mapping.txt'

## dictionary to keep track of hashes (warn in case of hash collision)
key_hash_d = {}

## pyodbc connection string details
DATABASE = 'CaisisDBName'
SERVER_NAME = 'ServerName'
connStr = ('DRIVER={SQL Server};SERVER=' + SERVER_NAME +';DATABASE=' + DATABASE +';Trusted_Connection=yes')   
conn = pyodbc.connect(connStr)
cur = conn.cursor()

caisis_pt_id_to_de_id = dict((x.split('\t')[0], x.split('\t')[1].strip()) for x in open(patient_id_mapping_file,'r').readlines()[1:])
print 'querying ' + DATABASE + ' for ' + metadata['diseaseGroup']
table_d = {}
for tab in [x['table'] for x in metadata['tables']]:
    table_d[tab] = []

## loop through patients, gather appropriate table info, de-id
## (must loop through patients in order to de-id dates)
## output de-identification mappings to date and key map files
with open(output_date_offset_file, 'w') as date_map:
    ## all dates for a patient will shift by the same random digit (not zero)
    day_change_range = range(-21, 22); day_change_range.remove(0)
    date_map.write('CaisisPatientId\tDayShift\n')

    with open(output_de_id_key_mapping_file, 'w') as key_hash_map:
        key_hash_map.write('CaisisKeyName\tCaisisKeyValue\tDeIdKey\n')

        for caisis_id, de_id in caisis_pt_id_to_de_id.items():
            day_change = random.choice(day_change_range)
            date_map.write(caisis_id + '\t' + str(day_change) + '\n')
            
            for tables in metadata['tables']:                
                table_name =  tables['table'] 
                fields = tables['fields']
                query_list = [table_name + '.' + f for f in tables['fields']]
                query_string = 'SELECT ' + ','.join(query_list) + ' FROM '+ table_name

                ## query by patient id unless a single join is necessary (dictated by metadata file)
                if tables['patientIdInTable'] == "True":
                    query_string += ' WHERE ' + table_name + '.PatientId = '+ caisis_id
                else:
                    joining_table = tables['joinOn'][0]
                    joining_key = tables['joinOn'][1]
                    query_string += ' INNER JOIN ' + joining_table + ' ON ' +joining_table + '.' + joining_key + '=' + \
                                    tables['table'] +'.' + joining_key + ' WHERE ' + joining_table + '.PatientId = '+ caisis_id     
                cur.execute(query_string)
                rows = cur.fetchall()
                
                # loop through each row in query return
                for r in rows:
                    de_id_r = ['NONE'] * len(r)                    
                    for index in range(len(r)):
                        field_name = query_list[index].split('.')[1]
                        field_value = r[index]
                        if 'Id' in field_name:
                            ## hash on name and key number of database keys
                            if field_value:
                                field_value = str(field_value)
                                hashed_key = hashlib.sha1(field_name + field_value).hexdigest()
                                de_id_r[index] = hashed_key
                                ## check for hash collisions - if found, print out warning and write out to file
                                ## but will NOT overwrite original hash in dictionary
                                if hashed_key in key_hash_d and key_hash_d[hashed_key] != (field_name,field_value):
                                    print 'WARNING: Potential hash collision @ ' + hashed_key + ' with ' + \
                                          field_name + ','  + field_value + ' and ' + str(key_hash_d[hashed_key])
                                else:
                                    # map hashed keys to a tuple of field name and field value
                                    key_hash_d[hashed_key] = (field_name,field_value)
                                key_hash_map.write(field_name + '\t' + field_value + '\t' + hashed_key + '\n')
                            else:                                
                                de_id_r[index] = 'None'                        
                        elif type(r[index]) == datetime.datetime:                            
                            de_id_r[index] = field_value + datetime.timedelta(days=day_change)                            
                        else:
                            de_id_r[index] = field_value
                    ## store the deidentified data in the table_d dictionary
                    de_identified_record = [de_id] + de_id_r                    
                    table_d[table_name].append(de_identified_record)  


## output tables to file
for each_table in metadata['tables']:
    with open(output_file_dir + each_table['table']+'.tsv','w') as out:
        out.write('PatientId\t' + '\t'.join(each_table['fields'])+'\n')
        for each_record in table_d[each_table['table']]:
            out.write('\t'.join([str(r) for r in each_record])+'\n')
