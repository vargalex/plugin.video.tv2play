# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcaddon, re, xbmcplugin, json, os, sys, base64, time, locale, random, struct, socket
from resources.lib import client, control
from resources.lib.utils import py2_decode, safeopen

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
    from urllib.parse import quote_plus, quote
else:
    from urlparse import parse_qsl
    from urllib import quote_plus, quote

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')
base_url = "https://tv2play.hu"
api_url = "%s/api" % base_url
auth_url = "%s/authenticate" % api_url
userinfo_url = "%s/users/me" % api_url
logout_url = "%s/logout" % api_url
musorokURL = "https://tv2-prod.d-saas.com/grrec-tv2-prod-war/JSServlet4?&rn=&cid=&ts=%d&rd=0,TV2_W_CONTENT_LISTING,800,[*platform:web;*domain:tv2play;*currentContent:SHOW;*country:HU;*userAge:18;*pagingOffset:%d],[displayType;channel;title;itemId;duration;isExtra;ageLimit;showId;genre;availableFrom;director;isExclusive;lead;url;contentType;seriesTitle;availableUntil;showSlug;videoType;series;availableEpisode;imageUrl;totalEpisode;category;playerId;currentSeasonNumber;currentEpisodeNumber;part;isPremium]"
searchURL = "https://tv2-prod.d-saas.com/grrec-tv2-prod-war/JSServlet4?rn=&cid=&ts=%d&rd=0,TV2_W_SEARCH_RESULT,80,[*platform:web;*domain:tv2play;*query:#SEARCHSTRING#;*country:HU;*userAge:18;*pagingOffset:%d],[displayType;channel;title;itemId;duration;isExtra;ageLimit;showId;genre;availableFrom;director;isExclusive;lead;url;contentType;seriesTitle;availableUntil;showSlug;videoType;series;availableEpisode;imageUrl;totalEpisode;category;playerId;currentSeasonNumber;currentEpisodeNumber;part;isPremium]"
epgURL = "%s/epg/data?date=%%s" % api_url
streamingJwtUrl = "%s/premium/streaming-jwt?playerId=live/%%s" % api_url

try:
    locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
except:
    try:
        locale.setlocale(locale.LC_ALL, "")
    except:
        pass
base_path = py2_decode(control.dataPath)
searchFileName = os.path.join(base_path, "search.history")

