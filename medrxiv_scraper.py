import pandas as pd
from bs4 import BeautifulSoup
import requests

class medRxivExtractor:
    def __init__(self,data_folder: str = './data/'):
        self.data_folder = data_folder
    
    def extract_article_text(self, subject_matter : str = 'microbiology'):
        res = requests.get('https://www.medrxiv.org/archive')
        content = res.content
        soup = BeautifulSoup(content)
        
        
        titles = []
        for ix,i in enumerate(soup.find_all('a', {"class": "highwire-cite-linked-title"})):
            titles.append(i.text)
            
        
        hrefs = []
        for i in soup.find_all('span', {"class": "highwire-cite-metadata-doi highwire-cite-metadata"}):
            print(i.text)
            clean_ref = i.text.partition('doi: ')[2]
            hrefs.append(clean_ref.strip()) 
            
        assert len(hrefs) == len(titles),'Number of Article Titles and Articles Link Do Not Match'
        
        mini_dict = {}
        mini_dict['title']=titles
        mini_dict['href']=hrefs
        
        return mini_dict
    
    def access_paper(self, input_dict):
        
        abstracts = []
        
        for ix,href in enumerate(input_dict['href']):
            res = requests.get(href)
            content = res.content
            soup = BeautifulSoup(content)
            
            for ix,i in enumerate(soup.find_all('meta')):
                if len(i['content'])>2000:
                    abstracts.append(i["content"].partition('### Competing Interest Statement')[0])
                    
        abstracts = list(set(abstracts))
        
        try:
            assert len(abstracts) == len(input_dict['href']),f'Warning: # Abstracts != # Links {len(abstracts),len(input_dict['href'])}'
        except Exception as e:
            print(e)
        
        return abstracts
            
            
    def __call__(self):
        return self.extract_article_text()
            
        
            
        