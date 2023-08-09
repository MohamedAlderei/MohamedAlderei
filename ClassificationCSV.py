from datetime import datetime
import requests
import time
import json
import csv
from urllib.parse import urlencode, urljoin
import os



# Function to store processed incident numbers to a file

def store_processed_incidents(incident_numbers):
    with open('processed_incidents.txt', 'a') as file:
        for number in incident_numbers:
            file.write(number + '\n')

# Function to get the set of processed incident numbers from a file


def get_processed_incidents():
    try:
        with open('processed_incidents.txt', 'r') as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()


# Function to classify incidents using the given endpoint

def classify_incidents(incidents):
    url = "https://apigtw.nonprod.azure.adia.ae/azfnaaoin0001-dev/1.0/LogAnalyticsAOINonProd"
    headers = {
        "Ocp-Apim-Subscription-Key": "7cba9ff1a77444b9b0096ed8faa50f20",
        "Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyJ9.eyJhdWQiOiIyNWMzMWI1OS01N2E5LTQ3MmMtODQ5ZC1hM2JhYmUyNjI0ZmYiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vODUwNmM2OWYtMDA1ZC00MjFiLWI2NzAtOWE4Y2NkNWFlZTYzL3YyLjAiLCJpYXQiOjE2OTE1NTcyNzUsIm5iZiI6MTY5MTU1NzI3NSwiZXhwIjoxNjkxNTYyMjI5LCJhaW8iOiJBVVFBdS84VUFBQUFJZEFJbEplQW5hOFVLRVJpa1FLdG91STRyV0VOOWJsbk5tMkt3NU4xeFh0UUNaZ0c4UFdKUEk2eWxjN0w5cW5kMkhwY2tVWUZ1M0JNZUU1WTZlVHJmZz09IiwiYXpwIjoiMjVjMzFiNTktNTdhOS00NzJjLTg0OWQtYTNiYWJlMjYyNGZmIiwiYXpwYWNyIjoiMCIsImVtYWlsIjoiTW9oYW1lZC5BbERlcmVpQGFkaWEuYWUiLCJuYW1lIjoiTW9oYW1lZCBIdW1haWQgQWxEZXJlaSIsIm9pZCI6IjQ3OWRlNWQ4LWMwYmQtNGU3NC04ODc5LWJhZjVlYTNlMjQzZiIsInByZWZlcnJlZF91c2VybmFtZSI6Ik1vaGFtZWQuQWxEZXJlaUBhZGlhLmFlIiwicmgiOiIwLkFUa0FuOFlHaFYwQUcwSzJjSnFNelZydVkxa2J3eVdwVnl4SGhKMmp1cjRtSlA4NUFCMC4iLCJyb2xlcyI6WyJnLWFwcC1BT0ktTm9uUHJvZEdlbmVyYWxVc2VyIl0sInNjcCI6IlVzZXIuUmVhZCIsInN1YiI6IjdFd1dyaTZ6MmNZM0ZHOTdqTWpPZm9MckVuc3NzcmkzQ0RicUEycU5QT2ciLCJ0aWQiOiI4NTA2YzY5Zi0wMDVkLTQyMWItYjY3MC05YThjY2Q1YWVlNjMiLCJ1cG4iOiJNb2hhbWVkLkFsRGVyZWlAYWRpYS5hZSIsInV0aSI6InNFMnB1R0dQeUVLXzZROWN3YVdwQUEiLCJ2ZXIiOiIyLjAifQ.MXD9mzFnBREciuArMb-i20YBHQ6lK7aXvA5gqR4SLoNJsettRqZrzDqpQ71A5FfVSeTBMuumSEOdCGde2wSOuVLgb6KgLcLaJN-nv3x-FE7Psm5eL6Du9I66sV5lDHKyrhnfWFlUcSFB_QCEmYXQYXMAdnTl-JypXXQ2RVZercP9E3bYl8cYP7ruLlzK-OTFbvwnLKbzig_jPknjTol452zJzcN_H6PkirtmD_4PPGPxUvX32OmJXFod9VFjuiIpYlRT8dWRIZdfFGwkHGWBsMq_ApFhQb-ewgngKX2EhsKh_h2rKY6GVJ9cq2GPL6ocbNFk44EyH_Me4uQfqtnEow",
        "instanceName": "azcgaoin0001"
    }   

    # Prepare the list of incidents with required fields

    incident_list = []
    for incident in incidents:
        incident_list.append({'Incident number': incident['number'], 'Description': incident['description']})
   
    # Prepare the JSON prompt for the classification request

    prompt = {
        "prompt": "Please classify incidents using these 4 classes (Batch Job Error, Access Errors, System and software Error, File related issues) and give a breif summary of the description with fieldnames Incident number, Class, and Summary and remove the description in machine readable JSON format)",
        "incidents": incident_list
    }   

    # JSON payload for the request
    payload = {
        "prompt": json.dumps(prompt),
        "model": "NonProd_text-davinci-003",
        "tokens": 1000,
        "temp": 0.1,
        "rawResponse": "True",
        "confidential": "True"
    }

    # Send a POST request to classify the incidents
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            classified_incidents = json.loads(response.text)
            file_exists = os.path.isfile('classified_incidents.csv')
            with open('classified_incidents.csv', 'a', newline='') as csvfile:
                fieldnames = ['Incident number', 'Class', 'Summary']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                for incident in classified_incidents:
                    writer.writerow({'Incident number': incident['Incident number'], 'Class': incident['Class'], 'Summary': incident['Summary']})
            print('Classified incidents written to CSV file', response.text)
            return classified_incidents
        except json.decoder.JSONDecodeError:
            print("Failed to decode JSON. Response:", response.text)
            return None
    else:
        print("Error in classification:", response.text)
        return None
        
def fetch_incidents_from_servicenow():
    username = 'Power.BI'
    password = 'Test100z!'
    base_url = 'https://adia.service-now.com/api/now/table/incident'
    query_params = {'sysparm_query': 'business_service=db7e471f1b6a05104b6b6573604bcb29^state=1^ORstate=2^ORstate=3^ORDERBYDESCsys_created_on', 
                    'sysparm_display_value': 'true', 'sysparm_fields': 'number,description,sys_created_on,state,business_service', 
                    'sysparm_limit': '1', 
                    'sysparm_order_by': 'sys_created_on'
                    }
    url = urljoin(base_url, '?' + urlencode(query_params))
    auth = (username, password)
    processed_incidents = get_processed_incidents()

    try:
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            incidents = response.json()['result']
            new_incidents = [incident for incident in incidents if incident['number'] not in processed_incidents]
            if new_incidents:
                print("Fetched incidents:")
                new_incident_numbers = []
                for incident in new_incidents:
                    incident_info = f"Incident Number: {incident['number']}\nDescription: {incident['description']}\n"
                    print(incident_info)
                    new_incident_numbers.append(incident['number'])
                store_processed_incidents(new_incident_numbers)
                classify_incidents(new_incidents) # Call the classify_incidents function with the new incidents

        else:
            print(f"Failed to fetch incidents. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching incidents: {e}")

if __name__ == "__main__":
    interval_seconds = 10
    while True:
        fetch_incidents_from_servicenow()
        time.sleep(interval_seconds)




    
