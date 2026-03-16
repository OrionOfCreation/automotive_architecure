from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

state = {
    "radar": {
        "front_left": 255, "front_right": 255,
        "rear_left":  255, "rear_right":  255,
    },
    "lights": {
        "low_beam": 0, "high_beam": 0,
        "turn_left": 0, "turn_right": 0,
    },
    "emergency_braking": 0,
    "speed": 0,
    "gas": 0,   # Capteur gaz habitacle 0-255
}

def _set(keys, value, cast=int, lo=None, hi=None):
    v = cast(value)
    if lo is not None: v = max(lo, v)
    if hi is not None: v = min(hi, v)
    d = state
    for k in keys[:-1]: d = d[k]
    d[keys[-1]] = v

# ── Global ─────────────────────────────────────────────────
@app.route("/api/all", methods=["GET"])
def get_all():
    return jsonify(state)

@app.route("/api/all", methods=["POST"])
def set_all():
    for section, values in request.get_json(force=True).items():
        if section in state:
            if isinstance(values, dict): state[section].update(values)
            else: state[section] = values
    return jsonify({"status": "ok", "state": state})

# ── Radar (1-4) ────────────────────────────────────────────
@app.route("/api/radar/front_left",  methods=["GET","POST"])
def radar_fl():
    if request.method=="POST": _set(["radar","front_left"],  request.json["value"], lo=0, hi=255)
    return jsonify({"sensor":"front_left",  "value": state["radar"]["front_left"]})

@app.route("/api/radar/front_right", methods=["GET","POST"])
def radar_fr():
    if request.method=="POST": _set(["radar","front_right"], request.json["value"], lo=0, hi=255)
    return jsonify({"sensor":"front_right", "value": state["radar"]["front_right"]})

@app.route("/api/radar/rear_left",   methods=["GET","POST"])
def radar_rl():
    if request.method=="POST": _set(["radar","rear_left"],   request.json["value"], lo=0, hi=255)
    return jsonify({"sensor":"rear_left",   "value": state["radar"]["rear_left"]})

@app.route("/api/radar/rear_right",  methods=["GET","POST"])
def radar_rr():
    if request.method=="POST": _set(["radar","rear_right"],  request.json["value"], lo=0, hi=255)
    return jsonify({"sensor":"rear_right",  "value": state["radar"]["rear_right"]})

# ── Éclairage (5-8) ────────────────────────────────────────
@app.route("/api/lights/low_beam",   methods=["GET","POST"])
def light_lb():
    if request.method=="POST": _set(["lights","low_beam"],   request.json["status"], lo=0, hi=1)
    return jsonify({"light":"low_beam",   "status": state["lights"]["low_beam"]})

@app.route("/api/lights/high_beam",  methods=["GET","POST"])
def light_hb():
    if request.method=="POST": _set(["lights","high_beam"],  request.json["status"], lo=0, hi=1)
    return jsonify({"light":"high_beam",  "status": state["lights"]["high_beam"]})

@app.route("/api/lights/turn_left",  methods=["GET","POST"])
def light_tl():
    if request.method=="POST": _set(["lights","turn_left"],  request.json["status"], lo=0, hi=1)
    return jsonify({"light":"turn_left",  "status": state["lights"]["turn_left"]})

@app.route("/api/lights/turn_right", methods=["GET","POST"])
def light_tr():
    if request.method=="POST": _set(["lights","turn_right"], request.json["status"], lo=0, hi=1)
    return jsonify({"light":"turn_right", "status": state["lights"]["turn_right"]})

# ── AFU (9) ────────────────────────────────────────────────
@app.route("/api/braking/emergency", methods=["GET","POST"])
def braking():
    if request.method=="POST": _set(["emergency_braking"], request.json["status"], lo=0, hi=1)
    return jsonify({"emergency_braking": state["emergency_braking"]})

# ── Vitesse (10) ───────────────────────────────────────────
@app.route("/api/speed", methods=["GET","POST"])
def speed():
    if request.method=="POST": _set(["speed"], request.json["value"], lo=0, hi=100)
    return jsonify({"speed": state["speed"]})

# ── Gaz habitacle (11) ─────────────────────────────────────
@app.route("/api/gas", methods=["GET","POST"])
def gas():
    if request.method=="POST": _set(["gas"], request.json["value"], lo=0, hi=255)
    return jsonify({"gas": state["gas"]})

if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║   API Tableau de bord véhicule           ║")
    print("║   http://localhost:5000/api/all          ║")
    print("║   11 endpoints · GET + POST              ║")
    print("╚══════════════════════════════════════════╝")
    app.run(debug=True, port=5000)
