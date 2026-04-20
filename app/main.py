# MAIN
from flask import Flask, request, jsonify
app = Flask(__name__)


@app.route("/saludo")
def saludo():
    nombre = request.args.get("nombre")

    if not nombre:
        return jsonify({"error": "Falta el parámetro nombre"}), 400

    return jsonify({"mensaje": f"Hola {nombre}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