def produce_header():
    hungarianIPRanges = [
        "5.38.128.0/17",
        "5.63.192.0/18",
        "5.148.192.0/18",
        "5.187.128.0/17",
        "5.204.0.0/16",
        "5.206.128.0/18",
        "31.46.0.0/16",
        "31.171.224.0/20",
        "37.17.160.0/20",
        "37.76.0.0/17",
        "37.191.0.0/18",
        "37.220.128.0/20",
        "37.220.192.0/18",
        "37.234.0.0/16",
        "46.35.192.0/19",
        "46.107.0.0/16",
        "46.139.0.0/16",
        "46.249.128.0/19",
        "46.251.16.0/20",
        "62.77.208.0/20",
        "62.77.224.0/20",
        "62.100.224.0/19",
        "62.112.192.0/19",
        "62.165.192.0/18",
        "62.201.64.0/18",
        "77.110.128.0/19",
        "77.110.160.0/19",
        "77.111.64.0/19",
        "77.111.96.0/20",
        "77.111.112.0/20",
        "77.111.128.0/18",
        "77.221.32.0/19",
        "77.234.64.0/19",
        "77.242.144.0/20",
        "77.243.208.0/20",
        "78.92.0.0/16",
        "78.108.16.0/20",
        "78.131.0.0/17",
        "78.139.0.0/18",
        "78.153.96.0/19",
        "79.120.128.0/19",
        "79.120.176.0/20",
        "79.120.192.0/19",
        "79.120.224.0/20",
        "79.121.0.0/18",
        "79.121.64.0/19",
        "79.122.0.0/17",
        "79.172.192.0/18",
        "80.64.64.0/20",
        "80.77.112.0/20",
        "80.95.64.0/20",
        "80.95.80.0/20",
        "80.98.0.0/15",
        "80.244.96.0/20",
        "80.249.160.0/20",
        "80.252.48.0/20",
        "81.0.64.0/20",
        "81.16.192.0/20",
        "81.17.176.0/20",
        "81.22.176.0/20",
        "81.93.192.0/20",
        "81.94.176.0/20",
        "81.94.240.0/20",
        "81.160.128.0/17",
        "81.182.0.0/15",
        "82.131.128.0/19",
        "82.131.160.0/20",
        "82.131.224.0/19",
        "82.141.128.0/18",
        "82.150.32.0/19",
        "84.0.0.0/14",
        "84.21.0.0/19",
        "84.206.0.0/16",
        "84.224.0.0/16",
        "84.225.0.0/17",
        "84.225.128.0/18",
        "84.225.192.0/18",
        "84.236.0.0/17",
        "85.66.0.0/15",
        "85.90.160.0/19",
        "85.238.64.0/19",
        "86.59.128.0/17",
        "86.101.0.0/16",
        "86.109.64.0/19",
        "87.97.0.0/18",
        "87.97.64.0/20",
        "87.97.80.0/20",
        "87.97.96.0/19",
        "87.101.112.0/20",
        "87.229.0.0/17",
        "87.242.0.0/18",
        "88.87.224.0/20",
        "88.132.0.0/17",
        "88.132.128.0/18",
        "88.132.192.0/19",
        "88.132.224.0/20",
        "88.209.192.0/18",
        "89.132.0.0/14",
        "89.147.64.0/20",
        "89.148.64.0/18",
        "89.223.128.0/17",
        "89.251.32.0/20",
        "91.82.96.0/19",
        "91.82.192.0/20",
        "91.83.0.0/19",
        "91.83.64.0/20",
        "91.83.160.0/20",
        "91.83.192.0/20",
        "91.83.208.0/20",
        "91.83.224.0/20",
        "91.104.0.0/16",
        "91.120.0.0/16",
        "91.135.112.0/20",
        "91.137.128.0/17",
        "91.144.64.0/18",
        "91.146.128.0/18",
        "91.147.192.0/19",
        "92.52.192.0/19",
        "92.52.224.0/19",
        "92.61.96.0/20",
        "92.61.112.0/20",
        "92.63.240.0/20",
        "92.245.64.0/19",
        "92.249.128.0/17",
        "93.89.160.0/20",
        "94.21.0.0/16",
        "94.27.128.0/17",
        "94.44.0.0/16",
        "94.248.128.0/19",
        "94.248.160.0/20",
        "94.248.192.0/19",
        "94.248.240.0/20",
        "95.168.32.0/19",
        "95.168.64.0/19",
        "95.171.64.0/19",
        "109.61.0.0/18",
        "109.61.64.0/20",
        "109.61.112.0/20",
        "109.74.48.0/20",
        "109.105.0.0/19",
        "109.110.128.0/19",
        "109.199.32.0/19",
        "130.43.192.0/18",
        "130.93.192.0/18",
        "134.255.0.0/17",
        "145.236.0.0/16",
        "146.110.0.0/16",
        "147.7.0.0/16",
        "148.6.0.0/16",
        "149.200.0.0/17",
        "151.0.64.0/18",
        "152.66.0.0/16",
        "157.181.0.0/16",
        "158.249.0.0/16",
        "160.114.0.0/16",
        "171.19.0.0/16",
        "171.31.0.0/16",
        "176.63.0.0/16",
        "176.77.128.0/17",
        "176.226.0.0/17",
        "176.241.0.0/18",
        "178.48.0.0/16",
        "178.164.128.0/17",
        "178.210.224.0/19",
        "178.238.208.0/20",
        "188.6.0.0/16",
        "188.36.0.0/16",
        "188.44.128.0/17",
        "188.127.128.0/19",
        "188.142.128.0/19",
        "188.142.160.0/19",
        "188.142.192.0/18",
        "188.143.0.0/17",
        "188.156.0.0/15",
        "193.6.0.0/16",
        "193.68.32.0/19",
        "193.91.64.0/19",
        "193.224.0.0/16",
        "193.225.0.0/16",
        "194.38.96.0/19",
        "194.88.32.0/19",
        "194.143.224.0/19",
        "194.149.0.0/19",
        "194.149.32.0/19",
        "194.152.128.0/19",
        "194.176.224.0/19",
        "195.38.96.0/19",
        "195.56.0.0/16",
        "195.70.32.0/19",
        "195.111.0.0/16",
        "195.184.0.0/19",
        "195.184.160.0/19",
        "195.199.0.0/16",
        "195.228.0.0/16",
        "212.16.128.0/19",
        "212.24.160.0/19",
        "212.40.64.0/19",
        "212.40.96.0/19",
        "212.48.240.0/20",
        "212.51.64.0/18",
        "212.52.160.0/19",
        "212.92.0.0/19",
        "212.96.32.0/19",
        "212.105.224.0/19",
        "212.108.192.0/18",
        "213.16.64.0/18",
        "213.157.96.0/19",
        "213.163.0.0/19",
        "213.163.32.0/19",
        "213.178.96.0/19",
        "213.181.192.0/19",
        "213.197.80.0/20",
        "213.197.96.0/19",
        "213.222.128.0/18",
        "213.253.192.0/18",
        "217.13.32.0/20",
        "217.13.96.0/20",
        "217.20.128.0/20",
        "217.21.16.0/20",
        "217.27.208.0/20",
        "217.65.96.0/20",
        "217.65.112.0/20",
        "217.79.128.0/20",
        "217.112.128.0/20",
        "217.116.32.0/20",
        "217.144.48.0/20",
        "217.150.128.0/20",
        "217.173.32.0/20",
        "217.197.176.0/20",
    ]
    headers = None
    if control.setting("chooseRandomIP") == "true":
        randomIP = control.setting("randomIP")
        if randomIP == "":
            xbmc.log("TV2Play: Random IP requested and not setted yet. Choosing one IP from Hungarian addresses.", xbmc.LOGINFO)
            randomRange = hungarianIPRanges[random.randrange(len(hungarianIPRanges))]
            xbmc.log("TV2Play: IP Range selected: %s" % randomRange, xbmc.LOGINFO)
            addr, preflen = randomRange.split('/')
            addr_min = struct.unpack('!L', socket.inet_aton(addr))[0]
            addr_max = addr_min | (0xffffffff >> int(preflen))
            randomIP = str(socket.inet_ntoa(struct.pack('!L', random.randint(addr_min, addr_max))))
            control.setSetting("randomIP", randomIP)
            xbmc.log("TV2Play: Using random IP for requests: %s" % randomIP, xbmc.LOGINFO)
        headers = {"X-Forwarded-For": randomIP}
    return headers

