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



# AI Search Tools for Software Engineering

> *"All models are wrong. Some are useful."* — Box  
> *"All optimizers are slow. Some are cheap."* — Menzies

This lecture is based on the code:

- [oneplus1/ez2.py](oneplus1/ez2.py)
- [oneplus1/locals.py](oneplus1/locals.py)
- [oneplus1/sa.py](oneplus1/sa.py)

---

## 1. The Setup: Search as Walking a Space

A **candidate solution** is just a row — a list of values, one per column:

```python
s = choice(d.rows)[:]   # pick a random row, copy it
```

**Decision space** = all possible rows (the Xs).  
**Objective space** = the quality of those rows (the Ys).

We never see the full space. We get a **budget** of `b` evaluations:

```python
def oneplus1(d, mutator, accept, b=1000, restart=0):
    h, best, best_e = 0, None, 1E32
    while True:
        if h >= b: return          # <-- the hard stop
```

Everything that follows is about spending that budget wisely.

---

## 2. Energy: Mapping a Row to a Scalar

To compare candidates we need one number. That number is **energy**:
distance from the current row to "heaven" — the ideal Y values.

```python
def disty(d:Data, r:Row) -> float:
    return minkowski(
        (norm(y, r[y.at]) - y.goal) for y in d.cols.y)
```

- `norm` maps each Y to [0,1]  
- `y.goal` is 1 (maximize) or 0 (minimize), set from the column name  
- `minkowski` aggregates: `(Σ dᵢᵖ / n)^(1/p)`

Lower energy = closer to heaven. Search = minimize energy.

Not for now, but there are are other measures

<img width="954" height="357" alt="image" src="https://github.com/user-attachments/assets/5cb89aa2-7306-42da-b415-90e7174737d4" />


---

## 3. The Cheap Oracle Trick

Real SE data has **no Y labels**. Measuring a row's true Y is expensive
(run the build, run the tests, measure the system). So we cheat:

```python
def score(r):
    near = nearest(d, r, d.rows)   # find closest labeled row
    for y in d.cols.y:
        r[y.at] = near[y.at]       # borrow its Y values
    return disty(d, r)
```

This is **lazy Y-value imputation** — borrow from the nearest neighbor
instead of evaluating from scratch. It is fast and surprisingly accurate
when the space is smooth.

---

## 4. The 1+1 Loop

The simplest search: one current solution, one candidate. Keep the better.

```python
# inside oneplus1:
for sn in mutator(s):        # generate one (or more) candidates
    h += 1
    en = score(sn)
    if accept(e, en, h, b):  # should we move?
        s, e = sn, e
    if en < best_e:           # track the global best separately
        best, best_e = sn[:], en
        yield h, best_e, best
```

`accept` is the **only thing that differs** between algorithms. Everything
else — the loop, the budget, the restart logic — lives in `oneplus1`.

This is the **strategy pattern** in functional style: pass behavior in,
share structure.

---

## 5. Hill Climbing (Local Search)

Accept only if strictly better. Simple. Fast. Gets stuck.

```python
# ls in locals.py
def accept(e, en, *_):
    return en < e
```

The `*_` discards `h` and `b` — hill climbing does not need them.

**Neighborhood design matters.** `ls` offers two neighborhood widths:

```python
def mutate(s):
    x = choice(list(d.cols.x))          # pick one feature
    for _ in range(n if rand() < p else 1):
        sn = s[:]; sn[x.at] = nearby(x, sn[x.at]); yield sn
```

With probability `p`, take `n` steps along the same axis (deep probe).  
Otherwise, take one step (wide probe).  
This is **variable neighborhood search** — vary the neighborhood to
escape shallow local optima.

---

## 6. Simulated Annealing

Accept worse solutions early; tighten as budget runs out.  
The key is the **Boltzmann acceptance criterion**:

```
P(accept worse) = exp((e - en) / T)
```

where temperature `T` decreases as evaluations increase.  
In `sa.py`, the cooling schedule is embedded directly:

```python
def accept(e, en, h, b):
    return en < e or rand() < exp((e - en) / (1 - h/b))
```

`1 - h/b` starts near 1.0 (hot, permissive) and falls toward 0 (cold,
strict). As `h → b`, the exponent blows up and acceptance probability
collapses to 0. SA becomes hill climbing at the end of its budget.

SA also mutates **multiple features at once**:

```python
def mutate(s):
    sn = s[:]
    for x in choices(list(d.cols.x), k=max(1, int(m*len(d.cols.x)))):
        sn[x.at] = nearby(x, sn[x.at])
    yield sn
```

`m=0.5` means mutate half the features per step. Larger jumps, more
exploration — appropriate when temperature is high.

---

## 7. Restarts: Escaping Local Optima

Both algorithms share the same restart logic in `oneplus1`:

```python
if restart and h - last_improvement > restart:
    s, e, last_improvement = choice(d.rows)[:], 1E32, 0
    break
```

If no improvement in `restart` evaluations, abandon the current basin
and jump to a new random starting point. Reset `e` to `1E32` so the
new trajectory is judged on its own merits.

This is cheap because `choice(d.rows)` is O(1) — we always have a
pool of labeled rows to restart from.

---

## 8. The 2×2 Experiment

`locals.py` sets up a **factorial comparison**:

```
                restarts=0      restarts=100
accept=better   lsRminus        ls
accept=Boltzmann saRplus(!)      sa
```

Twenty runs. Each run: shuffle, subsample 50 rows, run all four algos,
record `100*e` (energy as a percentage).

