from time import sleep
import requests
from lcu_driver import Connector
from requests import get
import re
import time
from bs4 import BeautifulSoup
import os
import json

try:
    ver = "v1.4"
    newestPath = "11.8.1"
    config = {
        "provider": "u.gg",
        "autoclose": False,
        "checkfornewver": True
    }

    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    })


    def getConfig():
        global config
        with open("config.json", "r") as op0:
            config = json.load(op0)


    def checkVersion():
        request = get(url="https://raw.githubusercontent.com/ppizzopet/quickrunes/main/version.txt")
        data = request.json()
        if "v" + str(data) == ver:
            return
        else:
            print("New version is available!")
            print("")


    def getLatestPath():
        global newestPath
        request = get(url="https://ddragon.leagueoflegends.com/api/versions.json")
        data = request.json()
        newestPath = data[0]


    try:
        getConfig()
    except:
        print("Can't get config! Using default.")
        print("")

    try:
        getLatestPath()
    except:
        print("Can't get latest path! Using " + newestPath + ".")
        print("")

    print(f" Quick Runes {ver} ")
    print("")
    print("Ready for making runes!")

    champion = ""

    runes = {1: None,
             2: None,
             3: None,
             4: None,
             5: None,
             6: None,
             7: None,
             8: None,
             9: None,
             10: None,
             11: None
             }

    championList = {}

    runesList = {"Attack Speed": 5005,
                 "Adaptive Force": 5008,
                 "Scaling CDR": 5007,
                 "Armor": 5002,
                 "Magic Resist": 5003,
                 "Scaling Bonus Health": 5001}


    def fetchChampionList():
        global championList
        request = get(url=f"http://ddragon.leagueoflegends.com/cdn/{newestPath}/data/en_US/champion.json")
        data = request.json()
        for championName in data["data"]:
            championList.update({int(data["data"][championName]["key"]): str(championName)})


    def fetchRunesList():
        global runesList
        request = get(url=f"http://ddragon.leagueoflegends.com/cdn/{newestPath}/data/en_US/runesReforged.json")
        data = request.json()
        for rune in data:
            runesList.update({rune["name"]: rune["id"]})
            for slot in rune["slots"]:
                for perk in slot["runes"]:
                    runesList.update({perk["name"]: perk["id"]})


    def cleanTags(text):
        tagRE = re.compile(r'<[^>]+>')
        return str(tagRE.sub('', text))


    def getKey(val):
        for key, value in runesList.items():
            if val == value:
                return key


    def fetchRunes():
        global runes
        if config["provider"] == "u.gg":
            request = get(url=f"https://u.gg/lol/championList/{champion}/runes")
            soup = BeautifulSoup(request.content, 'html.parser')

            runes[1] = cleanTags(str(
                soup.find("body").find(class_="rune-tree_v2 primary-tree").find(class_="rune-tree_header").find(
                    class_="perk-style-title")))
            runes[2] = \
            soup.find("body").find(class_="rune-tree_v2 primary-tree").find(class_="perk-row keystone-row").find(
                class_="perks").find(class_="perk keystone perk-active").find("img")["alt"].replace("The Keystone ", "")

            i = 3
            for perk in soup.find("body").find(class_="rune-tree_v2 primary-tree").find_all(class_="perk perk-active"):
                runes[i] = perk.find("img")["alt"].replace("The Rune ", "")
                i += 1

            runes[6] = cleanTags(str(
                soup.find("body").find(class_="secondary-tree").find(class_="rune-tree_v2").find(
                    class_="rune-tree_header").find(
                    class_="perk-style-title")))

            i = 7
            for perk in soup.find("body").find(class_="secondary-tree").find(class_="rune-tree_v2").find_all(
                    class_="perk perk-active"):
                runes[i] = perk.find("img")["alt"].replace("The Rune ", "")
                i += 1

            i = 9
            for perk in soup.find("body").find(class_="rune-tree_v2 stat-shards-container_v2").find_all(
                    class_="shard shard-active"):
                runes[i] = perk.find("img")["alt"].replace("The ", "").replace(" Shard", "")
                i += 1

        elif config["provider"] == "op.gg":
            request = get(url=f"https://na.op.gg/champion/{champion}", headers=headers)
            soup = BeautifulSoup(request.content, 'html.parser')
            keystones = soup.find_all(class_="perk-page__item perk-page__item--mark")
            runes[1] = getKey(
                int(str(keystones[0])[int(str(keystones[0]).find(".png?")) - 4:int(str(keystones[0]).find(".png?"))]))
            runes[6] = getKey(
                int(str(keystones[1])[int(str(keystones[1]).find(".png?")) - 4:int(str(keystones[1]).find(".png?"))]))

            keystonePerk = \
            soup.find(class_="perk-page__item perk-page__item--keystone perk-page__item--active").find("img")["src"]
            runes[2] = getKey(
                int(str(keystonePerk)[int(str(keystonePerk).find(".png?")) - 4:int(str(keystonePerk).find(".png?"))]))
            i = 3
            perkPage = soup.find_all(class_="perk-page__row")
            for j in range(1, 9):
                if perkPage[j].find(class_="perk-page__item perk-page__item--active") is not None:
                    perk = perkPage[j].find(class_="perk-page__item perk-page__item--active").find("img")["src"]
                    runes[i] = getKey(int(str(perk)[int(str(perk).find(".png?")) - 4:int(str(perk).find(".png?"))]))
                    i += 1
                    if i == 6:
                        i = 7
            fragments = soup.find(class_="fragment-page").findAll(class_="active tip")
            i = 9
            for f in fragments:
                sizeOfId = f["src"].find(".png")
                id = str(f["src"])[sizeOfId - 4:sizeOfId]
                runes[i] = getKey(int(id))
                i += 1

        del i


    async def getRTillNot(connection):
        global champion
        con = await connection.request('get', '/lol-champ-select/v1/current-champion')
        jsonid = await con.json()
        if con.status != 404 and jsonid != 0:
            champion = championList[jsonid]
        else:
            time.sleep(4)
            await getRTillNot(connection)


    fetchRunesList()

    fetchChampionList()

    connector = Connector()


    def clear():
        if os.name == 'nt':
            _ = os.system('cls')

        else:
            _ = os.system('clear')


    @connector.ready
    async def connect(connection):
        while True:
            print(" ")
            print("Getting champion...")
            await getRTillNot(connection)

            print(f"Making runes for {champion}... ({config['provider']})")
            fetchRunes()

            print(" ")
            print(runes[1] + " | " + runes[2] + " - " + runes[3] + ", " + runes[4] + ", " + runes[5])
            print(runes[6] + " | " + runes[7] + ", " + runes[8])
            print(runes[9] + " - " + runes[10] + " - " + runes[11])
            print(" ")

            print("Applying runes...")
            request2 = await connection.request('get', '/lol-perks/v1/pages')
            pages = await request2.json()
            page0 = pages[0]
            await connection.request('put', '/lol-perks/v1/pages/' + str(page0["id"]),
                                     data={"name": f"QuickRunes {champion}", "current": True,
                                           "primaryStyleId": runesList[runes[1]],
                                           "selectedPerkIds": [runesList[runes[2]], runesList[runes[3]],
                                                               runesList[runes[4]], runesList[runes[5]],
                                                               runesList[runes[7]], runesList[runes[8]],
                                                               runesList[runes[9]], runesList[runes[10]],
                                                               runesList[runes[11]]],
                                           "subStyleId": runesList[runes[6]]})
            print("Done !")
            print(" ")
            if config["checkfornewver"]:
                try:
                    checkVersion()
                except:
                    print("Unable to check version.")

            sleep(5)
            if config["autoclose"]:
                break
            clear()
            print(f" Quick Runes {ver} ")
            print("")
            print("Ready for making another runes!")


    connector.start()
except Exception as e:
    print(e)
    time.sleep(10)
