from flask import Flask, render_template, request, redirect, url_for, abort, session
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCENARIO_PATH = os.path.join(BASE_DIR, "scenarios.json")
PACKS_DIR = os.path.join(BASE_DIR, "packs")
DATING_PACK_PATH = os.path.join(PACKS_DIR, "dating_confidence_pack.json")

# IMPORTANT: change this before going live and keep it secret.
UNLOCK_CODE_DATING = os.environ.get("DATING_UNLOCK_CODE", "DATING-UNLOCK-123")

# Secret key for sessions (change this in production)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")

with open(SCENARIO_PATH, "r", encoding="utf-8") as f:
    SCENARIOS = json.load(f)

with open(DATING_PACK_PATH, "r", encoding="utf-8") as f:
    DATING_PACK = json.load(f)


PRODUCTS = [
    {
        "slug": "dating-confidence-pack",
        "name": "Dating & Social Confidence Pack",
        "price": "$4.99",
        "description": "15+ micro-scenarios to practice messaging, first dates, and confident communication.",
        "preview_url": "/store/dating-confidence-preview",
        "premium_url": "/premium/dating-confidence",
        "buy_url": "https://your-gumroad-or-payhip-link-here"
    }
]


def premium_unlocked() -> bool:
    return session.get("premium_unlocked_dating", False)


def get_scenario(scenario_id: int):
    for s in SCENARIOS:
        if s.get("id") == scenario_id:
            return s
    return None


def get_dating_scenario(scenario_id: int):
    for s in DATING_PACK:
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
    return render_template("store.html", products=PRODUCTS, premium_unlocked=premium_unlocked())


@app.route("/store/dating-confidence-preview")
def dating_confidence_preview():
    # show first few scenarios as a text preview
    preview_scenarios = DATING_PACK[:3]
    return render_template(
        "pack_preview.html",
        pack_name="Dating & Social Confidence Pack",
        scenarios=preview_scenarios,
        premium_unlocked=premium_unlocked()
    )


@app.route("/unlock", methods=["GET", "POST"])
def unlock():
    error = None
    success = False

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        if not code:
            error = "Please enter your unlock code."
        elif code == UNLOCK_CODE_DATING:
            session["premium_unlocked_dating"] = True
            success = True
        else:
            error = "That unlock code is not valid. Please check it and try again."

    return render_template(
        "unlock.html",
        error=error,
        success=success
    )


@app.route("/premium/dating-confidence")
def premium_dating_pack():
    if not premium_unlocked():
        # user must buy the pack and unlock with code
        return redirect(url_for("store"))

    return render_template(
        "premium_pack.html",
        pack_name="Dating & Social Confidence Pack",
        scenarios=DATING_PACK
    )


@app.route("/premium/dating-confidence/<int:scenario_id>")
def premium_dating_scenario(scenario_id):
    if not premium_unlocked():
        return redirect(url_for("store"))

    scenario = get_dating_scenario(scenario_id)
    if not scenario:
        abort(404)

    return render_template("premium_scenario.html", scenario=scenario)


@app.route("/premium/dating-confidence/<int:scenario_id>/result")
def premium_dating_result(scenario_id):
    if not premium_unlocked():
        return redirect(url_for("store"))

    scenario = get_dating_scenario(scenario_id)
    if not scenario:
        abort(404)

    choice_id = request.args.get("choice")
    if not choice_id:
        return redirect(url_for("premium_dating_scenario", scenario_id=scenario_id))

    choice_data = None
    for choice in scenario.get("choices", []):
        if choice.get("id") == choice_id:
            choice_data = choice
            break

    if not choice_data:
        return redirect(url_for("premium_dating_scenario", scenario_id=scenario_id))

    return render_template("premium_result.html", scenario=scenario, choice=choice_data)


if __name__ == "__main__":
    app.run(debug=True)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")