headers = produce_header()

def getSearches():
    addDirectoryItem('[COLOR lightgreen]Új keresés[/COLOR]', 'newsearch', '', 'DefaultFolder.png')
    try:
        file = safeopen(searchFileName, "r")
        olditems = file.read().splitlines()
        file.close()
        items = list(set(olditems))
        items.sort(key=locale.strxfrm)
        if len(items) != len(olditems):
            file = safeopen(searchFileName, "w")
            file.write("\n".join(items))
            file.close()
        for item in items:
            addDirectoryItem(item, 'historysearch&search=%s' % item, '', 'DefaultFolder.png')
        if len(items) > 0:
            addDirectoryItem('[COLOR red]Keresési előzmények törlése[/COLOR]', 'deletesearchhistory', '', 'DefaultFolder.png')
    except:
        pass
    endDirectory()

def deleteSearchHistory():
    if os.path.exists(searchFileName):
        os.remove(searchFileName)

def getText(title, hidden=False):
    search_text = ''
    keyb = xbmc.Keyboard('', title, hidden)
    keyb.doModal()

    if (keyb.isConfirmed()):
        search_text = keyb.getText()

    return search_text

def doSearch():
    search_text = getText(u'Add meg a keresend\xF5 film c\xEDm\xE9t')
    if search_text != '':
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        file = safeopen(searchFileName, "a")
        file.write("%s\n" % search_text)
        file.close()
        musorok(searchURL.replace("#SEARCHSTRING#", quote(search_text).replace("%", "%%")))

