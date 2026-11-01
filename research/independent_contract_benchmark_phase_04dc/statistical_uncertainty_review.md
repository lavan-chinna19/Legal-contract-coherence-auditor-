# Statistical Uncertainty and Wilson Interval Review

## Uncertainty Scope
All metric proportions are accompanied by exact two-sided Wilson 95% confidence intervals.
For paired model comparisons, cluster bootstrap confidence intervals resampling at the document-family level are used to avoid inflating sample sizes.

## Key Observations
- Small sample sizes in the test partition for positive cases yield wide Wilson intervals (e.g. 2/2 has Wilson interval [0.3424, 1.0]).
- Conversely, negative controls (N=16) provide tight specificity bounds, conclusively demonstrating C3's false positive rate (11/16, specificity 31.25%, CI [0.1416, 0.5560]).
