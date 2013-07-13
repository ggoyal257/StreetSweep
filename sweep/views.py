from django.http import HttpResponse
from django.utils import simplejson
import fileinput,re,urllib,json,urllib2,datetime

def index(request):
    #return getWard(request,41.9085,-87.6346)
    return getWard(request,41.9051,-87.6283)
    #return HttpResponse("Hello, world. You're at the poll index.")
    
def getWard(request,latitude,longitude):
    print latitude, longitude
    latitude = float(latitude)
    longitude = float(longitude)
    wardSection = str(getSectionWard(latitude,longitude))
    url = 'http://data.cityofchicago.org/resource/8h6a-imtk.json?ward_section_concatenated=' + wardSection
    response = urllib.urlopen(url);
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    data = simplejson.load(f)
    cleaningDate =  getNextCleaningDay(data)
    currDate = datetime.datetime.now()
    numOfdays = None
    if cleaningDate is not None:
        numOfdays = (cleaningDate-currDate).days
        cleaningDate = cleaningDate.strftime("%Y-%m-%d")
    print cleaningDate,numOfdays
    some_data = {
   #'wardsection': getSectionWard(latitude,longitude) ,
   #'data': data
   'days' : str(numOfdays),
   'cleaningDate' : cleaningDate,
   'wardsection' : wardSection,
   }
    data = simplejson.dumps(some_data)
    #data = json.loads(response.read())
    return HttpResponse(data, mimetype='application/json')

def getNextCleaningDay(data):
    monthData = {}
    for elem in data:
        month = elem['month_name'].upper()
        dates = elem['dates']
        dates = dates.split(',')
        monthData[month] = dates
    curr_month = datetime.datetime.now().strftime("%B").upper()
    curr_day = datetime.datetime.now().day
    if monthData.has_key(curr_month):
        #print monthData[curr_month]
        for day in monthData[curr_month]:
            if int(day) >= curr_day:
                return createdate(curr_month,day)
                #return curr_month,day
    next_month = getNextMonth().upper()
    if monthData.has_key(next_month):
        return createdate(next_month,monthData[next_month][0])
        #return next_month,monthData[next_month]
    return None 
    
def createdate(month,day):
    dateStr = month.lower() + ' ' +str(day) + ' ' + str(datetime.datetime.now().year)
    return datetime.datetime.strptime(dateStr, '%B %d %Y')
def getNextMonth():
    curr_date = datetime.datetime.now()
    if curr_date.month == 12:
        month = 1
        year = curr_date.year+1
    else:
        month  = curr_date.month + 1
        year = curr_date.year
    return datetime.date(year, month, 1).strftime("%B")
    
def parseKML(filename):
    dataDict = {}
    filein = open(filename,'r')
    data = filein.read()
    filein.close()
    pattern = 'name:</b> (.*?)<br>'
    name = re.findall(pattern,data)
    pattern = 'geometry:</b> (.*),'
    geometry = re.findall(pattern,data)
    #print geometry
    for i in range(0,len(name)):
        #x = []
        #y = []
        coo = geometry[i]
        coo = coo.split(',')
        coo = coo[1:]
        poly = []
        for co in coo:
            co = co.split('-')
            #x.append(co[0].strip())
            #y.append('-' + co[1])
            #x.append(float(co[0].strip()))
            #y.append(-(float(co[1])))
            poly.append([float(co[0].strip()),-(float(co[1]))])
        #print name[i]
        dataDict[name[i]] = poly
    
    #print dataDict['4308'][1]    
    return dataDict
    
def getSectionWard(x,y):
    value = ''
    dataDict = parseKML('Street Sweeping - 2012.kml')
    for key in dataDict.keys():
        if pointInPolygon(x,y,dataDict[key]):
            print  key
            value = key
    return value
    
def pointInPolygon(x,y,poly):
    n = len(poly)
    inside = False
    p1x,p1y=poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i%n]
        if y > min(p1y,p2y):
            if y<= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters= (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x<= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside
    