def main_folders():
    artPath = py2_decode(control.artPath())
    addDirectoryItem("Műsorok", "musorok", os.path.join(artPath, "tv2play.png"), None)
    if hasPremium:
        addDirectoryItem("Élő", "elo", os.path.join(artPath, "live.png"), None)
    addDirectoryItem("Keresés", "search", "", "DefaultAddonsSearch.png")
    r = client.request("%s/channels" % api_url, headers=headers)
    channels = sorted(json.loads(r), key=lambda k:k["id"])
    for channel in channels:
        if channel["slug"] != "spiler2" and (not channel["isPremium"] or hasPremium):
            try:
                logopath = os.path.join(artPath, "%s%s" % (channel["slug"], ".png"))
            except:
                logopath = ''
            addDirectoryItem(channel["name"], 
                            "apisearch&param=%s&ispremium=%s" % (channel["slug"], channel["isPremium"]), 
                            logopath, 
                            logopath,
                            meta={'title': channel["name"]})
    endDirectory(type="")

def musorok(url):
    pageOffset = 0
    allItems = []
    totalResults = 50
    while totalResults >= 50:
        r = client.request(url % (int(time.time()), pageOffset), headers=headers)
        matches=re.search(r'(.*)var data = (.*)};(.*)', r, re.S)
        if matches:
            result = json.loads("%s}" % matches.group(2))
            totalResults = result["recommendationWrappers"][0]["recommendation"]["totalResults"]
            if totalResults > 0:
                allItems.extend(result["recommendationWrappers"][0]["recommendation"]["items"])
        else:
            allItemCnt = 0
            allItems = []
            totalResults = 0
        pageOffset=len(allItems)
        if "SEARCH_RESULT" in url:
            totalResults = 0
    if control.setting('programorder') == '1':
        allItemsSorted=sorted(allItems, key=lambda k: locale.strxfrm("%s%s" % ("000" if k["contentType"] == "SHOW" else "001", (k["title"] if isinstance(k["title"], str) else k["title"].encode("utf-8")).lower())))
    else:
        allItemsSorted = allItems
    for item in allItemsSorted:
        if hasPremium or not "isPremium" in item or item["isPremium"] == "false":
            if item["contentType"] == "SHOW":
                addDirectoryItem(item["title"].encode("utf-8"),
                                 "apisearch&param=%s&ispremium=%s" % (quote_plus(item["url"]), item["isPremium"] if "isPremium" in item else ""),
                                 ("%s/%s" % (base_url, item["imageUrl"]) if "https://" not in item["imageUrl"] else item["imageUrl"]) if "imageUrl" in item else "",
                                 "DefaultFolder.png",
                                 meta={'title': item["title"].encode("utf-8"), 'plot': item["lead"].encode('utf-8') if "lead" in item else ''})
            else:
                addDirectoryItem(item["title"].encode("utf-8"),
                                "playvideo&param=%s&ispremium=%s" % (item["url"], item["isPremium"] if "isPremium" in item else ""),
                                ("%s/%s" % (base_url, item["imageUrl"]) if "https://" not in item["imageUrl"] else item["imageUrl"]) if "imageUrl" in item else "",
                                "DefaultFolder.png",
                                meta={'title': item["title"].encode("utf-8"), 'duration': int(item["duration"]) if "duration" in item else 0, 'plot': item["lead"].encode('utf-8') if "lead" in item else ''}, isFolder=False)
    endDirectory(type="tvshows")

