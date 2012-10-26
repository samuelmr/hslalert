#!/usr/bin/python

import gtfs_realtime_pb2
from xml.etree import ElementTree
from urllib import urlopen
import time

lang='fi';
# poikkeusURL = 'http://www.poikkeusinfo.fi/xml/v2/' + lang

def index(req):
  et = ElementTree
  tree = et.ElementTree()
  # tree.parse(urlopen(poikkeusURL))
  tree.parse(open('poikkeus.xml'))
  msg = gtfs_realtime_pb2.FeedMessage()
  msg.header.gtfs_realtime_version = "1.0"
  msg.header.incrementality = msg.header.FULL_DATASET
  disruptions = tree.getroot()
  if (disruptions):
    dtime = time.strptime(disruptions.attrib['time'], '%Y-%m-%dT%H:%M:%S')
    msg.header.timestamp = int(time.mktime(dtime))

  # i = disruptions.find('INFO')
  # print i
  # print et.dump(disruptions)
  # print et.dump(tree)
  et.dump(disruptions)

  print list(disruptions)

  # alerts = list(disruptions.iterfind('DISRUPTION'))
  # for a in alerts:
  #   print a
  # for d in disruptions.find('DISRUPTION'):
  #   print d
    
  #  ent.vehicle.trip.schedule_relationship = ent.vehicle.trip.SCHEDULED
  #   cnt += 1
  #   # fe = gtfs_realtime_pb2.FeedEntity()
  #   ent = msg.entity.add()
  #   ent.id = str(cnt)

  # parser = XMLParser()
  # disruptions = parser.feed(poikkeusXML)
  # msg = xml2gtfs(disruptions)
  # parser.close()

  print(msg);
  # return msg.SerializeToString()

print index(1)
