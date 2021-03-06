import json
import requests
import pickle
from bs4 import BeautifulSoup 
import re
import time

base_url_github_jobs = "https://jobs.github.com/positions.json?"

#If it is the first time running the script, set this to True
to_dump = False


skills = {
    #Programming Languages
    "Python":           ["python", "python2", "python3", "python-3.x"],
    "Cython":           ["cython"],
    "JavaScript":       ["js", "javascript", "es6", "jquery", "rx.js", "d3.js", "ajax", "vanilla js"],
    "TypeScript":       ["typescript"],
    "C#":               ["c#", "c#.net"],
    "C++":              ["c\+\+"],
    "C":                ["c"],
    "Ruby":             ["ruby", "rails", "ruby with rails", "ruby-on-rails"],
    "Java":             ["java", "java 8", "java 10", "java-ee", "jvm"],
    "PHP":              ["php"],
    "Go":               ["go", "golang"],
    "R":                ["r"],
    "Scala":            ["scala"],
    "Tableau":          ["tableau"],
    "SAS":              ["sas"],
    "Cobol":            ["cobol"],
    "Haskel":           ["haskel"],
    "Erlang":           ["erlang"],
    "F#":               ["f#"],
    "Lisp":             ["scheme", "lisp", "common lisp", "clojure"],
    "Bash":             ["bash"],
    "X++":              ["x\+\+"],
    "Rust":             ["rust"],
    "Groovy":           ["groovy", "apache groovy"],
    "Perl":             ["perl"],
    "Elixir":           ["elixir"],
    "SmallTalk":        ["smalltalk"],
    "Objective-C":      ["objective-c"],
    "Fortran":          ["fortran"],
    "Solidity":         ["solidity"],
    "Matlab":           ["matlab", "simulink"],
    "Q#":               ["q#", "quantum-computing"],
    #Frameworks
    "React":            ["react", "react.js", "react-native", "reactjs", "react native", "rx.js", "rxjs"],
    "Node":             ["node.js", "nodejs", "node"],
    "Vue":              ["vue", "vuejs", "vue.js", "vuex"],
    "Angular":          ["angular", "angularjs"],
    ".NET":             [".net", ".net-core", "xamarin", "asp.net"],
    "Redux":            ["redux", "redux.js"],
    "Ember":            ["ember", "ember.js"],
    "Pyramid":          ["pyramid"],
    "Flask":            ["flask"],                  
    "Django":           ["django", "django-models"],                 
    "Spring":           ["spring boot", "spring-boot", "spring"],            
    "Laravel":          ["laravel"],
    "CherryPy":         ["cherrypy"],
    "Qt":               ["qt", "qt-creator"],
    "gRPC":             ["grpc"],
    "openCL":           ["opencl"],
    "NGRX":             ["ngrx"],
    "Celery":           ["celery"],
    "PyTorch":          ["pytorch"],
    "Symfony":          ["symfony", "symfony2"],
    "TurboGears":       ["turbogears", "turbogears2"],
    #Containers
    "Docker":           ["docker"],
    "Kubernetes":       ["kubernetes"],
    "OpenShift":        ["openshift"],
    #Mobile Dev
    "Apple":            ["apple", "ios", "swift", "rxswift", "osx", "macos"],
    "Android":          ["android","kotlin", "gradle"],
    #Cloud (CI/CD)
    "Cloud":            ["cloud", "continuous-integration", "travis-ci"],
    "AWS":              ["aws", "aws-lambda", "amazon-ec2", "ec2", "ecs", "sqs", "redshift", "lambda", "kinesis", "s3", "amazon-web-services"],
    "Terraform":        ["terraform"],
    "Heroku":           ["heroku"],
    "Google Cloud":     ["google cloud", "dataflow", "biqquery", "google-cloud-platform", "google-bigquery"],
    "Jenkins":          ["jenkins", "jenkins-groovy"],
    #Web dev
    "Wordpress":        ["wordpress"],
    "Drupal":           ["drupal"],
    "HTML":             ["html", "html5"],
    "CSS":              ["css", "css3", "sass", "scss"],
    "Bootstrap":        ["bootstrap"],
    "Svelte":           ["svelte"],
    "Azure":            ["azure"],
    #Data query
    "SQL":              ["mysql", "redis", "nginx", "sql", "mongo", "mongodb", "nosql", "mssql", "postgresql", "rethinkdb", "postgres", "cassandra","dynamodb", "database"],
    "GraphQL":          ["graphql"],
    "Kafka":            ["kafka", "apache-kafka"],
    #OS
    "Linux":            ["linux", "unix", "debian", "centos"],
    "Microsoft":        ["microsoft", "windows", "windbg"],
    #Gaphics
    "OpenGL":           ["opengl"],
    "Metal":            ["metal"],
    "Unity":            ["unity", "unity3d"],
    "Cuda":             ["cuda"],
    "WebGL":            ["webgl"],
    "OpenCV":           ["opencv"],
    #Big Data
    "Apache Spark":     ["spark", "apache spark", "apache-spark", "spark-streaming", "pyspark"],
    "Apache Hadoop":    ["hadoop", "apache hadoop"],
    "Apache Hive":      ["hive", "apache-hive"],
    "Apache Airflow":   ["apache-airflow", "airflow"],
    "ETL":              ["etl"],
    "Apache Beam":      ["apache-beam"],
    #Data Science
    "TensorFlow":       ["tensorflow", "tensorflow 2.0", "keras"],
    "Machine Learning": ["machine learning", "ml", "ai","artificial-intelligence", "machine-learning", "nlp", "data-science", "neural-network", "deep-learning"],
    "Python Libraries": ["numpy", "pandas", "scipy", "matplotlib", "scikit-learn"],
    #Testing
    "Jasmine":          ["jasmine"],
    "Unit Test":        ["unit test", "unit testing", "unit tests", "jest","testing", "automated-tests", "test", "tdd"],
    "E2E":              ["e2e", "cucumber"],
    "Espresso":         ["espresso"],
    "EarlGrey":         ["earlgrey"],
    "Sikuli-x":         ["sikuli-x"],
    "PyTest":           ["pytest"],
    #Security
    "Security":         ["security","penetration-testing", "cryptography", "encryption"],
    "PyHook":           ["pyhook"],
    "SysAdmin":         ["sysadmin"],
    "ElasticSearch":    ["elasticsearch"],
    #DevOps
    "DevOps":           ["devops"],
    #WebScraping
    "WebScraping":      ["scrapy", "web-scraping", "prometheus"],
    #Electronics
    "FPGA":             ["fpga", "soc"],
    "VHDL":             ["vhdl", "modelsim"],
    "Embedded":         ["embedded", "qnx", "plc"],
    #Automation
    "Ansible":          ["ansible"],
    "Automation":       ["automation", "puppet", "salt-stack"],
    #Networks
    "Networking":       ["networking", "tcp-ip", "dns"],
    #IoT
    "IoT":              ["iot", "yocto"],
    #Blockchain
    "Truffle":          ["truffle"],
    #???
    "RabbitMQ":         ["rabbitmq", "rabbit-mq"]
}

