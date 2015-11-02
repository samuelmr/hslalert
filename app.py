import os
import time
from urllib import urlopen
from xml.etree.ElementTree import ElementTree
from google.protobuf import text_format

from flask import Flask
from flask import request
import iso8601
from calendar import timegm

import gtfs_realtime_pb2

poikkeusURL = 'http://www.poikkeusinfo.fi/xml/v3'
agency_id = 'HSL'

tree = ElementTree()

app = Flask(__name__)


@app.route('/')
def index():
    return getDisruptions()


def getDisruptions():
    """Get alerts from HSL XML interface and format them into GTFS-RT"""
    tree.parse(urlopen(poikkeusURL))
    msg = gtfs_realtime_pb2.FeedMessage()
    msg.header.gtfs_realtime_version = "1.0"
    msg.header.incrementality = msg.header.FULL_DATASET
    disruptions = tree.getroot()
    if (disruptions is not None):
        msg.header.timestamp = int(timegm(
            iso8601.parse_date(disruptions.attrib['time']).utctimetuple()))

        for disruption in list(disruptions):
            if (disruption.tag == 'DISRUPTION'):
                entity = msg.entity.add()
                entity.id = disruption.attrib['id']
                entity.alert.effect = int(disruption.attrib['effect'])

                for line in list(disruption.find('TARGETS')):
                    inf = entity.alert.informed_entity.add()
                    inf.agency_id = agency_id
                    if 'route_type' in line.attrib and line.attrib['route_type']:
                        inf.route_type = int(line.attrib['route_type'])
                    if 'id' in line.attrib and line.attrib['id']:
                        inf.route_id = line.attrib['id']
                        inf.trip.route_id = line.attrib['id']
                        if 'direction' in line.attrib and line.attrib['direction']:
                            inf.trip.direction_id = int(line.attrib['direction'])-1
                    if 'deptime' in line.attrib and line.attrib['deptime']:
                        start_time = iso8601.parse_date(line.attrib['deptime'])
                        inf.trip.start_date = start_time.strftime("%Y%m%d")
                        inf.trip.start_time = start_time.strftime("%H:%M:%S")

                v = disruption.find('VALIDITY')
                entity.is_deleted = (v.attrib['status'] == 0)
                vper = entity.alert.active_period.add()
                vper.start = int(timegm(
                    iso8601.parse_date(v.attrib['from']).utctimetuple()))
                vper.end = int(timegm(
                    iso8601.parse_date(v.attrib['to']).utctimetuple()))

                texts = list(disruption.find('INFO'))
                for t in texts:
                    if t.text and t.attrib['lang']:
                        head = entity.alert.description_text.translation.add()
                        head.language = t.attrib['lang']
                        head.text = t.text

    if 'debug' in request.args:
        return text_format.MessageToString(msg)
    else:
        return msg.SerializeToString()


def main(debug=False):
    port = int(os.environ.get('PORT', 5000))
    app.debug = debug
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
