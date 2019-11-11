from flask import Flask
from bs4 import BeautifulSoup
import requests

app = Flask(__name__, subdomain_matching=True)

def getPage():
    return BeautifulSoup(requests.get('https://teamtrees.org').content, 'html.parser')

@app.route('/', subdomain='api')
def get_trees():
    page = getPage()
    treecount = page.select('#totalTrees')[0]['data-count']
    return treecount


@app.route('/')
def index():
    return 'Home'


app.config['SERVER_NAME'] = 'localhost:443'
app.run()
