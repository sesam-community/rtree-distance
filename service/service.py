import json
import logging
import os
import shelve

import requests

from flask import Flask, Response, request
from rtree import index
from shapely.geometry import shape
from transit.decoder import Decoder

app = Flask(__name__)

logger = logging.getLogger('service')
transit_decoder = Decoder()

base_data_url = os.environ["BASE_DATA_URL"]
base_data_property = os.environ.get("BASE_DATA_PROPERTY", "geojson")
source_property = os.environ.get("SOURCE_PROPERTY", "geojson")
target_property = os.environ.get("TARGET_PROPERTY", "matches")

# build spatial index
idx = index.Index('rtree')
with shelve.open('state.dat') as db:
    r = requests.get(base_data_url, params={"since": db.get("since", None)})
    base_data = transit_decoder.decode(r.json())
    updated = None
    for i, e in enumerate(base_data):
        updated = e["_updated"]
        s = shape(e[base_data_property])
        idx.insert(i, s.bounds, obj=(e["_id"], s))
    db["since"] = updated


def transform(entity):
    try:
        s = shape(entity.get(source_property))
        candidates = idx.intersection(s.bounds, objects=True)
        entity[target_property] = [{"_id": n.object[0], "distance": s.distance(n.object[1])} for n in candidates]
    except Exception as e:
        logger.warning("Failed to convert entity '%s': %s", entity.get("_id"), e)
    return entity


@app.route('/transform', methods=["POST"])
def post():
    entities = request.json
    return Response(json.dumps([transform(e) for e in entities]), mimetype='application/json', )


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
