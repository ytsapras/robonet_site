#!/usr/bin/python
######################################################################################################
#                            ARTEMiS MODEL SUBSCRIBER
#
# Script to download the latest model parameters from ARTEMiS
######################################################################################################

#########################
# PACKAGE IMPORT

#########################
# MAIN FUNCTION
def sync_artemis_models():
    '''Function to sync a local copy of the ARTEMiS model fit files for all events from the
       server at the Univ. of St. Andrews.
    '''

    # Read configuration:

    # Rsync the contents of ARTEMiS' model files directory, creating a log file listing
    # all files which were updated as a result of this rsync and hence which have been
    # updated.

    # Read the list of updated models:

    # Loop over all updated models and update the database:

    # Read the fitting model parameters from the model file:

    # Query the DB to check whether the event exists in the database already:

    # If event is known to the DB, submit the updated model parameters as a new model object:

    # If the event is unknown to the DB, create an entry for it, updating it with all
    # currently known information:

    # Log the update in the script log:


###########################
# COMMANDLINE RUN SECTION:
if __name__ == '__main__':

    sync_artemis_models()
