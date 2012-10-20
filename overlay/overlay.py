from flask import Flask, render_template

from stats import Store


app = Flask(__name__)
app.jinja_env.line_statement_prefix = '%'
store = Store()


@app.route("/")
def overlay():
    data = store.get_data()
    total = data['total']
    players = [ data['player:' + name] for name in data['players']['list'] ]
    return render_template('overlay.html', total=total, players=players)


if __name__ == "__main__":
    app.run()
