#!/usr/bin/python3

import time
from pubTempHumid import PubTempHumid as pth
from pubLight import PubLight as pl
from pubAirQuality import PubAirQuality as paq

pth = pth()
pl = pl()
paq = paq()

while True:
    pth.publish()
    pl.publish()
    paq.publish()

    time.sleep(1)
