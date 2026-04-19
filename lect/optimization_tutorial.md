# The History of Optimization

---

## Table of Contents

| # | Topic | Era / Algorithm |
|---|---|---|
| 1 | [What Is Optimization?](#1-what-is-optimization) | Foundations |
| 2 | [Terminology Quick Reference](#2-terminology-quick-reference) | Glossary |
| 3 | [Era 1 — Trajectory Methods](#3-era-1-trajectory-methods-minimal-memory) | SA, Hill Climbing |
| 4 | [Era 2 — Discrete Populations](#4-era-2-discrete-populations-genetic-algorithms) | GA, GP |
| 5 | [Era 3 — Continuous Vectors](#5-era-3-continuous-vectors-differential-evolution) | ES, DE, CMA-ES |
| 6 | [Era 4 — Multi-Objective](#6-era-4-multi-objective-the-pareto-revolution) | NSGA-I/II/III, MOEA/D |
| 7 | [Era 5 — Training Wall](#7-era-5-training-wall-multi-fidelity-triage) | Hyperband, ASHA, DEHB |
| 8 | [Era 6 — Surrogates](#8-era-6-heavy-simulation-surrogate-models) | BO, SMAC |
| 9 | [Era 7 — Extreme Scarcity](#9-era-7-extreme-scarcity-binary-contrastive-surrogates) | EZR/LITE |
| 10 | [SE Applications Map](#10-software-engineering-applications) | SBSE Literature |
| 11 | [Live Code: All Algorithms on POM3](#11-live-code-all-algorithms-on-pom3) | pymoo + MOOT |
| — | 11.1 Unified Setup & Data Loading | POM3 from MOOT |
| — | 11.2 GA (single-obj baseline) | pymoo GA |
| — | 11.3 DE (single-obj) | pymoo DE |
| — | 11.4 CMA-ES (single-obj) | pymoo CMA-ES |
| — | 11.5 NSGA-II | pymoo NSGA-II |
| — | 11.6 NSGA-III | pymoo NSGA-III |
| — | 11.7 SPEA2 | pymoo SPEA2 |
| — | 11.8 MOEA/D | pymoo MOEA/D |
| — | 11.9 SMS-EMOA | pymoo SMS-EMOA |
| — | **11.10 Full Comparison: HV, IGD, D2H, Spread** | All metrics, all algorithms |
| 12 | [Evaluation Metrics](#12-evaluation-metrics) | HV, IGD, GD, **D2H**, Spread, ε |
| 13 | [Comparisons and Pitfalls](#13-comparisons-and-pitfalls) | Comparing all algorithms |
| 14 | [Summary & References](#14-summary--references) | |

---

## 1. What Is Optimization?

### 1.1 The Formal Problem

Every optimization problem has the same skeleton:

```
minimize   F(x) = [f_1(x), ..., f_k(x)]     ← objectives (k=1: single, k≥2: multi)
subject to g_i(x) ≤ 0,  i = 1..m            ← inequality constraints
           h_j(x) = 0,  j = 1..p            ← equality constraints
           x ∈ X                             ← feasible search space
```

- **x** = the *decision variables* — what you control (compiler flags, team sizes, etc.)
- **F(x)** = the *objective(s)* — what you want to minimize or maximize
- **X** = the *search space* — may be continuous, discrete, or mixed

### 1.2 Why Classical Methods Fail in Software Engineering

| Classical Assumption | Why It Breaks in SE |
|---|---|
| f(x) is differentiable | Test outcomes, build times — no analytic gradient exists |
| f(x) is unimodal | Software config spaces are rugged, full of local optima |
| Evaluations are cheap | Compiling + running a test suite costs seconds to minutes |
| Single objective | Real projects trade off speed, correctness, cost, defects |
| Continuous variables | Many SE decisions are discrete (on/off flags, categorical choices) |

**Evolutionary and search-based algorithms** require only one thing: you can *evaluate* a candidate solution. No gradient, no smoothness, no convexity required.

### 1.3 The Fitness Landscape Intuition

Imagine the search space as geographic terrain where elevation = f(x):

- **Gradient descent**: Follows the slope downhill. Perfect on smooth bowls. Trapped in valleys on rugged terrain.
- **Random search**: Samples everywhere. Exponentially inefficient as dimensions grow.
- **Evolutionary search**: Maintains a *population* of solutions. Selection pressure focuses the search on promising regions. Mutation and crossover explore new territory. It *learns the landscape* as it searches.

The history of optimization is the story of how algorithms got smarter about navigating this terrain under increasingly tight hardware constraints.

---

## 2. Terminology Quick Reference

| Term | Plain-English Meaning |
|---|---|
| **Objective** | A scorecard: the mathematical function you want to improve |
| **Heuristic** | A rule-of-thumb strategy; fast but not guaranteed optimal |
| **Pareto Front** | The boundary of best trade-offs in multi-objective space |
| **Surrogate** | A cheap mathematical stand-in for an expensive real function |
| **Fidelity** | How much budget (e.g., training epochs) you give one evaluation |
| **Epistemic Uncertainty** | "Map ignorance" — uncertainty from lack of sampled data |
| **Acquisition Function** | The logic that decides *where* to sample next (mean vs variance) |
| **Decomposition** | Slicing a multi-objective problem into scalar sub-problems |
| **Centroid** | Geometric center of a cluster (e.g., center of the "best" solutions) |
| **Vectorization** | Processing whole arrays of floats natively at the CPU level |
| **Dominance** | Solution a *dominates* b if a is no worse on all objectives and better on at least one |
| **Non-dominated** | A solution no other solution dominates; Pareto-optimal candidates |
| **SBSE** | Search-Based Software Engineering — applying search to SE tasks |

---

## 3. Era 1: Trajectory Methods (Minimal Memory)

**Hardware force:** Kilobytes of RAM.
When memory was scarce, algorithms could only remember *where they currently stood*, not where the whole population was. These are *single-point* methods that trace a trajectory through the search space.

---

### 3.1 Hill Climbing

The simplest possible optimizer: always move to a better neighbor.

**Problem it solved:** Random search with no learning. Hill climbing reuses information from the current position to guide the next step.

**Problem it introduced:** Gets permanently stuck in the first local optimum it finds. Restarts help but are ad-hoc.

```
s = random_solution()
max_iterations = 1000
no_improve = 0
max_no_improve = 100

while no_improve < max_no_improve and iteration < max_iterations:
    neighbor = small_random_change(s)
    if f(neighbor) < f(s):
        s = neighbor
        no_improve = 0
    else:
        no_improve += 1
    iteration += 1
```

---

### 3.2 Simulated Annealing (SA)

**Problem it solved:** Hill climbing's fatal flaw — permanent entrapment in local optima.

**Key insight:** Occasionally accept *worse* moves with a probability that depends on how bad the move is and a "temperature" T. At high T (early), almost any move is accepted (exploration). As T decreases (cooling), only good moves are accepted (exploitation).

**The physics analogy:** Molten metal anneals into a low-energy crystal structure when cooled slowly. Cool too fast → brittle, suboptimal structure. Cool slowly → optimal crystal.

```
s = random_solution()
T = T_initial
while T > T_min:
    candidate = neighbor(s)
    Δ = f(candidate) - f(s)
    if Δ < 0 or random() < exp(-Δ / T):   # always accept improvements,
        s = candidate                       # sometimes accept worse moves
    T = T * cooling_rate                   # geometric cooling schedule
return s
```

**Key parameters:**
- `T_initial`: High enough that most moves are accepted at the start
- `cooling_rate`: Typically 0.95–0.999; lower = faster cooling = less exploration
- `T_min`: Stopping criterion

**SE Application:** SA was used in early SBSE work for test case prioritization and the Next Release Problem (Harman & Jones, 2001). Its single-point nature made it feasible when populations were too memory-expensive.

**Problem it introduced:** Sensitive to cooling schedule. No population = no parallel exploration. Cannot directly handle multi-objective problems.

---

## 4. Era 2: Discrete Populations (Genetic Algorithms)

**Hardware force:** Megabytes of RAM.
We could now afford to store a *population* — a "cloud" of candidate solutions. This enabled parallel exploration and information sharing via crossover.

---

### 4.1 The Canonical Genetic Algorithm (GA)

Introduced by Holland (1975), popularized by Goldberg (1989).

**Problem it solved:** Single-point methods' lack of diversity and population-level intelligence. A population can explore multiple basins simultaneously.

**Core operators:**

| Operator | Role | Analogy |
|---|---|---|
| Selection | Choose fitter individuals to reproduce | Survival of the fittest |
| Crossover | Combine two parents → offspring | Sexual reproduction |
| Mutation | Small random change | Genetic mutation |
| Elitism | Always carry the best forward | Protected species |

**Representation:**
```
Binary:  [1, 0, 1, 1, 0, 0, 1, 0]      ← for discrete/combinatorial problems
Integer: [3, 1, 4, 1, 5, 9, 2, 6]      ← for scheduling, ordering problems
Real:    [0.73, -1.24, 3.14, 0.05]     ← for continuous parameter optimization
Tree:    (+, (*, x1, 5.0), x2)         ← for programs (Genetic Programming / GenProg)
```

**Full GA pseudocode:**

```python
population = [random_individual() for _ in range(N)]
evaluate(population)

for generation in range(max_gen):
    new_pop = [best(population)]              # elitism: keep the best
    while len(new_pop) < N:
        p1 = tournament_select(population)   # select parents
        p2 = tournament_select(population)
        c1, c2 = crossover(p1, p2)           # recombine
        c1, c2 = mutate(c1), mutate(c2)      # perturb
        new_pop += [c1, c2]
    population = new_pop
    evaluate(population)

return best(population)
```

**Tournament selection** (most common): Pick k individuals at random, return the best. Larger k = stronger selection pressure.

**Single-point crossover:**
```
Parent A:  [1 0 1 | 1 0 0 1 0]
Parent B:  [0 1 0 | 0 1 1 0 1]
                ↑ cut point
Child 1:   [1 0 1   0 1 1 0 1]    ← A's head + B's tail
Child 2:   [0 1 0   1 0 0 1 0]    ← B's head + A's tail
```

**Problems with simple GA (→ motivate next eras):**
1. Binary encoding of real numbers creates **Hamming cliffs** — nearby numbers have very different bit strings
2. No principled mutation **step-size control** — too large = random walk; too small = no progress
3. Population converges prematurely — all individuals become similar
4. Single objective only — cannot natively handle trade-offs
5. Crossover designed for bits, not floats — motivated Differential Evolution

---

### 4.2 Genetic Programming (GP)

GA where the individual is a **syntax tree** representing a program.

**Problem it solved:** Automating program synthesis and repair — letting evolution write code rather than tuning parameters.

```
        IF
       /   \
    x > 5   THEN        →   A mini-program evolved to satisfy a test suite
    /     \
 assign   return
  x←x+1     x
```

**SE Application — GenProg** (Le Goues et al., 2012):
GP is the engine of GenProg, the landmark automated program repair tool.
- Each individual is a *patch*: a list of AST-level edits (insert, delete, swap)
- Fitness = weighted fraction of passing tests: `w_neg * (failing tests fixed) + w_pos * (passing tests kept)`
- Operators: insert/delete/replace AST nodes drawn from existing code in the same file
- Key paper: Le Goues, C. et al. "GenProg: A Generic Method for Automatic Software Repair." IEEE TSE 38(1), 2012.

---

## 5. Era 3: Continuous Vectors (Differential Evolution)

**Hardware force:** Dedicated floating-point units (FPUs).
CPUs gained hardware for fast vector math. Bit-flipping GAs were outclassed by native float operations.

---

### 5.1 Evolution Strategies (ES) — Self-Adaptive Step Sizes

**Problem it solved:** GA's lack of step-size control for real-valued optimization.

**Key insight:** Include the mutation step size σ *inside the individual itself* and let evolution tune it.

```
Individual: (x_1,...,x_n, σ_1,...,σ_n)
              ↑ solution       ↑ these are also evolved

Mutation:
  σ'_i = σ_i * exp(τ * N(0,1))      ← update step size first
  x'_i = x_i + σ'_i * N(0,1)       ← then mutate the solution
```

If a large σ produces improvements, individuals with large σ survive and pass it on. The algorithm learns the right step size automatically.

**CMA-ES** (Hansen, 2001) extends this to adapt the full covariance matrix of the search distribution — the gold standard for smooth, continuous, single-objective problems up to ~200 variables.

---

### 5.2 Differential Evolution (DE)

**Problem it solved:** Fixed, manually-tuned mutation step sizes. Awkward binary encoding of real numbers.

**Key insight:** Use the *population itself* as a self-scaling source of mutation directions. If vectors A and B are both in the population, then `F*(A-B)` is a mutation step that automatically scales to the current population's spread.

```
Mutation (DE/rand/1):
  For each target x_i, pick 3 distinct random individuals a, b, c:
  mutant v = a + F * (b - c)          ← vector difference = adaptive step

Crossover (binomial):
  j_rand = random index (ensures at least one gene from mutant)
  trial_j = v_j    if rand() < CR or j == j_rand
           = x_ij  otherwise

Selection (greedy):
  x_i(next) = trial  if f(trial) ≤ f(x_i)
             = x_i   otherwise
```

**Why DE works well:**
- When population has converged, `b - c` is small → small, precise steps (exploitation)
- Early in search, `b - c` is large → bold exploratory steps (exploration)
- Self-scaling: no manual σ to tune
- Two parameters only: F (scale, ~0.5–0.8) and CR (crossover rate, ~0.7–0.9)

**Common DE variants (DE/x/y/z notation):**

| Variant | Mutation | Character |
|---|---|---|
| DE/rand/1/bin | `a + F*(b-c)` | Standard, good exploration |
| DE/best/1/bin | `x_best + F*(b-c)` | Faster convergence, less diversity |
| DE/current-to-best/1/bin | `x_i + F*(x_best-x_i) + F*(a-b)` | Balanced, popular in practice |

**SE Application:** DE is used in SBSE for continuous configuration tuning (Nair et al., 2018 FLASH; various hyperparameter optimization studies). It outperforms GA on continuous software configuration spaces because most config spaces have real-valued knobs (cache sizes, timeout values, thread counts).

**Problem it introduced:** Still single-objective. As SE problems grew to involve multiple conflicting goals simultaneously, a new paradigm was needed.

---

## 6. Era 4: Multi-Objective (The Pareto Revolution)

**Hardware force:** CPU + RAM sufficient for population-level multi-objective bookkeeping.

### 6.1 Why Multi-Objective Matters

Real SE decisions almost always involve trade-offs:

| SE Problem | Objective 1 | Objective 2 | Objective 3 |
|---|---|---|---|
| Test selection | Maximize fault detection | Minimize runtime | — |
| Automated repair | Maximize tests passing | Minimize patch size | — |
| Next Release Problem | Maximize feature value | Minimize dev cost | — |
| Process modeling (POM3) | Minimize idle rate | Minimize cost | Maximize completion |
| Software configuration | Maximize throughput | Minimize latency | Minimize memory |
| Refactoring | Maximize cohesion | Minimize coupling | Minimize effort |

**Scalarization (the naive approach):**
```
f_combined = w1*f1 + w2*f2     ← requires choosing weights in advance
```

Problems: If we do not know the right weights, it cannot discover non-convex parts of the Pareto front. You get one point per run. You need to repeat for every trade-off you want to explore.

**Alternative approach:** Find the entire *Pareto front* in one run, then let the decision-maker choose.

---

### 6.2 Pareto Dominance

Solution **a dominates** solution **b** (written a ≺ b) if:
1. a is no worse than b on *all* objectives
2. a is strictly better than b on *at least one* objective

**The Pareto front** = the set of solutions not dominated by any other. These represent the best achievable trade-offs.

```
Example (2 objectives, both minimized):

  Solution | f1 | f2 | Status
  ---------|----|----|-------------------
    A      |  1 |  4 | Pareto-optimal ✓
    B      |  2 |  3 | Pareto-optimal ✓
    C      |  3 |  2 | Pareto-optimal ✓
    D      |  4 |  1 | Pareto-optimal ✓
    E      |  3 |  4 | Dominated by B ✗
    F      |  2 |  5 | Dominated by A ✗

  f2 ↑
   5 |        F
   4 |  A          E
   3 |     B
   2 |        C
   1 |           D
     +------------→ f1
       1  2  3  4
  
  Pareto front: A–B–C–D (the "knee curve")
```

A good MOEA must do two things simultaneously:
1. **Converge** its solutions toward the true Pareto front
2. **Spread** solutions uniformly along the front

---

### 6.3 NSGA-I — The First Multi-Objective GA

Srinivas & Deb (1994). Introduced *non-dominated sorting* as a fitness assignment.

**Problem it solved:** How to rank solutions when you have multiple objectives — sort by Pareto dominance layer.

**Algorithm:**
```
Assign fitness by Pareto rank:
  F1 = non-dominated solutions in population     (rank 1, highest fitness)
  F2 = non-dominated in (population - F1)        (rank 2)
  F3 = ... and so on

Apply fitness sharing within each rank to reward spread:
  f_shared(i) = f_dummy(i) / Σ sh(d(i,j))
  where sh(d) = 1 - (d/σ_share)^α  if d < σ_share, else 0
```

**Problems with NSGA-I (→ directly motivated NSGA-II):**

| Problem | Description |
|---|---|
| **O(MN³) complexity** | Sorting was computed naively: slow for large N |
| **Requires σ_share** | Niche radius must be set manually; fragile, problem-specific |
| **No elitism** | Good solutions could be lost by genetic drift across generations |

---

### 6.4 NSGA-II — The Workhorse of MOEA

Deb, Pratap, Agarwal & Meyarivan (2002). One of the most cited papers in EC (~25,000 citations).

**Three innovations that fixed all of NSGA-I's problems:**

#### Fix 1: Fast Non-Dominated Sort — O(MN²)

```
For each individual p:
    S_p = {}    (set p dominates)
    n_p = 0     (count of individuals dominating p)
    for each q ≠ p:
        if p dominates q: S_p.add(q)
        elif q dominates p: n_p += 1
    if n_p == 0: p is in Front 1

For each p in Front 1:
    for q in S_p:
        n_q -= 1
        if n_q == 0: q joins Front 2
                                         → O(MN²) total
```

#### Fix 2: Crowding Distance — No σ_share Needed

For each solution on a front, measure the average side-length of the cuboid of nearest neighbors in objective space:

```
For front F, objective m:
  Sort F by f_m
  distance[first] = distance[last] = ∞   (always keep extremes)
  For i in 2...|F|-1:
    distance[i] += (f_m[i+1] - f_m[i-1]) / (f_m_max - f_m_min)
```

High crowding distance = isolated solution = valuable for diversity → prefer it in selection.
This requires **zero user parameters**.

#### Fix 3: Elitist (N+N) Selection

```
NSGA-II main loop:

P_t = initial population of size N
Q_t = create_offspring(P_t)              ← crossover + mutation

R_t = P_t ∪ Q_t                          ← combined pool of 2N solutions
Sort R_t into fronts F_1, F_2, F_3, ...

P_{t+1} = []
for each front F_i:
    if |P_{t+1}| + |F_i| ≤ N:
        P_{t+1} += F_i                   ← take entire front
    else:
        sort F_i by crowding distance ↓  ← fill remaining spots from
        P_{t+1} += F_i[:N - |P_{t+1}|]  ← least-crowded in overflow front
        break

→ Best N solutions from 2N always survive. No good solution is ever discarded.
```

**NSGA-II Summary:**

| Property | Value |
|---|---|
| Complexity | O(MN²) per generation |
| Diversity mechanism | Crowding distance (parameter-free) |
| Elitism | Yes — (N+N) pool |
| Operators | SBX crossover + polynomial mutation |
| Best for | 2–3 objectives, moderate N, any encoding |
| Weakness | Crowding distance degrades when M > 3 |

---

### 6.5 NSGA-III — Scaling to Many Objectives

Deb & Jain (2014). Extended NSGA-II for **many-objective** problems (M ≥ 4).

**Problem it solved:** In 10 dimensions, crowding distance loses discriminating power — everything looks equidistant. NSGA-II's diversity mechanism essentially breaks above 3 objectives.

**Key change:** Replace crowding distance with **structured reference points** on the normalized objective hyperplane.

```
Reference points: uniformly distributed directions on the unit simplex
  For M=3, 6 divisions: 28 reference points
  For M=5, 6 divisions: 210 reference points

Population niche preservation:
  1. Normalize objective space (translate to ideal point, project to hyperplane)
  2. Associate each solution with its nearest reference line
  3. When filling overflow front:
     - Find reference point r with fewest associated solutions (ρ_r smallest)
     - If ρ_r = 0: pick solution closest to r's line (best convergence)
     - If ρ_r > 0: pick randomly from solutions near r (maintain diversity)
```

This ensures approximately uniform coverage of all reference directions regardless of M.

---

### 6.6 MOEA/D — Decomposition-Based

Zhang & Li (2007). An entirely different philosophy: **decompose** the multi-objective problem into N scalar sub-problems, one per weight vector.

**Problem it solved:** MOEAs that operate in objective space scale poorly to high dimensions. Decomposition works in a low-dimensional *weight space* instead.

```
Define N weight vectors: λ_1, ..., λ_N (uniform distribution on simplex)
For each λ_i, define a neighborhood T_i = k nearest weight vectors

Main loop:
  For each sub-problem i:
    Select 2 parents from neighborhood T_i
    Generate offspring by crossover + mutation
    Update neighbors: if offspring improves f(λ_j) for any j in T_i, replace
    Update reference point z* = best seen per objective
```

Scalarization function (Tchebycheff):
```
f_λ(x) = max_i { λ_i * |f_i(x) - z*_i| }
```

**Why MOEA/D is competitive:** Decomposition transforms the multi-objective problem into cooperative single-objective sub-problems. Sub-problems share information with neighbors, yielding fast convergence. Scales to M=5–15 objectives better than sorting-based methods.

---

### 6.10 Summary: All Multi-Objective Algorithms

| Algorithm | Year | Selection | Diversity | Strength | Notes |
|---|---|---|---|---|---|
| NSGA-I | 1994 | Pareto rank | Fitness sharing (σ required) | Historic | Replaced by NSGA-II |
| NSGA-II | 2002 | Pareto rank | Crowding distance | 2–3 obj | The workhorse of SBSE |
| MOEA/D | 2007 | Scalarized neighbors | Weight vector decomp. | 3–10 obj | Best for structured fronts |
| NSGA-III | 2014 | Pareto rank | Reference points | 4+ obj | Many-objective standard |

---

### 6.11 NSGA-I → NSGA-II → NSGA-III: The Problem/Solution Chain

| Version | Year | Problem Fixed | Key Mechanism |
|---|---|---|---|
| NSGA-I | 1994 | No multi-obj support | Non-dominated sorting |
| NSGA-II | 2002 | O(N³), no elitism, σ required | Fast sort + crowding dist + (N+N) |
| NSGA-III | 2014 | Crowding breaks at M>3 | Structured reference points |
| MOEA/D | 2007 | Sorting scales poorly | Weight-vector decomposition |

---

## 7. Era 5: Training Wall (Multi-Fidelity Triage)

**Hardware force:** GPU training costs. A single deep learning evaluation can take hours.

### 7.1 The Problem: Expensive Evaluations

Standard EAs evaluate every individual completely. When one evaluation = training a neural network for 100 epochs, a population of 100 × 500 generations = **5,000,000 full training runs**. Completely infeasible.

**Multi-fidelity insight:** A bad configuration performs poorly even after only 5 epochs. We can *kill bad candidates early* using cheap proxy evaluations.

---

### 7.2 Successive Halving

The core multi-fidelity primitive:

```
configs = sample(n)           ← start with many configs
budget  = b_min               ← minimal compute budget

while len(configs) > 1:
    run each config for `budget` epochs
    configs = top_half(configs)     ← eliminate bottom 50%
    budget  = budget * 2            ← double budget for survivors

return configs[0]   ← winner trained for full budget
```

**Problem with Successive Halving alone:** If you start with budget b_min and double k times, total work = O(n log n). But what if a good config looks bad at low fidelity? It gets killed unfairly.

---

### 7.3 Hyperband

Li et al. (2017). Run multiple Successive Halving *brackets* with different starting budgets — hedging against the risk that any given early-stopping ratio kills a late bloomer.

```
Hyperband:
  INPUTS:
    b_max = max epochs you can give one config   (e.g. 81)
    B     = total epochs you can afford          (e.g. 405)
    η     = keep-rate: top 1/η survive each round (e.g. 3 → keep top third)

  for each bracket s = s_max, s_max-1, ..., 0:
    n_s = ceil(B / b_max * η^s / (s+1))   ← configs to start with
    r_s = b_max * η^{-s}                   ← initial budget per config
    
    run Successive_Halving(n_s, r_s)       ← each bracket is one SHA run

return best across all brackets
```

**Problem with Hyperband:** Initial configurations are drawn **uniformly at random**. There is no learning from which regions of the config space were good. Each bracket starts fresh.

---

### 7.3b ASHA — Asynchronous Successive Halving Algorithm

Li, Jamieson et al. (2018). **ASHA** fixes a critical practical limitation of Hyperband: *synchronous* waiting.

**Problem with Hyperband in practice:** Standard SHA/Hyperband is *synchronous* — it waits for all N workers to finish their current budget before promoting survivors. With heterogeneous hardware (some configs train faster than others), slow workers create a bottleneck. Most workers sit idle waiting.

**ASHA's key idea:** Make promotion *asynchronous*. As soon as any worker finishes and its metric is in the top 1/η of all results seen so far at that rung, promote it immediately. Never wait.

```
ASHA architecture:
  rungs = {b_1: {}, b_2: {}, ..., b_max: {}}  ← completed results per fidelity

  On each worker becoming free:
    if config in rung r and rank ≤ 1/η of all results in rung r:
        promote to rung r+1   ← don't wait for all configs to finish
    else:
        sample new random config at rung r=1

  → Workers are NEVER idle. Parallelism is near-perfect.
```

**ASHA vs Hyperband:**

| Property | Hyperband | ASHA |
|---|---|---|
| Scheduling | Synchronous brackets | Asynchronous rungs |
| Parallelism | Limited (workers wait) | Near-perfect (no waiting) |
| Promotion rule | After full bracket | As soon as eligible |
| Use case | Single machine | Large GPU clusters |
| Typical speedup | — | 3–8× over synchronous |

**SE Application:** ASHA is the standard HPO backend for large-scale ML experiments on SE datasets. Ray Tune and SageMaker use ASHA by default for distributed HPO.

**Note on pymoo:** ASHA and Hyperband/DEHB require multi-fidelity evaluation (training for k epochs at varying budgets), which is an external training loop — not an optimization problem pymoo can wrap. These are implemented in Ray Tune, Optuna (with pruners), and the DEHB package. We skip pymoo code for these and show DEHB separately.

---

### 7.4 DEHB — Differential Evolution + Hyperband

Awad, Mallik & Hutter (2021). **DEHB** = replace Hyperband's random sampling with DE mutations that *learn from previous evaluations*.

**Problem it solved:** Hyperband's random sampling ignores information from past brackets. DE provides a search model that improves proposals over time.

```
DEHB architecture:
  Maintain DE population P_b for each fidelity level b

Main loop (Hyperband scheduling):
  For each bracket and fidelity b:

    if first iteration and b == b_min:
        sample random configs
    else:
        For each target x_i in P_b:
            a, b_vec, c = sample parents (population or parent pool)
            mutant = a + F*(b_vec - c)
            trial = binomial_crossover(x_i, mutant, CR)

    Evaluate trial at fidelity b

    Greedy selection:
        if f(trial) ≤ f(x_i):
            replace x_i in P_b

    Promote best configs → parent pool for next fidelity

Update global best configuration (incumbent)

← Information flows upward through fidelity levels
← DE mutations encode what worked at lower fidelity
```

**Why DEHB wins:**

| Property | Hyperband | DEHB |
|---|---|---|
| Fidelity scheduling | Hyperband | Hyperband |
| Config generation | Random | DE mutation (learns) |
| Parallelism | Limited | Excellent |
| Config inheritance | No | Yes (lower→higher fidelity) |
| Use case | No prior | High-dim, parallel HPO |

**SE Application:** DEHB is the method of choice for hyperparameter optimization of ML models on SE tasks (e.g., defect prediction models, code smell detectors), where many candidate configurations must be screened cheaply.

---

## 8. Era 6: Heavy Simulation (Surrogate Models)

**Hardware force:** Extreme evaluation costs — physical simulations, hardware-in-the-loop, large-scale builds.

### 8.1 The Problem

When each evaluation costs hours (or runs on expensive hardware), even multi-fidelity triage isn't enough. We need to *model the fitness landscape* and optimize against the model.

### 8.2 Bayesian Optimization (EGO)

Build a **Gaussian Process (GP) surrogate** — a probabilistic model that predicts both the mean and uncertainty of f(x) everywhere in X.

```
Initialize: evaluate f at a few random points → dataset D = {(x_i, y_i)}

Repeat until budget exhausted:
  1. Fit GP to D: gives μ(x), σ(x) at every untried x
  2. Compute acquisition function a(x) using μ and σ
  3. Next query: x_next = argmax a(x)     ← maximize acquisition
  4. Evaluate: y_next = f(x_next)  ← the expensive real evaluation
  5. Update D = D ∪ {(x_next, y_next)}
  
return x with best y in D
```

**Acquisition functions** control the exploration-exploitation trade-off:

| Acquisition | Formula | Behavior |
|---|---|---|
| **UCB** | μ(x) + κ·σ(x) | Simple, tunable trade-off |
| **EI (Expected Improvement)** | E[max(0, f(x) - f*)] | Expected reward over current best |
| **PI (Probability of Improvement)** | P(f(x) > f*) | Risk-averse; exploits more |

**SE Application — FLASH** (Nair et al., 2018): Uses a sequential model-based method (similar to BO) for software configuration optimization. Samples configurations sequentially, fits a surrogate, queries where the surrogate predicts improvement. Demonstrates that much fewer evaluations are needed find near-optimal configurations for systems with 10²⁴ possible settings.

---

### 8.3 SMAC — Bayesian Optimization with Random Forests

**Problem with GP:** GP assumes a smooth, continuous landscape. Software configurations often involve categorical variables (algorithms, encodings), conditional parameters (if kernel=rbf, then gamma matters), and discontinuous jumps.

**SMAC** (Hutter et al., 2011) replaces the GP with an **ensemble of Random Forests**:
- Handles categorical + continuous + conditional variables natively
- Variance estimate: disagreement among trees = epistemic uncertainty
- Better suited to software/ML configuration spaces than GP

```
model.fit(X_sampled, y_sampled)           ← fit Random Forest surrogate
mu, sigma = model.predict(X_candidates)  ← mean + uncertainty from forest
next_x = argmax(EI(mu, sigma, f_best))   ← expected improvement
```

---

## 9. Era 7: Extreme Scarcity (Binary Contrastive Surrogates)

**Hardware force:** Severe label parsimony. You cannot afford even 20–30 evaluations. Labels are expensive expert annotations, physical experiments, or rare real-world events.

### 9.1 LITE — "Likely"

**Problem it solved:** GP and Random Forests need enough data to fit a regression model. With fewer than ~15 labeled points, regression is unreliable. We need a smarter representation.

**Key insight:** Instead of fitting a regression surrogate of the whole space, split the few labeled examples into "Best" and "Rest" clusters and build a *binary contrastive classifier*.

```
Initialization:
  Label sqrt(N) candidates from unlabeled pool
  best, rest = split(labeled, top = sqrt(|labeled|))

Dual Surrogate:
  model_b = fit(best)     ← distribution of good solutions
  model_r = fit(rest)     ← distribution of bad solutions

Acquisition (Likely & Nearer):
  For each unlabeled candidate x:
    L = P(x | model_b)                    ← "Likely": how much like Best?
    score(x) = L^2 / (L + P(x | model_r)) ← penalize if also like Rest (you can also use acquisions like best/rest)

next_x = argmax(score)   ← query this point, update best/rest, repeat
```

**Why it works at extreme scarcity:**
- Does not need to fit a full regression surface
- Classification (is this more like Best or Rest?) works with very few examples
- The L² numerator aggressively rewards similarity to Best
- The denominator penalizes candidates that also look like Rest

## 9.2 EZR — "Nearer"

**Problem it solved:** Simplifies the process further by removing the need for probabilistic models like Naive Bayes.

**Key insight:** Uses the medians (centroids) of the clusters directly. An acquisition is "nearer" if its Euclidean distance to the Best centroid is smaller than to the Rest centroid.


**SE Application:** EZR/LITE achieves near-optimal results on MOOT datasets (including POM3, SS-*, XOMO) with only 20–30 labeled samples — datasets where alternatives need 100+ evaluations. Menzies et al. (2025) show rank-0 optimization in 16–22 evaluations across 118 datasets.

---

## 10. Software Engineering Applications

### 10.1 SBSE Literature Map by Algorithm

| SE Problem | Algorithm Family | Key References |
|---|---|---|
| **Automated Program Repair** | GP | GenProg (Le Goues 2012), PAR (Kim 2013), Prophet (Long 2016) |
| **Test Suite Generation** | NSGA-II | EvoSuite (Fraser & Arcuri 2011) |
| **Test Case Prioritization** | NSGA-II, SA | Yoo & Harman (2007, 2012) |
| **Next Release Problem** | GA, NSGA-II | Bagnall (2001), Greer & Ruhe (2004) |
| **Software Refactoring** | NSGA-II | O'Keeffe & Cinnéide (2008) |
| **Process Modeling (POM3)** | NSGA-II, DE, LITE | Menzies et al. (2007), MOOT (2025) |
| **Software Configuration** | DE, BO, SMAC | FLASH (Nair 2018), irace |
| **Hyperparameter Optimization** | DEHB, SMAC, BOHB | Awad (2021), Hutter (2011) |
| **Fault Localization** | GA, SA | Abreu et al. (2009) |
| **Model-Based Testing** | GA | Various |
| **Feature Model Optimization** | NSGA-II | Henard et al. (2015) |
| **Energy Optimization** | NSGA-II | Sahin et al. (2016) |

---

## 11. Live Code: All Algorithms on POM3

> **Goal:** Run every major optimizer on the **same SE dataset** so you can directly compare behavior, convergence, and Pareto-front quality side by side.

### 11.1 About POM3

**POM3** is the canonical software process model dataset from the MOOT repository. It models *agile development* scenarios where project requirements form a dependency tree that partially emerges at runtime (Boehm & Turner, 2004).

**Decision variables (9):** Team composition, requirements churn, criticality, pool size, etc.
**Objectives (3):** Minimize cost, minimize idle time, maximize completion rate.

This is a real multi-objective SE optimization problem used in dozens of papers in the SBSE literature.

**Data convention (MOOT format):**
- Columns starting with uppercase → numeric features (decision variables)
- Columns starting with lowercase → categorical features
- Columns ending with `-` → minimize this objective
- Columns ending with `+` → maximize this objective

```
Example header:
  Culture, Criticality, CriticalityModifier, InitialKnownPercent, ...
  cost-, idle-, completion+
```

### 11.2 Unified Setup (run once — all snippets below share it)

```python
# pip install pymoo pandas numpy matplotlib
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.indicators.hv import HV

# ── Load POM3a ────────────────────────────────────────────────────────────────
URL = "https://raw.githubusercontent.com/timm/moot/refs/heads/master/optimize/process/pom3d.csv"
df  = pd.read_csv(URL)

# ── Parse MOOT conventions ────────────────────────────────────────────────────
#  uppercase col start → numeric variable  |  ends '-' → minimize  |  ends '+' → maximize
obj_cols  = [c for c in df.columns if c.endswith('+') or c.endswith('-')]
feat_cols = [c for c in df.columns if c not in obj_cols and c[0].isupper()]
X_data    = df[feat_cols].values.astype(float)
Y_data    = df[obj_cols].values.astype(float)
signs     = np.array([-1.0 if c.endswith('+') else 1.0 for c in obj_cols])
Y_pymoo   = Y_data * signs          # pymoo always minimizes; negate max objectives
xl, xu    = X_data.min(0), X_data.max(0)

print(f"POM3a: {len(df)} rows | features: {feat_cols} | objectives: {obj_cols}")

# ── Shared problem class ──────────────────────────────────────────────────────
class POM3(Problem):
    """Nearest-neighbour lookup into the pre-evaluated POM3 table."""
    def __init__(self, n_obj_override=None):
        n_obj = n_obj_override or len(obj_cols)
        super().__init__(n_var=len(feat_cols), n_obj=n_obj, xl=xl, xu=xu)
        self._Xn = (X_data - xl) / (xu - xl + 1e-9)
    def _evaluate(self, X, out, *args, **kwargs):
        Xn  = (X - xl) / (xu - xl + 1e-9)
        idx = [np.argmin(np.linalg.norm(self._Xn - x, axis=1)) for x in Xn]
        out["F"] = Y_pymoo[idx, :self.n_obj]

problem   = POM3()                       # 3-objective
TERM      = get_termination("n_gen", 100)
REF_POINT = Y_pymoo.max(0) * 1.1
hv_calc   = HV(ref_point=REF_POINT)
results   = {}                           # store all (name → res) for comparison
```

### 11.3 Genetic Algorithm (GA) — Single-Objective Baseline

GA is the historical starting point. We use it as a **single-objective** optimizer by
aggregating all objectives into a weighted sum — the pre-MOEA approach. This shows *why*
multi-objective methods are needed: you get one point, not a trade-off curve.

```python
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.problem import ElementwiseProblem

class POM3Scalar(ElementwiseProblem):
    """Single-objective: D2H scalarization — distance to heaven (ideal point).
    Objectives normalised to [0,1]; heaven is (0,0,...,0).
    This is the scalarization used in recent SBSE/MOOT literature.
    """
    def __init__(self):
        super().__init__(n_var=len(feat_cols), n_obj=1, xl=xl, xu=xu)
        self._Xn  = (X_data - xl) / (xu - xl + 1e-9)
        lo, hi    = Y_pymoo.min(0), Y_pymoo.max(0)
        self._Yn  = (Y_pymoo - lo) / (hi - lo + 1e-9)   # normalised objectives
    def _evaluate(self, x, out):
        xn  = (x - xl) / (xu - xl + 1e-9)
        idx = np.argmin(np.linalg.norm(self._Xn - xn, axis=1))
        # D2H scalar: distance from this row to heaven (0,…,0) in global-normalised space
        out["F"] = float(np.linalg.norm(self._Yn[idx]))

res_ga = minimize(POM3Scalar(), GA(pop_size=100), TERM, seed=42, verbose=False)

# Map back to original objectives
xn  = (res_ga.X - xl) / (xu - xl + 1e-9)
idx = np.argmin(np.linalg.norm((X_data - xl)/(xu - xl + 1e-9) - xn, axis=1))
print("GA best (weighted sum) → original objectives:")
for col, val in zip(obj_cols, Y_data[idx]):
    print(f"  {col}: {val:.4f}")
print("⚠  GA gives ONE point — cannot reveal trade-offs between objectives.")
```

### 11.4 Differential Evolution (DE) — Single-Objective

DE uses the same scalar wrapper but with a smarter, self-scaling mutation strategy.
Compare DE vs GA convergence speed on the same problem.

```python
from pymoo.algorithms.soo.nonconvex.de import DE

res_de = minimize(
    POM3Scalar(),
    DE(pop_size=50, variant="DE/rand/1/bin", CR=0.9, F=0.8),
    TERM, seed=42, verbose=False
)

xn  = (res_de.X - xl) / (xu - xl + 1e-9)
idx = np.argmin(np.linalg.norm((X_data - xl)/(xu - xl + 1e-9) - xn, axis=1))
print("DE best → original objectives:")
for col, val in zip(obj_cols, Y_data[idx]):
    print(f"  {col}: {val:.4f}")
```

### 11.5 CMA-ES — Covariance Matrix Adaptation

CMA-ES is the gold standard for continuous single-objective optimization.
It adapts the full covariance matrix of mutations — learning correlations between variables.

```python
from pymoo.algorithms.soo.nonconvex.cmaes import CMAES

res_cmaes = minimize(
    POM3Scalar(),
    CMAES(x0=np.full(len(feat_cols), 0.5) * (xu - xl) + xl, sigma=0.3),
    get_termination("n_gen", 200),   # CMA-ES needs more generations to warm up
    seed=42, verbose=False
)

xn  = (res_cmaes.X - xl) / (xu - xl + 1e-9)
idx = np.argmin(np.linalg.norm((X_data - xl)/(xu - xl + 1e-9) - xn, axis=1))
print("CMA-ES best → original objectives:")
for col, val in zip(obj_cols, Y_data[idx]):
    print(f"  {col}: {val:.4f}")
print("CMA-ES adapts its search shape to the fitness landscape curvature.")
```

### 11.6 NSGA-II — The Multi-Objective Workhorse

Now we switch to the true multi-objective formulation. All three POM3 objectives are
optimized simultaneously. NSGA-II returns a **Pareto front**, not a single point.

```python
from pymoo.algorithms.moo.nsga2 import NSGA2

res_nsga2 = minimize(
    problem,   # 3-objective POM3
    NSGA2(pop_size=100, sampling=FloatRandomSampling(),
          crossover=SBX(prob=0.9, eta=15), mutation=PM(eta=20),
          eliminate_duplicates=True),
    TERM, seed=42, verbose=False
)

results["NSGA-II"] = res_nsga2
print(f"NSGA-II: {len(res_nsga2.F)} Pareto solutions | HV: {hv_calc(res_nsga2.F):.4f}")
for i, col in enumerate(obj_cols):
    v = res_nsga2.F[:, i] * signs[i]
    print(f"  {col}: [{v.min():.3f}, {v.max():.3f}]")
```

### 11.7 NSGA-III — Many-Objective Extension

NSGA-III replaces crowding distance with structured reference points.
For 3 objectives it is comparable to NSGA-II; its advantage grows with M ≥ 4.

```python
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions

ref_dirs = get_reference_directions("das-dennis", problem.n_obj, n_partitions=6)

res_nsga3 = minimize(
    problem,
    NSGA3(pop_size=len(ref_dirs)+1, ref_dirs=ref_dirs,
          sampling=FloatRandomSampling(),
          crossover=SBX(prob=0.9, eta=30),
          mutation=PM(prob=1/problem.n_var, eta=20)),
    TERM, seed=42, verbose=False
)

results["NSGA-III"] = res_nsga3
print(f"NSGA-III: {len(res_nsga3.F)} Pareto solutions | HV: {hv_calc(res_nsga3.F):.4f}")
```

### 11.8 SPEA2 — Strength Pareto + k-NN Archive

SPEA2 uses a strength-based fitness (how many solutions you dominate) and an external
archive with k-nearest-neighbour density for truncation.

```python
from pymoo.algorithms.moo.spea2 import SPEA2

res_spea2 = minimize(
    problem,
    SPEA2(pop_size=100, sampling=FloatRandomSampling(),
          crossover=SBX(prob=0.9, eta=15), mutation=PM(eta=20)),
    TERM, seed=42, verbose=False
)

results["SPEA2"] = res_spea2
print(f"SPEA2:   {len(res_spea2.F)} Pareto solutions | HV: {hv_calc(res_spea2.F):.4f}")
```

### 11.9 MOEA/D — Decomposition into Scalar Sub-Problems

MOEA/D decomposes the 3-objective problem into N scalar Tchebycheff sub-problems,
one per weight vector. Neighbors share offspring and reference-point updates.

```python
from pymoo.algorithms.moo.moead import MOEAD

# Weight vectors for decomposition (same Das-Dennis grid as NSGA-III)
ref_dirs_moead = get_reference_directions("das-dennis", problem.n_obj, n_partitions=6)

res_moead = minimize(
    problem,
    MOEAD(ref_dirs=ref_dirs_moead,
          n_neighbors=15,          # each sub-problem has 15 neighbours
          prob_neighbor_mating=0.7,
          sampling=FloatRandomSampling(),
          crossover=SBX(prob=0.9, eta=20),
          mutation=PM(eta=20)),
    TERM, seed=42, verbose=False
)

results["MOEA/D"] = res_moead
print(f"MOEA/D:  {len(res_moead.F)} Pareto solutions | HV: {hv_calc(res_moead.F):.4f}")
```

### 11.9 SMS-EMOA — Hypervolume Contribution Selection

SMS-EMOA removes the solution with the *smallest hypervolume contribution* in each
generation — directly maximizing the most theoretically grounded quality indicator.

```python
from pymoo.algorithms.moo.sms import SMSEMOA

res_sms = minimize(
    problem,
    SMSEMOA(pop_size=100, sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.9, eta=15), mutation=PM(eta=20)),
    TERM, seed=42, verbose=False
)

results["SMS-EMOA"] = res_sms
print(f"SMS-EMOA:{len(res_sms.F)} Pareto solutions | HV: {hv_calc(res_sms.F):.4f}")
```

### 11.10 Full Multi-Metric Comparison: All Algorithms

> **Before running:** make sure you have executed sections 11.2–11.9 so that
> `results` contains all MOEA entries. Single-objective algorithms (GA, DE, CMA-ES)
> produce one point, not a front; their scores are computed by wrapping that point
> as a degenerate "front" of size 1.

```python
# ── Distance to Heaven (D2H) helper ──────────────────────────────────────────
# ── Global normalisation bounds (computed once from the full dataset) ─────────
_d2h_lo = Y_pymoo.min(0)
_d2h_hi = Y_pymoo.max(0)

def distance_to_heaven(F):
    """
    D2H (Distance to Heaven) — SBSE/MOOT definition (Menzies et al., 2025).

    Normalise objectives against the GLOBAL dataset range (not the front itself,
    which would make a 1-point front always score 0).
    Heaven = (0, 0, ..., 0) in normalised space = best on every objective.
    D2H = mean Euclidean distance from each solution to heaven. Lower = better.
    """
    Fn = (F - _d2h_lo) / (_d2h_hi - _d2h_lo + 1e-9)
    return float(np.linalg.norm(Fn, axis=1).mean())

# ── IGD helper ────────────────────────────────────────────────────────────────
from pymoo.indicators.igd import IGD
from pymoo.indicators.gd  import GD
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

# Build best-known reference front from ALL algorithm results combined
all_F   = np.vstack([res.F for res in results.values()])
nd_idx  = NonDominatedSorting().do(all_F, only_non_dominated_front=True)
ref_pf  = all_F[nd_idx]             # proxy for true Pareto front

igd_calc = IGD(ref_pf)
gd_calc  = GD(ref_pf)

# ── Spread (Delta) helper ─────────────────────────────────────────────────────
def spread_delta(F):
    """
    Spread Δ: measures how uniformly solutions are distributed along the front.
    Computed per objective as std of consecutive distances, normalised by range.
    Lower is better (0 = perfectly uniform).
    Only meaningful for fronts with >= 3 points.
    """
    if len(F) < 3:
        return float('nan')
    deltas = []
    for m in range(F.shape[1]):
        sorted_f = np.sort(F[:, m])
        gaps     = np.diff(sorted_f)
        rng      = sorted_f[-1] - sorted_f[0] + 1e-9
        deltas.append(gaps.std() / rng)
    return float(np.mean(deltas))

# ── Single-obj algorithms: wrap best point as a 1-point front ─────────────────
def scalar_best_as_front(res_scalar):
    """Return the best single-obj result as a (1, n_obj) array in pymoo space."""
    xn  = (res_scalar.X - xl) / (xu - xl + 1e-9)
    idx = np.argmin(np.linalg.norm((X_data - xl)/(xu - xl + 1e-9) - xn, axis=1))
    return Y_pymoo[idx:idx+1]   # shape (1, n_obj)

# ── Collect all results including single-objective ───────────────────────────
all_results = {
    "GA"    : scalar_best_as_front(res_ga),
    "DE"    : scalar_best_as_front(res_de),
    "CMA-ES": scalar_best_as_front(res_cmaes),
}
for name, res in results.items():
    all_results[name] = res.F          # already (N, n_obj) pymoo-space

# ── Random baseline ───────────────────────────────────────────────────────────
rng      = np.random.default_rng(42)
rand_idx = rng.choice(len(Y_pymoo), 200, replace=False)
rand_nd  = NonDominatedSorting().do(Y_pymoo[rand_idx], only_non_dominated_front=True)
all_results["Random"] = Y_pymoo[rand_idx][rand_nd]

# ── Compute all metrics ───────────────────────────────────────────────────────
rows = []
for name, F in all_results.items():
    hv   = hv_calc(F) if len(F) > 1 else 0.0
    igd  = float(igd_calc(F))
    gd   = float(gd_calc(F))
    d2h  = distance_to_heaven(F)
    sp   = spread_delta(F)
    rows.append((name, len(F), hv, igd, gd, d2h, sp))

# ── Print comparison table ────────────────────────────────────────────────────
print(f"{'Algorithm':<12} {'|Pareto|':>8} {'HV↑':>10} {'IGD↓':>9} {'GD↓':>9} {'D2H↓':>9} {'Spread↓':>9}")
print("─" * 72)
for name, n, hv, igd, gd, d2h, sp in rows:
    sp_str = f"{sp:9.4f}" if sp == sp else "      n/a"  # sp==sp is False when nan
    print(f"{name:<12} {n:>8}  {hv:>9.4f}  {igd:>8.4f}  {gd:>8.4f}  {d2h:>8.4f} {sp_str}")

print("""
Legend:
  |Pareto| = number of non-dominated solutions found
  HV↑      = Hypervolume (higher is better)
  IGD↓     = Inverted Generational Distance to best-known front (lower is better)
  GD↓      = Generational Distance (convergence only, lower is better)
  D2H↓     = Distance to Heaven — mean dist (global-normalised) to ideal point (lower is better)
  Spread↓  = Distribution uniformity across front (lower is better; n/a for 1-point)
""")

# ── Bar chart: all metrics side by side ──────────────────────────────────────

algo_names = [r[0] for r in rows]
hv_vals    = np.array([r[2] for r in rows])
d2h_vals   = np.array([r[5] for r in rows])
igd_vals   = np.array([r[3] for r in rows])

pal = ["#94a3b8","#f97316","#3b82f6","#6366f1",
       "#10b981","#a855f7","#f59e0b","#ef4444","#14b8a6"]

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
fig.suptitle("POM3a — Multi-Metric Algorithm Comparison (100 generations)",
             fontsize=11, fontweight='bold')

def hbar(ax, vals, title, xlabel, invert=False):
    colors = pal[:len(algo_names)]
    y = np.arange(len(algo_names))
    bars = ax.barh(y, vals, color=colors, edgecolor='white', height=0.6)
    ax.set_yticks(y); ax.set_yticklabels(algo_names, fontsize=8)
    ax.set_title(title, fontsize=9, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=8)
    ax.bar_label(bars, fmt="%.4f", padding=3, fontsize=7)
    if invert: ax.invert_xaxis()
    ax.grid(axis='x', alpha=0.3)
    ax.tick_params(labelsize=7)

hbar(axes[0], hv_vals,  "Hypervolume ↑",           "HV (higher = better)")
hbar(axes[1], d2h_vals, "Distance to Heaven (D2H) ↓", "D2H (lower = better)", invert=True)
hbar(axes[2], igd_vals, "IGD ↓",                   "IGD (lower = better)",  invert=True)

plt.tight_layout()
plt.savefig("pom3_metrics_comparison.png", dpi=150)
plt.show()
print("Saved: pom3_metrics_comparison.png")
```


# 11.10 pymoo Cheatsheet

| Concept | How pymoo expresses it | Example |
|---|---|---|
| **Problem (batch)** | Subclass `Problem`, override `_evaluate(self, X, out)` | `out["F"] = X @ weights` |
| **Problem (single row)** | Subclass `ElementwiseProblem`, override `_evaluate(self, x, out)` | `out["F"] = float(f(x))` |
| **Objectives** | `out["F"]` — shape `(N, n_obj)` or scalar | always **minimise**; negate to maximise |
| **Constraints** | `out["G"]` — shape `(N, n_con)` | feasible when `G ≤ 0` |
| **Bounds** | `xl=`, `xu=` in constructor | numpy arrays or scalars |
| **Run** | `minimize(problem, algorithm, termination, seed=)` | returns `Result` |
| **Termination** | `get_termination("n_gen", 100)` | also `"n_eval"`, `"time"` |
| **Results** | `res.F` — objective values of final population | `res.X` — decision variables |
| **Pareto front** | `res.F` after a MOEA — already non-dominated | single-obj: `res.F` is scalar |
| **Crossover** | `SBX(prob=0.9, eta=15)` | Simulated Binary Crossover |
| **Mutation** | `PM(eta=20)` or `PM(prob=1/n_var, eta=20)` | Polynomial Mutation |
| **Sampling** | `FloatRandomSampling()` | also `BinaryRandomSampling`, `PermutationRandomSampling` |
| **Reference dirs** | `get_reference_directions("das-dennis", M, n_partitions=p)` | needed by NSGA-III, MOEA/D |
| **Hypervolume** | `HV(ref_point=r).do(F)` or `hv(F)` | `ref_point` must be dominated by all F |
| **IGD / GD** | `IGD(ref_pf).do(F)` | needs a reference front |
| **Non-dom sort** | `NonDominatedSorting().do(F, only_non_dominated_front=True)` | returns index array |
| **Algorithm swap** | change the second arg to `minimize()` | everything else stays the same |

```python
problem   = MyProblem()                          # define what to optimise
algorithm = NSGA2(pop_size=100, ...)             # pick a solver
res       = minimize(problem, algorithm, TERM)   # run it; res.F is your front
```

---

## 12. Evaluation Metrics

Metrics assess an approximation set on two dimensions: **convergence** (are solutions close to the true Pareto front?) and **diversity** (are they spread across it?).

| Metric | Needs true PF? | Measures | Direction |
|---|---|---|---|
| **HV** | No (needs ref point) | Convergence + diversity | ↑ higher |
| **IGD** | Yes (or proxy) | Convergence + diversity | ↓ lower |
| **GD** | Yes (or proxy) | Convergence only — gameable | ↓ lower |
| **D2H** | No | Convergence + rough diversity; works for single-obj results | ↓ lower |
| **Δ (Spread)** | No | Diversity / uniformity only | ↓ lower |

### 12.1 Hypervolume (HV)

```
HV(S, r) = λ({ q : ∃ s ∈ S, s dominates q AND q dominates r })
  S = approximation set,  r = reference point,  λ = Lebesgue measure
```

Strictly Pareto-compliant and monotone. Does not require a known true front — only a reference point weakly dominated by all solutions. Complexity O(N^{M/2} log N) makes it expensive for M > 4.

### 12.2 Distance to Heaven (D2H)

Used in the MOOT/LITE SBSE work (Menzies et al., 2025). Heaven is the ideal point — best achievable value on every objective simultaneously.

```
1. Normalise each objective to [0,1] using the GLOBAL dataset range
   (not the front's own range — a 1-point front must not auto-score 0)
2. Heaven = (0, 0, …, 0)  in normalised space
3. D2H(S) = mean over s ∈ S of  ‖s_normalised‖₂
```

Key advantage: works for both single-point (single-objective) and full Pareto fronts, so all algorithms in Section 11.10 are comparable on the same scale.

### 12.3 IGD, GD, and Spread

**GD** measures how close your solutions are to the reference front (convergence only). **IGD** reverses direction — each point on the reference front finds its nearest solution in S — capturing both convergence and coverage of the front. GD can be gamed (one point on the true front scores 0); IGD cannot. When the true PF is unknown, build a proxy from the union of all algorithm results filtered to non-dominated solutions.

**Spread Δ** is orthogonal to convergence: it measures uniformity of gaps between solutions. A well-converged but clustered front scores badly on Δ.

---

## 13. Comparisons and Pitfalls

### 13.1 Full Comparison Table

| Algorithm | Era | Obj. | pymoo? | Key Innovation | SE Use Case |
|---|---|---|---|---|---|
| SA | 1 | 1 | ✗ (custom) | Probabilistic acceptance | Test prioritization |
| GA | 2 | 1 | ✓ `GA` | Crossover + population | GenProg, NRP |
| GP | 2 | 1 | ✗ DEAP | Evolves programs / trees | GenProg, EvoSuite |
| ES / CMA-ES | 3 | 1 | ✓ `CMAES` | Self-adaptive σ, covariance | HPO continuous |
| DE | 3 | 1 | ✓ `DE` | Vector-difference mutation | Config optimization |
| NSGA-I | 4 | 2–3 | ✗ (historic) | Non-dominated sorting | Historic SBSE |
| NSGA-II | 4 | 2–3 | ✓ `NSGA2` | Fast sort + crowding dist | EvoSuite, NRP |
| SPEA2 | 4 | 2–3 | ✓ `SPEA2` | Strength + kNN archive | Pareto spread |
| MOEA/D | 4 | 3+ | ✓ `MOEAD` | Tchebycheff decomposition | Structured fronts |
| NSGA-III | 4 | 4+ | ✓ `NSGA3` | Reference-point niching | Many-obj configs |
| SMS-EMOA | 4 | 2–3 | ✓ `SMSEMOA` | Hypervolume contribution | Best HV theory |
| GDE3 | 4 | 2+ | ✗ | DE + Pareto selection | Continuous MOO |
| Hyperband | 5 | 1 | ✗ multi-fid | SHA brackets | DL HPO |
| ASHA | 5 | 1 | ✗ multi-fid | Async promotion | GPU cluster HPO |
| DEHB | 5 | 1 | ✗ multi-fid | DE + Hyperband | ML HPO for SE |
| BO/EGO | 6 | 1 | ✗ GPyOpt | GP surrogate + EI/UCB | Config expensive |
| SMAC | 6 | 1 | ✗ SMAC3 | RF surrogate + EI | ML HPO mixed |
| LITE/EZR | 7 | 1–3 | ✗ custom | Binary contrastive classifier | Scarce-label SBSE |

### 13.2 Common Pitfalls

1. **Forgetting evaluation cost**: In SE, fitness evaluation dominates runtime. Every design decision should be made with "total evaluations" as the primary budget, not "generations".

2. **Using NSGA-II for M > 3**: Crowding distance loses meaning in high dimensions. Switch to NSGA-III or MOEA/D.

3. **Not normalizing objectives**: NSGA-II/III degrade if f1 ∈ [0,1] and f2 ∈ [0,1000]. Always normalize.

4. **Misinterpreting the Pareto front**: It is not "the answer." It is the trade-off surface. You still need domain knowledge to select a specific point.

5. **Using GA for continuous problems**: Real-valued encoding in a GA is awkward. Use DE or CMA-ES instead.

6. **Ignoring LITE/EZR for very sparse budgets**: If you can only afford 20 evaluations, no standard MOEA will find a good Pareto front. LITE-style approaches are specifically designed for this regime, which is the norm in expensive SE optimization.

---

## 14. Summary & References

### 14.1 The Full Historical Arc

| Era | Constraint | Algorithm | Solves | Leaves Open |
|---|---|---|---|---|
| 1 | KB RAM | SA / Hill Climbing | Local optima escape | No population, single-obj only |
| 2 | MB RAM | GA / GP | Parallel search, program evolution | Step size control, real values |
| 3 | FPU hardware | DE / CMA-ES | Real-valued, self-scaling | Multi-objective |
| 4 | Complex goals | NSGA-II / NSGA-III / MOEA/D | Pareto front, trade-off analysis | Expensive evaluations |
| 5 | GPU training costs | Hyperband / DEHB | Budget triage, multi-fidelity | No learning from history (Hyperband) |
| 6 | Simulation costs | BO / SMAC | Surrogate modeling | Needs 100-200 evals to fit a good model |
| 7 | Label scarcity | LITE / EZR | <100 evals, sparse regimes | Active research area |

### 14.2 Key Papers

**Foundational EA:**
- Holland, J.H. (1975). *Adaptation in Natural and Artificial Systems*. U. Michigan Press.
- Goldberg, D.E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley.
- Storn, R. & Price, K. (1997). Differential Evolution. *Journal of Global Optimization* 11(4).
- Deb, K. (2001). *Multi-Objective Optimization Using Evolutionary Algorithms*. Wiley.

**NSGA Family:**
- Srinivas, N. & Deb, K. (1994). Multiobjective Optimization Using Nondominated Sorting in GAs. *ECJOR* 2(3).
- Deb, K., Pratap, A., Agarwal, S. & Meyarivan, T. (2002). A fast and elitist MOEA: NSGA-II. *IEEE TEC* 6(2).
- Deb, K. & Jain, H. (2014). NSGA-III: Evolutionary Many-Objective Optimization. *IEEE TEC* 18(4).
- Zhang, Q. & Li, H. (2007). MOEA/D. *IEEE TEC* 11(6).

**Multi-Fidelity & Surrogates:**
- Li, L. et al. (2017). Hyperband. *JMLR* 18(185).
- Awad, N.H., Mallik, N. & Hutter, F. (2021). DEHB. *IJCAI 2021*.
- Jones, D.R., Schonlau, M. & Welch, W.J. (1998). EGO. *Journal of Global Optimization* 13.
- Hutter, F., Hoos, H. & Leyton-Brown, K. (2011). SMAC. *LION 2011*.

**SBSE Applications:**
- Harman, M. & Jones, B.F. (2001). Search-Based Software Engineering. *IST* 43(14).
- Le Goues, C. et al. (2012). GenProg. *IEEE TSE* 38(1).
- Fraser, G. & Arcuri, A. (2011). EvoSuite. *ESEC/FSE 2011*.
- Yoo, S. & Harman, M. (2012). Regression Testing Survey. *STVR* 22(2).
- Nair, V. et al. (2018). FLASH. *ESEC/FSE 2018*.
- Menzies, T. et al. (2025). MOOT. *arXiv:2511.16882*.

---
