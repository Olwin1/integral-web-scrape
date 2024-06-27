import os
import requests
from bs4 import BeautifulSoup
import time
# Session setup with the cookie
session = requests.Session()
session.cookies.set('IntegralSession', 'j2hhe5dltjqu9ffpggpf2n5ru2', domain='my.integralmaths.org')

id_list = [2, 5, 4, 15, 32, 31, 7, 59, 57, 60, 58]

base_urls = [f'https://my.integralmaths.org/course/view.php?id={page_id}' for page_id in id_list]


def setup_soup(url, session):
    response = session.get(url)
    return BeautifulSoup(response.text, 'html.parser')

# returns a list of all the sections on a page
def get_sections(soup):
    return soup.find_all(attrs={"class": "sectionname"})

def extract_pages(soup):
    return [element.findChildren("a")[0].get("href") for element in get_sections(soup)] 

def extract_subpages(url, session):
    soup = setup_soup(url, session)

    return [element.findChildren("a")[0].get("href") for element in get_sections(soup)[1:]] # the subpages have a title with no link so first element is skipped 
    
def get_course_subpages(base_url, session): # Accetps the base url of a course page
    soup = setup_soup(base_url, session)

    results = [] # 2D array of all subpages found

    pages = extract_pages(soup)
    for page_url in pages:
        results.extend(extract_subpages(page_url, session))

    results.append(pages[0])
    results.append(pages[-1])

    return list(filter(lambda x: x != [], results)) # prune erronous empty results

def get_sectionids(url_results):
    return [int(url.split("sectionid=")[1]) for url in url_results]

def get_all_subpages(session):
    sub_pages = []

    for page_id in id_list:
        url = f'https://my.integralmaths.org/course/view.php?id={page_id}'
        sub_pages.append([page_id, get_course_subpages(url, session)])

    return sub_pages


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
            
# sub_pages = get_all_subpages(base_url, session)
# sectionIds = get_sectionids(sub_pages)
# print(f"Downloading from section of the following ids: {sectionIds}")
# for sectionId in sectionIds:
#     downloadPdfs(getPdfIds(2, sectionId))
# print("Done!")

sub_pages = get_all_subpages(session)
print("Got all subpages!")

pdfids = []

null_pages = []

for element in sub_pages:
    course_id = element[0]
    section_ids = get_sectionids(element[1])
    for section_id in section_ids:
        resource_ids = getPdfIds(course_id, section_id)
        pdfids.extend(resource_ids)
        
        resource_count = len(resource_ids)

        if resource_count == 0:
            print("!!Null page found!!")
            null_pages.append(f"https://my.integralmaths.org/course/view.php?id={course_id}&sectionid={section_id}")
        else:
            print(f"Added {len(resource_ids)} new resource IDs")

print("All resource Ids extracted!")
print("writing to txt file...")

with open("rsrc_ids.txt", "w") as savefile:
    for Id in pdfids:
        savefile.write(Id)
        savefile.write("\n")

print("Done, now saving null pages...")

with open("null_pages.txt", "w") as savefile:
    for url in null_pages:
        savefile.write(url)
        savefile.write("\n")