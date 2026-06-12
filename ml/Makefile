.PHONY: install features train rules pipeline clean

# ─── Setup ───────────────────────────────────────────────────
install:
	pip install -r requirements.txt

# ─── Pipeline (run in order) ─────────────────────────────────
features:
	jupyter nbconvert --to notebook --execute notebooks/02_feature_engineering.ipynb \
		--output notebooks/02_features_executed.ipynb \
		--ExecutePreprocessor.timeout=600

train:
	jupyter nbconvert --to notebook --execute notebooks/03_model_training.ipynb \
		--output notebooks/03_train_executed.ipynb \
		--ExecutePreprocessor.timeout=600

rules:
	jupyter nbconvert --to notebook --execute notebooks/04_rule_engine.ipynb \
		--output notebooks/04_rules_executed.ipynb \
		--ExecutePreprocessor.timeout=120

pipeline: features train rules
	@echo "✓ ML pipeline complete. Artifacts saved to models/artifacts/"

# ─── Clean ───────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f notebooks/*_executed.ipynb
