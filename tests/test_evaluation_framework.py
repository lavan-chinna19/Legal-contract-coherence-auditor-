"""
tests/test_evaluation_framework.py — Unit Tests for Prompt 14 Evaluation Framework.
Tests bootstrap calculations, baseline estimators, and benchmark interfaces.
"""
import pytest
import numpy as np

from src.evaluation.bootstrap import bootstrap_ci, bootstrap_kendall_tau, wilson_score_interval
from src.evaluation.baselines import MajorityVoteBaseline, LogisticRegressionBaseline
from src.config import ClauseRecord


def test_bootstrap_ci_basic():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    mean_val, lower, upper = bootstrap_ci(data, n_boot=200, ci=0.95, seed=42)
    assert 2.5 <= mean_val <= 3.5
    assert lower < mean_val < upper


def test_bootstrap_kendall_tau():
    x = [1, 2, 3, 4, 5, 6, 7, 8]
    y = [1.1, 2.2, 3.1, 4.0, 5.2, 6.1, 7.3, 8.2]  # Strong positive correlation
    tau, pval, lower, upper = bootstrap_kendall_tau(x, y, n_boot=200, ci=0.95, seed=42)
    assert tau > 0.8
    assert pval < 0.05
    assert lower > 0.5


def test_wilson_score_interval():
    p, low, high = wilson_score_interval(k=5, n=100, ci=0.95)
    assert abs(p - 0.05) < 1e-4
    assert 0.01 < low < 0.05
    assert 0.05 < high < 0.12


def test_majority_vote_baseline():
    maj = MajorityVoteBaseline()
    X = np.zeros((10, 2))
    y = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1])
    maj.fit(X, y)
    preds = maj.predict(X)
    assert (preds == 0).all()


def test_logistic_regression_baseline():
    lr = LogisticRegressionBaseline()
    np.random.seed(42)
    u = np.random.randn(20, 16)
    v = u + np.random.randn(20, 16) * 0.1  # Correlated pairs
    labels = np.array([1] * 10 + [0] * 10)
    lr.fit_from_embeddings(u, v, labels)
    
    assert lr.is_fitted
    probs = lr.predict_coherence_proba(u[:5], v[:5])
    assert len(probs) == 5
    assert (probs >= 0.0).all() and (probs <= 1.0).all()
