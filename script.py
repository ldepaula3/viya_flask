from flask import Flask, request
import json
import codecs
import requests
import random
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup

baseUrl = "http://seu_ip"

# cat /opt/sas/viya/config/etc/SASSecurityCertificateFramework/tokens/consul/default/client.token
consul = 'seu-client-token';

username = "seu-usuario"
password = "sua-senha"
client_secret = password

# Saved Project 
# Replace it with the same model name you published to MAS
savedProject = 'forest'

app = Flask(__name__)	

@app.route('/')
def main():
	f = codecs.open("index.html", 'r', 'utf-8')
	document = f.read()
	template = """{0}"""
	template = template.format(document)
	return template

def auth():

	urlToken1 = baseUrl + "/SASLogon/oauth/clients/consul?callback=false&serviceId=app"
	tokenFinal = ''
	headers = {
	    "X-Consul-Token": consul
	}

	try:
		firstToken = requests.post(urlToken1, headers=headers).json()["access_token"]
	except requests.exceptions.RequestException as e: 
	    print(e)

	
	urlToken2 = baseUrl + "/SASLogon/oauth/clients"

	headers2 = {
	    "Content-Type" : "application/json",
	    "Authorization": "Bearer " + firstToken
	}

	body = {"client_id": "usuario_oath", "client_secret": client_secret, "scope": ["openid", "*"], "resource_ids": "none", "authorities": ["uaa.none"], "authorized_grant_types": ["password"],"access_token_validity": 36000}

	try:
		secToken = requests.post(urlToken2, data = json.dumps(body), headers=headers2)
	except requests.exceptions.RequestException as e: 
	    print(e)

	urlToken3 = baseUrl + "/SASLogon/oauth/token?grant_type=password&username=" + username + "&password=" + password

	headers3 = {
	    "Content-Type" : "application/x-www-form-urlencoded",
	    "Accept": "application/json"
	}

	try:
		tokenFinal = requests.get(urlToken3, headers=headers3, auth=HTTPBasicAuth('usuario_oath', password)).json()["access_token"]
		print(tokenFinal)
	except requests.exceptions.RequestException as e: 
	    print(e)

	return tokenFinal

@app.route('/process', methods=['POST'])
def view_do_something():

	if request.method == 'POST':
		tokenFinal = auth()

		url = baseUrl + '/microanalyticScore/modules/'+ savedProject +'/steps/score'

		dt = request.json

		if dt["rp_pooled_ind"]:
		   rp_pooled_ind = 'Y'
		else:
		   rp_pooled_ind = 'N'

		mou_onnet_pct_MOM = random.uniform(0.0, 1.0)

		mou_total_pct_MOM = random.uniform(0.0, 1.0)

		payload = {'inputs':[{'name':'Est_HH_Income','value': dt["Est_HH_Income"] * 12},
		                     {'name':'calls_total','value': dt["calls_total"]},
		                     {'name':'data_usage_amt','value': dt["data_usage_amt"]},
		                     {'name':'equip_age','value': dt["equip_age"]},
		                     {'name':'lifestage','value': dt["lifestage"]},
		                     {'name':'mou_onnet_pct_MOM','value': mou_onnet_pct_MOM},
		                     {'name':'mou_total_pct_MOM','value': mou_total_pct_MOM},
		                     {'name':'rp_pooled_ind','value': rp_pooled_ind},
		                     {'name':'sales_channel','value': dt["sales_channel"]}
		                    ]}

		headers = {
		    "Content-Type": "application/json",
		    "Authorization": "Bearer " + tokenFinal}
		
		r = requests.post(url, data=json.dumps(payload), headers=headers).json()
		
		return str(r["outputs"][0]['value'])

	else:
		return "NO OK"

if __name__ == '__main__':
    app.run()