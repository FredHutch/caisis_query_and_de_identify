# caisis_query_and_de_identify
===============================
query caisis database based on metadata input, de-identify, and output tables to tsv
------------------------------------------------------------------------------------

- de_id_caisis_query.py will pull data from caisis tables (through pyodbc) according to the tables and fields listed in the metadata.json file.
these fields will be deidentified in the following way:
    * all datetime objects will be shifted by a random number of days (within 22 days either way, consistent on a patient level)
    * any field with the string 'Id' in it will be hashed by the field name and value

# *Note* 
This means any data pulled that does not fit either of the two above criteria will **NOT** be altered in anyway
It's up to the creator of the metadata file and the operator at run time to ensure that the data being pulled from Caisis is consistent with these assumptions
it's assumed that none of the fields specified in the metadata.json file contain any other types of PHI *(i.e. no names or identifiers beyond the caisis primary and foreign keys)*

- de_id_specimen_files.py will replace the patient identifier on each line (it's assumed that the first column contains the patient identifier and there is no other PHI within the file) with the previously created non identifying unique key for this cohort (within the id mapping file)

- sweeper.py will look through all output files searching for potential PHI based on patterns and lists of names *(just an extra safety precaution/due diligence)*

for general Caisis info: [link](www.caisis.org)

for Caisis data model specifics: refer to resources/Caisis_60_ERD_PC.pdf

### general tips for data validation:
*double check hashed_keys_mapping to ensure there are no duplicate hashes
*double check at least one output table file against Caisis; ensure the correct number of rows for the query
*double check accurate field values for at least one patient in at least one table
*pick one patient from date_offsets_mapping file and check at least two tables containing dates to ensure that all dates are shifted by the same amount of days and that number is what's represented in the mapping file
