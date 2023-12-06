import hashlib
from model import *
from bs4 import BeautifulSoup
from plyer import notification
def md5(text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()
def alert(__MESSAGE__):
    return notification.notify(
        title='',
        message=__MESSAGE__,
        app_name='Pisilinux Developer', 
        timeout=10, 
    )
