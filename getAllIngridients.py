# Get all the ingridients!
import requests
import json
from types import SimpleNamespace

alphabet = list (range (0,612))
for idx, nr in enumerate(alphabet): # High Quality API. NaN/10 would void*
    per = 100.0*(int(idx) / int(len(alphabet)))
    print("Searching the ingridients, ID: " + str(nr) + " Progress: "+ str(per) + "%")
    elIngridReq = requests.get('https://www.thecocktaildb.com/api/json/v1/1/lookup.php?iid=' + str(nr))
                                                # What?
    elIngridObj = json.loads(elIngridReq.content, object_hook=lambda d: SimpleNamespace(**d))

    if elIngridObj.ingredients is None: # it reads nicely, but i would much rather have an exception or some == null wtf python get reked
        continue

    f = open(str(nr) + ".json", "w")
    f.write(str(elIngridReq.content))
    f.close()
    print("Got " + str(nr) + " ingridients and countin ...")
