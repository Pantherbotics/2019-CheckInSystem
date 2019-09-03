import urllib.request, json 
import time

def getjson(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e: 
        print(e)
        return "ERROR: 404"

while True:
    cts = getjson("http://3863.us/ScannedId.php?psswd=nphs3863&id=000000")
    print(cts["isPresent"])
