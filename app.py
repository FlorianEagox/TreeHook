from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests
import json
import time
import threading
from secrets import token_urlsafe

app = Flask(__name__, subdomain_matching=True)
app.config['SERVER_NAME'] = 'localhost:443'
# app.debug = True
hooks = []


def write_hooks():
    with open("hooks.json", 'w+') as file:
        file.write(json.dumps([hook[0] for hook in hooks]))


def get_page():
    return BeautifulSoup(requests.get('https://teamtrees.org').content, 'html.parser')


@app.route('/', subdomain='api')
def get_trees():
    page = get_page()
    treecount = page.select_one('#totalTrees')['data-count']
    return treecount


@app.route('/donations', subdomain='api')
def get_donations():
    page = get_page()
    donations_tag = page.select(('#top-donations' if bool(request.args.get('top') == 'True') else '#recent-donations') + ' .media')
    donations = []
    for donation in donations_tag:
        donations.append({
            'name': donation.select_one("strong").get_text(),
            'treeCount': int(donation.select_one(".feed-tree-count").get_text().split(" ")[0].replace(',', '')),
            'message': donation.select_one(".medium").get_text()
        })
    return json.dumps(donations)

@app.route('/hooks', subdomain='api', methods=['POST', 'DELETE'])
def create_hook():
    if request.method == 'POST':
        hook = {
            "url": request.args.get('url'),
            "delay": int(request.args.get('delay')),
            "top": request.args.get('top'),
            "token": token_urlsafe(24),
            "active": True
        }
        thread = threading.Thread(target=hook_thread, args=[hook])
        thread.start()
        hooks.append((hook, thread))
        write_hooks()
        return hook['token']
    if request.method == 'DELETE':
        try:
            index = [hook['token'] for hook in [hook[0] for hook in hooks]].index(request.args.get('token'))
            hooks[index][0]['active'] = False
            hooks[index][1].join()
            del hooks[index]
            write_hooks()
            return "Deleted " + request.args.get('token')
        except:
            return "Couldn't find token " + request.args.get('token'), 404



@app.route('/')
def index():
    return render_template("index.html")


def hook_thread(hook):
    request_url = f'http://api.{app.config["SERVER_NAME"]}/donations?top={hook["top"]}'
    previous_donations = requests.get(request_url).text
    while(hook['active']):
        time.sleep(hook['delay'])
        new_donations = requests.get(request_url).text
        
        print(str(hash(new_donations)) + " " + str(hash(previous_donations)))
        if not hash(new_donations) == hash(previous_donations):
            diff = []
            previous_donations_object = json.loads(previous_donations)
            for donation in json.loads(new_donations):
                if donation not in previous_donations_object:
                    diff.append(donation)
            result = {
                "newDonations": diff,
                "treeCount": get_trees()
            }
            requests.get(hook['url'], data=json.dumps(result))
            previous_donations = new_donations


if __name__ == "__main__":
    app.run()
    threading.Thread(target=app.run).start()
    with open('hooks.json') as file:
        for hook in json.load(file):
            thread = threading.Thread(target=hook_thread, args=[hook])
            thread.start()
            hooks.append((hook, thread))