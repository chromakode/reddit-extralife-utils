import sys
import json

from jinja2 import Environment, Template


env = Environment(line_statement_prefix='%')

bio_template = env.from_string("""
<h1>Greetings!</h1>

<h2>We're playing games for 24 hours at reddit HQ to raise money for Children's Miracle Network hospitals.</h2>
<br>
<h3><a rel="nofollow" href="http://www.extra-life.org/team/reddit" target="_blank">Support our Extra Life Team</a></h3>
<h3><a rel="nofollow" href="http://www.extra-life.org/index.cfm?fuseaction=cms.page&amp;id=1005&amp;eventID=501" target="_blank">Extra Life FAQ</a></h3>

The marathon starts at 8AM PDT on October 20th.

<br><br><br>
<h2>our SF gamers:</h2>

<table>
<tbody>
% for player in players
    % set xlurl = 'xlid' in player and 'http://www.extra-life.org/index.cfm?fuseaction=donorDrive.participant&participantID=%s' % player['xlid']
    <tr>
    <td style="width:125px">
        % if xlurl
        <a href="{{ xlurl }}" target="_blank">
        % endif
        <img src="http://www.redditstatic.com/about/avatar/{{ player['name'] }}.png" height="100" alt="{{ player['name'] }}">
        % if xlurl
        </a>
        % endif
    </td>
    <td style="width:16em">
        <h3>
        % if xlurl
        <a href="{{ xlurl }}" style="color:black" target="_blank">
        % endif
        {{ player['name'] }}
        % if xlurl
        </a>
        % endif
        </h3>
    </td>
    <td style="width:7em"><h4><a href="http://www.reddit.com/about/team/#user/{{ player['name'] }}" target="_blank">about</a></h4></td>
    % if xlurl
        <td style="width:7em"><h4><a href="{{ xlurl }}" target="_blank">donate</a></h4></td>
    % endif
    % if 'stream' in player
        <td style="width:7em"><h4><a href="{{ player['stream'] }}" target="_blank">stream</a></h4></td>
    % endif
    </tr>
% endfor
</tbody>
</table>
""")

PLAYERS = json.load(open(sys.argv[1]))
print bio_template.render(players=PLAYERS)
