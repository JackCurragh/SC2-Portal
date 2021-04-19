from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3
from werkzeug.exceptions import abort
import mpld3
import matplotlib as plt

import io
import base64

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


app = Flask(__name__)
app.config["SECRET_KEY"] = "aaabbbbaaabbbb"


@app.route("/")
def index():
    # service home page of the portal
    conn = get_db_connection()
    studies = conn.execute("SELECT * FROM study_info").fetchall()
    conditions = list_conditions(conn)
    formatted_conditions = format_conditions(conn, conditions)

    condition_info = get_condition_info(conn)
    formatted_condition_info = format_conditions_info(condition_info)
    condition_keys = sort_condition_keys(condition_info)

    conn.close()

    return render_template(
        "index.html",
        studies=studies,
        conditions=formatted_conditions,
        conditions_keys=condition_keys,
        condition_info=formatted_condition_info,
    )


@app.route("/query", methods=["GET", "POST"])
def query():
    fig, ax = plt.pyplot.subplots()
    ax.plot([1, 2, 3], [2, 4, 6])
    x = mpld3.fig_to_html(fig)
    return x


@app.route("/image", methods=["GET", "POST"])
def plotView():

    # Generate plot
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("title")
    axis.set_xlabel("x-axis")
    axis.set_ylabel("y-axis")
    axis.grid()
    axis.plot(range(5), range(5), "ro-")

    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)

    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode("utf8")

    return render_template("image.html", image=pngImageB64String)


def get_db_connection():
    # set up sqlite connection
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def list_conditions(conn):
    # get names of conditions from sqlite file
    conditions = conn.execute("SELECT * FROM conditions LIMIT 1").fetchall()
    return list(dict(conditions[0]).keys())


def get_distinct_values(conn, condition):
    # get the distinct enteries for inputed condition. Values returned not rows
    values = conn.execute("SELECT DISTINCT %s FROM conditions;" % condition).fetchall()
    return [row[0] for row in values]


def get_condition_info(conn):
    condition_info = conn.execute("SELECT * FROM condition_info;").fetchall()
    return condition_info


def format_conditions_info(conditions_info):
    formatted_condition_info = {}
    for row in conditions_info:
        if row["condition"] not in formatted_condition_info:
            formatted_condition_info[row["condition"]] = {}

        for key in row.keys():
            if key == "condition":
                continue
            else:
                formatted_condition_info[row["condition"]][key] = row[key]
    return formatted_condition_info


def sort_condition_keys(condition_info):
    # order the condition names based on the priority value in condition info
    dict_for_sorting = {}
    for row in condition_info:
        dict_for_sorting[row[0]] = int(row[-2])
    return sorted(dict_for_sorting, key=dict_for_sorting.__getitem__)


def format_conditions(conn, conditions):
    # This function prepares db info for display in index.html
    formatted = {}
    for condition in conditions:
        # format the codition title in upper case and removing _
        # j = str.title(condition).replace("_", " ")
        values = get_distinct_values(conn, condition)
        include_none = False

        if condition == "elongating" or condition == "initiating":
            values = [condition if x == 1 else "Not " + condition for x in values]
        rename_dict = {
            "chx": "Cycloheximide",
            "ltm": "Lactimidomycin",
            "harr": "Harringtonine",
        }

        if None in values:
            # remove nones for sorting
            values = [p for p in values if p]
            include_none = True

        if condition == "treatment":
            values = [rename_dict[value] for value in values]

        if condition not in ["sra_run", "study"]:
            values = [str.title(value) for value in values]
        try:
            values = [int(i) for i in values]
        except:
            pass

        formatted[condition] = sorted(values)
        if include_none:
            # reintroduce nones
            formatted[condition].append(None)
    return formatted


# To tidy up the output from the sqlite db.

# Write function to tidy up condition names
# - capitlaise
# - remove hyphens for spaces

# Write function to tidy up values
# - merge similars
# - capitalise
# - order numbers
