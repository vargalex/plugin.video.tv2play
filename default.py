# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcaddon, re, xbmcplugin, json, os, sys, base64, time
from resources.lib import client, control
from resources.lib.utils import py2_decode

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
    from urllib.parse import quote_plus
else:
    from urlparse import parse_qsl
    from urllib import quote_plus

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')
base_url = "https://tv2play.hu"
api_url = "%s/api" % base_url
auth_url = "%s/authenticate" % api_url
userinfo_url = "%s/users/me" % api_url
logout_url = "%s/logout" % api_url

def main_folders():
    artPath = py2_decode(control.artPath())
    addDirectoryItem("Műsorok", "musorok", os.path.join(artPath, "tv2play.png"), None)
    r = client.request("%s/channels" % api_url)
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

def musorok():
    pageOffset = 0
    allItemCnt = -1
    allItems = []
    while len(allItems) != allItemCnt:
        r = client.request("https://tv2-bud.gravityrd-services.com/grrec-tv2-war/JSServlet4?rd=0,TV2_W_CONTENT_LISTING,800,[*platform:web;*domain:tv2play;*currentContent:SHOW;*country:HU;*userAge:16;*pagingOffset:%d],[displayType;channel;title;itemId;duration;isExtra;ageLimit;showId;genre;availableFrom;director;isExclusive;lead;url;contentType;seriesTitle;availableUntil;showSlug;videoType;series;availableEpisode;imageUrl;totalEpisode;category;playerId;currentSeasonNumber;currentEpisodeNumber;part;isPremium]" % pageOffset)
        matches=re.search(r'(.*)var data = (.*)};(.*)', r, re.S)
        if matches:
            result = json.loads("%s}" % matches.group(2))
            if allItemCnt == -1:
                onv = result["recommendationWrappers"][0]["recommendation"]["outputNameValues"]
                for variable in onv:
                    if variable["name"] == "allItemCount":
                        allItemCnt = int(variable["value"])
                        break
            allItems.extend(result["recommendationWrappers"][0]["recommendation"]["items"])
        else:
            allItemCnt = 0
            allItems = []
        pageOffset=len(allItems)
    allItemsSorted=sorted(allItems, key=lambda k:k["title"])
    for item in allItemsSorted:
        if hasPremium or not "isPremium" in item or item["isPremium"] == "false":
            addDirectoryItem(item["title"].encode("utf-8"),
                             "apisearch&param=%s&ispremium=%s" % (quote_plus(item["url"]), item["isPremium"] if "isPremium" in item else ""),
                             ("%s/%s" % (base_url, item["imageUrl"]) if "https://" not in item["imageUrl"] else item["imageUrl"]) if "imageUrl" in item else "",
                             "DefaultFolder.png",
                             meta={'title': item["title"].encode("utf-8"), 'plot': item["lead"].encode('utf-8') if "lead" in item else ''})
    endDirectory(type="tvshows")


def apiSearchSeason(season):
    r = client.request("%s%s/search/%s" % (api_url, "/premium" if ispremium else "", param), cookie="jwt=%s" % jwtToken if jwtToken else None)
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
        r = client.request("%s/ribbons/%s" % (api_url, ribbon), cookie="jwt=%s" % jwtToken if jwtToken else None)
        if r:
            data = json.loads(r)
            addDirectoryItem(data["title"].encode("utf-8"),
                            "apiribbons&param=%s&page=0" % data["id"],
                            thumb,
                            "DefaultFolder.png",
                            meta={'title': data["title"].encode("utf-8"), 'plot': plot})
    endDirectory(type="tvshows")