def elo():
    data = json.loads(client.request(epgURL % time.strftime("%Y-%m-%d"), cookie="jwt=%s" % jwtToken, headers = headers))
    lives = []
    for item in data:
        if item["live"]:
            startTime = time.strptime(item["broadcastTime"][11:16], "%H:%M")
            epochTime = time.mktime(startTime)
            epochTime += item["length"]*60
            endTime = time.localtime(epochTime)
            lives.append({"start": startTime, "end": endTime, "title": "%s - %s" % (item["title"], item["titlePart"]), "channel": item["epgChannel"], "thumb": "%s/%s" % (base_url, item["imageUrl"]), "plot": item["text"]})
    sortedLives = sorted(lives, key=lambda x: x["start"])
    for live in sortedLives:
        addDirectoryItem("[COLOR yellow]%02d:%02d-%02d:%02d[/COLOR]: %s" % (live["start"].tm_hour, live["start"].tm_min, live["end"].tm_hour, live["end"].tm_min, live["title"]), "playlive&channel=%s" % live["channel"], live["thumb"], "", meta={"title": live["title"], "plot": live["plot"]}, isFolder=False)
    endDirectory(type="tvshows")

def playLive(channel):
    data = json.loads(client.request(streamingJwtUrl % channel, cookie="jwt=%s" % jwtToken, headers=headers))
    url = data["url"]
    token = data["token"]
    data = json.loads(client.request(url, post=token.encode("utf-8"), headers=headers))
    url = "https:%s" % data["bitrates"]["hls"]
    m3u_url = data['bitrates']['hls']
    m3u_url = re.sub('^//', 'https://', m3u_url)
    if control.setting("useisa") == "true":
        item = control.item(path=m3u_url)
        from inputstreamhelper import Helper
        is_helper = Helper('hls')
        if is_helper.check_inputstream():
            if sys.version_info < (3, 0):  # if python version < 3 is safe to assume we are running on Kodi 18
                item.setProperty('inputstreamaddon', 'inputstream.adaptive')   # compatible with Kodi 18 API
            else:
                item.setProperty('inputstream', 'inputstream.adaptive')  # compatible with recent builds Kodi 19 API
            item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    else:
        from resources.lib import m3u8_parser
        r = client.request(m3u_url, headers=headers)
        root = os.path.dirname(m3u_url)
        sources = m3u8_parser.parse(r)
        try:
            sources.sort(key=lambda x: int(x['resolution'].split('x')[0]), reverse=True)
        except:
            pass

        auto_pick = control.setting('autopick') == '1'

        if len(sources) == 1 or auto_pick == True:
            source = sources[0]['uri']
        else:
            result = xbmcgui.Dialog().select(u'Min\u0151s\u00E9g', [str(source['resolution']) if 'resolution' in source else 'Unknown' for source in sources])
            if result == -1:
                source = sources[0]['uri']
            else:
                source = sources[result]['uri']
        stream_url = root + '/' + source
        item = control.item(path=stream_url)
    control.resolve(int(sys.argv[1]), True, item)

def apiSearchSeason(season):
    r = client.request("%s%s/search/%s" % (api_url, "/premium" if ispremium else "", param), cookie="jwt=%s" % jwtToken if jwtToken else None, headers=headers)
    data = json.loads(r)
    ribbons = []
    index = 0
    plot = ''
    thumb = ''
    if data["contentType"] == "channel":
        ribbons = data["ribbonIds"]
    else:
        if "seasonNumbers" in data and len(data["seasonNumbers"])>0:
            for page in data["pages"]:
                if page["seasonNr"] == season:
                    break
                index+=1
        for tab in data["pages"][index]["tabs"]:
            if tab["tabType"] == "RIBBON":
                ribbons += tab["ribbonIds"]
            if tab["tabType"] == 'SHOW_INFO':
                if plot == '' and "description" in tab["showData"]:
                    plot = tab["showData"]["description"].encode('utf-8')
                if thumb == '' and "imageUrl" in tab["showData"]:
                    thumb = "%s/%s" % (base_url, tab["showData"]["imageUrl"]) if "https://" not in tab["showData"]["imageUrl"] else tab["showData"]["imageUrl"]
    for ribbon in ribbons:
        r = client.request("%s/ribbons/%s" % (api_url, ribbon), cookie="jwt=%s" % jwtToken if jwtToken else None, headers=headers)
        if r:
            data = json.loads(r)
            addDirectoryItem(data["title"].encode("utf-8"),
                            "apiribbons&param=%s&page=0" % data["id"],
                            thumb,
                            "DefaultFolder.png",
                            meta={'title': data["title"].encode("utf-8"), 'plot': plot})
    endDirectory(type="tvshows")

