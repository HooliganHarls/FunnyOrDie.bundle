# PMS plugin framework


####################################################################################################

PLUGIN_PREFIX     = "/video/funnyordie"

DEBUG                       = False

FOD_ART = 'art-default.png'
FOD_ICON = 'icon-default.png'

URL_PATTERN = 'http://www.funnyordie.com/browse/videos/%s/all/%s/%s%s'

CATEGORY_LIST = [
    { 'title': 'All', 'key': 'all' },
    { 'title': 'Stand Up', 'key': 'stand_up' },
    { 'title': 'Animation', 'key': 'animation' },
    { 'title': 'Web Series', 'key': 'web_series' },
    { 'title': 'Not Safe For Work', 'key': 'nsfw' },
    { 'title': 'Sketch', 'key': 'sketch' },
    { 'title': 'Sports', 'key': 'sports' },
    { 'title': 'Clean Comedy', 'key': 'clean_comedy' },
    { 'title': 'Politics', 'key': 'politics' },
    { 'title': 'Music', 'key': 'music' },
    { 'title': 'Parody', 'key': 'parody' },
    { 'title': 'Real Life', 'key': 'real_life' },
]

SORTS = [
    {
        'title': 'Most Buzz',
        'key': 'most_buzz',
        'allow_date_filter': True
    },
    {
        'title': 'Most Recent',
        'key': 'most_recent',
        'allow_date_filter': False
    },
    {
        'title': 'Most Viewed',
        'key': 'most_viewed',
        'allow_date_filter': True
    },
    {
        'title': 'Most Favorited',
        'key': 'most_favorited',
        'allow_date_filter': True
    },
    {
        'title': 'Highest Rated',
        'key': 'highest_rated',
        'allow_date_filter': True
    },
]

DATE_FILTERS = [
    {
        'title': 'Today',
        'key': 'today'
    },
    {
        'title': 'This Week',
        'key': 'this_week'
    },
    {
        'title': 'This Month',
        'key': 'this_month'
    },
    {
        'title': 'All Time',
        'key': 'all_time'
    },
]



####################################################################################################

def Start():
    Plugin.AddPrefixHandler(PLUGIN_PREFIX, Menu, "Funny or Die", FOD_ICON, FOD_ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    MediaContainer.art = R(FOD_ART)
    DirectoryItem.thumb = R(FOD_ICON)

def Menu():

    dir = MediaContainer(title1="Funny or Die",viewGroup="List")
    for c in CATEGORY_LIST:
        Log(c['key'])
        dir.Append(Function(DirectoryItem(CategoryOptions,"%s" % c['title'],"%s" % c['title']),category=c['key']))
    return dir

def CategoryOptions(sender,category=''):
    dir = MediaContainer(title1=sender.title1,title2=sender.itemTitle,viewGroup="List")

    for s in SORTS:
        Log(category)
        Log(s['key'])
        if s['allow_date_filter']:
            dir.Append(Function(DirectoryItem(DateOptions,"%s" % s['title'],"%s" % s['title']),category=category,s=s['key']))
        else:
            dir.Append(Function(DirectoryItem(VideoList,"%s" % s['title'],"%s" % s['title']),category=category,s=s['key'],date='all_time',page=1))
    return dir

def DateOptions(sender,category='',s=''):
    dir = MediaContainer(title1=sender.title2,title2=sender.itemTitle,viewGroup="List")

    for d in DATE_FILTERS:
        dir.Append(Function(DirectoryItem(VideoList,d['title'],d['title']),category=category,s=s,date=d['key'],page=1))
    return dir

def VideoList(sender,category='',s='',date='',page=1):
    if page == 1:
        t = sender.title2
    else:
        t = sender.title1
    dir = MediaContainer(title1=t,title2="Page %s" % (page),viewGroup="InfoList")
    url = makeUrl(category,s,date,page)
    xml = HTML.ElementFromURL(url, cacheTime=360000, errors='replace')
    for e in xml.xpath('//div[@class="detailed_vp"]'):
        href = e.xpath('.//a')[0].get('href')
        id = href.split('/')[2]
        Log('id: ' + id)
        vi = makeVideoItemFromId(id)
        Log("appended: ")
        Log(vi)
        dir.Append(vi)
                


    dir.Append(Function(DirectoryItem(VideoList,"Next Page...","Next Page..."),category=category,s=s,date=date,page=page+1))

    return dir

#######################

def makeUrl(category,s,date_filter,page):
    page_text = ''
    if page>1:
        page_text = '/page_%d' % page
    cat_text = category
    sort_text = s
    date_text = date_filter

    return URL_PATTERN % (cat_text,sort_text,date_text,page_text)

def makeVideoItemFromId(id):

    url = "http://www.funnyordie.com/player/%s" % id
    xml = XML.ElementFromURL(url, cacheTime=360000, errors='replace')
    n = {
        'ns': 'http://xspf.org/ns/0/'
    }

    try:
        file = xml.xpath('//ns:location/text()',namespaces=n)[0]
    except:
        Log('file')
        Log(XML.StringFromElement(xml))
        return None
    try:
        image = xml.xpath('//ns:image/text()',namespaces=n)[0]
    except:
        Log('image')
        Log(XML.StringFromElement(xml))
        return None
    try:
        title = xml.xpath('//ns:title/text()',namespaces=n)[0]
    except:
        Log('title')
        Log(XML.StringFromElement(xml))
        return None
    try:
        summary = xml.xpath('//ns:annotation/text()',namespaces=n)[0]
    except:
        Log('summary')
        Log(XML.StringFromElement(xml))
        return None

    try:
        duration = int(float(xml.xpath('//ns:meta[@rel="duration"]/text()',namespaces=n)[0]))*1000
    except:
        duration = 0

    rating = 0
    try:
        rating = int(round(float(xml.xpath('//ns:percentage/text()',namespaces=n)[0])/10))
    except Exception, e:
        pass


    vi = VideoItem(
        file,
        title=title,
        subtitle='',
        summary=summary,
        thumb=image,
        art=R(FOD_ART)
    )
    Log("vi:")
    Log(vi)

    return vi
