import sys
import re
import json
from urllib2 import urlopen

from bs4 import BeautifulSoup
import couchdb


class Store(object):
    db_name = 'extralife'

    def __init__(self):
        self.server = couchdb.client.Server()

        if not self.db_name in self.server:
            self.server.create(self.db_name)
        self.db = self.server[self.db_name]

    def get_data(self):
        return { row.id : row.doc for row in self.db.view('_all_docs', include_docs=True) }

    def update(self, data):
        for k, v in data.iteritems():
            v['_id'] = k
        self.db.update(data.values())


def get_team_raised():
    try:
        team_url = 'http://www.extra-life.org/index.cfm?fuseaction=donorDrive.team&page=5&eventID=508&teamID=7951'
        print >> sys.stderr, team_url
        soup = BeautifulSoup(urlopen(team_url))
        return soup.find('h5').stripped_strings.next()
    except:
        return '?'


amount_re = re.compile(r'actualamount: "(\d+)"')
def get_player_raised(xlid):
    try:
        player_url = 'http://www.extra-life.org/index.cfm?fuseaction=donorDrive.participant&participantID=%s' % xlid
        print >> sys.stderr, player_url
        soup = BeautifulSoup(urlopen(player_url))
        script = soup.select('.thermoBox script')[0].text
        amount = amount_re.search(script).group(1)
        return '$' + amount
    except:
        return '?'


def update(players_path):
    players = json.load(open(players_path))
    store = Store()

    data = store.get_data()

    total = get_team_raised()
    data_total = data.get('total')
    if not data_total:
        data_total = data['total'] = {}
    data_total['updated'] = total != data_total.get('value')
    data_total['value'] = total

    player_stats = []
    for player in players:
        player_key = 'player:' + player['name']
        player_data = data.get(player_key)
        if not player_data:
            player_data = data[player_key] = player.copy()

        raised = get_player_raised(player['xlid'])
        player_data['raised_updated'] = raised != player_data.get('raised')
        player_data['raised'] = raised

    data['players'] = data.get('players', {})
    data['players']['list'] = [ player['name'] for player in players ]

    store.update(data)
    print >> sys.stderr, data


if __name__ == "__main__":
    update(sys.argv[1])
