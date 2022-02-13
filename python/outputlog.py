# Crokinole Reference - Script to Generate webpages

## Output Log
### function to output text to a file to aid traceback

from datetime import datetime
import os
path = os.getcwd()
parent_path = os.path.abspath(os.path.join(path, os.pardir))

## Location of output log
log_output_location = parent_path + '/logs/'
run_log = 'run_log.txt'
path_to_file = log_output_location + run_log
run_log_input_checks = 'Input_Checks.txt'
path_to_file_input_checks = log_output_location + run_log_input_checks

## Function
def generate(text):
    f = open(path_to_file, 'a') #open file, a=append
    f.write(str(datetime.now())+" "+text)
    f.write('\n') #new line
    f.close()
    
def generate_input_check(text):
    f = open(path_to_file_input_checks, 'a') #open file, a=append
    f.write(str(datetime.now())+" "+text)
    f.write('\n') #new line
    f.close()
    
    
