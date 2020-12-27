# Quick and Dirty CocktailDB ripper
# imports into database
# see the sql file in repo
# have fun

# BSD 2-Clause License
#
# Copyright (c) 2020, tomgrassmann
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import json
import os
import requests
from pathlib import Path
from types import SimpleNamespace
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="YOUR-USER",
  password="YOUR-PASS",
  database="YOUR-DB"
)

def getIngredientId(iname):
    mycursor = mydb.cursor()
    sql = "SELECT * FROM ingredients WHERE name = \""+ iname.strip() +"\""
    mycursor.execute(sql)
    res = mycursor.fetchall()
    if mycursor.rowcount == 0:
        mycursor = mydb.cursor()

        sql = "INSERT INTO ingredients (name, alternative, role) VALUES (%s, %s, %s)"
        val = (iname.strip(), "NULL", "NULL")
        mycursor.execute(sql, val)
        mydb.commit()
        return mycursor.lastrowid
    else:
        return res[0][0]

def nowInsert(name, zutaten, rezept, type, glass, isAlk, tags):
    # Insert Drink
    mycursor = mydb.cursor()

    sql = "INSERT INTO drinks (name, isAlcoholic, recept, glass, type, image, credits) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (name, isAlk, rezept, glass, type, "NULL", "Ripped from www.thecocktaildb.com")
    mycursor.execute(sql, val)
    mydb.commit()
    DRINKID = mycursor.lastrowid
    # Drink inserted
    # Now Tag the Drink
    for tag in tags:
        mycursor = mydb.cursor()
        sql = "INSERT INTO tags (drinkid, tag) VALUES (%s, %s)"
        val = (DRINKID, tag)
        mycursor.execute(sql, val)
        mydb.commit()
    # Drink is tagged, now magic with ingredients
    for stuff in zutaten:
        zid = getIngredientId(stuff[0])
        mycursor = mydb.cursor()
        sql = "INSERT INTO DrinkIngredients (drinkid, ingredientid, menge) VALUES (%s, %s, %s)"
        val = (DRINKID, zid, stuff[1])
        mycursor.execute(sql, val)
        mydb.commit()

    return

def prepareForInsert(drink):
    name    = drink.strDrink
    zutaten = list()
    tags    = [] if drink.strTags is None else drink.strTags.split(",")
    glass   = "N/A" if drink.strGlass is None else drink.strGlass
    type    = "N/A" if drink.strCategory is None else drink.strCategory
    rezept  = drink.strInstructions
    isAlk   = 1 if drink.strAlcoholic == "Alcoholic" else 0

    for ing in range(1, 16):
        if getattr(drink, "strIngredient"+str(ing)) is None:
            continue
        else:
            iname = getattr(drink, "strIngredient"+str(ing))
            imeas = "N/A" if getattr(drink, "strMeasure"+str(ing)) is None else getattr(drink, "strMeasure"+str(ing))
            zutaten.append([iname, imeas])


    print("Importing ... " + str(name) + "\n")
    nowInsert(name, zutaten, rezept, type, glass, isAlk, tags)


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
        elCocktailObj = json.loads(elCocktailReq.content, object_hook=lambda d: SimpleNamespace(**d))
        prepareForInsert(elCocktailObj.drinks[0])
        print("Got " + str(len(allTheCocktails)) + " cocktails and countin ...")
