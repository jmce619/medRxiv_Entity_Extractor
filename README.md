# medRxiv_Entity_Extractor

We are developing a system to automate the retrieval of clinical trial results from recent submissions to the medRxiv research paper archive.

Since the nature of the publicates varies in language structure and methodology presentation (as it is published by different authors, universities, etc..), we are implementing various entity recognition approaches to pick up pertinent data.

## Background

The problem: We want to scrape the most recent submissions and gather results from "Results" sections and/or Tables reporting results.

The challenge: Result sections are written differently, tables are displayed differently, methodologies are different, etc.. We need a find a way to normalize/group similar results. As an initial challenge - we are going to train an Entity Recognition model to pick up on methodologies, subject matter - anything consisten we think our tuned transformer can pick up on after decent labeling.

We are also going to extract tables from the full paper pdfs via a couple methods. One using tabula , and one will be using layoutMLv3. Both of these methods will input the pdf tables into dataframes which can be manipulated and sent to our Cloud Platform.

### Structure of medRxiv archive listings page

<p float="left">
  <img src="./img/main1.png" width="250" />
  <img src="./img/main2.png" width="250" /> 
  <img src="./img/main3.png" width="250" />
</p>
We can loop through each html element and create a dataframe to work with.

```
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
```
<p float="center">
    <img src="./img/df12.png" width="700"/>
</p>

### Structure of medRxiv paper summary

<p float="left">
  <img src="./img/article5.png" width="300"/>
  <img src="./img/article6.png" width="300"/>
</p>

We will train a custom NER model to pick up on concepts, methods, and study results.

### NER Annotator Tool

My go to tool is Tecoholic's NER annotator that I use consistently.

<p float="left">
  <img src="./img/tool2.png" width="300"/>
  <img src="./img/tool3.png" width="300"/>
</p>


### Look inside full pdf papers

<p float="center">
  <img src="./img/paper1.png" width="200" />
  <img src="./img/paper2.png" width="200" /> 
  <img src="./img/paper3.png" width="200" />
</p>



### Example tables from papers

<p float="left">
  <img src="./img/table1.png" width="250" />
  <img src="./img/table2.png" width="250" /> 
  <img src="./img/table3.png" width="250" />
</p>
