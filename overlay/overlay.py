import sys
import json
import re
from urllib2 import urlopen

from bs4 import BeautifulSoup
from flask import Flask, render_template
from werkzeug.contrib.cache import SimpleCache


PLAYERS = json.load(open(sys.argv[1]))


app = Flask(__name__)
app.jinja_env.line_statement_prefix = '%'
cache = SimpleCache()


def memoize(timeout=30):
    def wrapper(f):
        def wrapped(*args, **kwargs):
            cache_key = 'memoize:' + f.__name__ + ':' + json.dumps([args, kwargs])
            cached = cache.get(cache_key)
            if cached:
                return cached
            val = f(*args, **kwargs)
            cache.set(cache_key, val, timeout=timeout)
            return val
        return wrapped
    return wrapper


def track_changes(f):
    def wrapped(*args, **kwargs):
        cache_key = 'track_changes_last:' + f.__name__ + ':' + json.dumps([args, kwargs])
        last = cache.get(cache_key)
        val = f(*args, **kwargs)
        cache.set(cache_key, val)
        changed = last is not None and last != val
        return val, changed
    return wrapped


@memoize()
@track_changes
def team_raised():
    try:
        team_url = 'http://www.extra-life.org/index.cfm?fuseaction=donorDrive.team&page=5&eventID=508&teamID=7951'
        soup = BeautifulSoup(urlopen(team_url))
        return soup.find('h5').stripped_strings.next()
    except:
        return '?'


amount_re = re.compile(r'actualamount: "(\d+)"')
@memoize()
@track_changes
def player_raised(xlid):
    try:
        player_url = 'http://www.extra-life.org/index.cfm?fuseaction=donorDrive.participant&participantID=%s' % xlid
        soup = BeautifulSoup(urlopen(player_url))
        script = soup.select('.thermoBox script')[0].text
        amount = amount_re.search(script).group(1)
        return '$' + amount
    except:
        return '?'


@app.route("/")
def overlay():
    total, total_changed = team_raised()

    player_stats = []
    for player in PLAYERS:
        stats = player.copy()
        stats['raised'], stats['raised_changed'] = player_raised(player['xlid'])
        player_stats.append(stats)

    return render_template('overlay.html', total=total, total_changed=total_changed, players=player_stats)


if __name__ == "__main__":
    app.run()
