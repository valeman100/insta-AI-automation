import os
import imapclient
import pyzmail
from bs4 import BeautifulSoup
from lxml import etree


def get_last_email_from(sender_email):
    server = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    server.login(os.getenv('GMAIL_USERNAME'), os.getenv('GMAIL_PASSWORD'))
    server.select_folder('INBOX')
    messages = server.search(['ALL'])

    message = None
    for email_id in messages[::-1]:
        raw_message = server.fetch([email_id], ['BODY[]', 'FLAGS'])
        from_ = pyzmail.PyzMessage.factory(raw_message[email_id][b'BODY[]']).get_address('from')
        if from_[1] == sender_email:
            # if from_[1] == 'vale.mannucci@live.it':
            message = pyzmail.PyzMessage.factory(raw_message[email_id][b'BODY[]'])
            break

    body = message.html_part.get_payload().decode(message.html_part.charset)
    server.logout()
    return body


def get_urls_from_html(html):
    parsed_html = BeautifulSoup(html, features="html.parser")
    email = parsed_html.contents[0]
    dom = etree.HTML(str(email))

    res = dom.xpath(
        '//a[@style="box-sizing: border-box; font-family: Arial, Helvetica, sans-serif; font-size: 18px; color: inherit !important; text-decoration: underline !important;"]')

    urls = []
    for element in res[3:]:
        urls.append(element.get('href'))

    return urls
