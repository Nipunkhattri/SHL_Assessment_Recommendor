import requests
import json
from bs4 import BeautifulSoup
import time

def get_total_pages(soup, table_type):
    """Get total number of pages for a table type"""
    pagination = soup.find_all('ul', class_='pagination')[table_type]
    last_page = pagination.find_all('li', class_='pagination__item')[-2]
    return int(last_page.text.strip())

def get_assessment_details(url):
    """Get assessment details from individual assessment page"""
    try:
        # print(f"Fetching details for URL: {url}")
        full_url = f"https://www.shl.com{url}"
        response = requests.get(full_url)
        details = {
            'duration': 'Not specified',
            'description': 'Not specified',
            'url': full_url
        }
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            duration_divs = soup.find_all('div', class_='product-catalogue-training-calendar__row typ')
            
            for div in duration_divs:
                heading = div.find('h4')
                if heading:
                    if 'Assessment length' in heading.text:
                        duration_text = div.find('p').text.strip()
                        if "minutes" in duration_text.lower():
                            details['duration'] = duration_text.split('=')[-1].strip() + " minutes"
                    if 'Description' in heading.text:
                        description_text = div.find('p').text.strip()
                        details['description'] = description_text
        
        return details
    except Exception as e:
        print(f"Error fetching details: {e}")
        return {
            'duration': 'Not specified',
            'description': 'Not specified',
            'url': full_url
        }

def scrape_table(soup):
    """Scrape single table data"""
    assessments = []
    rows = soup.find_all('tr')[1:]  
    
    for row in rows:
        print(f"Processing row: {row}")
        assessment = {}
        
        title_cell = row.find('td', class_='custom__table-heading__title')
        if title_cell and title_cell.find('a'):
            title_link = title_cell.find('a')
            assessment['name'] = title_link.text.strip()
            
            assessment_url = title_link.get('href')
            details = get_assessment_details(assessment_url)
            assessment.update(details)
            
            remote_cell = row.find_all('td', class_='custom__table-heading__general')[0]
            assessment['RemoteTesting'] = 'Yes' if remote_cell.find('span', class_='catalogue__circle -yes') else 'No'
            
            adaptive_cell = row.find_all('td', class_='custom__table-heading__general')[1]
            assessment['Adaptive/IRT Support'] = 'Yes' if adaptive_cell.find('span', class_='catalogue__circle -yes') else 'No'
            
            test_type_cell = row.find_all('td', class_='custom__table-heading__general')[-1]
            test_types = test_type_cell.find_all('span', class_='product-catalogue__key')
            assessment['TestTypes'] = [type_span.text.strip() for type_span in test_types]
            
            # print(f"Assessment found: {assessment}")
            assessments.append(assessment)
    
    return assessments

def scrape_shl_catalog():
    base_url = "https://www.shl.com/solutions/products/product-catalog/"
    all_assessments = []
    
    page = 1
    while True:
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?start={(page-1)*12}"
            
        print(f"Scraping page {page}")
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if page == 1:
            total_pages = get_total_pages(soup, 0)
        
        print(f"Total pages: {total_pages}")
        
        tables = soup.find_all('div', class_='custom__table-responsive')
        for table in tables:
            page_assessments = scrape_table(table)
            all_assessments.extend(page_assessments)
        
        if page == total_pages:
            break
            
        page += 1

    # print(all_assessments)
    
    with open("assessments.json", "w", encoding='utf-8') as f:
        json.dump(all_assessments, f, indent=2, ensure_ascii=False)

    print(f"Total assessments scraped: {len(all_assessments)}")

if __name__ == "__main__":
    scrape_shl_catalog()
    print("Scraping completed and data saved to assessments.json.")