def stats(skills, companies, occ_vect, num_jobs, filename):
    """
    Returns the occurrence vector and the companies dictionary, and the total numb of jobs.
    """

    jobs = pickle.load(open(filename, 'rb'))

    positions = ["data science","data scientist","data analyst"]

    #REGEX: forcing a space or / or , before the keyword, or a space / , . or \n afterwards.
    #       This avoids ambigous keys like c to be recognized when they shouldn't.
    #       Since Go is a verb, if it is used in the description will give a false positive.
    prefix_regex = r"[ \/,\(]"
    suffix_regex = r"[ \/,\.\n\)]"

    
    for job in jobs:
        num_jobs += 1
        soup = BeautifulSoup(job['description'].lower(), "html.parser")
        job_description = soup.text
        
        #Skips job posting that I already scanned before
        #Assumption: Companies post the job position with the same title in different job websites
        if(job['company'] in companies):
            if(job['title'] in companies[job['company']] and job['title'] not in positions):
                continue
            else:
                companies[job['company']].append(job['title'])
        else:
            companies[job['company']] = []
            companies[job['company']].append(job['title'])

        for key in skills.keys():
            for skill in skills[key]:
                regex = prefix_regex + skill + suffix_regex
            
                #If I find a match, I'll search for the next skill key by breaking the loop
                if( re.search(regex, job_description) ):
                    occ_vect[key] += 1
                    break

    print("Scanned %d jobs posting (GitHub jobs)." % (num_jobs))

    return occ_vect, companies, num_jobs

def print_stats(occ_vect, num_jobs):
    """
    Given the occurrence vector, prints on terminal the stats.
    """

    sorted_skills = sorted(occ_vect.items(), key=lambda kv: kv[1], reverse=True)
    top15_skills = sorted_skills[:15]
    top15_skills_names = [ x[0] for x in top15_skills]
    top15_skills_values = [int(x[1]) for x in top15_skills]
    print("Analyzed a total of {} jobs".format(num_jobs))
    print("")
    for i in range(15):
        percentage = ( top15_skills_values[i] / num_jobs ) * 100
        print("%20s =\t%d occurrences, present in %.2f%% of the job postings." % (top15_skills_names[i], top15_skills_values[i], percentage))
        
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


#initialize occ_vect to 0
occ_vect = {}
for key in skills.keys():
    occ_vect[key] = 0

companies = {}
num_jobs = 0
occ_vect, companies, total_jobs = stats(skills, companies, occ_vect, num_jobs, '.\Data\jobs_data_github_jobs.txt')
occ_vect, companies, total_jobs = read_stackoverflow(occ_vect, companies, total_jobs)
print_stats(occ_vect, total_jobs)