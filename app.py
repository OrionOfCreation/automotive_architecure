from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── État initial ────────────────────────────────────────────
state = {
    # Radar de recul – 4 capteurs sur le pare-chocs ARRIÈRE
    # arr_g_ext  = Arrière Gauche  Extérieur
    # arr_g_int  = Arrière Gauche  Intérieur
    # arr_d_int  = Arrière Droit   Intérieur
    # arr_d_ext  = Arrière Droit   Extérieur
    # Valeurs : 0 (obstacle très proche) → 255 (voie libre)
    "radar": {
        "arr_g_ext": 255,
        "arr_g_int": 255,
        "arr_d_int": 255,
        "arr_d_ext": 255,
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
    # Gaz d'échappement dans l'habitacle en ppm (0–255)
    "gas": 0,
}

# ── Helper ──────────────────────────────────────────────────
def _set(keys, value, cast=int, lo=None, hi=None):
    v = cast(value)
    if lo is not None: v = max(lo, v)
    if hi is not None: v = min(hi, v)
    d = state
    for k in keys[:-1]: d = d[k]
    d[keys[-1]] = v

# ═══════════════════════════════════════════════════════════
#  GLOBAL
# ═══════════════════════════════════════════════════════════
@app.route("/api/all", methods=["GET"])
def get_all():
    """Retourne l'état complet du véhicule."""
    return jsonify(state)

@app.route("/api/all", methods=["POST"])
def set_all():
    """Met à jour l'état complet (utile pour les scénarios de test)."""
    for section, values in request.get_json(force=True).items():
        if section in state:
            if isinstance(values, dict): state[section].update(values)
            else: state[section] = values
    return jsonify({"status": "ok", "state": state})

# ═══════════════════════════════════════════════════════════
#  RADAR ARRIÈRE – endpoints 1 à 4
# ═══════════════════════════════════════════════════════════
@app.route("/api/radar/arr_g_ext", methods=["GET", "POST"])
def radar_arr_g_ext():
    """Capteur Arrière Gauche Extérieur."""
    if request.method == "POST":
        _set(["radar", "arr_g_ext"], request.json["value"], lo=0, hi=255)
    return jsonify({"sensor": "arr_g_ext", "value": state["radar"]["arr_g_ext"]})

@app.route("/api/radar/arr_g_int", methods=["GET", "POST"])
def radar_arr_g_int():
    """Capteur Arrière Gauche Intérieur."""
    if request.method == "POST":
        _set(["radar", "arr_g_int"], request.json["value"], lo=0, hi=255)
    return jsonify({"sensor": "arr_g_int", "value": state["radar"]["arr_g_int"]})

@app.route("/api/radar/arr_d_int", methods=["GET", "POST"])
def radar_arr_d_int():
    """Capteur Arrière Droit Intérieur."""
    if request.method == "POST":
        _set(["radar", "arr_d_int"], request.json["value"], lo=0, hi=255)
    return jsonify({"sensor": "arr_d_int", "value": state["radar"]["arr_d_int"]})

@app.route("/api/radar/arr_d_ext", methods=["GET", "POST"])
def radar_arr_d_ext():
    """Capteur Arrière Droit Extérieur."""
    if request.method == "POST":
        _set(["radar", "arr_d_ext"], request.json["value"], lo=0, hi=255)
    return jsonify({"sensor": "arr_d_ext", "value": state["radar"]["arr_d_ext"]})

# ═══════════════════════════════════════════════════════════
#  ÉCLAIRAGE – endpoints 5 à 8
# ═══════════════════════════════════════════════════════════
@app.route("/api/lights/low_beam", methods=["GET", "POST"])
def light_lb():
    if request.method == "POST":
        _set(["lights", "low_beam"], request.json["status"], lo=0, hi=1)
    return jsonify({"light": "low_beam", "status": state["lights"]["low_beam"]})

@app.route("/api/lights/high_beam", methods=["GET", "POST"])
def light_hb():
    if request.method == "POST":
        _set(["lights", "high_beam"], request.json["status"], lo=0, hi=1)
    return jsonify({"light": "high_beam", "status": state["lights"]["high_beam"]})

@app.route("/api/lights/turn_left", methods=["GET", "POST"])
def light_tl():
    if request.method == "POST":
        _set(["lights", "turn_left"], request.json["status"], lo=0, hi=1)
    return jsonify({"light": "turn_left", "status": state["lights"]["turn_left"]})

@app.route("/api/lights/turn_right", methods=["GET", "POST"])
def light_tr():
    if request.method == "POST":
        _set(["lights", "turn_right"], request.json["status"], lo=0, hi=1)
    return jsonify({"light": "turn_right", "status": state["lights"]["turn_right"]})

# ═══════════════════════════════════════════════════════════
#  AFU – endpoint 9
# ═══════════════════════════════════════════════════════════
@app.route("/api/braking/emergency", methods=["GET", "POST"])
def braking():
    if request.method == "POST":
        _set(["emergency_braking"], request.json["status"], lo=0, hi=1)
    return jsonify({"emergency_braking": state["emergency_braking"]})

# ═══════════════════════════════════════════════════════════
#  VITESSE – endpoint 10
# ═══════════════════════════════════════════════════════════
@app.route("/api/speed", methods=["GET", "POST"])
def speed():
    if request.method == "POST":
        _set(["speed"], request.json["value"], lo=0, hi=100)
    return jsonify({"speed": state["speed"]})

# ═══════════════════════════════════════════════════════════
#  GAZ HABITACLE – endpoint 11
# ═══════════════════════════════════════════════════════════
@app.route("/api/gas", methods=["GET", "POST"])
def gas():
    if request.method == "POST":
        _set(["gas"], request.json["value"], lo=0, hi=255)
    return jsonify({"gas": state["gas"]})

# ── Lancement ───────────────────────────────────────────────
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════╗")
    print("║   API Tableau de bord véhicule               ║")
    print("║   http://localhost:5000/api/all              ║")
    print("╠══════════════════════════════════════════════╣")
    print("║   Radar : arr_g_ext · arr_g_int              ║")
    print("║           arr_d_int · arr_d_ext              ║")
    print("╚══════════════════════════════════════════════╝")
    app.run(debug=True, port=5000)
