<p align="center">
  <a href="https://github.com/txt/seai26spr/blob/main/README.md"><img 
     src="https://img.shields.io/badge/Home-%23ff5733?style=flat-square&logo=home&logoColor=white" /></a>
  <a href="https://github.com/txt/seai26spr/blob/main/docs/lect/syllabus.md#top"><img 
      src="https://img.shields.io/badge/Syllabus-%230055ff?style=flat-square&logo=openai&logoColor=white" /></a>
  <a href="https://docs.google.com/spreadsheets/d/19HJRraZex9ckdIaDHaTi0cGsvUcIhdTH6kIGoC_FODY/edit?gid=0#gid=0"><img 
      src="https://img.shields.io/badge/Teams-%23ffd700?style=flat-square&logo=users&logoColor=white" /></a>
  <a href="https://moodle-courses2527.wolfware.ncsu.edu/course/view.php?id=8118&bp=s"><img 
      src="https://img.shields.io/badge/Moodle-%23dc143c?style=flat-square&logo=moodle&logoColor=white" /></a>
  <a href="https://discord.gg/vCCXMfzQ"><img 
      src="https://img.shields.io/badge/Chat-%23008080?style=flat-square&logo=discord&logoColor=white" /></a>
  <a href="https://github.com/txt/seai26spr/blob/main/LICENSE.md"><img 
      src="https://img.shields.io/badge/©%20timm%202026-%234b4b4b?style=flat-square&logoColor=white" /></a></p>
<h1 align="center">:cyclone: CSC491/591 (013): Software Engineering and AI <br>NC State, Spring '26</h1>
<img src="https://raw.githubusercontent.com/txt/seai26spr/main/docs/lect/banner.png"> 





# SBSE Lecture: Applications, Surrogates, Rigor, and the Simple Wins

**Prerequisites:** search algorithms, MOO, HPO (prior lectures)

---


**Central question for today:**
> Search is powerful. But *when* do we need it, and how do we
> know it worked?

---

## Part 1 — Classic SE Applications

### 1.1 Test Generation

The original killer app for SBSE. The idea: treat coverage
as a fitness function, then search for inputs that maximize it.

**Branch coverage as fitness:**

```
fitness(t) = 1 - d(t) / (d(t) + 1)
```

Where `d(t)` is the branch distance — how far the test `t`
was from flipping a branch. This turns a binary hit/miss into
a smooth landscape. AUSTIN, EvoSuite, Randoop all do this.

**Mutation testing upgrade:**
- Coverage is a weak proxy. Mutation score is better.
  - Mutation testing injects bugs to test your tests.
  - Mutant: A version of your code with one small change (e.g., > becomes <).
  - Killed: Your test suite fails (This is good; your tests caught the bug).
  - Survived: Your test suite passes (This is bad; your tests are blind to this bug).
- But: *N* mutants × search = expensive.
- Trick: subsume mutants; search for tests that kill *classes*.
  - Subsumption: Many mutants are redundant. If killing "Mutant A" always kills "Mutant B," then B is subsumed by A. You only need to track A. This shrinks the pool of bugs you have to test against.
  - Kill Classes: Instead of looking for a test for every individual mutant, we group mutants into "equivalence classes" (groups that fail for the same reason). You then search for the minimal set of tests that kills every class of bug, rather than every individual bug.

**Fuzzing connection:**
- AFL = coverage-guided fuzzing = hill-climbing on branch bitmap
  - Instead of storing a massive list of every instruction hit, it uses a fixed-size byte array (usually 64KB) to map "edge transitions"—the jump from one block of code to another.
  - How it Works (The Hashing Trick) When the compiler instruments your code, it assigns a random ID to every code block. When you move from Block A to Block B, the fuzzer calculates adds index in the bitmap
- LibFuzzer, HonggFuzz — evolutionary flavor
- Grey-box fuzzing: partial program analysis + random mutation
- SBSE framing: fitness = new coverage found per unit time

**Key insight:** EvoSuite (Fraser & Arcuri 2011) showed GA-generated
tests match or beat human tests on branch/mutation coverage.
But humans still win on *fault revelation* — fitness ≠ test quality.

---

### 1.2 Automated Bug Repair

**GenProg (Le Goues et al. 2012):**
- Representation: AST patches (delete, replace, insert)
- Fitness: failing tests pass, passing tests don't break
- GP over patch space; early results looked great

**The replication crisis:**
- Later studies: most GenProg "fixes" were test-suite patches,
  not real fixes (delete the failing code path)
- Lesson: **fitness function ≠ correctness**

**Modern repair:**
- Template-based: CapGen, SimFix — constrain search space
- Learning-based: CodeBERT, LLMs generate candidate patches
  - Originally, template-based repair required humans to manually write "Fix Patterns" (e.g., if you see a NullPointerException, add an if (x != null)).
  - Learning-based repair (the modern way) uses Deep Learning to learn those templates automatically from GitHub. Instead of a human defining the template, the model sees 10,000 fixes for a specific bug and "learns" the probabilistic shape of a correct patch.
- Oracle problem remains: what does "fixed" mean?

**Fault localization first:**
- Ochiai, Tarantula: rank lines by pass/fail correlation
- SBFL is itself a search problem (rank aggregation)
- Better localization → smaller search space for repair

<img width="897" height="636" alt="image" src="https://github.com/user-attachments/assets/1f643534-c753-4a17-964d-e38fa702f44d" />

---

### 1.3 Refactoring & Architecture

**Refactoring as optimization:**
- Objectives: coupling, cohesion, complexity, size
- Decision variables: which classes/methods to move/merge
- Operators: move method, extract class, inline method