def apiSearch():
    r = client.request("%s%s/search/%s" % (api_url, "/premium" if ispremium else "", param), cookie="jwt=%s" % jwtToken if jwtToken else None)
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
    r = client.request("%s/ribbons/%s/%s" % (api_url, param, page), cookie="jwt=%s" % jwtToken if jwtToken else None)
    data = json.loads(r)
    dirType = 'videos'
    for card in data["cards"]:
        thumb = "%s/%s" % (base_url, card["imageUrl"]) if "https://" not in card["imageUrl"] else card["imageUrl"]
        title = card["title"].encode('utf-8')
        if "contentLength" in card:
            plot = ""
            if control.setting('fillLead') == 'true':
                try:
                    r = client.request("%s%s/search/%s" % (api_url, "/premium" if card["isPremium"] else "", card["slug"]), cookie="jwt=%s" % jwtToken if jwtToken else None)
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
    r = client.request("%s/ribbons/%s/%d" % (api_url, param, int(page)+1))
    if r != None:
        addDirectoryItem(u'[I]K\u00F6vetkez\u0151 oldal >>[/I]', 'apiribbons&param=%s&page=%d' % (param, int(page)+1), '', 'DefaultFolder.png')
    endDirectory(type=dirType)

def playVideo():
    from resources.lib import m3u8_parser
    try:
        splittedParam = param.split("/")
        splittedParam[-1] = quote_plus(splittedParam[-1])
        joinedParam = "/".join(splittedParam)
        r = client.request("%s%s/search/%s" % (api_url, "/premium" if ispremium else "", joinedParam), cookie="jwt=%s" % jwtToken if jwtToken else None)
        data = json.loads(r)
        playerId = data["playerId"]
        title = data["title"]
        plot = data["lead"] if "lead" in data else ""
        thumb = "%s/%s" % (base_url, data["imageUrl"]) if "https://" not in data["imageUrl"] else data["imageUrl"]
        r = client.request("%s%s/streaming-url?playerId=%s&stream=undefined" % (api_url, "/premium" if ispremium else "", playerId), cookie="jwt=%s" % jwtToken if jwtToken else None)
        data = json.loads(r)
        if (data["geoBlocked"] != False):
            xbmcgui.Dialog().notification("TV2 Play", "A tartalom a tartózkodási helyedről sajnos nem elérhető!", xbmcgui.NOTIFICATION_ERROR)
            return
        r = client.request(data["url"])
        json_data = json.loads(r)
        m3u_url = json_data['bitrates']['hls']
        m3u_url = json_url = re.sub('^//', 'https://', m3u_url)
        r = client.request(m3u_url)

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

def doSearch():
    search_text = getText(u'Add meg a keresend\xF5 kifejez\xE9st')
    if search_text != '':
        global keyword
        global page
        functionIdx = page
        keyword = quote_plus(search_text)
        page = '1'
        global mode2Sub 
        mode2Sub[int(functionIdx)]()

def doLogout():
    control.setSetting("loggedIn", "false")
    control.setSetting("jwtToken", "")
    control.setSetting("hasPremium", "false")
    control.setSetting("email", "")
    control.setSetting("password", "")

def logout():
    if control.yesnoDialog("Valóban ki szeretne jelentkezni?") == 1:
        try:
            res = client.request(logout_url, cookie="jwt=%s" % jwtToken if jwtToken else None)
        except:
            pass
        doLogout()

def login():
    loginData = json.dumps({"email": control.setting("email"), "password": control.setting("password"), "stayLoggedIn": True, "deviceToken": {"token": None, "platform": "web"}}).encode('utf-8')
    jwtToken = ""
    try:
        authAnswer = json.loads(client.request(auth_url, post=loginData, headers={"Content-Type": "application/json;charset=UTF-8", "Content-Length": len(loginData)}))
        if authAnswer["success"]:
            jwtToken = authAnswer["token"]
            res = json.loads(client.request(userinfo_url, cookie="jwt=%s" % jwtToken))
            if res["success"]:
                control.setSetting("hasPremium", str(res["isPremium"]))
    except:
        pass
    return jwtToken

def getJWTToken():
    if control.setting("email") and control.setting("password"):
        jwtToken =  control.setting("jwtToken")
        if jwtToken:
            m = re.search('(.*)\.(.*)\.(.*)', base64.b64decode(jwtToken).decode("utf-8"))
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
                xbmc.log("TV2 Play: jwtToken not match to (.*)\.(.*)\.(.*). jwtToken: %s" % jwtToken, xbmc.LOGERROR)
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
ispremium = True if params.get('ispremium') in ["true", "True"] else False

if action == None:
    main_folders()
elif action == 'musorok':
    musorok()
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