def apiSearch():
    r = client.request("%s%s/search/%s" % (api_url, "/premium" if ispremium else "", param), cookie="jwt=%s" % jwtToken if jwtToken else None, headers=headers)
    data = json.loads(r)
    if "seasonNumbers" in data and len(data["seasonNumbers"])>0:
        if "seo" in data and "description" in data["seo"] and data["seo"]["description"] != None:
            plot = data["seo"]["description"].encode('utf-8')
        else:
            plot = ""
        for season in data["seasonNumbers"]:
            addDirectoryItem("%s. évad" % season, 
                            "apisearchseason&param=%s&page=%s&ispremium=%s" % (param, season, ispremium),
                            '', 
                            "DefaultFolder.png", 
                            meta={'title': "%s. évad" % season, 'plot': plot})
        endDirectory(type="movies")
    else:
        apiSearchSeason(0)


def apiRibbons():
    r = client.request("%s/ribbons/%s/%s" % (api_url, param, page), cookie="jwt=%s" % jwtToken if jwtToken else None, headers=headers)
    data = json.loads(r)
    dirType = 'videos'
    for card in data["cards"]:
        thumb = "%s/%s" % (base_url, card["imageUrl"]) if "https://" not in card["imageUrl"] else card["imageUrl"]
        title = card["title"].encode('utf-8')
        if "contentLength" in card:
            plot = ""
            if control.setting('fillLead') == 'true':
                try:
                    r = client.request("%s%s/search/%s" % (api_url, "/premium" if card["isPremium"] else "", card["slug"]), cookie="jwt=%s" % jwtToken if jwtToken else None, headers=headers)
                    episode = json.loads(r)
                    plot = episode["lead"] if "lead" in episode else ""
                    if plot.startswith("<p>"):
                        plot = plot[3:]
                    if plot.endswith("</p>"):
                        plot = plot[:-4]
                except:
                    pass
            if 'EPISODE' in card['cardType']:
                dirType = 'episodes'
            if 'MOVIE' in card['cardType']:
                dirType = 'movies'
            addDirectoryItem(title, 
                            "playvideo&param=%s&ispremium=%s" % (card["slug"], card["isPremium"]), 
                            thumb, 
                            "DefaultFolder.png", 
                            meta={'title': title, 'duration': int(card["contentLength"]), 'plot': plot}, isFolder=False)
        else:
            if card["cardType"] != "ARTICLE":
                addDirectoryItem(title, 
                                "apisearch&param=%s" % quote_plus(card["slug"]), 
                                thumb, 
                                "DefaultFolder.png", 
                                meta={'title': title, 'plot': card["lead"].encode('utf-8') if "lead" in card else ''})           
    r = client.request("%s/ribbons/%s/%d" % (api_url, param, int(page)+1), cookie="jwt=%s" % jwtToken if jwtToken else None, headers=headers)
    if r != None:
        addDirectoryItem(u'[I]K\u00F6vetkez\u0151 oldal >>[/I]', 'apiribbons&param=%s&page=%d' % (param, int(page)+1), '', 'DefaultFolder.png')
    endDirectory(type=dirType)

