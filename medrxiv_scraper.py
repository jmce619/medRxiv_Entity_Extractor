import pandas as pd
from bs4 import BeautifulSoup
import requests
from pypdf import PdfReader
import io
from tabula import read_pdf


class medRxivExtractor:
    def __init__(self,data_folder: str = './data/'):
        self.data_folder = data_folder
    
    def extract_article_text(self):

        res = requests.get('https://www.medrxiv.org/archive')
        content = res.content
        soup = BeautifulSoup(content)

        a = soup.find_all('a', {"class": "highwire-cite-linked-title"})
        b = soup.find_all('span',{"class":'highwire-citation-authors'})
        c = soup.find_all('span', {"class": "highwire-cite-metadata-doi highwire-cite-metadata"})

        assert len(a) > 0, 'No Articles Found'
        assert len(a) == len(b) == len(c), 'Mismatched article metadata'

        list_dict = []
        for ix,(i,j,k) in enumerate(zip(a,b,c)):
            list_dict.append({'title':i.text,'authors':j.text,'href':k.text.partition('doi: ')[2].strip().replace('doi.org','www.medrxiv.org/content') +'v1','full_pdf':k.text.partition('doi: ')[2].strip().replace('doi.org','www.medrxiv.org/content') + 'v1.full.pdf'})

        return pd.DataFrame(list_dict)
    
    def access_archive_listing(self, input_df):
        
        abstracts = []  
        for ix,href in enumerate(input_df['href']):
            res = requests.get(href)
            content = res.content
            soup = BeautifulSoup(content)
            for ix,i in enumerate(soup.find_all('div',{"class":"section abstract"})):
                abstracts.append(i.text.partition('Abstract')[2].replace('\n',''))

        abstracts = list(set(abstracts))
        
        try:
            assert len(abstracts) == len(input_df['href']),f"Warning: # Abstracts != # Links {len(abstracts),len(input_df['href'])}"
        except Exception as e:
            print(e)
            
        input_df['abstracts'] = abstracts
        
        return input_df

    def extract_pdf_tables(self, input_df):

        full_tables = []
        for i in input_df['full_pdf']:
            tables = []
            dfs = read_pdf(i, pages='all')
            for table in dfs:
                tables.append(table)
            full_tables.append(tables)
        input_df['tables'] = full_tables

        return input_df
    
    def extract_abstract_entities(self,input_df):
    
        concepts_batch = []
        summary_batch = []
        method_batch = []
        conclusion_batch = []
        confidence_intervals_batch = []
        results_batch = []

        for i in input_df['abstract']:

            concepts = []
            summary = ''
            method = ''
            conclusion = ''
            confidence_intervals = []
            results = []

            doc1 = abstract_ner_model(i)

            #displacy.render(doc1,style = 'ent')

            for j in doc1.ents:
                if j.label_ == 'CONCEPT':
                    concepts.append(j.text)

                if j.label_ == 'METHOD_SUMM':
                    method += j.text

                if j.label_ == 'STUDY_SUMM':
                    summary += j.text

                if j.label_ == 'CONC_SUMM':
                    conclusion += j.text

                if j.label_ == 'RESULTS':
                    results.append(j.text)

                if j.label_ == 'CONF_INT':
                    confidence_intervals.append(j.text)

            concepts_batch.append(concepts)
            summary_batch.append(summary)
            method_batch.append(method)
            conclusion_batch.append(conclusion)
            confidence_intervals_batch.append(confidence_intervals)
            results_batch.append(results)

        input_df['concepts'] = concepts_batch
        input_df['summary'] = summary_batch
        input_df['method'] = method_batch
        input_df['conclusion'] = conclusion_batch
        input_df['results'] = results_batch
        input_df['confidence_intervals'] = confidence_intervals_batch

        return input_df
            
            
    def __call__(self):
        
        mini_df = self.extract_article_text()
        abstract_df = self.access_archive_listing(mini_df)
        table_df = self.extract_pdf_tables(abstract_df)
        full_df = self.extract_abstract_entities(table_df)

      
        return full_df
        
        
        