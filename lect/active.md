.

# active

History of optimization — the full arc: tiny models (SA, low RAM) → genetic algorithms (more RAM) → local search (more CPU) → surrogates (more data) → "why use the optimizer at all?" That narrative is pure transcript.
Surrogates — the core paradox — the insight that it's "weird" to run a sophisticated optimizer against a 50-example surrogate, and therefore just explore the surrogate directly. Extended discussion. Not in notes.
Active learning mechanics — uncertainty vs. certainty sampling, the transition slope, the honest confession that 18 months of grad work on it was no better than greedy search. Notes just say "next week."
SMAC / Bayesian optimization — Gaussian processes, random forest ensembles as surrogates, TPI, uncertainty quantification via tree disagreement. Absent from notes.
Multi-fidelity / HyperBand — successive halving, epochs, "loosey-goosey fast then tighten up." Not in notes.
NSGA-II, crowding distance, hyper-volume — the fat Pareto frontier problem, non-dominated sorting as a patch for broken domination. Not in notes.
Near-enough / bandit / reward-free RL taxonomy — ~dozen samples vs ~20k vs ~1M. Very clean taxonomy, entirely transcript-only.
"Fix bugs early" myth — tracing 12 papers back to last century, 6-6 split. Not in notes.
