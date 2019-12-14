from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_value(html, info_name):
    
    info_value = ''
    
    items = html.select('.product-attributes-list .attribute-label')
    for item in items:
        item_heading = item.get_text().strip()
        try:
            item_next = item.find_next().get_text().strip()
            if info_name == item_heading:
                info_value = item_next
                break
        except:
            pass
      
    return info_value 

def get_details(url):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp
    
    try:
        title = html.select('.product_title')[0].get_text().strip()
        stamp['title'] = title
    except: 
        stamp['title'] = None
        
    try:
        country = html.select('.posted_in a')[0].get_text().strip()
        stamp['country'] = country
    except: 
        stamp['country'] = None    

    try:
        number = html.select('.summary-inner .stock')[0].get_text().strip()
        number = number.replace('in stock','').strip()
        stamp['number'] = number
    except: 
        stamp['number'] = None 

    try:
        price = html.select('.summary-inner .woocommerce-Price-amount')[0].get_text().strip()
        stamp['price'] = price.replace('£', '').strip()
    except: 
        stamp['price'] = None
        
    grouping = ''  
    try:
        counter = 0
        for breadcrumb_item in html.select('.woocommerce-breadcrumb a'):
            if counter > 0:
                if grouping:
                    grouping += ' / ' 
                grouping += breadcrumb_item.get_text().strip()    
            counter = counter + 1
            
        grouping_last = html.select('.breadcrumb-last')[0].get_text().strip()
        grouping += ' / ' + grouping_last
    except:
        pass
    
    try:
        condition_items = html.select('.summary-inner p strong')
        for condition_item in condition_items:
            condition_text = condition_item.get_text().strip() 
            if condition_text == 'Condition:':
                condition = condition_item.parent.get_text().strip()
                
        condition = condition.replace('Condition:', '').strip()        
    except:
        condition = None
    
    stamp['condition'] = condition
    
    stamp['grouping'] = grouping        
        
    stamp['currency'] = 'GBP'

    # image_urls should be a list
    images = []                    
    try:
        image_items = html.select('.wp-post-image')
        for image_item in image_items:
            img = image_item.get('src')
            if img not in images:
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
    
    try:
        raw_text = html.select('#tab-description')[0].get_text().strip()
        stamp['raw_text'] = raw_text.replace('\n', ' ')
    except:
        stamp['raw_text'] = None
        
    if stamp['raw_text'] == None and stamp['title'] != None:
        stamp['raw_text'] = stamp['title']
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    stamp['url'] = url
    
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):

    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('h3.product-title a'):
            item_link = item.get('href')
            if item_link not in items:
                items.append(item_link)
    except:
        pass
    
    try:
        next_url_elem = html.select('a.next')[0]
        if next_url_elem:
            next_url = next_url_elem.get('href')
    except:
        pass   
    
    shuffle(list(set(items)))
    
    return items, next_url

def get_subcategories(url):

    items = []

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item in html.select('.category-link'):
            item_link = item.get('href')
            if item_link not in items:
                items.append(item_link)
    except:
        pass
   
    shuffle(list(set(items)))
    
    return items

item_dict = {
'Commonwealth':'https://www.1st4stamps1840.co.uk/product-category/commonwealth',
'Great Britain':'https://www.1st4stamps1840.co.uk/product-category/great-britain'
    }
    
for key in item_dict:
    print(key + ': ' + item_dict[key])   

selection = input('Choose category: ')
            
category_url = item_dict[selection]
subcategories = get_subcategories(category_url)
for subcategory in subcategories:
    subcategories2 = get_subcategories(subcategory)
    for subcategory2 in subcategories2:
        page_url = subcategory2
        while(page_url):
            page_items, page_url = get_page_items(page_url)
            for page_item in page_items:
                    stamp = get_details(page_item)
