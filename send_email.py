from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
import base64
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

#set logger
logger = logging.getLogger(__name__) 
logger.setLevel(logging.DEBUG) 

def convert_filetime(dateString):
    date_time_obj = datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S.%f')
    return date_time_obj.strftime("%Y%m%d_%H_%M_%S_%f")

def error_email(note):
    message = Mail(
        from_email='Results@testandgo.com',
        to_emails= 'ali@lts.com',
        subject='NASEN Contact Scrapper Error',
        html_content=f'''
                    <p>Issue with code has occured. {note} Please check logs.</p>
                    '''
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        logger.debug(response.status_code)
        logger.debug(response.body)
        logger.debug(response.headers)
    except Exception as e:
        logger.exception(e.message)

def send_email(file, result):
    #set file name
    file_path = file

    if not result:
        message = "No updates since previous check. Spreadsheet should be blank."
    else:
        message = "Please see attached for NASEN Contact updates."

    # Email Setup
    message = Mail(
        from_email='ali@lts.com',
        to_emails=[To('ali@lts.com')],
        subject='NASEN Contact Update',
        html_content=f"""   <p>{message}
                            <br>
                            <br>Thanks,
                            <br>Allison Li</p>
                            """
    )

    # Attach CSV
    with open(file_path, 'rb') as f:
        data = f.read()
        f.close()
    encoded = base64.b64encode(data).decode()

    message.attachment = Attachment(FileContent(encoded),
                                FileName(f'{file_path}'),
                                FileType('text/csv'),
                                Disposition('attachment'),
                                ContentId('Content ID 1'))
    
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        logger.debug(response.status_code)
        logger.debug(response.body)
        logger.debug(response.headers)
    except Exception as e:
        error_email("email send failed")
        logger.exception(e.message)

#load environmental variables
load_dotenv()
API_key = os.environ.get('SENDGRID_API_KEY')

