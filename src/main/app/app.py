from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import os
from database import db, Secret, AuditLog
from jenkins_client import JenkinsClient
from crypto_utils import encrypt_value, decrypt_value

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-prod")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///secrets.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
jenkins = JenkinsClient()

def log_action(action, secret_name, user="admin", details=""):
    entry = AuditLog(action=action, secret_name=secret_name, user=user,
                     details=details, timestamp=datetime.utcnow())
    db.session.add(entry)
    db.session.commit()

@app.route("/")
def dashboard():
    secrets = Secret.query.order_by(Secret.updated_at.desc()).all()
    expiring = [s for s in secrets if s.days_until_expiry is not None and s.days_until_expiry <= 7]
    return render_template("dashboard.html", secrets=secrets, expiring=expiring)

@app.route("/secrets/add", methods=["GET", "POST"])
def add_secret():
    if request.method == "POST":
        name = request.form["name"].strip().upper().replace(" ", "_")
        value = request.form["value"]
        description = request.form.get("description", "")
        expires_days = request.form.get("expires_days", type=int)

        if Secret.query.filter_by(name=name).first():
            flash(f"Secret '{name}' already exists.", "error")
            return redirect(url_for("add_secret"))

        expires_at = None
        if expires_days:
            from datetime import timedelta
            expires_at = datetime.utcnow() + timedelta(days=expires_days)

        secret = Secret(
            name=name,
            encrypted_value=encrypt_value(value),
            description=description,
            expires_at=expires_at
        )
        db.session.add(secret)
        db.session.commit()

        jenkins.push_credential(name, value, description)
        log_action("CREATE", name, details=f"Expiry: {expires_at}")
        flash(f"Secret '{name}' created and pushed to Jenkins.", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_secret.html")

@app.route("/secrets/<int:secret_id>/rotate", methods=["POST"])
def rotate_secret(secret_id):
    secret = Secret.query.get_or_404(secret_id)
    new_value = request.form.get("new_value", "").strip()
    if not new_value:
        flash("New value cannot be empty.", "error")
        return redirect(url_for("dashboard"))

    secret.encrypted_value = encrypt_value(new_value)
    secret.updated_at = datetime.utcnow()
    from datetime import timedelta
    secret.expires_at = datetime.utcnow() + timedelta(days=90)
    db.session.commit()

    jenkins.push_credential(secret.name, new_value, secret.description)
    log_action("ROTATE", secret.name, details="Manual rotation")
    flash(f"Secret '{secret.name}' rotated and synced to Jenkins.", "success")
    return redirect(url_for("dashboard"))

@app.route("/secrets/<int:secret_id>/delete", methods=["POST"])
def delete_secret(secret_id):
    secret = Secret.query.get_or_404(secret_id)
    name = secret.name
    db.session.delete(secret)
    db.session.commit()
    jenkins.delete_credential(name)
    log_action("DELETE", name)
    flash(f"Secret '{name}' deleted.", "success")
    return redirect(url_for("dashboard"))

@app.route("/audit")
def audit_log():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template("audit.html", logs=logs)

@app.route("/api/secrets", methods=["GET"])
def api_list_secrets():
    secrets = Secret.query.all()
    return jsonify([{
        "id": s.id, "name": s.name, "description": s.description,
        "created_at": s.created_at.isoformat(),
        "expires_at": s.expires_at.isoformat() if s.expires_at else None,
        "days_until_expiry": s.days_until_expiry
    } for s in secrets])

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "jenkins_connected": jenkins.is_connected()})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_ENV") == "development")
