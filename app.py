import gtfs_realtime_pb2
from flask import Flask
from xml.etree import ElementTree
from urllib import urlopen
import time
import os

poikkeusURL = 'http://www.poikkeusinfo.fi/xml/v2/'

gtfs_version = '20120224'
agency_id = 'HSL'

linetypes = {}
linetypes['1'] = 3 # Helsingin sisainen
linetypes['2'] = 0 # raitiovaunut
linetypes['3'] = 3 # Espoon sisainen
linetypes['4'] = 3 # Vantaan sisainen
linetypes['5'] = 3 # seutuliikenne
linetypes['6'] = 1 # metro
linetypes['7'] = 4 # lautta
linetypes['12'] = 2 # lahiliikennejunat
linetypes['36'] = 3 # Kirkkonummen sisainen
linetypes['39'] = 3 # Keravan sisainen

weekdays = ['Su', 'Ma', 'Ti', 'Ke', 'To', 'Pe', 'La', 'Su']
weekdays[-1] = 'Su';
lt = time.localtime()
wd = weekdays[lt[6]+1]
yd = weekdays[lt[6]]

et = ElementTree
tree = et.ElementTree()

app = Flask(__name__)

@app.route('/')
def index():
  return getDisruptions()

@app.route('/<lang>')
def with_lang(lang):
  return getDisruptions(lang)

def getDisruptions(lang='fi'):
  tree.parse(urlopen(poikkeusURL + lang))
  # tree.parse(open('.trash/poikkeus.xml'))
  msg = gtfs_realtime_pb2.FeedMessage()
  msg.header.gtfs_realtime_version = "1.0"
  msg.header.incrementality = msg.header.FULL_DATASET
  disruptions = tree.getroot()
  # et.dump(disruptions)
  if (disruptions is not None):
    dtime = time.strptime(disruptions.attrib['time'], '%Y-%m-%dT%H:%M:%S')
    msg.header.timestamp = int(time.mktime(dtime))

    alerts = list(disruptions)
    cnt = 0;
    for a in alerts:
      if (a.tag == 'DISRUPTION'):
        # print a
        cnt += 1
        ent = msg.entity.add()
        ent.id = a.attrib['id']
        inf = ent.alert.informed_entity.add()
        inf.agency_id = agency_id
        targets = list(a.find('TARGETS'))
        for t in targets:
          if (t.tag == 'LINETYPE'):
            inf.route_type = linetypes[t.attrib['id']]
          elif (t.tag == 'LINE'):
            inf.route_id = t.attrib['id']
            inf.route_type = linetypes[t.attrib['linetype']]
        v = a.find('VALIDITY')
        ent.is_deleted = (v.attrib['status'] == 0)
        ftime = time.strptime(v.attrib['from'], '%Y-%m-%dT%H:%M:%S')
        ttime = time.strptime(v.attrib['to'], '%Y-%m-%dT%H:%M:%S')
        vper = ent.alert.active_period.add()
        vper.start = int(time.mktime(ftime))
        vper.end = int(time.mktime(ttime))
  
        # print 
        texts = list(a.find('INFO'))
        # print texts
        for t in texts:
          head = ent.alert.header_text.translation.add()
          head.language = t.attrib['lang']
          head.text = t.text

  # print msg
  return msg.SerializeToString()

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  # app.debug = True
  app.run(host='0.0.0.0', port=port)

