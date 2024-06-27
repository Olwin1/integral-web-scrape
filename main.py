import os
import requests
from bs4 import BeautifulSoup
import time
# Session setup with the cookie
session = requests.Session()
session.cookies.set('IntegralSession', 'j2hhe5dltjqu9ffpggpf2n5ru2', domain='my.integralmaths.org')

# Define the base URL and the initial id
def getPdfIds(courseId, sectionId):
    base_url = f'https://my.integralmaths.org/course/view.php?id={courseId}&sectionid={sectionId}'
    response = session.get(base_url)

    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find_all("div", {"class": "activityinstance"})
    links = []
    for div in divs:
        pdf_link = div.find('a')["href"]
        if "resource/view.php?id=" in pdf_link:
            links.append(pdf_link.split("?id=", 1)[1])
    return links



def downloadPdfs(ids):
    print(f"Dowloading Pdfs of ids: {ids}")
    # Define the base URL and the initial id
    base_url = 'https://my.integralmaths.org/mod/resource/view.php?id='

    # Function to create directories if they do not exist
    def create_directory(path):
        if not os.path.exists(path):
            os.makedirs(path)

    # Function to download and save PDF
    def download_pdf(url, path):
        response = session.get(url)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)

    # Loop to iterate through the ids
    for i in ids:  # Adjust the range as needed
        time.sleep(0.5)
        url = f'{base_url}{i}'
        response = session.get(url)
        
        if response.status_code != 200:
            print(f'Failed to access {url}')
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract navigation structure for directory path
        nav = soup.find('div', {'id': 'page-navbar'}).find('nav', {'role': 'navigation'})
        directories = []
        if nav:
            for li in nav.find_all('li'):
                a_tag = li.find('a')
                if a_tag:
                    dir_name = a_tag.text.strip()
                    dir_name = ''.join(e for e in dir_name if e.isalnum() or e.isspace() or e == ':').replace(': ', '-').replace(' ', '_')
                    directories.append(dir_name)
        
        # Create the full directory path
        if directories:
            dir_path = os.path.join(*directories)
            create_directory(dir_path)
        
            # Extract PDF link
            resource_div = soup.find('div', {'class': 'resourceworkaround'})
            if resource_div and resource_div.find('a'):
                pdf_link = resource_div.find('a')['href']
                
                # Define PDF path
                pdf_name = os.path.basename(pdf_link)
                pdf_path = os.path.join(dir_path, pdf_name)
                
                # Download and save PDF
                download_pdf(pdf_link, pdf_path)
                print(f'Downloaded {pdf_name} to {pdf_path} of id {i}')
            else:
                print(f'No PDF link found on page {url}')
        else:
            print(f'No navigation structure found on page {url}')
downloadPdfs(getPdfIds(2, 3))
