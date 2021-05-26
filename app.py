from flask import (
    Flask,
    render_template,
    request,
    url_for,
    flash,
    redirect,
    render_template_string,
)
import sqlite3
from werkzeug.exceptions import abort

from plotting_tgs import plot_transcript_graph
from GTF_to_TG import construct_graph_from_file

fasta_path = "/home/jack/sarscov2_processing/references/sarscov2_genome.fasta"
gtf_path = "/home/jack/sarscov2_processing/references/sarscov2.gtf"


app = Flask(__name__)
app.config["SECRET_KEY"] = "aaabbbbaaabbbb"


@app.route("/", methods=["GET", "POST"])
def index():
    # service home page of the portal
    conn = get_db_connection()
    studies = conn.execute("SELECT * FROM study_info").fetchall()
    conditions = list_conditions(conn)
    formatted_conditions, before_after = format_conditions(conn, conditions)
    condition_info = get_condition_info(conn)
    formatted_condition_info = format_conditions_info(condition_info)
    condition_keys = sort_condition_keys(condition_info)
    url = " "
    if request.method == "POST":
        form_list = request.form.getlist("hello")
        input_dict = parse_form_result(form_list, before_after, formatted_conditions)
        query = construct_query_string(input_dict)
        trips_id = run_query(query, conn)
        url = build_trips_url(trips_id)
    conn.close()

    return render_template(
        "index.html",
        studies=studies,
        conditions=formatted_conditions,
        conditions_keys=condition_keys,
        condition_info=formatted_condition_info,
        url=url,
    )


@app.route("/query", methods=["GET", "POST"])
def query():
    shape_string = construct_graph_from_file(gtf_path, fasta_path)
    return render_template("query.html")


@app.route("/test", methods=["GET", "POST"])
def plotView():
    conn = get_db_connection()
    results = conn.execute("select * from conditions").fetchall()
    studys = {}
    for i in results:
        if i["study"] not in studys:
            studys[i["study"]] = [i["sra_run"]]
        else:
            studys[i["study"]].append(i["sra_run"])

    print(studys)

    return render_template("test.html", studys=studys)


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
    values = conn.execute(
        "SELECT DISTINCT %s FROM conditions WHERE trips_id > 0;" % condition
    ).fetchall()
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
    before_after = {}
    for condition in conditions:
        # format the codition title in upper case and removing _
        # j = str.title(condition).replace("_", " ")
        values = get_distinct_values(conn, condition)

        before_after[condition] = {}

        include_none = False

        if condition == "elongating" or condition == "initiating":
            for x in values:
                if x == 1:
                    before_after[condition][condition] = x
                else:
                    before_after[condition][f"Not {condition}"] = x

            values = [
                str.title(condition) if x == 1 else "Not " + str.title(condition)
                for x in values
            ]
            formatted[condition] = sorted(values)
            continue

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
            for value in values:
                before_after[condition][rename_dict[value]] = value

            values = [rename_dict[value] for value in values]
            formatted[condition] = sorted(values)
            continue

        if condition not in ["sra_run", "study"]:
            before_after[condition] = {str.title(value): value for value in values}
            values = [str.title(value) for value in values]
        elif condition in ["sra_run", "study"]:
            before_after[condition] = {value: value for value in values}
        try:
            values = [int(i) for i in values]
        except:
            pass

        formatted[condition] = sorted(values)
        if include_none:
            # reintroduce nones
            formatted[condition].append(None)

    return formatted, before_after


def parse_form_result(form_list, before_after, conditions):
    input_dict = {condition: [] for condition in conditions}

    for item in form_list:
        for condition in conditions:
            if item in before_after[condition].keys():
                input_dict[condition].append(before_after[condition][item])
                print(before_after[condition][item])

    return input_dict


def construct_query_string(input_dict):
    string = "SELECT trips_id FROM conditions WHERE "
    number_added = 0
    for title in input_dict:
        if len(input_dict[title]) > 1:
            title_string = title + " IN " + str(tuple(i for i in input_dict[title]))
            string = string + title_string + " AND "
            number_added += 1

        elif len(input_dict[title]) == 1:
            title_string = title + " == '" + str(input_dict[title][0])
            string = string + title_string + "' AND "
            number_added += 1

        elif len(input_dict[title]) == 0:
            continue
    if number_added > 0:
        return string[:-5] + ";"
    else:
        return string[:-7] + ";"


def run_query(query, conn):
    result = conn.execute(query).fetchall()
    trips_ids = []
    for row in result:
        trips_ids.append(row["trips_id"])
    return trips_ids


def build_trips_url(trips_id):

    if len(trips_id) > 0:
        base_url = (
            "https://trips.ucc.ie/hg19_sarscov2/wuhcor1_hg19/interactive_plot/?files="
        )
        for file in trips_id:
            base_url += file + ","

        tail_url = "&tran=NC_045512&minread=5&maxread=150&user_dir=fiveprime&ambig=F&cov=F&lg=T&nuc=F&rs=0&crd=F"
        return base_url + tail_url
    else:
        return "Oops! Looks like your query returned no files!"
