from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sqlite3


def get_paper_info(paper):
    title_element = paper.find('a', class_='gsc_a_at')
    if title_element is None:
        return None
    title = title_element.text
    author_and_place_published = paper.find('div', class_='gs_gray').text
    #date_match = re.search(r'\d{4}', author_and_place_published)
    #if not date_match:
    #    return None
    #date = date_match.group()
    #print(date)
    #authors = author_and_place_published[:author_and_place_published.rfind(date)].strip()
    #print(authors)
    #place_published = ""
    #place_published_element = paper.find_all('div', class_='gs_gray')[1]
    #if place_published_element:
        #place_published = place_published_element.text.replace(date, "").strip()

    citations_element = paper.find('a', class_='gsc_a_ac')
    citations = int(citations_element.text) if citations_element and citations_element.text else 0

    return {
        'title': title,
        #'date': date,
       # 'authors': authors,
       # 'place_published': place_published,
        'citations': citations
    }


def update_citations(database_path, papers):
    # Connect to the database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    for paper in papers:
        # Use the whole title for matching
        title = paper['title']

        # Create the SQL string
        sql_string = "UPDATE entries SET cite = ? WHERE title = ?"
        
        # Print the SQL string and parameters for debugging purposes
        print(f"Executing SQL: {sql_string} with parameters: ({paper['citations']}, {title})")

        # Update the citation number using the whole title
        cursor.execute(
            sql_string,
            (paper['citations'], title)
        )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def update_citations_2(database_path, papers):
    # Connect to the database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    for paper in papers:
        # Create a pattern using the first 8 words of the title
        title_pattern = ' '.join(paper['title'].split()[:8])

        # Fetch the current citation count for the paper from the database
        cursor.execute("SELECT cite FROM entries WHERE title LIKE ?", (f"%{title_pattern}%",))
        result = cursor.fetchone()

        if result:
            current_citations = result[0]

            # Update the citation count only if the new count is larger than the current count
            if paper['citations'] > current_citations:
                # Create the SQL string
                sql_string = "UPDATE entries SET cite = ? WHERE title LIKE ?"

                # Print the SQL string and parameters for debugging purposes
                print(f"Executing SQL: {sql_string} with parameters: ({paper['citations']}, {title_pattern})")

                # Update the citation number using the title pattern
                cursor.execute(
                    sql_string,
                    (paper['citations'], f"%{title_pattern}%")
                )
            else:
                print(f"Skipping update for '{title_pattern}' as the new citation count ({paper['citations']}) is not larger than the current count ({current_citations})")
        else:
            print(f"Paper with title pattern '{title_pattern}' not found in the database")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def download_papers(user_id):
    url = f'https://scholar.google.com/citations?user={user_id}&hl=en&cstart=0&pagesize=100'
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    papers = soup.find_all('tr', class_='gsc_a_tr')
    paper_data = [get_paper_info(paper) for paper in papers]
    paper_data = list(filter(None, paper_data))
    return paper_data

if __name__ == '__main__':
    user_id = 'DDLTYpAAAAAJ'
    papers = download_papers(user_id)
    print(papers)
    database_path = "./information_.db"
    update_citations_2(database_path, papers)