**Architecture recovery:**
- Cluster source files by dependency into "subsystems"
- Fitness: Modular Quality (MQ) = intra-cluster / inter-cluster
- SA or GA over partition space

**Practical note:** These are expensive evaluations (recompile,
re-analyze). Surrogate models (next section) help a lot here.

---

### 1.4 Planning: Next-Release Problem


<img width="1106" height="495" alt="image" src="https://github.com/user-attachments/assets/eb1b6d62-11cf-4075-a085-3662b2f4c122" />

**Setup:**
- *N* features, each with cost and value
- Budget constraint; some features depend on others
- Which features go in the next release?

This is a **constrained 0/1 knapsack** variant.

```
maximize  Σ value(i) * x(i)
subject to Σ cost(i) * x(i) ≤ Budget
           x(j) = 1  if x(i) = 1 and i depends on j
```

GA encodes `x` as a bit-string. Works well at scale
(hundreds of features) where exact methods fail.

**Requirements prioritization:**
- Stakeholders rank features (AHP, value mapping)
- SBSE resolves conflicts between stakeholders
- Objective: maximize agreement across stakeholders

---

### 1.5 Software Configuration Tuning

Modern systems (databases, compilers, ML pipelines) have
**hundreds of configuration knobs**. Getting them right
matters enormously.

<img width="723" height="687" alt="image" src="https://github.com/user-attachments/assets/874d544c-e9e2-4510-8385-60b10ba7c323" />

<img width="708" height="546" alt="image" src="https://github.com/user-attachments/assets/351d41e7-537d-4db9-bac1-1f9af145eac5" />



**MySQL example (real numbers):**
- 200+ configuration parameters
- Throughput can vary 10× across configs
- Default config is almost never optimal for a workload

**SBSE framing:**
```
Decision space:  config vector x ∈ {bool, int, float, enum}^N
Objective:       maximize throughput(x)  (or minimize latency)
Oracle:          run benchmark — takes 5–30 minutes per eval
Budget:          maybe 100 evals before dev patience runs out
```

This is exactly where BO with RF surrogate shines.
Tools: SMAC, FLASH, iracee, Ottertune (ML-based DBA).

**Multi-objective config:**
- Throughput vs. latency vs. memory vs. energy
- Pareto front → operator picks operating point
- NSGA-II works but BO-based MOO    needs
  far fewer evaluations

**Compiler flags:**
- GCC/LLVM: hundreds of `-O` sub-flags
- Fitness: binary size, runtime, compilation time
- SBSE finds flag combinations that beat `-O3` on specific
  workloads (iterative compilation literature)

---

### 1.6 Test Suite Optimization

Distinct from test *generation* — here we already have
tests and want to manage them.

