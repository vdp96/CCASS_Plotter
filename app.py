from flask import Flask, request, render_template
from wrapper import wrapper
from library import plotter
app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/plot_trend", methods=["GET", "POST"])
def get_investor_details():
    # if request.method == "POST":
    stock_code = request.form.get("stock_code", None)
    start_date = request.form.get("start_date", None)
    end_date = request.form.get("end_date", None)

    data = plotter.get_investor_details(stock_code=stock_code, start_date=start_date, end_date=end_date)
    return render_template("plotter.html", data=data)


@app.route("/find_transactions")
def find_transactions():
    if request.method == "GET":
        stock_code = request.form.get("stock_code")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        threshold = request.form.get("threshold")
    return plotter.find_transactions(stock_code=stock_code, start_date=start_date, end_date=end_date, threshold=threshold)


if __name__ == "__main__":
    app.run()
