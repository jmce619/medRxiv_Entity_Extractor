import pandas as pd
from bs4 import BeautifulSoup
import requests
from pypdf import PdfReader
import io
from tabula import read_pdf


class medRxivExtractor:
    def __init__(self,data_folder: str = './data/'):
        self.data_folder = data_folder
    
    def extract_article_text(self, subject_matter : str = 'microbiology'):
        res = requests.get('https://www.medrxiv.org/archive')
        content = res.content
        soup = BeautifulSoup(content)
        
        
        list_dict = []
        for ix,(i,j,k) in enumerate(zip(soup.find_all('a', {"class": "highwire-cite-linked-title"}),soup.find_all('span',{"class":'highwire-citation-authors'}),soup.find_all('span', {"class": "highwire-cite-metadata-doi highwire-cite-metadata"}))):
            list_dict.append({'title':i.text,'authors':j.text,'href':k.text.partition('doi: ')[2].strip().replace('doi.org','www.medrxiv.org/content') +'v1','full_pdf':k.text.partition('doi: ')[2].strip().replace('doi.org','www.medrxiv.org/content') + 'v1.full.pdf'})


        return pd.DataFrame(list_dict)
    
    def access_archive_listing(self, input_df):
        
        abstracts = []  
        for ix,href in enumerate(input_df['href']):
            res = requests.get(href)
            content = res.content
            soup = BeautifulSoup(content)
            for ix,i in enumerate(soup.find_all('div',{"class":"section abstract"})):
                abstracts.append(i.text.partition('Abstract')[2])

        abstracts = list(set(abstracts))
        
        try:
            assert len(abstracts) == len(input_df['href']),f"Warning: # Abstracts != # Links {len(abstracts),len(input_df['href'])}"
        except Exception as e:
            print(e)
            
        input_df['abstracts'] = abstracts
        
        return input_df

    def extract_pdf_tables(self, input_pdfs):

        full_tables = []
        for i in input_pdfs:
            dfs = read_pdf(i, pages='all')
            for table in dfs:
                full_tables.append(table)

        return full_tables
            
            
    def __call__(self):
        mini_df = self.extract_article_text()
        full_df = self.access_archive_listing(mini_df)
        tables = self.extract_pdf_tables(mini_df['full_pdf'])

            
        return full_df, tables
        
        