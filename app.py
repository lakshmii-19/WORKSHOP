"""
Flask Application for Smart Campus Lost & Found Matcher.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database
import matcher

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "campus-lost-found-secret-key-2025")

# Initialize database on application start
database.init_db()

CATEGORIES = [
    "Electronics",
    "Wallets & IDs",
    "Books & Notes",
    "Clothing & Apparel",
    "Personal Accessories",
    "Bags & Backpacks",
    "Keys & Cards",
    "Sports & Fitness",
    "Other"
]

@app.context_processor
def inject_globals():
    return {
        "categories": CATEGORIES
    }

@app.route("/")
def index():
    """Homepage dashboard showing metrics and lost & found items."""
    item_type_filter = request.args.get("type", "").strip() or None
    category_filter = request.args.get("category", "").strip() or None
    status_filter = request.args.get("status", "").strip() or None
    search_query = request.args.get("q", "").strip() or None

    items = database.get_all_items(
        item_type=item_type_filter,
        status=status_filter,
        category=category_filter,
        search=search_query
    )
    stats = database.get_dashboard_stats()

    return render_template(
        "index.html",
        items=items,
        stats=stats,
        current_type=item_type_filter,
        current_category=category_filter,
        current_status=status_filter,
        search_query=search_query
    )

@app.route("/report/<item_type>", methods=["GET", "POST"])
def report_item(item_type):
    """Report a lost or found item."""
    if item_type not in ["lost", "found"]:
        flash("Invalid report type.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        colour = request.form.get("colour", "").strip()
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        contact_info = request.form.get("contact_info", "").strip()

        if not name or not category or not colour or not location or not description:
            flash("Please fill in all required fields (Name, Category, Colour, Location, Description).", "error")
            return render_template("report.html", item_type=item_type, form_data=request.form)

        item_data = {
            "item_type": item_type,
            "name": name,
            "category": category,
            "colour": colour,
            "location": location,
            "description": description,
            "contact_info": contact_info,
            "status": "Active"
        }

        new_id = database.create_item(item_data)
        flash(f"Successfully recorded your {item_type} item report! Showing potential smart matches below.", "success")
        return redirect(url_for("item_detail", item_id=new_id))

    return render_template("report.html", item_type=item_type, form_data={})

@app.route("/item/<int:item_id>")
def item_detail(item_id):
    """Item detail view with smart match suggestions."""
    item = database.get_item_by_id(item_id)
    if not item:
        flash("Item not found.", "error")
        return redirect(url_for("index"))

    # Determine opposite type for smart matching
    opposite_type = "found" if item["item_type"] == "lost" else "lost"
    candidates = database.get_all_items(item_type=opposite_type, status="Active")
    matches = matcher.find_matches_for_item(item, candidates, min_threshold=0.10, top_k=6)

    return render_template(
        "item_detail.html",
        item=item,
        matches=matches,
        opposite_type=opposite_type
    )

@app.route("/item/<int:item_id>/status", methods=["POST"])
def update_status(item_id):
    """Update item status (e.g. Active to Returned)."""
    new_status = request.form.get("status")
    if new_status not in ["Active", "Returned"]:
        flash("Invalid status value.", "error")
        return redirect(url_for("item_detail", item_id=item_id))

    success = database.update_item_status(item_id, new_status)
    if success:
        flash(f"Item #{item_id} marked as {new_status}!", "success")
    else:
        flash("Could not update item status.", "error")

    # Redirect back to referring page or item detail
    referrer = request.referrer
    if referrer and ("/" in referrer):
        return redirect(referrer)
    return redirect(url_for("item_detail", item_id=item_id))

@app.route("/matches")
def smart_matches_dashboard():
    """Global campus smart matching board showing top pairs between active lost and found items."""
    lost_items = database.get_all_items(item_type="lost", status="Active")
    found_items = database.get_all_items(item_type="found", status="Active")
    pairings = matcher.find_all_campus_matches(lost_items, found_items, min_threshold=0.15)

    return render_template("matches.html", pairings=pairings)

# REST API Endpoints for dynamic client-side interactions
@app.route("/api/items", methods=["GET"])
def api_items():
    item_type = request.args.get("type")
    status = request.args.get("status")
    category = request.args.get("category")
    search = request.args.get("q")
    items = database.get_all_items(item_type=item_type, status=status, category=category, search=search)
    return jsonify({"success": True, "items": items, "count": len(items)})

@app.route("/api/item/<int:item_id>/matches", methods=["GET"])
def api_item_matches(item_id):
    item = database.get_item_by_id(item_id)
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404

    opposite_type = "found" if item["item_type"] == "lost" else "lost"
    candidates = database.get_all_items(item_type=opposite_type)
    matches = matcher.find_matches_for_item(item, candidates)
    return jsonify({"success": True, "target": item, "matches": matches})

@app.route("/api/item/<int:item_id>/status", methods=["POST"])
def api_update_status(item_id):
    data = request.get_json(silent=True) or request.form
    new_status = data.get("status")
    if new_status not in ["Active", "Returned"]:
        return jsonify({"success": False, "error": "Invalid status"}), 400

    success = database.update_item_status(item_id, new_status)
    if success:
        return jsonify({"success": True, "item_id": item_id, "new_status": new_status})
    return jsonify({"success": False, "error": "Item not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
