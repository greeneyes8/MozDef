#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Copyright (c) 2014 Mozilla Corporation
#
# Contributors:
# Anthony Verez averez@mozilla.com

from lib.alerttask import AlertTask
from lib.query_classes import SearchQuery


class AlertBroIntel(AlertTask):
    def main(self):
        search_query = SearchQuery(minutes=30)

        self.filtersFromKibanaDash(search_query, 'bro_intel_dashboard.json')

        # Search aggregations on field 'seenindicator', keep 50 samples of events at most
        self.searchEventsAggregated('seenindicator', samplesLimit=50)
        # alert when >= 5 matching events in an aggregation
        self.walkAggregations(threshold=5)

    # Set alert properties
    def onAggregation(self, aggreg):
        # aggreg['count']: number of items in the aggregation, ex: number of failed login attempts
        # aggreg['value']: value of the aggregation field, ex: toto@example.com
        # aggreg['events']: list of events in the aggregation
        category = 'bro'
        tags = ['bro']
        severity = 'NOTICE'

        summary = ('{0} {1}: {2}'.format(aggreg['count'], 'bro intel match', aggreg['value']))
        # append first 3 source IPs
        summary += ' sample sourceips: '
        for e in aggreg['events'][:3]:
            if 'sourceipaddress' in e['_source']['details'].keys():
                summary += '{0} '.format(e['_source']['details']['sourceipaddress'])

        # Create the alert object based on these properties
        return self.createAlertDict(summary, category, tags, aggreg['events'], severity)