# Pre-Registered Structural Coherence Evaluation Protocol

## Pre-Registration Declarations
1. **Primary Metric**: Balanced Accuracy and F1 on Eligible Held-Out Cases.
2. **Negative Control Rejection**: Specificity on Hard-Negative Controls (N3, N4).
3. **Frozen Models Evaluated**:
   - B0: Frozen Channel B (`models/coherence_classifier.pt`, threshold=0.70)
   - B1: Production Dual-Channel Ensemble (threshold=0.50)
   - B2: Cosine Similarity Baseline (threshold=0.60)
   - C1: Contextual Boundary Contrast Detector (threshold=0.50)
   - C2: Contextual Sequence BiLSTM (threshold=0.50)
   - C3: Heading-Based Topological DAG (threshold=0.50)
4. **Execution Rules**: Single sealed held-out evaluation pass. Zero parameter tuning or threshold adjustments on test data.
