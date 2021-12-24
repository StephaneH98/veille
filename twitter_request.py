import requests
import os
import json
from datetime import date, timedelta
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# To get the tweets : https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a
# To send the email : https://realpython.com/python-send-email/
# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='enter token here'
bearer_token = os.environ.get("BEARER_TOKEN")


## Mail parameters ##
port = 465 #For ssl
from_addr = ""
to_addr = ""
password = str("")


## Parameters ##
search_url = "https://api.twitter.com/2/tweets/search/recent"
today = date.today()
yesterday = str(today - timedelta(days=4)) + "T00:00:00.000Z"
max_results = 100

file_name = 'keyword.txt'

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {'query': '(from:CERT_FR)', 'tweet.fields': 'created_at,source,author_id','start_time':yesterday, 'max_results':max_results}


def send_mail(_mail_content):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Vulnerability report"
    message["From"] = from_addr
    message["To"] = to_addr

    # Create the HTML version of your message
    html = """\
    <html>
    <body>
        <p>Hi,<br>
        How are you?<br>
        This is the report of today : """ + str(today) + """</p>""" + _mail_content + """
    </body>
    </html>
    """

    # Turn these into html MIMEText objects
    html_part = MIMEText(html, "html")

    # Add HTML part to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(html_part)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addr, message.as_string())


def bearer_oauth(_r):
    """
    Method required by bearer token authentication.
    """

    _r.headers["Authorization"] = f"Bearer {bearer_token}"
    _r.headers["User-Agent"] = "v2RecentSearchPython"
    return _r

def connect_to_endpoint(_url, _params):
    response = requests.get(_url, auth=bearer_oauth, params=_params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def analyse_response(_json_response, _keywords):
    tweet_list = _json_response["data"]
    mail_content = ""
    for tweet in tweet_list:
        text = tweet["text"]
        contain_keyword(text, _keywords)
        if contain_keyword(text, _keywords) == 1:
            mail_content = add_content_to_mail(text, mail_content)
    return mail_content
                

def get_key_word_list():
    file = open(file_name, 'r')
    keywords=[]
    for line in file:
        keywords.append(line[:-1])   
    return keywords

def contain_keyword(_text, _keywords):
    for word in _keywords:
        if _text.find(word) != -1:
            return 1
    return 0

def add_content_to_mail(_text, _mail_content):
    _mail_content = _mail_content + "<p>" + _text + "</p>"
    return _mail_content

if __name__ == "__main__":
    keywords = get_key_word_list()  
    json_response = connect_to_endpoint(search_url, query_params)
    mail_content = analyse_response(json_response, keywords)
    send_mail(mail_content)