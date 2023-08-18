# NASEN_contact_scrapper
Selenium webscrapper for NASEN.org. Performs the following actions:
1. Scrapes contact info for all sites and stores as dictionary.
2. Checks new data against masterfile for differences. (masterfile was saved last time the code ran)
3. Sends result of check to designated emails using sendgrid.
4. Saves changes to masterfile.

