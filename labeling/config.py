from __future__ import annotations

from shared.paths import LABELING_OUTPUTS_DIR


RANDOM_SEED = 20260512
SAMPLE_SIZE = 100
HIGH_LIKE_SAMPLE_SIZE = 30

LABELED_SAMPLE_CSV = LABELING_OUTPUTS_DIR / "economic_label_sample_100.csv"
REVIEW_TEMPLATE_CSV = LABELING_OUTPUTS_DIR / "economic_label_review_template.csv"
FULL_LABELS_CSV = LABELING_OUTPUTS_DIR / "economic_labels_full.csv"
