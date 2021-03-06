from time import sleep
from lcu_driver import Connector
from requests import get
import re
from bs4 import BeautifulSoup
from sys import exit

print(" Quick Runes v1.2 ")
print("")

champion = ""

champions = {}

runeslist = {"Attack Speed": 5005,
             "Adaptive Force": 5008,
             "Scaling CDR": 5007,
             "Armor": 5002,
             "Magic Resist": 5003,
             "Scaling Bonus Health": 5001}

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



def fetchChampionsList():
    global champions
    request = get(url="http://ddragon.leagueoflegends.com/cdn/10.25.1/data/en_US/champion.json")
    data = request.json()
    for championname in data["data"]:
        champions.update({int(data["data"][championname]["key"]): str(championname)})

def fetchRunesList():
    global runeslist
    request = get(url="http://ddragon.leagueoflegends.com/cdn/10.25.1/data/en_US/runesReforged.json")
    data = request.json()
    for rune in data:
        runeslist.update({rune["name"]: rune["id"]})
        for perk in rune["slots"]:
            for perk in perk["runes"]:
                runeslist.update({perk["name"]: perk["id"]})


def cleantags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return str(TAG_RE.sub('', text))


def fetchRunes(champion):
    global runes
    request = get(url=f"https://u.gg/lol/champions/{champion}/runes")
    soup = BeautifulSoup(request.content, 'html.parser')

    runes[1] = cleantags(str(
        soup.find("body").find(class_="rune-tree_v2 primary-tree").find(class_="rune-tree_header").find(
            class_="perk-style-title")))
    runes[2] = soup.find("body").find(class_="rune-tree_v2 primary-tree").find(class_="perk-row keystone-row").find(
            class_="perks").find(class_="perk keystone perk-active").find("img")["alt"].replace("The Keystone ", "")

    i = 3
    for perk in soup.find("body").find(class_="rune-tree_v2 primary-tree").find_all(class_="perk perk-active"):
        runes[i] = perk.find("img")["alt"].replace("The Rune ", "")
        i += 1

    runes[6] = cleantags(str(
        soup.find("body").find(class_="secondary-tree").find(class_="rune-tree_v2").find(class_="rune-tree_header").find(
            class_="perk-style-title")))

    i = 7
    for perk in soup.find("body").find(class_="secondary-tree").find(class_="rune-tree_v2").find_all(class_="perk perk-active"):
        runes[i] = perk.find("img")["alt"].replace("The Rune ", "")
        i += 1

    i = 9
    for perk in soup.find("body").find(class_="rune-tree_v2 stat-shards-container_v2").find_all(class_="shard shard-active"):
        runes[i] = perk.find("img")["alt"].replace("The ", "").replace(" Shard", "")
        i += 1

    del i



fetchRunesList()

fetchChampionsList()

connector = Connector()


@connector.ready
async def connect(connection):
    global champion

    try:
        request1 = await connection.request('get', '/lol-champ-select/v1/current-champion')
    except:
        print("Can’t get lobby id, try again later.")
        exit(0)

    try:
        champion = champions[await request1.json()]
    except:
        print("You haven't picked champion yet or you aren't in the lobby, try again later.")
        exit(0)

    print(f"Making runes for {champion}...")
    fetchRunes(champion)

    print(" ")
    print(runes[1] + " | " + runes[2] + " - " + runes[3] + ", " + runes[4] + ", " + runes[5])
    print(runes[6] + " | " + runes[7] + ", " + runes[8])
    print(runes[9] + " - " + runes[10] + " - " + runes[11])
    print(" ")

    print("Applying runes...")
    request2 = await connection.request('get', '/lol-perks/v1/pages')
    pages = await request2.json()
    page0 = pages[0]
    await connection.request('put', '/lol-perks/v1/pages/' + str(page0["id"]), data={"name": "QuickRunes",
        "current": True, "primaryStyleId": runeslist[runes[1]], "selectedPerkIds": [runeslist[runes[2]],
        runeslist[runes[3]], runeslist[runes[4]], runeslist[runes[5]], runeslist[runes[7]], runeslist[runes[8]],
            runeslist[runes[9]], runeslist[runes[10]], runeslist[runes[11]]], "subStyleId": runeslist[runes[6]] })

    print("Done !")

    sleep(5)

try:
    connector.start()
except:
    print("Some error occurred, try again later.")