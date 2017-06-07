#!/usr/bin/python
######################################################################################################
#                            CONFIGURATION PARSER
#
# Script parse script configuration written in XML format using the
# generic <parameter...><value> construction.
######################################################################################################

#########################
# PACKAGE IMPORT
import xml.sax.handler
from os import path
from sys import argv
import socket

#############################
# MAIN CLASS: CONFIG HANDLER
class ConfigHandler(xml.sax.handler.ContentHandler):
    '''Configuation Handler class for generic XML files in parameter:value pair format.'''

    # Initialise:
    def __init__(self):
        self.ivalue = False
        self.par_name = None
        self.par_value = None
        self.mapping = {}

    # Define behaviour when the start of a new element is encountered:
    # When a parameter element is encountered, it marks the beginning of
    # a new parameter:value pair, where the parameter name attribute
    # indicates the name used to identify the parameter in the config dictionary:
    def startElement(self,name,attributes):
        if name == 'parameter':
            self.par_name = attributes['name']
        elif name == 'value':
            self.ivalue = True

    # Define behaviour to handle the parameter values:
    def characters(self,data):
        if self.ivalue == True: self.par_value = data

    # Define behaviour when the end-parameter tag is encountered:
    def endElement(self,name):
        if name == 'value':
            self.ivalue = False
            self.mapping[self.par_name] = self.par_value

################################
# CONFIG READER
def read_config(config_file_path):

    # Initialize and verify:
    config = {}
    if path.isfile(config_file_path) == False: return config

    # Contruct the configuration parser:
    parser = xml.sax.make_parser( )
    config_handler = ConfigHandler( )

    # Parse the contents of the XML file through the config handler:
    parser.setContentHandler(config_handler)
    parser.parse(config_file_path)
    config = config_handler.mapping

    return config

def read_config_for_code(code_name):
    """Function to read XML configuration files
    code_name = { 'obscontrol', 'artemis_subscriber' }    
    """
    
    configs = { 'obs_control': 'obscontrol_config.xml',
               'artemis_subscriber': 'artemis_sync.xml'}
    if code_name in configs.keys():
        config_file = configs[code_name]
    
    host_name = socket.gethostname()
    if 'rachel' in str(host_name).lower():
        config_file_path = path.join('/Users/rstreet/.robonet_site/',configs[code_name])
    elif 'cursa' in host_name:
        config_file_path = path.join('../configs',configs[code_name])
    else:
        config_file_path = path.join('/var/www/robonetsite/configs/',configs[code_name])
    
    if path.isfile(config_file_path) == False:
        raise IOError('Cannot find configuration file, looking for:'+config_file_path)
    script_config = read_config(config_file_path)
    
    return script_config

#################################
# TEST CONFIG PARSER:
if __name__ == '__main__':

    if len(argv) > 1: config_file_path = argv[1]
    else: config_file_path = raw_input('Please input path to an XML config file: ')

    config = read_config(config_file_path)

    if config == None: print 'ERROR: Cannot read file '+config_file_path
    else:
        print 'Input configuration:'
        for par,par_value in config.items(): print '    ',par, ':', par_value
