######################################################################################################
#                            UTILITY FUNCTIONS
#
# Basic useful utility functions
######################################################################################################

#########################
# PACKAGE IMPORT



##################################
# CONVERT SHORT TO LONG EVENT NAME
def short_to_long_name(short_name):
    '''Function to convert the name of a microlensing event in short-hand format to long-hand format.
    Input: Microlensing name string in short-hand format, e.g. OB150001
    Output: Long-hand name format, e.g. OGLE-2015-BLG-0001
           If an incompatible or long-hand name string is given, the same string is returned.
    '''

    # Definitions:
    survey_codes = { 'OB': 'OGLE', 'KB': 'MOA' }

    # Split the string into its components:
    survey = short_name[0:2]
    year = short_name[2:4]
    number = short_name[4:]

    # Interpret each component of the name string:
    if survey in survey_codes.keys():
        survey = survey_codes[survey]
        year = '20' + year
        while len(number) < 4: number = '0' + number

        long_name = survey + '-' + year + '-BLG-' + number
    else:
        long_name = short_name

    return long_name

##################################
# CONVERT LONG TO SHORT EVENT NAME
def long_to_short_name(long_name):
    '''Function to convert the name of a microlensing event in long-hand format to short-hand format.
        Input: Microlensing name string in long-hand format, e.g. OGLE-2015-BLG-0001
        Output: Long-hand name format, e.g. OB150001
        If an incompatible or long-hand name string is given, the same string is returned.
        '''
    
    # Definitions:
    survey_codes = { 'OGLE': 'OB', 'MOA': 'KB' }

    # Split the string into its components:
    components = long_name.split('-')

    # Interpret each component of the name string:
    if len(components) == 4:
        survey = components[0]
        if survey in survey_codes.keys():
            survey = survey_codes[survey]
            year = components[1][2:]
            number = components[3]
            while len(number) < 4: number = '0' + number
        
            short_name = survey + year + number
        else:
            short_name = long_name
    else:
        short_name = long_name

    return short_name

