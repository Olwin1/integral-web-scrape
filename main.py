import os
import requests
from bs4 import BeautifulSoup
import time

# Define the base URL and the initial id
base_url = 'https://my.integralmaths.org/mod/resource/view.php?id='
start_id = 319

# Session setup with the cookie
session = requests.Session()
session.cookies.set('IntegralSession', 'j2hhe5dltjqu9ffpggpf2n5ru2', domain='my.integralmaths.org')
