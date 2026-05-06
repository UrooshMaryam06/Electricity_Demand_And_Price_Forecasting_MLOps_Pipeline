import requests

with open('energy_dataset.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://127.0.0.1:8000/upload/dataset', files=files)
    print(response.json())
