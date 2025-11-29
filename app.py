from flask import Flask, render_template, request, redirect, url_for, abort, session
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCENARIO_PATH = os.path.join(BASE_DIR, "scenarios.json")
PACKS_DIR = os.path.join(BASE_DIR, "packs")
CATEGORIES_PATH = os.path.join(PACKS_DIR, "categories.json")
PACKS_META_PATH = os.path.join(PACKS_DIR, "packs_meta.json")
BLOG_POSTS_PATH = os.path.join(BASE_DIR, "blog_posts.json")

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")

# Load base scenarios (used on homepage and free practice)
with open(SCENARIO_PATH, "r", encoding="utf-8") as f:
    SCENARIOS = json.load(f)

with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
    CATEGORIES = json.load(f)

with open(PACKS_META_PATH, "r", encoding="utf-8") as f:
    PACKS_META = json.load(f)

with open(BLOG_POSTS_PATH, "r", encoding="utf-8") as f:
    BLOG_POSTS = json.load(f)


def get_category(slug: str):
    for c in CATEGORIES:
        if c.get("slug") == slug:
            return c
    return None


def get_pack(slug: str):
    for p in PACKS_META:
        if p.get("slug") == slug:
            return p
    return None


def load_pack_scenarios(filename: str):
    path = os.path.join(PACKS_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_blog_post(slug: str):
    for post in BLOG_POSTS:
        if post.get("slug") == slug:
            return post
    return None


def track_recent_scenario(label: str):
    recent = session.get("recent_scenarios", [])
    if label in recent:
        recent.remove(label)
    recent.insert(0, label)
    session["recent_scenarios"] = recent[:5]


@app.route("/")
def home():
    # Show a few core scenarios and some featured categories and posts
    featured_scenarios = SCENARIOS[:3]
    featured_categories = CATEGORIES[:3]
    recent = session.get("recent_scenarios", [])
    latest_posts = BLOG_POSTS[:2]
    return render_template(
        "home.html",
        scenarios=featured_scenarios,
        categories=featured_categories,
        recent=recent,
        posts=latest_posts,
    )


@app.route("/practice")
def practice():
    total = len(SCENARIOS)
    return render_template("practice.html", scenarios=SCENARIOS, total=total)


@app.route("/scenario/<int:scenario_id>")
def scenario_view(scenario_id):
    scenario = None
    for s in SCENARIOS:
        if s.get("id") == scenario_id:
            scenario = s
            break
    if not scenario:
        abort(404)
    track_recent_scenario(scenario.get("title", f"Scenario {scenario_id}"))
    return render_template("scenario.html", scenario=scenario)


@app.route("/scenario/<int:scenario_id>/result")
def scenario_result(scenario_id):
    scenario = None
    for s in SCENARIOS:
        if s.get("id") == scenario_id:
            scenario = s
            break
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


@app.route("/categories")
def categories_view():
    return render_template("categories.html", categories=CATEGORIES, packs=PACKS_META)


@app.route("/category/<slug>")
def category_detail(slug):
    category = get_category(slug)
    if not category:
        abort(404)
    packs = [p for p in PACKS_META if p.get("category_slug") == slug]
    return render_template("category_detail.html", category=category, packs=packs)


@app.route("/packs")
def packs_view():
    # simple listing for now
    return render_template("packs.html", packs=PACKS_META, categories=CATEGORIES)


@app.route("/pack/<slug>")
def pack_detail(slug):
    pack = get_pack(slug)
    if not pack:
        abort(404)
    scenarios = load_pack_scenarios(pack["scenarios_file"])
    return render_template("pack_detail.html", pack=pack, scenarios=scenarios, category=get_category(pack["category_slug"]))


@app.route("/blog")
def blog_index():
    return render_template("blog.html", posts=BLOG_POSTS)


@app.route("/blog/<slug>")
def blog_post(slug):
    post = get_blog_post(slug)
    if not post:
        abort(404)
    return render_template("blog_post.html", post=post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")




@app.route("/start")
def start_here():
    # Recommend a simple path: core practice, then a focus pack from a few key categories
    focus_categories = ["difficult-conversations", "dating-confidence", "workplace-assertiveness", "social-anxiety"]
    focus_packs = [p for p in PACKS_META if p.get("category_slug") in focus_categories]
    # group packs by category
    grouped = {}
    for p in focus_packs:
        grouped.setdefault(p["category_slug"], []).append(p)
    return render_template(
        "start_here.html",
        scenarios=SCENARIOS[:3],
        categories=CATEGORIES,
        focus_grouped=grouped,
    )


if __name__ == "__main__":
    app.run(debug=True)