- See [paper](https://arxiv.org/pdf/2008.00612)

- <img width="529" height="426" alt="image" src="https://github.com/user-attachments/assets/daf8868d-ff54-494e-996d-652dda1e32af" />


<img width="987" height="286" alt="image" src="https://github.com/user-attachments/assets/ca9f938b-d9c8-483b-b13e-e3d634fc488e" />


<img width="526" height="377" alt="image" src="https://github.com/user-attachments/assets/35439ff8-c80b-453e-9588-053fd433d084" />

<img width="553" height="316" alt="image" src="https://github.com/user-attachments/assets/ef4c32a1-53c0-4a9e-8cb1-6d5a38c35be8" />

<img width="288" height="199" alt="image" src="https://github.com/user-attachments/assets/92f54266-bbe9-48fe-afe5-824dc7f18ca8" />



<img width="540" height="375" alt="image" src="https://github.com/user-attachments/assets/68a767df-2a84-41ff-aec9-3b55cf23121b" />


**Test Case Prioritization (TCP):**
- Order tests so failures appear earlier
- Fitness: APFD (Average Percentage Faults Detected)
- Greedy works surprisingly well; GA adds little

**Test Suite Minimization:**
- Remove redundant tests while preserving coverage
- NP-hard; GA/ILP approaches
- Risk: removing tests that catch rare faults

**Regression test selection:**
- Which tests to re-run after a code change?
- Dependency analysis + search over test subsets
- Fitness: coverage of changed code × execution time

**The CI/CD pressure:**
- Google, Meta: millions of tests, seconds budget
- Prediction models (ML on past failures) + selection
- SBSE frames this as: minimize time, maximize fault detection

---

### 1.7 Effort Estimation & Project Scheduling

- See [paper](https://arxiv.org/pdf/2006.07240)

<img width="1040" height="675" alt="image" src="https://github.com/user-attachments/assets/9bd4cf98-332c-410e-82a5-e0b75b3730d2" />


- <img width="472" height="163" alt="image" src="https://github.com/user-attachments/assets/5501bd06-6c25-4485-8155-7b2652713bfa" />

 =<img width="574" height="200" alt="image" src="https://github.com/user-attachments/assets/fbeb2067-97e9-4bbc-947b-03cb52bc3e02" />

 <img width="655" height="546" alt="image" src="https://github.com/user-attachments/assets/4fc536c0-9738-4200-8823-d4130dda3026" />

 <img width="821" height="329" alt="image" src="https://github.com/user-attachments/assets/5bb2b02b-64cc-4b48-968b-04616e825715" />


Note: prudence checks on data:

<img width="702" height="477" alt="image" src="https://github.com/user-attachments/assets/97f13e7f-e2f9-459f-9694-00a02e286aca" />

<img width="854" height="802" alt="image" src="https://github.com/user-attachments/assets/7e980252-c154-4b14-91d7-fa7d452070c1" />

<img width="984" height="307" alt="image" src="https://github.com/user-attachments/assets/e7e57b3a-5fb9-4ea6-a635-00d788dae1ad" />



**Effort estimation:**
- Input: project features (size, complexity, domain)
- Output: person-months
- SBSE: search for the best analogy (CBR) or ensemble
  weights that minimize prediction error on past projects

**Project scheduling (multi-objective):**
```
Objectives: minimize duration, minimize cost, maximize quality
Constraints: precedence, resource limits, dependencies
```
- Classic ops-research problem now done with NSGA-II
- Uncertainty: task durations are distributions, not points
- Robust optimization: solutions that stay good under noise

---

### Part 1 Summary

| Application           | Representation       | Fitness                     |
|-----------------------|----------------------|-----------------------------|
| Test generation       | Input vectors        | Branch coverage / mut score |
| Bug repair            | AST patches          | Test suite pass/fail        |
| Refactoring           | Class partition      | MQ, coupling, cohesion      |
| Release planning      | Feature bitmask      | Value - penalty             |
| Config tuning         | Config vector        | Throughput / latency        |
| Test prioritization   | Test ordering        | APFD                        |
| Project scheduling    | Task assignment      | Time, cost, quality         |

**Take-home:** Every SE problem that's NP-hard is a candidate.
The hard part is defining fitness and choosing representation.

---

## Part 2 — Active Learning & Surrogate Models

### 2.1 Why Surrogates?

In all the applications above, **evaluation is expensive:**

- Running a test suite: seconds to minutes
- Recompiling and re-analyzing architecture: minutes
- Simulation-based fitness (e.g., autonomous driving): hours

With a budget of *B* evaluations, you need to be smart.

**Surrogate = cheap approximation of expensive fitness:**

```
f_true(x)   ← expensive (minutes/hours)
f_hat(x)    ← surrogate (milliseconds)
```

Train `f_hat` on a few true evaluations, use it to guide
search, occasionally query `f_true` to update `f_hat`.

This is **Bayesian Optimization** at its core.

---

### 2.2 Gaussian Process Surrogates

A GP defines a distribution over functions. Given training
data `{(x_i, y_i)}`, it predicts:

```
p(y* | x*)  ~  Normal(μ(x*), σ²(x*))
```

- `μ(x*)` = predicted mean (best guess)
- `σ(x*)` = predicted uncertainty (how lost we are)

**Algorithm:**

```
1. Evaluate f_true on initial Latin Hypercube sample
2. Fit GP to {(x_i, y_i)}
3. Maximize acquisition → candidate x*
4. Evaluate f_true(x*)
5. Update GP; goto 3
```

BO converges in **10–100 evaluations** where GA needs
thousands. That matters enormously in SE.

---

### 2.3 Acquisition Functions — The Heart of BO

The acquisition function answers: **given the surrogate,
where should I sample next?**

All three classics use the GP's `μ` and `σ`.
Let `f_best` = best value observed so far.

---

#### Probability of Improvement (PI)

```
PI(x) = P( f(x) > f_best )
       = Φ( (μ(x) - f_best) / σ(x) )
```

`Φ` = standard normal CDF.

- "What's the chance this point beats the current best?"
- **Pure exploiter** — only cares about *probability*,
  not *how much* better the point might be
- Pathology: drills into one region, ignores everything else
- Rarely used alone; mostly pedagogical

**Pathology example:**
```
f_best = 0.85

A: μ=0.90, σ=0.01 → PI very high  (almost certain win)
B: μ=0.50, σ=0.80 → PI lower      (uncertain, but could be 2.0)
```
PI always picks A. Misses the potentially great B entirely.

---

#### Expected Improvement (EI)

```
EI(x) = E[ max(f(x) - f_best, 0) ]

      = (μ(x) - f_best) · Φ(Z)  +  σ(x) · φ(Z)

        where Z = (μ(x) - f_best) / σ(x)
```

`Φ` = CDF,  `φ` = PDF of standard normal.

- First term: **exploitation** — how much better than best?
- Second term: **exploration** — reward high uncertainty
- EI = 0 when σ = 0 (already evaluated, no surprise left)
- EI > 0 whenever σ > 0, even if μ < f_best

**Why EI dominates in practice:**
- Automatically balances explore/exploit
- Scale-invariant: works regardless of f's magnitude
- Analytic — no sampling needed, fast to compute
- Default in Spearmint, GPyOpt, BoTorch

**Same example with EI:**
```
A: μ=0.90, σ=0.01, f_best=0.85
   Z = (0.90-0.85)/0.01 = 5.0
   EI ≈ 0.05·Φ(5) + 0.01·φ(5) ≈ 0.05

B: μ=0.50, σ=0.80
   Z = (0.50-0.85)/0.80 = -0.44
   EI = (-0.35)·Φ(-0.44) + 0.80·φ(-0.44)
      ≈ -0.35·0.33 + 0.80·0.36 ≈ 0.17
```
EI correctly prefers B — uncertain but potentially great.

---

#### Upper Confidence Bound (UCB)

```
UCB(x) = μ(x) + κ · σ(x)
```

`κ` = exploration parameter, typically 1–3.

- **Optimistic under uncertainty**: assume best case
- Higher `κ` → more exploration; lower → more exploitation
- Theoretically grounded: sublinear regret guarantees
  (GP-UCB, Srinivas et al. 2010)
- No CDF/PDF math — just addition

**The κ dial:**
```
κ = 0   → pure greedy (exploit only)
κ = 1   → mild exploration
κ = 3   → aggressive exploration
κ → ∞  → pure random search
```

Anneal `κ` over time: explore early, exploit late.

**Prefer UCB when:** you care about cumulative performance
over many queries (regret minimization), not just finding
one global optimum at the end.

---

#### Thompson Sampling (bonus)

```
1. Draw a sample function f̃ ~ GP posterior
2. x* = argmax f̃(x)   (maximize the drawn sample)
3. Evaluate f_true(x*)
```

Inherently stochastic — different sample each iteration.
Naturally parallel: draw *B* functions → *B* candidates
→ evaluate in parallel. Increasingly popular for batch
BO in SE config tuning.

---

#### When to Use Which

| Acquisition        | Use when...                             |
|--------------------|-----------------------------------------|
| PI                 | Teaching; illustrating greediness       |
| EI                 | Default. Finding one global optimum.    |
| UCB                | Online/sequential. Regret minimization. |
| Thompson Sampling  | Parallel evaluation budget available.  |

**SE-specific note:** most SE config problems have
discrete/categorical inputs. GPs struggle there — RF
surrogate + EI or UCB often outperforms pure GP-BO.

---

### 2.3 Random Forests as Surrogates

GPs scale as O(n³). For high-dimensional SE problems, RF
surrogates are often better:

- Ensemble of trees → natural uncertainty estimate
  (variance across tree predictions)
- Handle categorical features (feature flags, config options)
- SMAC (from prior lecture) uses RF surrogate

**BOHB** (Bayesian Optimization + HyperBand):
- Combine BO's sample efficiency with HyperBand's early stopping
- State of the art for HPO in ML pipelines

---

### 2.4 Active Learning for SE

Active learning is surrogate-based optimization applied
to **label-efficient learning** — when labels are expensive
(human annotation, test execution, expert review).

**The loop:**

```
Pool of unlabeled examples U
Labeled set L = small initial sample

repeat:
    Train model M on L
    Select x* = argmax acquisition(M, U)
    Obtain label y* = oracle(x*)   ← expensive step
    L = L ∪ {(x*, y*)}
until budget exhausted
```

**Acquisition strategies:**

| Strategy         | Select x* that...                     |
|------------------|---------------------------------------|
| Uncertainty      | M is least confident about            |
| Margin           | is closest to decision boundary       |
| QBC              | committee of models disagrees most on |
| Expected Error   | would most reduce future error        |
| Centroid         | is closest to cluster center of U     |

**SE use cases:**
- Effort estimation: label (story points) is expensive
- Defect prediction: label (is buggy?) costs inspection
- Configuration tuning: label (performance) costs a run
- Code review triage: label (needs review?) costs expert time

**Key result (your lab's angle):**
- ~20–50 labels often sufficient for good models in SE
- Centroid-based acquisition often matches or beats uncertainty
  sampling — simpler, no model needed for selection
- Random sampling within clusters beats pure random

**Incremental Bayes connection:**

```python
# Naive Bayes with Welford online updates
# No retraining needed — just update sufficient statistics
# Natural fit for active learning loops
```

The simplest active learner: maintain class statistics
incrementally, select next label by entropy or distance.

# `acquire` (EZR) vs Thompson Sampling

## Thompson Sampling

Maintains a *probability distribution over reward* for each option.
At each step, **samples** from those distributions and picks the argmax.
Exploration happens naturally — high-variance arms (different rows) get sampled sometimes
just by luck of the draw.

It is a **bandit** algorithm:
- options are independent
- rewards are stationary
- you pick one arm (row) at a time

 

## Delta Tho,pson to EZR 

### 1. Two-class model, not per-arm distributions

Split labeled rows into `best` (top √n) and `rest`, then ask:

> *"Is this unlabeled row more likely to come from `best` than `rest`?"*

That is a **classifier-as-acquisition-function**, not a per-option posterior.

```python
best, rest = clone(d, lab.rows[:int(n)]), clone(d, lab.rows[int(n):])
fn = lambda r: score(lab, best, rest, r)   # Naive Bayes likelihood ratio
```

### 2. Landscape, not bandits

Thompson assumes arms  (rows) are **independent**.  
`acquire` (EZR) assumes a *continuous landscape* over x-space — nearby rows
in x-space have correlated y-values. Proximity matters; Thompson ignores it.

### 3. Deterministic threshold, not stochastic sampling

Thompson explores via **sampling noise**.  
`acquire` (EZR) scans the unlabeled pool and takes the *first* row where
`score < 0` (i.e., P(best|x) > P(rest|x)):

```python
for j in range(len(unlab)):
    if fn(unlab[idx]) < 0:      # more likely best than rest
        add(best, add(lab, label(unlab.pop(idx))))
        break
```

No random draw — **exploitation-first**, with implicit exploration
from pool-scanning order (shuffled at the start).

 

## The Punchline

| | Thompson Sampling | `acquire` |
|---|---|---|
| Model | Beta/Gaussian per arm (rows) | Naive Bayes (best vs rest) |
| Assumption | Independent arms | Continuous x-space landscape |
| Exploration | Sampling variance | Unlabeled pool + shuffle |
| Update cost | O(1) per arm | O(1) incremental NB |

> Thompson explores by being *uncertain about rewards*.  
> `acquire` (EZR) explores by *not having labeled that region yet* —  
> the unlabeled pool is your uncertainty; the Bayes score is your
> exploitation signal.

**Closest relative:** Expected Improvement (EI) in Bayesian Optimization,
but with Naive Bayes as the surrogate instead of a Gaussian Process.
Same core idea, 1/100th the compute — which is why it matches SMAC
empirically without rebuilding expensive ensembles on every update.

### Part 2 Summary

```
Expensive fitness?  →  Use a surrogate
                        GP (smooth, low-D) or RF (high-D, mixed)
Few labels?         →  Active learning
                        Uncertainty / centroid / QBC acquisition
Rule of thumb:      →  50 labels is often enough in SE tasks
```

---

## Part 3 — Empirical Rigor

### 3.1 Why This Is Hard

SBSE results are **stochastic**. Run NSGA-II twice, get
different Pareto fronts. This means:

- Single-run comparisons are meaningless
- You must report distributions, not point estimates
- Statistical testing is mandatory, not optional

Common failure modes in published SBSE work:
- Report only the best run
- Compare median without testing significance
- Forget to run the baseline

---

### 3.2 Statistical Tests You Actually Need

## 3.2 Statistical Tests You Actually Need

**One question:** are these two lists of numbers the same?  
**One function:** `same(a, b)` — fail-fast, no scipy, no p-value theatre.

```python
def same(a, b):
    if not cohen(a, b):  return True  # effect too small to care
    if not ks(a, b):     return True  # same distribution shape
    return not cliffs(a, b)           # same rank order
```

### Step 1: Prudence check — Cohen's d

Before any test, ask: *is the difference even worth caring about?*

Cohen's d measures effect size in standard-deviation units:

```
        |mean(a) − mean(b)|
d =  ─────────────────────────
      sqrt((sd(a)² + sd(b)²)/2)
```

If `d < 0.2` (small effect threshold), **stop** — the distributions
are too close to matter, regardless of sample size.  
No test needed. Return `same = True`.

> **Why first?** Large samples make tiny differences "significant".
> Cohen stops you caring about noise.

---

### Step 2: Distribution shape — KS test

Kolmogorov-Smirnov: are the CDFs the same?

```python
def ks(a, b, conf=0.05):
    # walks sorted merge, tracks max CDF gap d
    c = sqrt(-log(conf/2) / 2)
    return d > c * sqrt((n1+n2)/(n1*n2))  # True = different
```

- Non-parametric, no normality assumption  
- Sensitive to **shape** differences (spread, skew), not just means  
- Pure Python — no scipy

---

### Step 3: Effect size — Cliff's delta

How often does a value from `a` beat one from `b`?

```
        #{a>b} − #{a<b}
δ =  ─────────────────────
           n(a) × n(b)
```

| δ       | Meaning         |
|---------|-----------------|
| < 0.147 | negligible      |
| < 0.33  | small           |
| < 0.474 | medium          |
| ≥ 0.474 | large           |

If `|δ| ≤ 0.147`, return `same = True`.

> Cliff's delta is Vargha-Delaney A₁₂ recentered at 0.  
> Same math, cleaner "no difference = 0" semantics.

---

### Comparing multiple treatments — Scott-Knott

`same()` plugs straight into Scott-Knott as its indistinguishability
predicate:

```python
def sk(rxs):          # rxs = {name: [values]}
    # 1. sort treatments by median
    # 2. find the split that minimises weighted variance
    # 3. if the two halves are not same(), recurse on each
    # 4. else merge — they're one group
```

Output: one rank number per treatment. Same rank = same group.

```
  1  A   10.02     # A and B statistically indistinguishable
  1  B   10.15
  2  C   12.22     # C and D form a separate, better group
  2  D   11.99
```

Better than pairwise tests:  
- no multiple-comparison inflation  
- meaningful clusters, not just "A ≠ B"  
- one consistent effect-size criterion throughout

---

### 3.3 Baselines and the "Simple Wins" Problem

**Mandatory baselines for any SBSE paper:**

1. **Random search** — sample uniformly from the search space
2. **(ε+1) archiver** — tiny, fast, often matches NSGA-II
3. **Domain default** — whatever practitioners use today

If your algorithm doesn't beat *random search*, you have
a fitness function problem, not an algorithm problem.

**Published horror stories:**
- Multiple SBSE papers where random search matched NSGA-II
  once proper baselines were added (Arcuri & Briand 2011)
- GenProg beaten by random single-edit patches on some
  benchmarks (Qi et al. 2014)

**The Arcuri-Briand checklist:**

```
□ Multiple independent runs (≥30)
□ Fixed evaluation budget (not wall time)
□ Wilcoxon + A₁₂ reported
□ Random search baseline included
□ Effect sizes discussed, not just p-values
```

This is now effectively required by top venues (ICSE, FSE,
TOSEM, EMSE).

---

### 3.4 Threats to Validity

Standard framing (Wohlin et al.):

- **Internal:** confounds within the experiment
  (e.g., tuned your algorithm, not the baseline)
- **External:** generalizability (one language, one domain)
- **Construct:** fitness ≠ what you actually care about
- **Conclusion:** statistical choices, multiple comparisons

In SBSE: **construct validity** is underreported.
Branch coverage fitness ≠ fault revelation. Say so.

---

## Part 4 — Modern Topics & The Simple Wins Argument

### 4.1 LLMs as Search Operators

- see [paper1](https://arxiv.org/pdf/2501.00125)
- see [paper2](https://arxiv.org/pdf/2603.22474)

Recent framing: use LLMs not to *replace* search, but as
**mutation/crossover operators** in evolutionary loops.

**LLM-as-mutator pipeline:**

```
1. Represent candidate as code/text
2. Prompt LLM: "Improve this to maximize [fitness]"
3. Evaluate LLM output → new candidate
4. Keep if better (hill climb) or use in population (GA)
```

Examples:
- **FunSearch** (DeepMind 2023): LLM mutations + evaluator
  found new cap-set solutions. Actual mathematical discovery.
- **AlphaCode 2**: LLM generates, filter + cluster, re-rank
- **ChatRepair**: iterative LLM repair with test feedback

**The tension:**
- LLMs are expensive evaluations themselves (API cost)
- Need surrogate thinking: don't call LLM every iteration
- Prompt engineering = search space design

**Key question:** Is the LLM doing the search, or are we
doing search over LLM outputs? (Answer: both.)

---

### 4.2 Search for Fairness & Explainability

- [paper](https://ieeexplore.ieee.org/abstract/document/9679036)

**Fairness as a multi-objective problem:**

```
Objective 1: maximize accuracy
Objective 2: minimize demographic parity gap
Objective 3: minimize individual fairness violations
```

Pareto front gives practitioners the trade-off curve —
let *them* choose the operating point (value judgment).

Tools: Themis (fairness testing), FLASH, FAIREA.

**Explainability via search:**
- Fit a decision tree to the Pareto front
  → "here's the rule that explains which configurations win"
- LIME/SHAP = local search in feature importance space
- Your `disty` tree approach: minimize variance in
  objective space, split on decision space features

This is a clean loop: search to optimize, then search
(decision tree) to explain *what* you optimized.

---

### 4.3 Energy-Aware SE

Emerging area: **energy consumption** as an objective.

- Green mining: measure energy of test suites, configurations
- Trade-off: faster code vs. lower power draw
- Multi-objective: performance × energy × correctness
- Carbon-aware scheduling: when to run CI based on grid mix

Early papers: Couto et al., Cruz & Abreu on energy profiling.
SBSE framing: energy measurement is the expensive oracle →
need surrogates immediately.

---

### 4.4 The "Simple Ain't Stupid" Argument

This is the most important thing in the lecture.

**The empirical record:**

Across 120+ SE tasks (defect prediction, effort estimation,
configuration, test prioritization):

```
Random forests ≈ deep learning
Naive Bayes ≈ SVM
50 labels ≈ 5000 labels (with right selection)
(ε+1) ≈ NSGA-II on most SE benchmarks
```

Why does this happen in SE?

1. **Small data:** SE datasets are tiny by ML standards.
   Complex models overfit; simple ones generalize.

2. **Noisy labels:** Bug reports, story points, code reviews
   are all noisy. Complexity doesn't help noise.

3. **Low intrinsic dimensionality:** Most SE datasets have
   a few dominant factors. Trees find them fast.

4. **The MOOT effect:**
   - Collect results from papers across many SE tasks
   - Re-run all algorithms on all tasks
   - Scott-Knott: most algorithms land in the same group
   - Conclusion: *algorithm choice matters less than
     data quality and problem formulation*

**Implications for how you do research:**

```
1. Always run the simple baseline first.
2. If simple wins → publish that (important result!).
3. If complex wins → dig into WHY (generalization story).
4. Never apologize for a simple method that works.
```

**The positive spin:**
Simple methods that work are *deployable*. Practitioners
actually use them. A 50-label active learner that runs in
seconds beats a GP surrogate that runs in hours — even if
the GP is technically better.

> "A method that people use beats a method that people ignore."

---

## Lecture Wrap-Up

### What We Covered

```
Classic applications   → test gen, repair, refactoring, planning
Active learning        → surrogates, BO, 50-label rule
Empirical rigor        → Wilcoxon + A₁₂ + Scott-Knott + baselines
Modern topics          → LLM operators, fairness MOO, energy
Simple wins            → the uncomfortable empirical truth
```

### The Through-Line

Every piece of SBSE requires you to answer three questions:

1. **What am I optimizing?** (fitness / objective design)
2. **How do I know it worked?** (statistical rigor + baselines)
3. **Is the complexity justified?** (simple baseline first)

Get those right and the algorithm choice is secondary.

---

## Discussion Questions

1. Pick one SE application. Propose a fitness function.
   What are the construct validity threats?

2. You have a budget of 50 evaluations to tune a build
   system with 30 boolean flags. Which surrogate and
   acquisition function would you use, and why?

3. A paper claims their new GA beats NSGA-II on 8/10
   benchmarks (p < 0.05 each). What questions do you ask
   before believing it?

4. An LLM-based repair tool fixes 40% of bugs in a
   benchmark. A random single-edit tool fixes 35%.
   Is the LLM tool worth deploying? What else do you need?

5. "Simple methods win because SE datasets are too small
   to reveal real differences." Argue for and against.

---

## References

### Foundations & Statistical Methods

Arcuri, A., & Briand, L. (2011). A practical guide for
  using statistical tests to assess randomized algorithms
  in software engineering. In *Proc. ICSE 2011*,
  pp. 1–10. IEEE. https://doi.org/10.1145/1985793.1985795

Harman, M., & Jones, B. F. (2001). Search-based software
  engineering. *Information and Software Technology*,
  43(14), 833–839.
  https://doi.org/10.1016/S0950-5849(01)00189-6

Vargha, A., & Delaney, H. D. (2000). A critique and
  improvement of the CL common language effect size
  statistics of McGraw and Wong. *Journal of Educational
  and Behavioral Statistics*, 25(2), 101–132.
  https://doi.org/10.3102/10769986025002101

Kruskal, W. H., & Wallis, W. A. (1952). Use of ranks in
  one-criterion variance analysis. *Journal of the American
  Statistical Association*, 47(260), 583–621.
  https://doi.org/10.1080/01621459.1952.10483441

Wolpert, D. H., & Macready, W. G. (1997). No free lunch
  theorems for optimization. *IEEE Transactions on
  Evolutionary Computation*, 1(1), 67–82.
  https://doi.org/10.1109/4235.585893

---

### Test Generation & Fuzzing

Fraser, G., & Arcuri, A. (2011). EvoSuite: Automatic test
  suite generation for object-oriented software. In
  *Proc. FSE 2011*, pp. 416–419. ACM.
  https://doi.org/10.1145/2025113.2025179

McMinn, P. (2004). Search-based software test data
  generation: A survey. *Software Testing, Verification
  and Reliability*, 14(2), 105–156.
  https://doi.org/10.1002/stvr.294

Zalewski, M. (2015). American Fuzzy Lop (AFL).
  https://lcamtuf.coredump.cx/afl/

Böhme, M., Pham, V.-T., & Roychoudhury, A. (2017).
  Coverage-based greybox fuzzing as Markov chain. In
  *Proc. CCS 2016*, pp. 1032–1043. ACM.
  https://doi.org/10.1145/2976749.2978428

---

### Bug Repair & Fault Localization

Le Goues, C., Nguyen, T., Forrest, S., & Weimer, W.
  (2012). GenProg: A generic method for automated software
  repair. *IEEE Transactions on Software Engineering*,
  38(1), 54–72. https://doi.org/10.1109/TSE.2011.104

Qi, Y., Mao, X., Lei, Y., Dai, Z., & Wang, C. (2014).
  The strength of random search on automated program
  repair. In *Proc. ICSE 2014*, pp. 254–265. ACM.
  https://doi.org/10.1145/2568225.2568254

Jones, J. A., & Harrold, M. J. (2005). Empirical
  evaluation of the Tarantula automatic fault-localization
  technique. In *Proc. ASE 2005*, pp. 273–282. IEEE.
  https://doi.org/10.1145/1101908.1101949

Abreu, R., Zoeteweij, P., Golsteijn, R., & van Gemund,
  A. J. C. (2009). A practical evaluation of spectrum-
  based fault localization. *Journal of Systems and
  Software*, 82(11), 1780–1792.
  https://doi.org/10.1016/j.jss.2009.06.035

---

### Refactoring & Architecture

Harman, M., Mansouri, S. A., & Zhang, Y. (2012).
  Search-based software engineering: Trends, techniques
  and applications. *ACM Computing Surveys*, 45(1), 11.
  https://doi.org/10.1145/2379776.2379787

O'Keeffe, M., & Ó Cinnéide, M. (2008). Search-based
  refactoring for software maintenance. *Journal of
  Systems and Software*, 81(4), 502–516.
  https://doi.org/10.1016/j.jss.2007.06.003

Mitchell, B. S., & Mancoridis, S. (2006). On the
  automatic modularization of software systems using the
  bunch tool. *IEEE Transactions on Software Engineering*,
  32(3), 193–208. https://doi.org/10.1109/TSE.2006.26

---

### Release Planning & Requirements

Bagnall, A. J., Rayward-Smith, V. J., & Whittley, I. M.
  (2001). The next release problem. *Information and
  Software Technology*, 43(14), 883–890.
  https://doi.org/10.1016/S0950-5849(01)00194-X

Ngo, M. N., Asadi, S., & Ruhe, G. (2008). Optimized
  software release planning with soft and hard dependency
  requirements. In *Proc. SEKE 2008*, pp. 407–412.

Zhang, Y., Harman, M., & Mansouri, S. A. (2007). The
  multi-objective next release problem. In *Proc. GECCO
  2007*, pp. 1129–1137. ACM.
  https://doi.org/10.1145/1276958.1277179

---

### Configuration Tuning

Nair, V., Menzies, T., Siegmund, N., & Apel, S. (2018).
  Finding faster configurations using FLASH. *IEEE
  Transactions on Software Engineering*, 46(7), 794–811.
  https://doi.org/10.1109/TSE.2018.2870895

Hutter, F., Hoos, H. H., & Leyton-Brown, K. (2011).
  Sequential model-based optimization for general
  algorithm configuration. In *Proc. LION 2011*,
  pp. 507–523. Springer.
  https://doi.org/10.1007/978-3-642-25566-3_40

Aken, D. V., Pavlo, A., Gordon, G. J., & Zhang, B.
  (2017). Automatic database management system tuning
  through large-scale machine learning. In *Proc.
  SIGMOD 2017*, pp. 1009–1024. ACM.
  https://doi.org/10.1145/3035918.3064029

Cooper, K. D., Subramanian, D., & Torczon, L. (2002).
  Adaptive optimizing compilers for the 21st century.
  *Journal of Supercomputing*, 23(1), 7–22.
  https://doi.org/10.1023/A:1015729001611

---

### Test Suite Optimization

Rothermel, G., Untch, R. H., Chu, C., & Harrold, M. J.
  (2001). Prioritizing test cases for regression testing.
  *IEEE Transactions on Software Engineering*, 27(10),
  929–948. https://doi.org/10.1109/32.962562

Elbaum, S., Malishevsky, A. G., & Rothermel, G. (2002).
  Test case prioritization: A family of empirical studies.
  *IEEE Transactions on Software Engineering*, 28(2),
  159–182. https://doi.org/10.1109/32.988497

Haghighatkhah, A., Mäntylä, M., Oivo, M., & Kuvaja, P.
  (2018). Test prioritization in continuous integration
  environments. *Journal of Systems and Software*, 146,
  80–98. https://doi.org/10.1016/j.jss.2018.08.061

---

### Effort Estimation & Scheduling

Lokan, C., & Mendes, E. (2009). Applying moving windows
  to software effort estimation. In *Proc. ESEM 2009*,
  pp. 351–362. IEEE.
  https://doi.org/10.1109/ESEM.2009.5316010

Alba, E., & Chicano, J. F. (2007). Software project
  management with GAs. *Information Sciences*, 177(11),
  2380–2401.
  https://doi.org/10.1016/j.ins.2006.12.020

---

### Bayesian Optimization & Surrogates

Snoek, J., Larochelle, H., & Adams, R. P. (2012).
  Practical Bayesian optimization of machine learning
  algorithms. In *Proc. NeurIPS 2012*, pp. 2951–2959.
  https://arxiv.org/abs/1206.2944

Srinivas, N., Krause, A., Kakade, S., & Seeger, M.
  (2010). Gaussian process optimization in the bandit
  setting: No regret and experimental design. In
  *Proc. ICML 2010*, pp. 1015–1022.
  https://arxiv.org/abs/0912.3995

Jones, D. R., Schonlau, M., & Welch, W. J. (1998).
  Efficient global optimization of expensive black-box
  functions. *Journal of Global Optimization*, 13(4),
  455–492. https://doi.org/10.1023/A:1008306431147

Mockus, J., Tiesis, V., & Zilinskas, A. (1978). The
  application of Bayesian methods for seeking the
  extremum. In L. C. W. Dixon & G. P. Szegö (Eds.),
  *Towards Global Optimization* (Vol. 2, pp. 117–129).
  North-Holland.

Falkner, S., Klein, A., & Hutter, F. (2018). BOHB:
  Robust and efficient hyperparameter optimization at
  scale. In *Proc. ICML 2018*, pp. 1437–1446.
  https://arxiv.org/abs/1807.01774

---

### Active Learning

Settles, B. (2012). *Active Learning*. Synthesis Lectures
  on Artificial Intelligence and Machine Learning.
  Morgan & Claypool.
  https://doi.org/10.2200/S00429ED1V01Y201207AIM018

Yu, Z., Kraft, N. A., & Menzies, T. (2019). Finding
  better active learners for faster literature reviews.
  *Empirical Software Engineering*, 24(6), 3348–3379.
  https://doi.org/10.1007/s10664-019-09729-6

Cohn, D. A., Ghahramani, Z., & Jordan, M. I. (1996).
  Active learning with statistical models. *Journal of
  Artificial Intelligence Research*, 4, 129–145.
  https://doi.org/10.1613/jair.295

---

### Empirical Rigor

Arcuri, A., & Briand, L. (2014). A hitchhiker's guide
  to statistical tests for assessing randomized
  algorithms in software engineering. *Software Testing,
  Verification and Reliability*, 24(3), 219–250.
  https://doi.org/10.1002/stvr.1486

Kitchenham, B., Pfleeger, S., Pickard, L., Jones, P.,
  Hoaglin, D., El Emam, K., & Rosenberg, J. (2002).
  Preliminary guidelines for empirical research in
  software engineering. *IEEE Transactions on Software
  Engineering*, 28(8), 721–734.
  https://doi.org/10.1109/TSE.2002.1027796

Wohlin, C., Runeson, P., Höst, M., Ohlsson, M. C.,
  Regnell, B., & Wesslén, A. (2012). *Experimentation
  in Software Engineering*. Springer.
  https://doi.org/10.1007/978-3-642-29044-2

Scott, A. J., & Knott, M. (1974). A cluster analysis
  method for grouping means in the analysis of variance.
  *Biometrics*, 30(3), 507–512.
  https://doi.org/10.2307/2529204

---

### Simple Wins / MOOT

Menzies, T., Kocaguneli, E., Turhan, B., Minku, L., &
  Peters, F. (2015). *Sharing Data and Models in Software
  Engineering*. Morgan Kaufmann.

Fu, W., & Menzies, T. (2017). Easy over hard: A case
  study on deep learning. In *Proc. FSE 2017*,
  pp. 49–60. ACM.
  https://doi.org/10.1145/3106237.3106256

Tantithamthavorn, C., McIntosh, S., Hassan, A. E., &
  Matsumoto, K. (2016). Automated parameter optimization
  of classification techniques for defect prediction
  models. In *Proc. ICSE 2016*, pp. 321–332.
  https://doi.org/10.1145/2884781.2884857

Agrawal, A., & Menzies, T. (2019). "Better data" is
  better than "better data miners." In *Proc. ICSE 2019*,
  pp. 1050–1061. IEEE.
  https://doi.org/10.1109/ICSE.2019.00107

---

### LLMs & Modern Topics

Romera-Paredes, B., Barekatain, M., Novikov, A., et al.
  (2024). Mathematical discoveries from program search
  with large language models. *Nature*, 625, 468–475.
  https://doi.org/10.1038/s41586-023-06924-6

Li, R., Allal, L. B., Zi, Y., et al. (2023).
  StarCoder: May the source be with you!
  https://arxiv.org/abs/2305.06161

Wei, J., Wang, X., Schuurmans, D., et al. (2022).
  Chain-of-thought prompting elicits reasoning in large
  language models. In *Proc. NeurIPS 2022*.
  https://arxiv.org/abs/2201.11903

---

### Fairness & Energy

Galhotra, S., Brun, Y., & Meliou, A. (2017). Fairness
  testing: Testing software for discrimination. In
  *Proc. FSE 2017*, pp. 498–510. ACM.
  https://doi.org/10.1145/3106237.3106277

Cruz, L., & Abreu, R. (2019). Catalog of energy patterns
  for mobile applications. *Empirical Software
  Engineering*, 24(4), 2209–2235.
  https://doi.org/10.1007/s10664-019-09682-4

Couto, M., Carção, T., Cunha, J., Fernandes, J. P., &
  Saraiva, J. (2017). Towards a green ranking for
  programming languages. In *Proc. SBLP 2017*,
  pp. 26–40. Springer.
  https://doi.org/10.1007/978-3-319-70082-1_2


*85-char width · CSC 591 SBSE · NC State*
