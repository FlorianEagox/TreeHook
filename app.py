from flask import Flask
from flask import request
from bs4 import BeautifulSoup
import requests
import json


app = Flask(__name__, subdomain_matching=True)

def getPage():
    return BeautifulSoup(requests.get('https://teamtrees.org').content, 'html.parser')

@app.route('/', subdomain='api')
def get_trees():
    page = getPage()
    treecount = page.select_one('#totalTrees')['data-count']
    return treecount


@app.route('/donations', subdomain='api')
def get_new_doners():
    page = getPage()
    donations_tag = page.select(('#top-donations' if request.args.get('top') else '#recent-donations') + ' .media')
    print(donations_tag)
    donations = []
    for donation in donations_tag:
        donations.append({
            'name': donation.select_one("strong").get_text(),
            'treeCount': int(donation.select_one(".feed-tree-count").get_text().split(" ")[0].replace(',', '')),
            'message': donation.select_one(".medium").get_text()
        })
    return json.dumps(donations)

@app.route('/')
def index():
    return 'Home'


app.config['SERVER_NAME'] = 'localhost:443'
app.run()
