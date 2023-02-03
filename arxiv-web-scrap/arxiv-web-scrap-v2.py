
from selenium import webdriver
import pandas as pd
import tarfile
import os
from urllib import request
import sys
import arxiv
from dataclasses import dataclass

OPTION_NUM_PER_PAGE = 1 # 1: 25, 2: 50, 3: 100, 4: 200  --> possible enumeration
MAX_NUM_PER_PAGE = 25   # choose in base of option_num_per_page

CURRENT_SIZE = 0    # current page size
GIVE_MORE_RESULTS = True
PREV_VERSION = "1"  # the one you want to compare to the latest version

@dataclass
class Search:
    type = ""
    order = ""
    version_max = ""
    papers_id = []
    titles = []
    links_pdf = []
    links_source = []
    links_info = []
    total_results = 0
    remaining_results = 0

website = "https://arxiv.org/search/advanced"
#options = webdriver.FirefoxOptions()
#options.add_argument("--headless")
driver = webdriver.Firefox()
#driver = webdriver.Firefox(options = options)
driver.get(website)

search = Search()

def start():
    q = input("Do you want a (1/2):\n1. Search by keywords\n2. Search for papers with more versions"
                + "\nInsert a number: ")
    if q == "1":
        search.type = "keywords"
        normal_search()
    elif q == "2":
        search.type = "versions"
        versions_search()
    else:
        driver.quit()
        sys.exit("Try again")

def normal_search():
    terms = input("\nEnter keywords for your search: ")
    q1 = input("\nAre you looking for papers of a specific year? (y/n): ")
    if q1 == "y":
        year = input("Enter year (2007-YYYY): ")
        if year.isdigit():
            if int(year) >= 2007: 
                driver.find_element('xpath', '//input[@id="date-year"]').send_keys(year)
            else:
                driver.quit()
                sys.exit("Try again")
        else:
            driver.quit()
            sys.exit("Try again")
    else:
        driver.find_element('xpath', '//input[@id="date-filter_by-0"]').click()

    driver.find_element('xpath', '//input[@id="terms-0-term"]').send_keys(terms)
    driver.find_element('xpath', '//button[@class="button is-link is-medium"]').click()

    search.order = input("\nWhich order do you prefer? Choose an option: \n1. Relevance\n" + 
                    "2. Submission Date (oldest first)\n3. Submission Date (newest first) \n"
                    + "Insert a number: ")

def versions_search():
    year = input("\nEnter a year to start the search (YYYY): ")
    version_max = input("Look for papers with a max number of versions (2-8): ")

    query = year[len(year) - 2:] # take last two digits
    query += "*v" + version_max     # result: YY*vX 

    search.version_max = version_max

    driver.find_element('xpath', '//input[@id="terms-0-term"]').send_keys(query)
    driver.find_element('xpath', '//select[@id="terms-0-field"]/option[9]').click()
    driver.find_element('xpath', '//button[@class="button is-link is-medium"]').click()

    search.order = input("\nWhich order do you prefer? Choose an option: \n1. Relevance\n" + 
                    "2. Submission Date (oldest first)\n3. Submission Date (newest first) \n"
                    + "Insert a number: ")

def choose_order(select_order):
    switcher = {
        '1': driver.find_element('xpath', '//select[@id="order"]/option[5]'),
        '2': driver.find_element('xpath', '//select[@id="order"]/option[4]'),
        '3': driver.find_element('xpath', '//select[@id="order"]/option[3]'),
    }
    return switcher.get(select_order)

def first_page():
    list_size = (driver.find_element('xpath', '/html/body/main/div[1]/div[1]/h1').text).split(" ")[-2]
    list_size = list_size.replace(",", "")
    if list_size.isdigit():
        search.remaining_results = int(list_size) # the full list size
        choose_order(search.order).click()
        driver.find_element('xpath', '//button[@class="button is-small is-link"]').click()
        get_page_size()
        extract_search_results(CURRENT_SIZE) # CURRENT SIZE initialized by get_page_size()
    else:
        driver.quit()
        sys.exit("No results found!")

def get_page_size():
    global CURRENT_SIZE, GIVE_MORE_RESULTS
    driver.find_element('xpath', '//select[@id="size"]/option[' + str(OPTION_NUM_PER_PAGE) + ']').click ()
    driver.find_element('xpath', '//button[@class="button is-small is-link"]').click()
    if search.remaining_results > MAX_NUM_PER_PAGE: 
        CURRENT_SIZE = MAX_NUM_PER_PAGE
        search.remaining_results -= MAX_NUM_PER_PAGE
    else:
        CURRENT_SIZE = search.remaining_results
        # no more elements for next page
        search.remaining_results = 0
        GIVE_MORE_RESULTS = False   

def extract_search_results(size):
    search.total_results += size
    for i in range(1, size+1):
        url_xpath = '/html/body/main/div[2]/ol/li[' + str(i) +']/div/p/a'
        paper_id = (driver.find_elements('xpath', url_xpath)[0].text).split(":")[-1]
        search_paper = next(arxiv.Search(id_list=[paper_id]).results())        
        search.papers_id.append(paper_id)
        search.titles.append(search_paper.title)
        search.links_pdf.append("https://arxiv.org/pdf/" + paper_id + ".pdf")
        search.links_info.append("https://arxiv.org/abs/" + paper_id)
        search.links_source.append("https://arxiv.org/e-print/" + paper_id)
    print("\nDone! " + str(size) + " results found.")

