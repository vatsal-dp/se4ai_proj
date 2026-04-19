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

# Theoretical Foundations for ezr.py and sa.py

This document explains the statistical, algorithmic, and software engineering concepts underlying `ezr.py` (a lightweight data mining toolkit) and `sa.py` (a simulated annealing optimizer). 

---

## 1. Incremental Statistics

### The Problem with Batch Statistics

Computing mean and standard deviation typically requires two passes over data:

```
μ = (1/n) Σ xᵢ           # first pass: compute mean
σ = √[(1/n) Σ (xᵢ - μ)²]  # second pass: compute variance
```

This is impractical for streaming data or when memory is constrained.

### Welford's Online Algorithm

Welford (1962) discovered a numerically stable single-pass algorithm. The key insight is maintaining running values that update incrementally:

```python
def add(i, v):
  # ...
  if "mu" in i:  # Num column
    d = v - i.mu
    i.mu += d / i.n
    i.m2 += d * (v - i.mu)  # Note: uses NEW i.mu
  # ...
```

The algorithm maintains:
- `i.mu`: running mean
- `i.m2`: sum of squared deviations from the current mean

**Why two different `d` values?** The line `i.m2 += d * (v - i.mu)` uses `d` (computed with the *old* mean) multiplied by the deviation from the *new* mean. This algebraic trick maintains the correct sum of squared deviations.

Standard deviation is then:

```python
def sd(i): return 0 if i.n < 2 else sqrt(i.m2 / (i.n - 1))
```

The `n-1` denominator is Bessel's correction for sample standard deviation (unbiased estimator).

---

## 2. Entropy and Information Theory

For symbolic (categorical) data, we measure "spread" using Shannon entropy:

```python
def ent(i):    
  return -sum(p*log(p,2) for n in i.has.values() if (p := n/i.n) > 0)
```

**Interpretation:** Entropy measures the average "surprise" or information content. Given a distribution over symbols:

- If one symbol dominates (p ≈ 1), entropy → 0 (no surprise)
- If all symbols equally likely, entropy is maximized (maximum uncertainty)

For k equally-likely symbols: H = log₂(k) bits.

**Example:** For `"aaaabbc"`:
- P(a) = 4/7, P(b) = 2/7, P(c) = 1/7
- H = -(4/7)log₂(4/7) - (2/7)log₂(2/7) - (1/7)log₂(1/7) ≈ 1.38 bits

---

## 3. Generating Gaussian Random Numbers

The code uses a clever approximation based on the Central Limit Theorem:

```python
def gauss(mu, sd1):
  return mu + 2 * sd1 * (sum(random.random() for _ in range(3)) - 1.5)
```

**How it works:**

1. `random.random()` returns Uniform(0,1) with mean=0.5, variance=1/12
2. Sum of 3 uniforms has mean=1.5, variance=3/12=0.25, sd=0.5
3. Subtracting 1.5 centers at zero
4. Multiplying by 2 scales sd from 0.5 to 1.0
5. Final scaling by `sd1` and shifting by `mu` gives N(mu, sd1²)

**Why only 3 samples?** The CLT converges quickly for uniform distributions. Three samples gives adequate approximation for most purposes, and it's fast.

---

## 4. Normalization Techniques

### Z-Score (Standard Score)

The z-score expresses how many standard deviations a value lies from the mean:

```python
def z(i, v): return (v - i.mu) / (sd(i) + 1/BIG)
```

The `1/BIG` prevents division by zero when sd=0.

**Properties:**
- z = 0 at the mean
- z = 1 means one standard deviation above mean
- Approximately 68% of data falls within z ∈ [-1, 1]
- Approximately 95% within z ∈ [-2, 2]

### Sigmoid Normalization

Raw z-scores are unbounded. The sigmoid function maps them to (0, 1):

```python
def norm(z): return 1 / (1 + exp(-1.7 * max(-3, min(3, z))))
```

This is a modified logistic function:

```
norm(z) = 1 / (1 + e^(-1.7z))
```

**Design choices:**

1. **Clamping to [-3, 3]:** Values beyond ±3 standard deviations are extreme outliers (~0.3% of normal data). Clamping prevents numerical overflow and reduces outlier influence.

2. **The 1.7 coefficient:** Standard logistic uses coefficient 1.0, giving norm(±3) ≈ {0.05, 0.95}. The 1.7 stretches the sigmoid so that ±3σ maps closer to {0, 1}, using more of the output range.

```
z     | norm(z) with 1.7
------+-----------------
-3    | 0.006
-1    | 0.154
 0    | 0.500
+1    | 0.846
+3    | 0.994
```

---

## 5. Distance Metrics

### Minkowski Distance

The generalized Minkowski distance between points x and y:

```
d(x,y) = (Σ |xᵢ - yᵢ|^p)^(1/p)
```