```python
seen = {sa:[], ls:[], lsRminus:[], saRplus:[]}
for _ in range(20):
    d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
    for algo in [sa, ls, lsRminus, saRplus]:
        seen[algo] += [100*e]

for algo, lst in seen.items():
    says(sorted(map(int, lst)) + [algo.__name__], 3)
```

The sorted output shows the **distribution** of outcomes, not just the
mean. A low median with a high max is a different story than a tight
cluster. Read the tails.

**The theoretical tension:** SA's probabilistic acceptance should
escape local optima better — but restarts may dominate that effect
at small budgets. Measure; do not assume.

---

## 9. The Big Picture

```
         NEIGHBORHOOD         ACCEPTANCE
         ──────────────────── ────────────────────
ls       variable-width (p,n) strict hill-climb
sa       multi-feature (m)    Boltzmann + cooling

         RESTART              BUDGET
         ──────────────────── ────────────────────
lsRminus none                 b=1000
saRplus  every 100 no-improve b=1000
```

All four share one engine (`oneplus1`), one energy function (`disty`),
one oracle trick (borrow Y from nearest neighbor). The differences
are **two lambdas**: `mutate` and `accept`.

That is the design lesson: separate the search strategy from the
search infrastructure. The infrastructure is boring and correct.
The strategy is where science happens.

---

---

# Appendix: Python Idioms for Newcomers

The code uses several Python features that are idiomatic but may be
unfamiliar. Here is a quick tour with examples taken directly from
the codebase.

---

### A1. Walrus Operator `:=`

Assigns a value **and** uses it in the same expression.

```python
# ent() in ez2.py
return -sum(p*log(p,2) for n in sym.has.values()
            if (p := n/sym.n) > 0)
```

`p := n/sym.n` computes the probability, binds it to `p`, and the
`if` tests it — all in one pass. Without walrus you'd need a
separate list comprehension or loop.

---

### A2. Generator Expressions

Like list comprehensions, but **lazy** — values are produced on demand,
not all at once. Passed directly to functions that consume iterables.

```python
# likes() in ez2.py
likelihoods = (like(x, v, prior)
               for x in d.cols.x if (v := row[x.at]) != "?")
return log(prior) + sum(map(log, likelihoods))
```

`sum()` pulls one value at a time. Nothing is stored. This matters
when rows are wide.

---

### A3. `yield` and Generators

A function with `yield` is a **generator** — it returns an iterator,
not a value. Callers pull items one at a time with `for`.

```python
# sa.py: mutate yields one candidate
def mutate(s):
    sn = s[:]
    for x in choices(list(d.cols.x), k=max(1, int(m*len(d.cols.x)))):
        sn[x.at] = nearby(x, sn[x.at])
    yield sn          # <-- one candidate per call

# oneplus1 pulls from it:
for sn in mutator(s):
    h += 1; en = score(sn)
```

`oneplus1` also yields — so `sa(d1)` is itself a generator:

```python
for h, e, row in sa(d1):   # pull results one improvement at a time
    says([h, e] + row, w=8)
```

---

### A4. `s[:]` — Shallow Copy

`sn = s` gives you an alias. `sn = s[:]` gives you a **copy**.
Mutating `sn` does not change `s`.

```python
s, e = sn, e       # BUG WAITING: if sn is s, both change together
sn = s[:]          # SAFE: sn is a fresh list with the same values
```

This appears everywhere a candidate is generated from the current
solution.

---

### A5. `dict` Subclass as Object (`O`)

The entire data model is built on one trick:

```python
class O(dict):
    __getattr__, __setattr__ = dict.__getitem__, dict.__setitem__
```

`o.x` and `o["x"]` do the same thing. You get dot notation for free,
plus all dict methods (`keys()`, `items()`, `get()`). No `__init__`
boilerplate per class.

---

### A6. `or` as a Default

```python
this = this or Num()           # if this is None/falsy, make a Num
n = c.has.get(v, 0) or 0      # get returns 0 if missing; or keeps it
```

Idiomatic for optional arguments and missing-key defaults. Watch out:
`0 or default` returns `default`, so do not use this when `0` is a
valid non-default value.

---

### A7. Annotations as Metadata, Not Types

Python does not enforce type annotations. `ez2.py` uses them to drive
the command-line dispatcher:

```python
def eg_s(n:int): the.seed=n; random.seed(n)

# main() reads them:
f(*[make(args.pop(0)) for make in f.__annotations__.values()])
```

`f.__annotations__` is `{'n': int}`. `main` pops the next CLI arg,
casts it with `int`, and passes it. The annotation is a **cast
instruction**, not a type check.

---

### A8. Docstring as Config

```python
"""
Options:
  -b bins=7
  -k k=1
  ...
"""
the = O(**{k: cast(v)
           for k,v in re.findall(r"(\S+)=(\S+)", __doc__)})
```

`re.findall` extracts every `name=value` pair from the module
docstring. One regex replaces an entire argparse setup. Change a
default by editing the docstring. The config and its documentation
are the same string.

---

### A9. `choice` vs `choices`

```python
choice(d.rows)           # one item, no replacement
choices(d.cols.x, k=3)  # list of 3, WITH replacement
```

`choices` (plural) is the multi-sample version. Used in `sa.mutate`
to pick `k` features to mutate in one step. `k` is computed
dynamically: `max(1, int(m * len(d.cols.x)))`.

---

### A10. Chained Clamp

```python
def z(num, v):
    return max(-3, min(3, (v - num.mu) / (sd(num) + 1/BIG)))
```

`min(3, x)` caps at 3. `max(-3, ...)` floors at -3. Together they
clamp to [-3, 3]. The `+ 1/BIG` in the denominator prevents
division by zero without an `if` branch.

