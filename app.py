from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ─── État initial du véhicule ───────────────────────────────────────────────
state = {
    # Radar de recul : 4 angles, valeurs de 0 (proche) à 255 (loin / rien)
    "radar": {
        "front_left":  255,
        "front_right": 255,
        "rear_left":   255,
        "rear_right":  255,
    },
    # Éclairage : 0 = éteint, 1 = allumé
    "lights": {
        "low_beam":   0,   # Feux de croisement
        "high_beam":  0,   # Pleins phares
        "turn_left":  0,   # Clignotant gauche
        "turn_right": 0,   # Clignotant droit
    },
    # Freinage d'urgence automatique : 0 = inactif, 1 = actif
    "emergency_braking": 0,
    # Vitesse en km/h (0–100)
    "speed": 0,
}

# ─── Helper ─────────────────────────────────────────────────────────────────
def _set(keys: list, value, cast=int, min_val=None, max_val=None):
    """Traverse nested dict via keys list and set value with optional clamping."""
    v = cast(value)
    if min_val is not None: v = max(min_val, v)
    if max_val is not None: v = min(max_val, v)
    d = state
    for k in keys[:-1]:
        d = d[k]
    d[keys[-1]] = v

# ═══════════════════════════════════════════════════════════════════════════
#  ENDPOINT GLOBAL  –  tout récupérer en une seule requête
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/api/all", methods=["GET"])
def get_all():
    """Retourne l'état complet du véhicule."""
    return jsonify(state)

@app.route("/api/all", methods=["POST"])
def set_all():
    """Met à jour l'état complet du véhicule (utile pour simuler des scénarios)."""
    data = request.get_json(force=True)
    for section, values in data.items():
        if section in state:
            if isinstance(values, dict):
                state[section].update(values)
            else:
                state[section] = values
    return jsonify({"status": "ok", "state": state})

# ═══════════════════════════════════════════════════════════════════════════
#  RADAR  (endpoints 1–4)
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/api/radar/front_left", methods=["GET"])
def get_radar_fl():
    return jsonify({"sensor": "front_left", "value": state["radar"]["front_left"]})

@app.route("/api/radar/front_left", methods=["POST"])
def set_radar_fl():
    _set(["radar", "front_left"], request.json["value"], min_val=0, max_val=255)
    return jsonify({"status": "ok", "value": state["radar"]["front_left"]})


@app.route("/api/radar/front_right", methods=["GET"])
def get_radar_fr():
    return jsonify({"sensor": "front_right", "value": state["radar"]["front_right"]})

@app.route("/api/radar/front_right", methods=["POST"])
def set_radar_fr():
    _set(["radar", "front_right"], request.json["value"], min_val=0, max_val=255)
    return jsonify({"status": "ok", "value": state["radar"]["front_right"]})


@app.route("/api/radar/rear_left", methods=["GET"])
def get_radar_rl():
    return jsonify({"sensor": "rear_left", "value": state["radar"]["rear_left"]})

@app.route("/api/radar/rear_left", methods=["POST"])
def set_radar_rl():
    _set(["radar", "rear_left"], request.json["value"], min_val=0, max_val=255)
    return jsonify({"status": "ok", "value": state["radar"]["rear_left"]})


@app.route("/api/radar/rear_right", methods=["GET"])
def get_radar_rr():
    return jsonify({"sensor": "rear_right", "value": state["radar"]["rear_right"]})

@app.route("/api/radar/rear_right", methods=["POST"])
def set_radar_rr():
    _set(["radar", "rear_right"], request.json["value"], min_val=0, max_val=255)
    return jsonify({"status": "ok", "value": state["radar"]["rear_right"]})

# ═══════════════════════════════════════════════════════════════════════════
#  ÉCLAIRAGE  (endpoints 5–8)
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/api/lights/low_beam", methods=["GET"])
def get_low_beam():
    return jsonify({"light": "low_beam", "status": state["lights"]["low_beam"]})

@app.route("/api/lights/low_beam", methods=["POST"])
def set_low_beam():
    _set(["lights", "low_beam"], request.json["status"], min_val=0, max_val=1)
    return jsonify({"status": "ok", "value": state["lights"]["low_beam"]})


@app.route("/api/lights/high_beam", methods=["GET"])
def get_high_beam():
    return jsonify({"light": "high_beam", "status": state["lights"]["high_beam"]})

@app.route("/api/lights/high_beam", methods=["POST"])
def set_high_beam():
    _set(["lights", "high_beam"], request.json["status"], min_val=0, max_val=1)
    return jsonify({"status": "ok", "value": state["lights"]["high_beam"]})


@app.route("/api/lights/turn_left", methods=["GET"])
def get_turn_left():
    return jsonify({"light": "turn_left", "status": state["lights"]["turn_left"]})

@app.route("/api/lights/turn_left", methods=["POST"])
def set_turn_left():
    _set(["lights", "turn_left"], request.json["status"], min_val=0, max_val=1)
    return jsonify({"status": "ok", "value": state["lights"]["turn_left"]})


@app.route("/api/lights/turn_right", methods=["GET"])
def get_turn_right():
    return jsonify({"light": "turn_right", "status": state["lights"]["turn_right"]})

@app.route("/api/lights/turn_right", methods=["POST"])
def set_turn_right():
    _set(["lights", "turn_right"], request.json["status"], min_val=0, max_val=1)
    return jsonify({"status": "ok", "value": state["lights"]["turn_right"]})

# ═══════════════════════════════════════════════════════════════════════════
#  AFU – Freinage d'urgence automatique  (endpoint 9)
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/api/braking/emergency", methods=["GET"])
def get_emergency_braking():
    return jsonify({"emergency_braking": state["emergency_braking"]})

@app.route("/api/braking/emergency", methods=["POST"])
def set_emergency_braking():
    _set(["emergency_braking"], request.json["status"], min_val=0, max_val=1)
    return jsonify({"status": "ok", "value": state["emergency_braking"]})

# ═══════════════════════════════════════════════════════════════════════════
#  VITESSE  (endpoint 10)
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/api/speed", methods=["GET"])
def get_speed():
    return jsonify({"speed": state["speed"]})

@app.route("/api/speed", methods=["POST"])
def set_speed():
    _set(["speed"], request.json["value"], min_val=0, max_val=100)
    return jsonify({"status": "ok", "value": state["speed"]})

# ─── Lancement ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║   API Tableau de bord véhicule           ║")
    print("║   http://localhost:5000/api/all          ║")
    print("╚══════════════════════════════════════════╝")
    app.run(debug=True, port=5000)
