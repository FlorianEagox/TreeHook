from flask import Flask
from flask import request
from bs4 import BeautifulSoup
import requests
import json
import time
import threading
import hashlib

app = Flask(__name__, subdomain_matching=True)
app.config['SERVER_NAME'] = 'localhost:443'

hooks = [{
    "url": "https://webhook.site/49147c97-3619-48b2-bd18-c6f79f584ea4",
    "delay": 1,
    "top": False
}]


def getPage():
    return BeautifulSoup(requests.get('https://teamtrees.org').content, 'html.parser')


@app.route('/', subdomain='api')
def get_trees():
    page = getPage()
    treecount = page.select_one('#totalTrees')['data-count']
    return treecount


@app.route('/donations', subdomain='api')
def get_donations():
    page = getPage()
    donations_tag = page.select(('#top-donations' if bool(request.args.get('top') == 'True') else '#recent-donations') + ' .media')
    donations = []
    for donation in donations_tag:
        donations.append({
            'name': donation.select_one("strong").get_text(),
            'treeCount': int(donation.select_one(".feed-tree-count").get_text().split(" ")[0].replace(',', '')),
            'message': donation.select_one(".medium").get_text()
        })
    return json.dumps(donations)

@app.route('/hooks/add', subdomain='api', methods=['POST'])
def create_hook():
    hook = {
        "url": request.args.get('url'),
        "delay": int(request.args.get('delay')),
        "top": request.args.get('top')
    }
    threading.Thread(target=hook_thread, args=[hook]).start()
    return "Thread created!"


@app.route('/')
def index():
    return 'Home'


def hook_thread(hook):
    request_url = f'http://api.{app.config["SERVER_NAME"]}/donations?top={hook["top"]}'
    previous_donations = requests.get(request_url).text
    while(True):
        time.sleep(hook['delay'])
        new_donations = requests.get(request_url).text
        
        print(str(hash(new_donations)) + " " + str(hash(previous_donations)))
        if not hash(new_donations) == hash(previous_donations):
            diff = []
            previous_donations_object = json.loads(previous_donations)
            for donation in json.loads(new_donations):
                if donation not in previous_donations_object:
                    diff.append(donation)
            requests.get(hook['url'], data=json.dumps(diff))
            previous_donations = new_donations


if __name__ == "__main__":
    threading.Thread(target=app.run).start()
