import epicevents.models.client 
import epicevents.models.contract
import epicevents.models.event 
import epicevents.models.collaborator  
import epicevents.models.role 

import os

# Set the JWT secret key for the tests
os.environ["EPICEVENTS_SECRET"] = "test-secret-test-secret-test-secret"