from flask import Flask, request
from wrapper import wrapper
app = Flask(__name__)


@app.route("/")
def hello():
    return "hello world"


@app.route("/plot_trend")
def get_investor_details():
    args = request.args
    return wrapper.get_investor_details(args)


@app.route("/find_transactions")
def find_transactions():
    args = request.args
    return wrapper.find_transactions(args)


if __name__ == "__main__":
    app.run()
