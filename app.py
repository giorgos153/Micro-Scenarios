from flask import Flask, render_template, request, redirect, url_for, abort
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCENARIO_PATH = os.path.join(BASE_DIR, "scenarios.json")
PACKS_DIR = os.path.join(BASE_DIR, "packs")
DATING_PACK_PATH = os.path.join(PACKS_DIR, "dating_confidence_pack.json")

with open(SCENARIO_PATH, "r", encoding="utf-8") as f:
    SCENARIOS = json.load(f)

# Products for the /store page
PRODUCTS = [
    {
        "slug": "dating-confidence-pack",
        "name": "Dating & Social Confidence Pack",
        "price": "$4.99",
        "description": "15 micro-scenarios to practice messaging, first dates, and confident communication.",
        "preview_url": "/store/dating-confidence-preview",
        "buy_url": "https://your-gumroad-or-payhip-link-here"
    }
]


def get_scenario(scenario_id: int):
    for s in SCENARIOS:
        if s.get("id") == scenario_id:
            return s
    return None


@app.route("/")
def index():
    total = len(SCENARIOS)
    return render_template("index.html", scenarios=SCENARIOS, total=total)


@app.route("/scenario/<int:scenario_id>")
def scenario_view(scenario_id):
    scenario = get_scenario(scenario_id)
    if not scenario:
        abort(404)
    return render_template("scenario.html", scenario=scenario)


@app.route("/scenario/<int:scenario_id>/result", methods=["GET"])
def scenario_result(scenario_id):
    scenario = get_scenario(scenario_id)
    if not scenario:
        abort(404)

    choice_id = request.args.get("choice")
    if not choice_id:
        return redirect(url_for("scenario_view", scenario_id=scenario_id))

    choice_data = None
    for choice in scenario.get("choices", []):
        if choice.get("id") == choice_id:
            choice_data = choice
            break

    if not choice_data:
        return redirect(url_for("scenario_view", scenario_id=scenario_id))

    return render_template("result.html", scenario=scenario, choice=choice_data)


@app.route("/store")
def store():
    return render_template("store.html", products=PRODUCTS)


@app.route("/store/dating-confidence-preview")
def dating_confidence_preview():
    try:
        with open(DATING_PACK_PATH, "r", encoding="utf-8") as f:
            pack_data = json.load(f)
    except FileNotFoundError:
        abort(404)

    # show first few scenarios as a preview (titles + situations only)
    preview_scenarios = pack_data[:3]
    return render_template(
        "pack_preview.html",
        pack_name="Dating & Social Confidence Pack",
        scenarios=preview_scenarios
    )


if __name__ == "__main__":
    app.run(debug=True)