def playVideo():
    from resources.lib import m3u8_parser
    try:
        splittedParam = param.split("/")
        splittedParam[-1] = quote_plus(splittedParam[-1])
        joinedParam = "/".join(splittedParam)
        r = client.request("%s%s/search/%s" % (api_url, "/premium" if ispremium else "", joinedParam), cookie="jwt=%s" % jwtToken if jwtToken else None, headers=headers)
        data = json.loads(r)
        playerId = data["playerId"] if "playerId" in data else data["coverVideoPlayerId"]
        title = data["title"]
        plot = data["lead"] if "lead" in data else ""
        imageItem = "imageUrl" if "imageUrl" in data else "coverVideoImageUrl"
        thumb = "%s/%s" % (base_url, data[imageItem]) if "https://" not in data[imageItem] else data[imageItem]
        r = client.request("%s%s/streaming-url?playerId=%s&stream=undefined" % (api_url, "/premium" if ispremium else "", playerId), cookie="jwt=%s" % jwtToken if jwtToken else None, headers=headers)
        data = json.loads(r)
        if (data["geoBlocked"] != False):
            xbmcgui.Dialog().notification("TV2 Play", "A tartalom a tartózkodási helyedről sajnos nem elérhető!", xbmcgui.NOTIFICATION_ERROR)
            return
        r = client.request(data["url"], headers=headers)
        json_data = json.loads(r)
        m3u_url = json_data['bitrates']['hls']
        m3u_url = json_url = re.sub('^//', 'https://', m3u_url)
        if control.setting("useisa") == "true":
            item = control.item(path=m3u_url)
            from inputstreamhelper import Helper
            is_helper = Helper('hls')
            if is_helper.check_inputstream():
                if sys.version_info < (3, 0):  # if python version < 3 is safe to assume we are running on Kodi 18
                    item.setProperty('inputstreamaddon', 'inputstream.adaptive')   # compatible with Kodi 18 API
                else:
                    item.setProperty('inputstream', 'inputstream.adaptive')  # compatible with recent builds Kodi 19 API
                item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        else:
            r = client.request(m3u_url, headers=headers)
            root = os.path.dirname(m3u_url)
            sources = m3u8_parser.parse(r)
            try: 
                sources.sort(key=lambda x: int(x['resolution'].split('x')[0]), reverse=True)
            except: 
                pass

            auto_pick = control.setting('autopick') == '1'

            if len(sources) == 1 or auto_pick == True:
                source = sources[0]['uri']
            else:
                result = xbmcgui.Dialog().select(u'Min\u0151s\u00E9g', [str(source['resolution']) if 'resolution' in source else 'Unknown' for source in sources])
                if result == -1:
                    source = sources[0]['uri']
                else:
                    source = sources[result]['uri']
            stream_url = root + '/' + source
            item = control.item(path=stream_url)
        item.setArt({'icon': thumb, 'thumb': thumb})
        item.setInfo(type='Video', infoLabels = {'Title': title, 'Plot': plot})
        control.resolve(int(sys.argv[1]), True, item)
    except:
        xbmcgui.Dialog().notification("TV2 Play", "Hiba a forrás elérésekor! Nem található?", xbmcgui.NOTIFICATION_ERROR)

