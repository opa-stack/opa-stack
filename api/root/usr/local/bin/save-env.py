#!/usr/bin/python3

# Simple script to save metadata that is lost after the build
# See https://docs.docker.com/docker-hub/builds/advanced/#environment-variables-for-building-and-testing

import os
import sys
import json
from typing import Dict

env = 'default'

data: Dict[str, dict] = {env: {}}

for i in sys.argv[1:]:
    data[env][i] = os.environ.get(i, '')

jsondata = json.dumps(data, indent=2)

print(jsondata)

open('/data/build-info-container.json', 'w').write(jsondata)