The code computes the *averaged* Minkowski distance:

```python
def minkowski(src):
  n, d = 0, 0
  for v in src: n, d = n + 1, d + v ** the.p
  return 0 if n == 0 else (d / n) ** (1 / the.p)
```

**Special cases:**
- p = 1: Manhattan distance (city-block)
- p = 2: Euclidean distance (default)
- p → ∞: Chebyshev distance (maximum coordinate difference)

**Why average?** Dividing by n makes the distance independent of dimensionality, allowing fair comparison across datasets with different numbers of features.

### Heterogeneous Distance (aha function)

Real datasets mix numeric and symbolic attributes. The `aha` function (named after David Aha's instance-based learning work) handles both:

```python
def aha(i, u, v):
  if u == v == "?": return 1           # both unknown: maximum distance
  if "has" in i: return u != v         # symbolic: 0 if same, 1 if different
  u = "?" if u == "?" else norm(z(i, u))
  v = "?" if v == "?" else norm(z(i, v))
  u = u if u != "?" else (0 if v > 0.5 else 1)  # unknown: assume worst case
  v = v if v != "?" else (0 if u > 0.5 else 1)
  return abs(u - v)                    # numeric: absolute difference
```

**Key design decisions:**

1. **Symbolic attributes:** Binary distance (0 or 1). This is the "overlap metric."

2. **Numeric attributes:** Normalized then differenced. Since both values are in [0,1], the distance is also in [0,1].

3. **Missing values:** Assume the worst case. If one value is known and > 0.5 (high), assume the unknown is 0 (low), maximizing distance. This is conservative—we don't pretend to know what we don't.

### Distance in X-space vs Y-space

The code separates:

- **distx:** Distance using independent variables (features/predictors)
- **disty:** Distance using dependent variables (goals/targets)

```python
def disty(i, row):
  return minkowski(norm(z(c, row[c.at])) - c.goal for c in i.cols.y)

def distx(i, row1, row2):
  return minkowski(aha(c, row1[c.at], row2[c.at]) for c in i.cols.x)
```

---

## 6. Multi-Objective Optimization

### Goal Encoding

Column names encode optimization direction:
- Suffix `+` or no suffix: maximize (goal = True = 1)
- Suffix `-`: minimize (goal = False = 0)

```python
def Num(n=0, s=" "): return Obj(at=n, txt=s, n=0, mu=0, m2=0, goal=s[-1]!="-")
```

### Scalarization via Distance-to-Heaven

Multi-objective optimization typically produces a Pareto frontier. For simplicity, we scalarize: combine multiple objectives into one number.

```python
def disty(i, row):
  return minkowski(norm(z(c, row[c.at])) - c.goal for c in i.cols.y)
```

**Interpretation:** Each objective is normalized to [0,1]. The "heaven point" is where all goals are achieved:
- For maximization goals: heaven = 1
- For minimization goals: heaven = 0

The `disty` function computes distance from this heaven point. **Lower is better.**

**Example:** For columns `[Weight-, Mpg+]`:
- A car with low weight (normalized to 0.2) and high mpg (normalized to 0.8)
- Goals: [0, 1] (minimize weight, maximize mpg)
- Distances from goals: |0.2 - 0| = 0.2, |0.8 - 1| = 0.2
- disty = √((0.2² + 0.2²)/2) ≈ 0.2

---

## 7. Simulated Annealing

Simulated annealing (Kirkpatrick et al., 1983) is a probabilistic optimization algorithm inspired by metallurgical annealing—slowly cooling metal to reduce defects.

### Core Idea

SA explores a solution space by:
1. Starting from a random solution
2. Repeatedly generating "neighbor" solutions via small mutations
3. Always accepting better solutions
4. Sometimes accepting worse solutions (to escape local optima)
5. Gradually reducing the probability of accepting worse solutions

<img src="https://upload.wikimedia.org/wikipedia/commons/d/d5/Hill_Climbing_with_Simulated_Annealing.gif">

### The Metropolis-Hastings Criterion

The key insight is the acceptance probability for worse solutions:

```
P(accept) = exp((current_energy - new_energy) / temperature)
```

Where:
- **Energy** = solution quality (lower is better, like `disty`)
- **Temperature** = starts high, decreases over time

**Behavior:**

| Condition | Result |
|-----------|--------|
| New solution is better | Always accept (probability > 1) |
| New solution is worse, high temperature | Often accept (explore) |
| New solution is worse, low temperature | Rarely accept (exploit) |

**Intuition:** Early on (high temperature), we explore freely, accepting worse solutions to escape local optima. Later (low temperature), we become greedy, only accepting improvements.

### Temperature Schedule

A simple linear cooling schedule:

```
T = 1 - (iteration / max_iterations)
```

- Starts at T = 1 (hot, exploratory)
- Ends at T → 0 (cold, greedy)

### Mutation Operators

To generate neighbor solutions, we mutate the current solution:

**Symbolic attributes:** Sample from the observed distribution. If a column has seen {red: 10, blue: 5, green: 2}, sample proportionally.

**Numeric attributes:** Add Gaussian noise centered at current value. The standard deviation of the column is a natural scale for "small" mutations. Use modulo arithmetic to keep values within observed bounds [LO, HI].

### Mutation Rate

Rather than mutating all features, mutate a random subset (e.g., 50%). This balances:
- Too few mutations → slow exploration
- Too many mutations → essentially random restart

---

## 8. Surrogate Modeling

### The Expensive Evaluation Problem

In many optimization scenarios, evaluating a solution's true quality is expensive (physical experiments, simulations, human evaluation). A **surrogate model** provides a cheap approximation.

### Nearest Neighbor as Surrogate

The simplest surrogate: find the most similar known solution and assume similar quality.

1. Given a candidate solution (with unknown Y-values)
2. Find its nearest neighbor in X-space (feature space)
3. Copy that neighbor's Y-values to the candidate
4. Compute quality from the borrowed Y-values

**Assumption:** Similar inputs produce similar outputs (smoothness/continuity). This is the foundation of instance-based learning.

**Trade-off:** The surrogate is only as good as the training data. Predictions in unexplored regions are unreliable—but SA's acceptance criterion will eventually reject poor solutions.

---

## 9. Python Implementation Patterns

### Duck Typing for Polymorphism

Instead of class hierarchies, we use structural typing:

```python
if "mu" in i:   # it's a Num
if "has" in i:  # it's a Sym  
if "rows" in i: # it's a Data
```

**Advantages:**
- No inheritance complexity
- Objects are just dictionaries with conventions
- Easy serialization (dicts are JSON-compatible)

### The Obj Class

```python
class Obj(dict):
  __getattr__, __setattr__, __repr__ = dict.__getitem__, dict.__setitem__, o
```

This one-liner creates a dict subclass where:
- `obj.x` is equivalent to `obj["x"]` (attribute access)
- `obj.x = v` is equivalent to `obj["x"] = v` (attribute assignment)
- `repr(obj)` uses our custom `o()` pretty-printer

### Factory Functions vs Classes

```python
def Num(n=0, s=" "): return Obj(at=n, txt=s, n=0, mu=0, m2=0, goal=s[-1]!="-")
```

Factory functions (capitalized by convention) return configured Obj instances. This is simpler than full classes when:
- No method inheritance needed
- Behavior is in standalone functions
- Objects are primarily data containers

### The `i` Convention

Throughout the code, `i` refers to "this instance"—the object being operated on:

```python
def add(i, v):    # add v to instance i
def mid(i):       # get midpoint of instance i
def sd(i):        # get standard deviation of instance i
```

This is a deliberate choice to avoid `self` outside of class definitions, keeping the functional style while maintaining clarity about which object is being modified.

---

## 10. Useful Functions in ezr.py

For your implementation, these functions are available:

| Function | Purpose |
|----------|---------|
| `nearest(data, row, rows)` | Find closest row to `row` in `rows` using X-distance |
| `distx(data, row1, row2)` | Distance between two rows in feature space |
| `disty(data, row)` | Distance from row to "heaven" (lower = better) |
| `gauss(mu, sd)` | Generate Gaussian random number |
| `sd(col)` | Standard deviation of a Num column |
| `pick(d, n)` | Weighted random selection from dict `d` with total count `n` |

---

## References

- Welford, B.P. (1962). ["Note on a method for calculating corrected sums of squares and products."](https://www.scribd.com/document/972081339/Welford-1962-Note-on-a-Method-for-Calculating-Corrected-Sums-of-Squares-and-Products) *Technometrics*,
  4(3), 419–420. 
- Shannon, C.E. (1948). ["A Mathematical Theory of Communication."](https://monoskop.org/images/b/be/Shannon_Claude_E_Weaver_Warren_The_Mathematical_Theory_of_Communication_1963.pdf) *Bell System Technical Journal*.
  Vol. 27, pp. 379–423, 623–656, July, October, 1948.
- Kirkpatrick, S., Gelatt, C.D., Vecchi, M.P. (1983). ["Optimization by Simulated Annealing."](https://www2.stat.duke.edu/~scs/Courses/Stat376/Papers/TemperAnneal/KirkpatrickAnnealScience1983.pdf).
  Science, 13 May 1983, Vol 220, Issue 4598, pp. 671-680, DOI: 10.1126/science.220.4598.671
- Aha, D.W., Kibler, D., Albert, M.K. (1991). ["Instance-Based Learning Algorithms."](https://www.cs.put.poznan.pl/mkomosinski/lectures/ML/Aha_IBL_1991.pdf) *Machine Learning*,  6, 37-66 (1991)
