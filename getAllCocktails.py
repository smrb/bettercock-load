# Get all the cocktails!
import requests
import json
from types import SimpleNamespace

# yes, this will give us the complete alphabet in lower case
# i dont know why, stole this from the internets
alphabet = list (map (chr, range (97,123)))
allTheCocktails = list()
for idx, letter in enumerate(alphabet): # High Quality API. NaN/10 would void*
    per = 100.0*(int(idx) / int(len(alphabet)))
    print("Searching the alphabet, letter: " + letter + " Progress: "+ str(per) + "%")
    elCocktailReq = requests.get('https://www.thecocktaildb.com/api/json/v1/1/search.php?f=' + letter)
                                                # What?
    elCocktailObj = json.loads(elCocktailReq.content, object_hook=lambda d: SimpleNamespace(**d))

    if elCocktailObj.drinks is None: # it reads nicely, but i would much rather have an exception or some == null wtf python get reked
        continue
    for cocktail in elCocktailObj.drinks:
        allTheCocktails.append(cocktail.idDrink)
        elCocktailReq = requests.get('https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i=' + str(cocktail.idDrink))
        print(str(cocktail.idDrink) + " "+ str(elCocktailReq.content))
        f = open(str(cocktail.idDrink) + ".json", "w")
        f.write(str(elCocktailReq.content))
        f.close()
    print("Got " + str(len(allTheCocktails)) + " cocktails and countin ...")

#    print(x.name, x.hometown.name, x.hometown.id)
#    print(letter)
