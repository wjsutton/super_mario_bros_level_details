import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep

# read csv of all page urls
worlds = pd.read_csv('world_pages.csv')
worlds_pages = worlds['world'].tolist()

# function to turn html tables into dataframes
def tableDataText(table):       
    rows = []
    trs = table.find_all('tr')
    headerow = [td.get_text(strip=True) for td in trs[0].find_all('th')] # header row
    if headerow: # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
    for tr in trs: # for every table row
        rows.append([td.get_text(strip=True) for td in tr.find_all('td')]) # data row
    return rows

# initiate list for dataframes from loop 
level_df = []
enemy_df = []
item_df =[]
gif_list = []

# loop through worlds_pages and extract level map and data tables
for i in range(len(worlds_pages)):
    print(i)
    # add sleep to prevent IP whitelisting
    sleep(30)
    url = worlds_pages[i] 
    
    try:
        page = requests.get(url,timeout = 60)
        
    except requests.ConnectionError as e:
        sleep(5*60)
        page = requests.get(url,timeout = 60)

    except requests.Timeout as e:
        sleep(15*60)
        page = requests.get(url,timeout = 60)

    soup = BeautifulSoup(page.content, 'html.parser')
    
    # find elements from html
    image = [x.get('src') for x in soup.find_all("img")]
    tables = soup.find_all("table",{"class":"wikitable"})
    infobox = soup.find_all("table",{"class":"infobox"})

    # find map image from list of images
    map = [s for s in image if "Map.png" in s]
    if len(map) >1:
        map = map[0]
    gifs = [s for s in image if "gif" in s]
    gif_list.append(gifs)

    # build level dataframe and append map image
    level = tableDataText(infobox[0])
    level = pd.DataFrame(level)
    # reduce data and transpose
    level = level[3:7]
    level = level.transpose()
    # replace headers with first row of data
    level = level.rename(columns=level.iloc[0]).drop(level.index[0])
    level['Map'] = map
    # add url for future joins
    level['url'] = url
    level_df.append(level)

    # build enemies dataframe
    if len(tables) > 0:
        enemies = tableDataText(tables[0])
        enemies = pd.DataFrame(enemies)
        # replace headers with first row of data
        enemies = enemies.rename(columns=enemies.iloc[0]).drop(enemies.index[0])
        # add url for future joins
        enemies['url'] = url
        enemy_df.append(enemies)

    # build items dataframe
    if len(tables) > 1:
        items = tableDataText(tables[1])
        items = pd.DataFrame(items)
        # replace headers with first row of data
        items = items.rename(columns=items.iloc[0]).drop(items.index[0])
        # add url for future joins
        items['url'] = url
        item_df.append(items)

# convert lists of dataframes into one dataframes
level_df = pd.concat(level_df)
enemy_df = pd.concat(enemy_df)
item_df = pd.concat(item_df)
#gif_list = set(gif_list)

gif_df = pd.DataFrame()
gif_df['url'] = gif_list

# writing data to csv
level_df.to_csv('data\\super_mario_bros_levels.csv', encoding="utf-8-sig", index=False)
enemy_df.to_csv('data\\super_mario_bros_enemies.csv', encoding="utf-8-sig", index=False)
item_df.to_csv('data\\super_mario_bros_items.csv', encoding="utf-8-sig", index=False)
gif_df.to_csv('data\\super_mario_bros_gifs.csv', encoding="utf-8-sig", index=False)
