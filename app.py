from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from data_renderer.registry import DATASETS


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    @app.get("/api/datasets")
    def list_datasets():
        return jsonify([dataset.metadata() for dataset in DATASETS.values()])

    @app.get("/api/datasets/<dataset_id>")
    def get_dataset(dataset_id: str):
        dataset = DATASETS.get(dataset_id)
        if dataset is None:
            return jsonify({"error": f"Unknown dataset: {dataset_id}"}), 404

        try:
            payload = dataset.load(request.args)
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        return jsonify(payload)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
