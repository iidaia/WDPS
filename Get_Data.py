import json
import requests
import pickle
from bs4 import BeautifulSoup 
import re
import time

base_url_github_jobs = "https://jobs.github.com/positions.json?"

#If it is the first time running the script, set this to True
to_dump = True

def gather_jobs_data(base_url):
    """
    Given a base_url API goes trough the pages and gather the JSON data for each job.
    Returns a list of jobs, in JSON format.
    """

    jobs_available = True
    page_numb = 1
    jobs = []

    while(jobs_available):
        url = base_url + "page=" + str(page_numb)
        response= requests.get(url)
        if(len(response.text) > 2):
            j = json.loads(response.text)
            for job in j:
                jobs.append(job)
                
        else:
            jobs_available = False

        page_numb += 1

    print("Found %d jobs" % (len(jobs)))

    return jobs


        
def dump_stackoverflow():
    """
    NOTE:stacoverflow even if you go over the total number of page, will keep loading
         an empty page without any error. For now I will check manually the total number
         of pages and update the variable.
    
    In order to avoid heavy load on the server of stackoverflow, I cache the prettified
    html and do the data analysis later.
    
    Returns nothing.
    """

    base_url = "https://stackoverflow.com/jobs?sort=i"
    page_numb = 1
    tot_pages = 20
    filename = "./Data/jobs_data_stackoverflow_jobs_page="
    
    for i in range(tot_pages):
        time.sleep(3)
        url= base_url + "&pg=" + str(page_numb)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        path = filename + str(page_numb)
        with open(path, 'w+', encoding='utf-8') as fw:
            fw.write(soup.prettify())
    
        page_numb += 1

def read_stackoverflow(occ_vect, companies, num_jobs):
    """
    Reads the dumped stack_overflow files and builds the occurrence vector.
    Returns the occurrence vector and the total number of jobs scanned.
    """

    base_filename = "./Data/jobs_data_stackoverflow_jobs_page="
    page_numb = 1
    total_jobs = num_jobs

    #This while(true) try except break is used because I don't know how many files I have
    #to scan.
    while(True):

        filename = base_filename + str(page_numb)
        
        try:
            with open(filename, 'r', encoding='utf-8') as fr:
                content = fr.read()
                soup = BeautifulSoup(content, "html.parser")
                
                #jobs_title = soup.findAll(name='a', attrs={'class':'s-link s-link__visited job-link'})
                jobs_title = soup.findAll(name='span', attrs={'class':'fav-toggle ps-absolute l16 c-pointer js-fav-toggle'})
                
                total_jobs += len(jobs_title)
                regex = r'(data-ga-label=")(.* data-href=")'
                
                jobs_body = soup.findAll(name='div', attrs={'class':'-job-summary'})
                
                for job_body in jobs_body:
                    match = re.search(regex, str(job_body)).group(0)
                    company = match.split("|")[0][15:].strip()
                    position = match.split("|")[1].strip()
  
                    #Skips job posting that I already scanned before
                    #Assumption: Companies post the job position with the same title in different job websites
                    if(company in companies):
                        if(position in companies[company]):
                            continue
                        else:
                            companies[company].append(position)
                    else:
                        companies[company] = []
                        companies[company].append(position)

                    soup_tags = BeautifulSoup(str(job_body), "html.parser")
                    job_tags = soup_tags.findAll(name='a', attrs={'class':'post-tag job-link no-tag-menu'})
                       
                    for job_tag in job_tags:
                        #There are leading spaces/tabs that I have to remove
                        job_tag_stripped = job_tag.text.strip()
                        
                        #TODO: I can improve this by having another hash table having the reverse
                        # of my dictionary. Going from O(n^2) to O(1)
                        for key in skills.keys():
                            for skill in skills[key]:
                                if(job_tag_stripped == skill):
                                    occ_vect[key] += 1

            page_numb += 1
        except:
            break


    return occ_vect, companies, total_jobs

if(to_dump):
    jobs = gather_jobs_data(base_url_github_jobs)
    pickle.dump(jobs, open("./Data/jobs_data_github_jobs.txt","wb"))
    dump_stackoverflow()

#initialize occ_vect to 0
occ_vect = {}

companies = {}
num_jobs = 0
occ_vect, companies, total_jobs = read_stackoverflow(occ_vect, companies, num_jobs)