def ask_for_more():
    global GIVE_MORE_RESULTS
    q = input("\nDo you want more results? (y/n): ") 
    if q == "y":
        next_page()
    else:
        GIVE_MORE_RESULTS = False
    
def next_page():
    driver.find_element('xpath', '/html/body/main/div[2]/nav[1]/a[2]').click()
    get_page_size()
    extract_search_results(CURRENT_SIZE)

def create_db():
    results_db = pd.DataFrame({'Paper ID': search.papers_id, 'Title': search.titles, 'Paper Info': search.links_info, 
                    'Link PDF': search.links_pdf, 'Link Source': search.links_source})
    results_db.to_csv('results.csv')
    print(str(search.total_results) + " results saved to results.csv")
    driver.quit()

def ask_download():
    to_download = input("\nDo you want to download the results? (y/n): ") 
    if to_download == "y":
        to_print = input("\nHow many files do you want to download? (1-" + str(search.total_results) + "): ")
        q = input("\nWhat do you want to download? (1/2/3)\n" + "1. PDF version\n2." +
                    " Source code folder\n3. Both (1/2/3)\nInsert number: ")
        if search.type == "versions": 
            q2 = input("\nDo you want to download also version n. " + PREV_VERSION + "? (y/n): ")
            if q2 == "y":
                if q == "1":
                    download_both_pdf(to_print)
                elif q == "2":
                    download_both_source(to_print)
                elif q == "3":
                    download_prev_both(to_print)
                else:
                    sys.exit("Try again")
            else:
                if q == "1":
                    download_pdf(to_print)
                elif q == "2":
                    download_source(to_print)
                elif q == "3":
                    download_both(to_print)
                else:
                    sys.exit("Try again")
    else:
        sys.exit("Bye!")

def download_pdf(to_print):
    for i in range(0, int(to_print)):
        request.urlretrieve(search.links_pdf[i], search.papers_id[i] + ".pdf")
    print("Download complete!")

def download_source(to_print):
    q = input("\nDo you also want to extract the folder? (y/n): ")
    if q == "y":
        for i in range(0, int(to_print)):
            source = request.urlretrieve(search.links_source[i], search.papers_id[i] + ".tar.gz")
            extract(source[0])
        print("Download and extraction complete!")
    else:
        for i in range(0, int(to_print)):
            request.urlretrieve(search.links_source[i], search.papers_id[i] + ".tar.gz")
        print("Download complete!")
    
def download_both(to_print):
    for i in range(1, int(to_print)+1):
        request.urlretrieve(search.links_pdf[i], search.papers_id[i] + ".pdf")
        request.urlretrieve(search.links_source[i], search.papers_id[i] + ".tar.gz")

def extract(filename):
    folder_name = filename.split(".tar.gz")[0]
    with tarfile.open(filename, "r:gz") as tar:
        tar.extractall(path = os.path.join("../jupyter", folder_name))

def get_prev_id(index):
    paper_id = search.papers_id[index]
    if paper_id[len(paper_id) - 2:].isdigit():  # no v in it
        prev_paper_id = paper_id + "v" + PREV_VERSION
        search.papers_id[index] += "v" + search.version_max
    else:
        prev_paper_id = paper_id.replace("v" + search.version_max, "v" + PREV_VERSION)
    return prev_paper_id

def download_both_pdf(to_print):
    for i in range(0, int(to_print)):
        prev_paper_id = get_prev_id(i)
        request.urlretrieve(search.links_pdf[i], search.papers_id[i] + ".pdf")
        request.urlretrieve("https://arxiv.org/pdf/" + prev_paper_id + ".pdf", prev_paper_id + ".pdf")
    print("Download complete!")


def download_both_source(to_print):
    q = input("\nDo you also want to extract the folder? (y/n): ")
    if q == "y":
        for i in range(0, int(to_print)):
            prev_paper_id = get_prev_id(i)
            source1 = request.urlretrieve(search.links_source[i], search.papers_id[i] + ".tar.gz")
            source2 = request.urlretrieve("https://arxiv.org/e-print/" + prev_paper_id, prev_paper_id + ".tar.gz")
            extract(source1[0])
            extract(source2[0])
        print("Download and extraction complete!")
    else:
        for i in range(0, int(to_print)):
            prev_paper_id = get_prev_id(i)
            source1 = request.urlretrieve(search.links_source[i], search.papers_id[i] + ".tar.gz")
            source2 = request.urlretrieve("https://arxiv.org/e-print/" + prev_paper_id, prev_paper_id + ".tar.gz")
        print("Download complete!")


def download_prev_both(to_print):
    for i in range(0, int(to_print)):
        prev_paper_id = get_prev_id(i)
        request.urlretrieve("https://arxiv.org/pdf/" + prev_paper_id + ".pdf", prev_paper_id + ".pdf")
        request.urlretrieve("https://arxiv.org/e-print/" + prev_paper_id, prev_paper_id + ".tar.gz")
        # also add download current version

if __name__ == "__main__":
    start()
    first_page()
    while search.remaining_results > 0 and GIVE_MORE_RESULTS:
        ask_for_more()
    create_db()
    ask_download()
        
