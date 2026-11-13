from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .labels import PRIMARY_TARGETS, derive_prediction_gates


NON_FEATURE_COLUMNS = {
    "spot_uid",
    "spot_id",
    "sample_id",
    "dataset_id",
    "split",
    "embedding_qc_pass",
}


def embedding_columns(frame: pd.DataFrame) -> list[str]:
    prefixes = ("embedding_", "center_", "context_", "neighbor_")
    return [column for column in frame.columns if column.startswith(prefixes) and column not in NON_FEATURE_COLUMNS]


def add_neighbor_features(
    frame: pd.DataFrame,
    feature_cols: list[str],
    k_neighbors: int = 6,
    group_col: str = "sample_id",
) -> pd.DataFrame:
    from sklearn.neighbors import NearestNeighbors

    out = frame.copy()
    neighbor_values = np.zeros((len(out), len(feature_cols)), dtype=np.float32)
    for _, indices in out.groupby(group_col, sort=False).groups.items():
        loc = np.asarray(list(indices), dtype=int)
        group = out.loc[loc]
        if len(group) <= 1:
            neighbor_values[loc] = group[feature_cols].to_numpy(dtype=np.float32)
            continue
        coordinates = group[["x", "y"]].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy()
        neighbors = min(k_neighbors + 1, len(group))
        knn = NearestNeighbors(n_neighbors=neighbors).fit(coordinates)
        neighbor_indices = knn.kneighbors(return_distance=False)
        features = group[feature_cols].to_numpy(dtype=np.float32)
        for row_index, neighbor_index in enumerate(neighbor_indices):
            selected = neighbor_index[neighbor_index != row_index][:k_neighbors]
            if len(selected) == 0:
                selected = np.asarray([row_index])
            neighbor_values[loc[row_index]] = features[selected].mean(axis=0)
    neighbor_frame = pd.DataFrame(
        neighbor_values,
        index=out.index,
        columns=[f"neighbor_{column}" for column in feature_cols],
    )
    return pd.concat([out, neighbor_frame], axis=1)


def _reference_stats(frame: pd.DataFrame, targets: list[str]) -> dict[str, dict[str, float]]:
    return {
        target: {
            "mean": float(pd.to_numeric(frame[target], errors="coerce").mean()),
            "std": float(pd.to_numeric(frame[target], errors="coerce").std(ddof=0)),
        }
        for target in targets
    }


@dataclass
class EMTVistaEnsemble:
    targets: list[str] = field(default_factory=lambda: list(PRIMARY_TARGETS))
    alpha: float = 10.0
    n_models: int = 5
    max_components: int = 48
    random_state: int = 31
    models: list[Pipeline] = field(default_factory=list)
    feature_columns: list[str] = field(default_factory=list)
    reference_stats: dict[str, dict[str, float]] = field(default_factory=dict)
    residual_scale: dict[str, float] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def _pipeline(self, n_samples: int, n_features: int) -> Pipeline:
        components = min(self.max_components, max(1, n_samples - 1), n_features)
        return Pipeline(
            [
                ("scale", StandardScaler()),
                ("pca", PCA(n_components=components, random_state=self.random_state)),
                ("ridge", Ridge(alpha=self.alpha)),
            ]
        )

    def fit(
        self,
        frame: pd.DataFrame,
        feature_cols: list[str] | None = None,
        sample_weight_col: str = "label_confidence",
    ) -> "EMTVistaEnsemble":
        self.feature_columns = feature_cols or embedding_columns(frame)
        if not self.feature_columns:
            raise ValueError("No image embedding columns were found")
        missing_targets = [target for target in self.targets if target not in frame.columns]
        if missing_targets:
            raise ValueError(f"Missing targets: {', '.join(missing_targets)}")

        train = frame.copy()
        x = train[self.feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
        y = train[self.targets].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
        weights = pd.to_numeric(train.get(sample_weight_col, 1.0), errors="coerce")
        if np.isscalar(weights):
            weights = np.ones(len(train), dtype=float)
        else:
            weights = weights.fillna(0.5).to_numpy(dtype=float)

        rng = np.random.default_rng(self.random_state)
        self.models = []
        for model_index in range(self.n_models):
            indices = rng.choice(len(train), size=len(train), replace=True)
            model = self._pipeline(len(indices), x.shape[1])
            model.fit(x[indices], y[indices], ridge__sample_weight=weights[indices])
            self.models.append(model)

        fitted = np.stack([model.predict(x) for model in self.models], axis=0).mean(axis=0)
        residuals = y - fitted
        self.residual_scale = {
            target: float(max(np.std(residuals[:, index], ddof=0), 1e-6))
            for index, target in enumerate(self.targets)
        }
        self.reference_stats = _reference_stats(train, self.targets)
        self.metadata = {
            "model": "bootstrap_pca_ridge_multitask",
            "n_models": self.n_models,
            "alpha": self.alpha,
            "max_components": self.max_components,
            "training_rows": len(train),
            "features": len(self.feature_columns),
            "targets": self.targets,
            "uncertainty": "bootstrap_standard_deviation_plus_training_residual_scale",
        }
        return self

    def predict(self, frame: pd.DataFrame) -> pd.DataFrame:
        if not self.models:
            raise RuntimeError("Model has not been fitted")
        x = frame[self.feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
        ensemble = np.stack([model.predict(x) for model in self.models], axis=0)
        mean = ensemble.mean(axis=0)
        spread = ensemble.std(axis=0)
        out = frame[
            [
                column
                for column in [
                    "spot_uid",
                    "spot_id",
                    "sample_id",
                    "dataset_id",
                    "split",
                    "spatial_dir",
                    "x",
                    "y",
                    "pixel_x",
                    "pixel_y",
                ]
                if column in frame.columns
            ]
        ].copy()
        for index, target in enumerate(self.targets):
            out[f"pred_{target}"] = mean[:, index]
            residual = self.residual_scale.get(target, 0.0)
            out[f"uncertainty_{target}"] = np.sqrt(spread[:, index] ** 2 + residual ** 2)
        uncertainty_columns = [f"uncertainty_{target}" for target in self.targets]
        out["mean_prediction_uncertainty"] = out[uncertainty_columns].mean(axis=1)
        threshold = float(out["mean_prediction_uncertainty"].quantile(0.80)) if len(out) else float("nan")
        out["abstain"] = out["mean_prediction_uncertainty"] >= threshold
        return derive_prediction_gates(out, self.reference_stats)

    def save(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, destination)
        return destination

    @classmethod
    def load(cls, path: str | Path) -> "EMTVistaEnsemble":
        model = joblib.load(path)
        if not isinstance(model, cls):
            raise TypeError(f"Unexpected model type in {path}")
        return model
