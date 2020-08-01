import json
import requests

header = {
    "Accept": "application/json" ,
    "Content-Type": "application/json" 
}
payload = [{"center": [29.961264, 76.826217],
  "radius": 30,
  "color": "red",
  "strip": [0.5, 0.3, 0.1],
  "trust": 95},
 {"center": [25.961264, 76.826217],
  "radius": 30,
  "color": "red",
  "strip": [0.5, 0.3, 0.1],
  "trust": 86},
 {"center": [21.961264, 72.826217],
  "radius": 30,
  "color": "red",
  "strip": [0.5, 0.3, 0.1],
  "trust": 3},
 {"center": [39.961264, 77.826217],
  "radius": 30,
  "color": "red",
  "strip": [0.5, 0.3, 0.1],
  "trust": 13},
 {"center": [32.961264, 71.826217],
  "radius": 30,
  "color": "red",
  "strip": [0.5, 0.3, 0.1],
  "trust": 41},
 {"center": [29.961264, 75.826217],
  "radius": 30,
  "color": "red",
  "strip": [0.5, 0.3, 0.1],
  "trust": 39}]
# response = requests.post('http://127.0.0.1:8000/grid/plot/', headers=header, data=json.dumps(payload)).json()
response = requests.post('http://127.0.0.1:8000/grid/', data=json.dumps(payload))
print(response.json())

