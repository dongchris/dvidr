Tutorial
================

Database tutorial:
    (1) Enter RDS console on AWS

    (2) Create PostgreSQL DB instance

        (a) Select the region of the database

        (b) Add username and password

        (c) Make database public

    (3) Download SQL client - in this case, the choice was SQL Workbench.

        (a) Download JDBC driver for PostgreSQL

    (4) Change security rules for RDS

        (a) Add inbound rule for 0.0.0.0 (allow traffic from anywhere as long as they have the correct username/password)

    (5) Connect to PostgreSQL database using the username/password and driver downloaded earlier. JDBC URL comes from the Amazon RDS console
  
    (6) CREATE tables according to schemas outlined in the Google Drive folder.

OCR tutorial:
   
    (1) install google cloud vision python package sudo pip install google-cloud-vision

    (2) enable google api on the google cloud platform
        
	(a) create google cloud platform account
        
	(b) set up storage
        
	(c) open vision API
        
	(d) set up API credentials, download the API key

        (e) put the API key to the bash profile

    (3) run the OCR script

Simply run $python pipeline.py in the 'code/main/' directory.


