# ML Experimentation & Observations

## Best Models
- Demand: RandomForest
- Price: RandomForest

## Clustering
- Chosen k: 3
- Best k by silhouette: 2

## Observations
- best_performing_model: RandomForest / RandomForest
- data_quality_issues: ['Handled missing and duplicate features during preprocessing.', 'Standardized time-based features and lagged values before training.']
- overfitting_patterns: ['Compared raw and PCA-based regression scores to spot instability.', 'Tracked train/test behavior for classification and clustering models.']
- deployment_speed: Artifacts are saved once and served through thin API endpoints.
- prefect_reliability: Local artifact logs provide a fallback when orchestration is unavailable.