def addDirectoryItem(name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None):
    url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
    if thumb == '': thumb = icon
    cm = []
    if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
    if not context == None: cm.append((context[0].encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
    item = xbmcgui.ListItem(label=name)
    item.addContextMenuItems(cm)
    item.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
    if Fanart == None: Fanart = addonFanart
    item.setProperty('Fanart_Image', Fanart)
    if isFolder == False: item.setProperty('IsPlayable', 'true')
    if not meta == None: item.setInfo(type='Video', infoLabels = meta)
    xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

def endDirectory(type='addons'):
    xbmcplugin.setContent(syshandle, type)
    #xbmcplugin.addSortMethod(syshandle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)

def getText(title, hidden=False):
    search_text = ''
    keyb = xbmc.Keyboard('', title, hidden)
    keyb.doModal()

    if (keyb.isConfirmed()):
        search_text = keyb.getText()

    return search_text

def doLogout():
    control.setSetting("loggedIn", "false")
    control.setSetting("jwtToken", "")
    control.setSetting("hasPremium", "false")
    control.setSetting("email", "")
    control.setSetting("password", "")

def logout():
    if control.yesnoDialog("Valóban ki szeretne jelentkezni?") == 1:
        try:
            res = client.request(logout_url, cookie="jwt=%s" % jwtToken if jwtToken else None, headers=headers)
        except:
            pass
        doLogout()

def login():
    loginData = json.dumps({"email": control.setting("email"), "password": control.setting("password"), "stayLoggedIn": True, "deviceToken": {"token": None, "platform": "web"}}).encode('utf-8')
    jwtToken = ""
    try:
        loginHeaders = {"Content-Type": "application/json;charset=UTF-8", "Content-Length": len(loginData)}
        if headers:
            loginHeaders.update(headers)
        authAnswer = json.loads(client.request(auth_url, post=loginData, headers=loginHeaders))
        if authAnswer["success"]:
            jwtToken = authAnswer["token"]
            res = json.loads(client.request(userinfo_url, cookie="jwt=%s" % jwtToken, headers=headers))
            if res["success"]:
                control.setSetting("hasPremium", str(res["isPremium"]))
    except:
        pass
    return jwtToken

def getJWTToken():
    if control.setting("email") and control.setting("password"):
        jwtToken =  control.setting("jwtToken")
        if len(jwtToken) > 0:
            m = re.search(r'(.*)\.(.*)\.(.*)', base64.b64decode(jwtToken).decode("utf-8"))
            if m:
                errMsg = ""
                try:
                    errMsg = "TV2 Play: cannot base64 decode the group 2: %s" % m.group(2)
                    decodedToken=base64.b64decode(m.group(2)+"===")
                    if sys.version_info[0] == 3:
                        errMsg = "TV2 Play: utf-8 decode error: %s" % decodedToken
                        decodedToken = decodedToken.decode("utf-8", "ignore")
                    errMsg = "TV2 Play: decodedToken is not a json object: %s" % decodedToken
                    jsObj = json.loads(decodedToken)
                    if "exp" in jsObj:
                        if jsObj["exp"]-int(time.time())>0:
                            return jwtToken
                        else:
                            xbmc.log("TV2 Play: jwtToken expired, request a new one.", xbmc.LOGINFO)
                    else:
                        xbmc.log("TV2 Play: match group 2 does not contains exp key: %s" % m.group(2), xbmc.LOGERROR)
                except:
                    xbmc.log(errMsg, xbmc.LOGERROR)
            else:
                xbmc.log("TV2 Play: jwtToken not match to (.*)\\.(.*)\\.(.*). jwtToken: %s" % jwtToken, xbmc.LOGERROR)
        jwtToken = login()
        if jwtToken:
            control.setSetting("loggedIn", "true")
            control.setSetting("jwtToken", jwtToken)
        else:
            control.setSetting("loggedIn", "false")
            control.setSetting("jwtToken", "")
            control.setSetting("hasPremium", "false")
            xbmcgui.Dialog().ok("TV2 Play", "Bejelentkezés sikerelen!")
        return jwtToken
    else:
        doLogout()
    return None

if control.setting("firstStart") in ["true", "True"]:
    if control.yesnoDialog("A [COLOR gold]PRÉMIUM[/COLOR] tartalmak eléréséhez [B]TV2 Play Prémium[/B] csomag szükséges! A kiegészítő beállításaiban megadhatod a bejelentkezési adataidat.", nolabel='Bezárás', yeslabel='Beállítások megnyitása') == True:
        control.openSettings()
    control.setSetting('firstStart', "false")

jwtToken = getJWTToken()
hasPremium = control.setting("hasPremium") == "true"

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
param = params.get('param')
page = params.get('page')
search = params.get('search')
ispremium = True if params.get('ispremium') in ["true", "True"] else False
channel = params.get('channel')

if action == None:
    main_folders()
elif action == 'musorok':
    musorok(musorokURL)
elif action == 'elo':
    elo()
elif action == 'playlive':
    playLive(channel)
elif action == 'apisearch':
    apiSearch()
elif action == 'apisearchseason':
    apiSearchSeason(int(page))
elif action == 'apiribbons':
    apiRibbons()
elif action == 'playvideo':
    playVideo()
elif action == 'logout':
    logout()
elif action == 'drmSettings':
    xbmcaddon.Addon(id='inputstream.adaptive').openSettings()
elif action == 'search':
    getSearches()
elif action == 'newsearch':
    doSearch()
elif action == 'deletesearchhistory':
    deleteSearchHistory()
elif action == 'historysearch':
    musorok(searchURL.replace("#SEARCHSTRING#", quote(search).replace("%", "%%")))
