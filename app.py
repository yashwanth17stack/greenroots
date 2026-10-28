from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3
import csv
import io
from pathlib import Path
from datetime import date

app = Flask(__name__)
app.secret_key = "change-this-secret-key-for-your-own-project"
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "trees.db"


def get_db_connection():
    """Open a SQLite connection and return rows by column name."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the database table the first time the application runs."""
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tree_name TEXT NOT NULL,
                species TEXT NOT NULL,
                planter TEXT NOT NULL,
                location TEXT NOT NULL,
                planted_on TEXT NOT NULL,
                height_cm REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Healthy',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "All").strip()

    query = "SELECT * FROM trees WHERE 1=1"
    params = []

    if search:
        query += """
            AND (tree_name LIKE ? OR species LIKE ? OR planter LIKE ? OR location LIKE ?)
        """
        term = f"%{search}%"
        params.extend([term, term, term, term])

    if status_filter in ("Healthy", "Needs attention"):
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY planted_on DESC, id DESC"

    with get_db_connection() as connection:
        trees = connection.execute(query, params).fetchall()

        total_trees = connection.execute(
            "SELECT COUNT(*) AS total FROM trees"
        ).fetchone()["total"]

        healthy_trees = connection.execute(
            "SELECT COUNT(*) AS total FROM trees WHERE status = 'Healthy'"
        ).fetchone()["total"]

        attention_trees = connection.execute(
            "SELECT COUNT(*) AS total FROM trees WHERE status = 'Needs attention'"
        ).fetchone()["total"]

        site_count = connection.execute(
            "SELECT COUNT(DISTINCT location) AS total FROM trees"
        ).fetchone()["total"]

        contributors = connection.execute(
            """
            SELECT planter, COUNT(*) AS tree_count
            FROM trees
            GROUP BY planter
            ORDER BY tree_count DESC, planter COLLATE NOCASE ASC
            LIMIT 8
            """
        ).fetchall()

        species_counts = connection.execute(
            """
            SELECT species, COUNT(*) AS tree_count
            FROM trees
            GROUP BY species
            ORDER BY tree_count DESC, species ASC
            LIMIT 6
            """
        ).fetchall()

    healthy_percent = round((healthy_trees / total_trees) * 100) if total_trees else 0
    attention_percent = 100 - healthy_percent if total_trees else 0

    return render_template(
        "index.html",
        trees=trees,
        total_trees=total_trees,
        healthy_trees=healthy_trees,
        attention_trees=attention_trees,
        site_count=site_count,
        contributors=contributors,
        species_counts=species_counts,
        healthy_percent=healthy_percent,
        attention_percent=attention_percent,
        search=search,
        status_filter=status_filter,
        today=date.today().isoformat(),
    )


@app.route("/add", methods=["POST"])
def add_tree():
    tree_name = request.form.get("tree_name", "").strip()
    species = request.form.get("species", "").strip()
    planter = request.form.get("planter", "").strip()
    location = request.form.get("location", "").strip()
    planted_on = request.form.get("planted_on", "").strip()
    height_raw = request.form.get("height_cm", "").strip()
    status = request.form.get("status", "Healthy").strip()
    notes = request.form.get("notes", "").strip()

    if not all([tree_name, species, planter, location, planted_on, height_raw]):
        flash("Please complete all required fields.", "error")
        return redirect(url_for("index") + "#add-tree")

    try:
        height_cm = float(height_raw)
        if height_cm <= 0:
            raise ValueError
    except ValueError:
        flash("Tree height must be a number greater than zero.", "error")
        return redirect(url_for("index") + "#add-tree")

    if status not in ("Healthy", "Needs attention"):
        status = "Healthy"

    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO trees
                (tree_name, species, planter, location, planted_on, height_cm, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (tree_name, species, planter, location, planted_on, height_cm, status, notes),
        )
        connection.commit()

    flash(f"Tree '{tree_name}' was added successfully.", "success")
    return redirect(url_for("index") + "#tree-records")


@app.route("/update-status/<int:tree_id>", methods=["POST"])
def update_status(tree_id):
    new_status = request.form.get("status", "")
    if new_status not in ("Healthy", "Needs attention"):
        flash("Please choose a valid health status.", "error")
        return redirect(url_for("index") + "#tree-records")

    with get_db_connection() as connection:
        connection.execute(
            "UPDATE trees SET status = ? WHERE id = ?",
            (new_status, tree_id),
        )
        connection.commit()

    flash("Tree health status updated.", "success")
    return redirect(url_for("index") + "#tree-records")


@app.route("/delete/<int:tree_id>", methods=["POST"])
def delete_tree(tree_id):
    with get_db_connection() as connection:
        connection.execute("DELETE FROM trees WHERE id = ?", (tree_id,))
        connection.commit()

    flash("Tree record deleted.", "success")
    return redirect(url_for("index") + "#tree-records")


@app.route("/export")
def export_csv():
    with get_db_connection() as connection:
        trees = connection.execute(
            """
            SELECT tree_name, species, planter, location, planted_on,
                   height_cm, status, notes
            FROM trees
            ORDER BY planted_on DESC, id DESC
            """
        ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Tree ID / Name", "Species", "Planted By", "Location",
        "Planting Date", "Height (cm)", "Health Status", "Notes"
    ])
    for tree in trees:
        writer.writerow([
            tree["tree_name"], tree["species"], tree["planter"],
            tree["location"], tree["planted_on"], tree["height_cm"],
            tree["status"], tree["notes"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tree-plantation-report.csv"},
    )


init_db()

if __name__ == "__main__":
    app.run(debug=True)
