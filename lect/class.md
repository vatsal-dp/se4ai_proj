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
<h1 align="center">:cyclone: CSC491/591 (013): Software Engineering and AI
<br>NC State, Spring '26</h1>
<img src="https://raw.githubusercontent.com/txt/seai26spr/main/docs/lect/banner.png">


# Naive Bayes: Why "Naive" is Actually Genius

---

## 1. Why Bother? (10 min)

Before we look at the algorithm, let us ask why anyone would
use it in 2026 when we have neural networks and gradient
boosting.

**Speed.** Training means reading each row once and updating
a counter or a sorted list. No matrix inversion, no gradient
descent, no epochs. Classification means one pass over the
columns.

**Memory.** You never store the rows. You store only summary
statistics — a frequency dictionary per symbolic column, a
sorted sample per numeric column. The model size is
proportional to the number of features, not the number of
training examples.

**Incrementality.** You can add a new row in O(1) time, and
— unusually — you can also *remove* a row in O(1) time. This
matters when data expires or when you want a sliding window
over a stream.

**Missing data.** If a value is `"?"`, you just skip that
column's contribution to the likelihood. No imputation, no
crash.

**Surprisingly competitive.** Domingos & Pazzani (1997)
compared NB against other learners (C4.5, PEBLS, and CN2) on 28 UCI
datasets[^dom]. NB won more often than any of them, including
domains with strong attribute dependencies.

[^dom]: Domingos, Pedro, and Michael Pazzani. "On the Optimality of the Simple Bayesian Classifier under Zero-One Loss." Machine Learning, vol. 29, no. 2-3, 1997, pp. 103-130.

We will come back to *why* it works so well at the end.
First, let us build it from scratch.

---

## 2. The Core Idea: Ranking, Not Probabilities  

Bayes' theorem:

```
P(class | row) = P(class) × P(row | class) / P(row)
```

- **Prior** `P(class)`: how common is this class in training?
- **Likelihood** `P(row | class)`: how plausible is this row
  if we already know the class?
- **Posterior** `P(class | row)`: updated belief after seeing
  the row.

The key insight: we never need the actual posterior value. We
only need to know *which class wins*. The denominator
`P(row)` is the same for every class — it cancels. So we
just compare:

```
P(yes) × P(row | yes)   vs   P(no) × P(row | no)
```

The class with the bigger product wins. That is it. NB is
not a probability estimator — it is a *ranker*.

This distinction matters. As Domingos & Pazzani show, NB's
probability estimates are often badly wrong, but its
*rankings* are correct far more often than you would expect.

**Why "Naive"?** We assume all features are independent given
the class:

```
P(row | class) = P(f1 | class) × P(f2 | class) × ...
```

This is almost never true. Weather features are correlated.
Words in a document are correlated. But NB still works — we
will prove why in Section 14.

---

## 3. The Zero Problem and Smoothing  

Suppose we are computing:

```
P(outlook=sunny | yes) × P(windy=true | yes) × ...
```

If `sunny` never appeared in any `yes` row in training, that
term is 0. Zero times anything is zero. The entire product
collapses, and we lose all information from every other
feature. One unseen value nukes the whole row.

**The fix: Laplace smoothing.** Add a small pseudocount to
every frequency before computing the ratio. We use two
smoothing parameters:

- `k` — smooths attribute frequencies (avoids zero when a
  value was never seen for a given class)
- `m` — smooths class priors (avoids zero for rare classes)

The formulas are:

```
P(value | class) = (count + k × prior) / (n_class + k)

P(class)         = (n_class + m) / (n_all + m × n_h)
```

where `n_h` is the number of distinct classes. With `k=1`
and `m=2` (the defaults in `ez_class.py`), no probability
is ever exactly zero, and the estimates are pulled only
gently toward the prior.

---

## 4. Avoiding Underflow: Log Space 

With many features, we multiply many small numbers together.
On a machine with 64-bit floats, the product quickly rounds
to zero even when the true value is not zero. This is called
**floating-point underflow**.

The fix: take the log of everything. The log of a product
is a sum of logs:

```
log(P(class) × P(f1|class) × P(f2|class) × ...)
= log P(class) + log P(f1|class) + log P(f2|class) + ...
```

Sums do not underflow. We compare log-posteriors, and the
class with the least-negative sum wins. We never convert
back to actual probabilities.

```python
# from ez_class.py
def like(i, row:Row, n_all:int, n_h:int) -> float:
    prior = (len(i.rows)+the.m) / (n_all+the.m*n_h)
    ls = [c.like(v,prior) for at,c in i.cols.x.items()
          if (v:=row[at])!="?"]
    return log(prior) + sum(log(v) for v in ls if v>0)
```

`"?" → skip`. `v > 0 → skip` catches any residual zeros.
The result is a single float, the log-posterior. The class
with the highest (least negative) value is predicted.

---

## 5. The Delegation Protocol  

`ez_class.py` has three classes that work together:
`Sym`, `Num`, and `Data`. The design pattern is
**delegation**: `Data.like` does not compute likelihoods
itself. It asks each column object for its own likelihood.

```
Data.like(row)
  → for each column c and value v:
      c.like(v, prior)      ← Sym or Num handles this
  → sum the logs
  → return log-posterior
```

### Sym (symbolic columns)

`Sym` is just a `dict` mapping values to counts.

```python
class Sym(dict):
    def add(i, v:Val) -> Val:
        if v != "?": i[v] = i.get(v,0) + 1
        return v

    def sub(i, v:Val) -> Val:
        if v != "?": i[v] = i.get(v,0) - 1
        return v

    def like(i, v:Val, prior:float=0) -> float:
        n = sum(i.values())
        return max(1/BIG, (i.get(v,0) + the.k*prior) / (n + the.k))
```

`add` and `sub` each touch one dictionary entry — O(1).
`like` applies the Laplace formula. `max(1/BIG, ...)` is
a belt-and-suspenders guard against zero.

### Num (numeric columns)

`Num` is a sorted list (via `insort`) that keeps a random
reservoir of at most `the.Keep` values.

```python
class Num(list):
    def add(i, v:Val) -> Val:
        if v != "?":
            i.seen += 1
            if len(i) < i.mx: insort(i, v)
            elif r() < i.mx/i.seen:
                i.pop(int(r()*len(i))); insort(i, v)
        return v

    def sub(i, v:Val) -> Val:
        if v != "?":
            i.seen -= 1
            if (p:=bisect_left(i,v)) < len(i) and i[p]==v:
                i.pop(p)
        return v
```

The reservoir sampling in `add` keeps the list bounded while
maintaining a representative sample. `sub` is an exact
deletion using binary search — O(log n).

For likelihoods, `Num` assumes a Gaussian distribution
parameterised by **median** and **spread**:

```python
    def mid(i) -> float: return i[len(i)//2] if i else 0

    def spread(i) -> float:
        if len(i) < 2: return 0
        n = max(1, len(i)//10)
        a, b = min(9*n, len(i)-1), min(n, len(i)-1)
        return (i[a]-i[b])/2.56

    def like(i, v:Qty, prior:float=0) -> float:
        s = i.spread() + 1/BIG
        return (1/sqrt(2*pi*s*s)) * exp(-((v-i.mid())**2)/(2*s*s))
```

Median is more robust than mean to outliers. The spread
`(90th percentile − 10th percentile) / 2.56` estimates the
standard deviation without being thrown off by extreme
values (2.56 = distance between the 10th and 90th
percentiles of a standard normal).

### Data (the container)

`Data` holds a list of rows and a `Cols` object that maps
column indices to `Sym` or `Num` instances. Column type
is decided by the **name**: uppercase first letter → `Num`,
lowercase → `Sym`.

```python
class Data:
    def add(i, row:Row) -> Row:
        i._mid = None
        for at,c in i.cols.all.items(): c.add(row[at])
        i.rows.append(row)
        return row

    def sub(i, row:Row) -> Row:
        i._mid = None
        for at,c in i.cols.all.items(): c.sub(row[at])
        i.rows.remove(row)
        return row

    def like(i, row:Row, n_all:int, n_h:int) -> float:
        prior = (len(i.rows)+the.m) / (n_all+the.m*n_h)
        ls = [c.like(v,prior) for at,c in i.cols.x.items()
              if (v:=row[at])!="?"]
        return log(prior) + sum(log(v) for v in ls if v>0)
```

`i.cols.x` contains only the input columns (not the class
label, not columns suffixed `X`). So the class column never
contributes to its own likelihood calculation.

**Try it yourself:**

```python
from ez_class import Data, csv
d = Data(csv("weather.csv"))
for row in d.rows:
    print(row, d.like(row, len(d.rows), 2))

['sunny', 85, 85, 0, 'no'] -12.37
['sunny', 80, 90, 1, 'no'] -9.39
['overcast', 83, 86, 0, 'yes'] -10.99
['rainy', 70, 96, 0, 'yes'] -7.95
['rainy', 68, 80, 0, 'yes'] -7.56
['rainy', 65, 70, 1, 'no'] -10.54
['overcast', 64, 65, 1, 'yes'] -12.65
['sunny', 72, 95, 0, 'no'] -7.65
['sunny', 69, 70, 0, 'yes'] -8.97
['overcast', 75, 90, 1, 'no'] -7.48
```

Rows that are typical of the dataset get higher (less
negative) log-likelihoods.

---

## 6. Incremental Speed: add and sub  

One of NB's underappreciated strengths is that you can add
*and remove* rows without retraining from scratch. This
matters for:

- **Streaming data**: the model grows with new observations.
- **Sliding windows**: old data expires and is removed.
- **Cross-validation**: hold out a fold by subtracting it,
  evaluate, then add it back.

Watch how `mid()` stays consistent as rows are deleted and
re-added:

```python
# from eg__addsub in ez_class.py
d1 = Data([d.cols.names] + d.rows[:the.Keep])
rows = d1.rows[:]
m1 = d1.mid()

for row in rows[::-1]:      # delete all rows
    d1.sub(row)

for row in rows:            # add them back
    d1.add(row)

m2 = d1.mid()
assert m1 == m2             # identical: order doesn't matter
```

**Try it yourself:**

```bash
./ez_class.py --addsub path/to/diabetes.csv
```

Watch the midpoints at 1/3 and 2/3 capacity match whether
you build the dataset by deleting or by adding. This is the
O(1) update guarantee in action.

---

## 7. Full Example: Classifying Weather Data  

### The data

```
outlook   temp  humidity  windy  play
sunny      85      85     false   no
sunny      80      90     true    no
overcast   83      86     false   yes
rainy      70      96     false   yes
rainy      68      80     false   yes
rainy      65      70     true    no
overcast   64      65     true    yes
sunny      72      95     false   no
sunny      69      70     false   yes
overcast   75      90     true    no
```

5 yes rows, 5 no rows, n=10.

### Step 1: Priors (m=2, n_h=2)

```
P(yes) = (5+2)/(10+2×2) = 7/14 = 0.500
P(no)  = (5+2)/(10+2×2) = 7/14 = 0.500
```

Equal counts → equal priors. The features will do the work.

### Step 2: Frequency tables

```
outlook:  sunny  overcast  rainy     windy:  false  true
  yes       1       2        2          yes    4      1
  no        3       1        1          no     2      3

temp (sorted):
  yes: [64,68,69,70,83]  median=69  spread=5.86
  no:  [65,72,75,80,85]  median=75  spread=5.08

humidity (sorted):
  yes: [65,70,80,86,96]  median=80  spread=10.16
  no:  [70,85,90,90,95]  median=90  spread=3.91
```

### Step 3: Classify `sunny, temp=72, humidity=90, windy=true`

**Log-posterior for yes** (prior=0.500):

```
outlook=sunny:  (1 + 1×0.5) / (5+1) = 1.5/6  = 0.250
windy=true:     (1 + 1×0.5) / (5+1) = 1.5/6  = 0.250
temp=72:        Gauss(72; μ=69, σ=5.86)        = 0.060
humidity=90:    Gauss(90; μ=80, σ=10.16)       = 0.024

log(0.500) + log(0.250) + log(0.250) + log(0.060) + log(0.024)
= -0.693   + -1.386    + -1.386    + -2.818    + -3.722
= -10.005
```

**Log-posterior for no** (prior=0.500):

```
outlook=sunny:  (3 + 1×0.5) / (5+1) = 3.5/6  = 0.583
windy=true:     (3 + 1×0.5) / (5+1) = 3.5/6  = 0.583
temp=72:        Gauss(72; μ=75, σ=5.08)        = 0.066
humidity=90:    Gauss(90; μ=90, σ=3.91)        = 0.102

log(0.500) + log(0.583) + log(0.583) + log(0.066) + log(0.102)
= -0.693   + -0.539    + -0.539    + -2.717    + -2.281
= -6.769
```

**Decision: no** (−6.769 > −10.005)

The decisive features were `outlook` and `windy`: sunny
appears 3× in no rows vs 1× in yes rows, and true wind
follows the same pattern. Together they outweigh everything
else.

---

## 8. The Full Classifier: bayes_class.py  

```python
def nbayes(src:Iterable, warmup:int=10) -> Confuse:
    rows = iter(src)
    d    = Data([next(rows)])
    every, ks, cf = Data([d.cols.names]), {}, Confuse()

    def best(k):
        return ks[k].like(r, len(every.rows), len(ks))

    for r in rows:
        k = r[d.cols.klass]
        if k not in ks: ks[k] = Data([d.cols.names])
        if len(every.rows) >= warmup:
            confuse(cf, str(k), str(max(ks, key=best)))
        ks[k].add(every.add(r))
    return cf
```

Walk through each line:

- `d = Data([next(rows)])` — reads the header row to learn
  column names and types.
- `every` — a `Data` holding all rows regardless of class,
  used for `n_all` in the prior formula.
- `ks` — a dict mapping each class label to its own `Data`
  holding only that class's rows.
- `warmup` — we wait for 10 rows before predicting. With
  fewer rows the frequency tables are too sparse to trust.
- `max(ks, key=best)` — calls `like` on each class-specific
  `Data`, returns the class with the highest log-posterior.
- `confuse(cf, str(k), str(...))` — records want vs got in
  the confusion matrix (see next section).
- `ks[k].add(every.add(r))` — the row goes into `every`
  and into its class-specific `Data`. The model learns
  *after* predicting, so we never cheat by training on test
  data.

This is a true online learner. Every row is classified using
only what came before it, then immediately incorporated into
the model.

Running on two real datasets:

```
▶ ./bayes_class.py --data ~/gits/moot/classify/diabetes.csv
          label,   n,  pd,  pf, prec, acc
tested_positive, 262,  74,  32,   55,  70
tested_negative, 496,  67,  25,   83,  70
       _OVERALL, 758,  70,  29,   70,  70

▶ ./bayes_class.py --data ~/gits/moot/classify/soybean.csv
                      label,   n,  pd, pf, prec, acc
           herbicide-injury,   8,  75,  0,   85,  99
      diaporthe-stem-canker,  10, 100,  0,   76,  99
              cyst-nematode,  14,  85,  0,  100,  99
diaporthe-pod-&-stem-blight,  15,  80,  0,  100,  99
               2-4-d-injury,  16,  50,  0,  100,  98
               charcoal-rot,  20,  95,  0,   79,  99
       rhizoctonia-root-rot,  20,  95,  0,   86,  99
             powdery-mildew,  20,  85,  0,   85,  99
               downy-mildew,  20,  95,  0,   90,  99
           bacterial-blight,  20,  65,  0,   68,  98
          bacterial-pustule,  20,  80,  0,   80,  98
          purple-seed-stain,  20,  80,  0,   94,  99
     phyllosticta-leaf-spot,  20,  45,  0,   81,  98
             brown-stem-rot,  44,  93,  0,   91,  98
                anthracnose,  44,  93,  0,   89,  98
           phytophthora-rot,  88,  96,  1,   93,  98
        alternarialeaf-spot,  91,  87,  3,   77,  94
         frog-eye-leaf-spot,  91,  70,  0,   95,  95
                 brown-spot,  92,  92,  5,   73,  94
                   _OVERALL, 673,  84,  0,   84,  98
```

But what do `pd`, `pf`, `prec`, `acc` actually mean?
That is what the next three sections explain.

---

## 9. The Confusion Matrix (2-class case)  

Given true class (want) and predicted class (got), we tally
four cells. Using the A/B/C/D notation from Menzies et al.
"Problems with Precision" (TSE 2007)[^me07]:

[^me07]: Problems with Precision: A Response to "Comments on 'Data Mining Static Code Attributes to Learn Defect Predictors'"
Menzies, Tim; Dekhtyar, Alex; Distefano, Justin; Greenwald, Jeremy.  IEEE Transactions on Software Engineering; New York Vol. 33, Iss. 9,  (Sep 2007): 637. DOI:10.1109/TSE.2007.70721

```
              Predicted
              yes      no
Actual  yes   D=TP     B=FN
        no    C=FP     A=TN
```

Four standard measures:

```
pd   = recall      = D / (B+D)       # of actual yes, how many caught?
pf   = false alarm = C / (A+C)       # of actual no, how many flagged?
prec = precision   = D / (D+C)       # of flagged, how many are real?
acc  = accuracy    = (A+D)/(A+B+C+D)
```

### Worked example

100 rows: 20 actually defective (pos), 80 not (neg).
Classifier finds 15 TP, 5 FN, 10 FP, 70 TN:

```
A=70   B=5   C=10   D=15

pd   = 15 / (5+15)    = 15/20  = 75%
pf   = 10 / (10+70)   = 10/80  = 13%
prec = 15 / (15+10)   = 15/25  = 60%
acc  = (70+15) / 100  = 85/100 = 85%
```

A useful reality check: a classifier that flags *everything*
gets pd=100% but pf=100%. One that flags *nothing* gets
pf=0% but pd=0%. Useful classifiers live in the middle.

---

## 10. The 3-Class Case  

With 3 classes (A, B, C), we generate *three separate*
binary confusion matrices using a **one-vs-rest** strategy.

For class X: label each row as `X` or `not-X`, compute
A, B, C, D as before, derive pd/pf/prec/acc independently.

### Example: 90 rows across 3 classes

Predictions yield:

```
Class A: TP=28, FN=2,  FP=8,  TN=52
Class B: TP=21, FN=9,  FP=4,  TN=56
Class C: TP=18, FN=6,  FP=3,  TN=63
```

For class A:

```
pd   = 28/(2+28)   = 93%
pf   =  8/(8+52)   = 13%
prec = 28/(28+8)   = 78%
acc  = (28+52)/90  = 89%
```

For class B:

```
pd   = 21/(9+21)   = 70%
pf   =  4/(4+56)   =  7%
prec = 21/(21+4)   = 84%
acc  = (21+56)/90  = 86%
```

For class C:

```
pd   = 18/(6+18)   = 75%
pf   =  3/(3+63)   =  5%
prec = 18/(18+3)   = 86%
acc  = (18+63)/90  = 90%
```

The `_OVERALL` row sums all TP, FP, FN, TN across classes
before recomputing the rates — as `stats.py` does.

---

## 11. How stats.py Tracks A/B/C/D Incrementally  

```python
def confuse(cf:Confuse, want:str, got:str) -> str:
    for x in (want, got):
        if x not in cf.klasses:
            cf.klasses[x] = o(label=x, tn=cf.total,
                               fn=0, fp=0, tp=0)
    for c in cf.klasses.values():
        if c.label == want:
            c.tp += got == want
            c.fn += got != want
        else:
            c.fp += got == c.label
            c.tn += got != c.label
    cf.total += 1
    return got
```

Key points:

- A new class is initialized with `tn=cf.total`: all rows
  seen so far that didn't mention this class count as true
  negatives — one-vs-rest applied retroactively in one line.
- Each call loops over **all known classes**, updating every
  one. This is how one-vs-rest is done incrementally with
  no row storage.
- `c.fp += got == c.label` catches cases where the
  classifier wrongly predicted *this* class for a row that
  was not it.

Then `confused()` derives the rates:

```python
c.pd, c.prec, c.pf, c.acc = (
    p(c.tp, c.tp+c.fn),  p(c.tp, c.fp+c.tp),
    p(c.fp, c.fp+c.tn),  p(c.tp+c.tn, c.tp+c.fp+c.fn+c.tn))
```

And `bayes_class.py` feeds it row by row:

```python
if len(every.rows) >= warmup:
    confuse(cf, str(k), str(max(ks, key=best)))
ks[k].add(every.add(r))
```

The `warmup` period lets the Bayes models accumulate enough
data before their predictions are scored.

---

## 12. The Problem with Precision 

From Menzies et al. "Problems with Precision" (TSE 2007)[^[me07],
the key equation derived from the Zhangs' formula is:

```
prec = 1 / (1 + (neg/pos) × pf/recall)
```

Rearranged:

```
pf = (pos/neg) × ((1 - prec)/prec) × recall
```

**Precision is not a free parameter.** Given a fixed
dataset — fixed neg/pos ratio — fixing recall and pf
*determines* precision. You cannot independently tune all
four measures. They are connected through the structure of
the data.

### Consequences for SE data

SE datasets often have very large neg/pos ratios. The paper
studied datasets with neg/pos of 1.04, 7.33, 9, 10.11,
13.29, 15.67, and 249. At high neg/pos, achieving high
precision requires pf to be vanishingly small — almost
never achievable in practice.

This explains why **precision is unstable** across datasets.
At very small pf values, tiny changes in pf cause huge
swings in prec (sudden jumps from 0 to 1). All other
measures — pd, pf, acc — vary far more smoothly. Precision
is a derived consequence of the data's neg/pos ratio, not
something a learner controls.

Practical advice: prefer pd and pf as evaluation measures.
They are stable. Precision is not.

### When low precision is still useful

- When missing a target is very costly (safety, security):
  aim for pd=100%, accept low precision.
- When false alarm inspection is cheap (search-style tools):
  users scan a few false alarms without minding.
- When selectivity is small: only a small fraction of data
  is returned, so even imprecise detectors surface real
  issues.

---

## 13. Eight Evaluation Criteria (§5.9) (10 min)

From Shrikanth & Menzies "Early Bird" (arXiv 2105.11082).
No single measure tells the whole story, and the measures
can contradict each other by design.

### Recall (pd) — maximize

```
Recall = TP / (TP + FN)
```

Of all actual defects, how many did we find? Trivially
maxed at 100% by flagging everything — but then PF=100%.

### False Positive Rate (PF) — minimize

```
PF = FP / (FP + TN)
```

Of all clean commits, how many did we wrongly flag? Trivially
zeroed by flagging nothing — but then Recall=0%.

### AUC — maximize

Area under the ROC curve (PF on x-axis, Recall on y-axis).
Threshold-free summary: 1.0 is perfect, 0.5 is random.

### D2H (Distance to Heaven) — minimize

"Heaven" is Recall=1, PF=0. D2H measures how far we are:

```
D2H = sqrt( (1-Recall)^2 + (0-PF)^2 ) / sqrt(2)
```

Aggregates both goals into one number, normalized to [0,1].

### G-Measure (GM) — maximize

Harmonic mean of Recall and specificity (1-PF):

```
GM = 2 × Recall × (1-PF) / (Recall + (1-PF))
```

GM and D2H combine the same two quantities differently.
Good GM does not guarantee good D2H, and vice versa.

### Brier Score — minimize

Mean squared error between actual outcome y ∈ {0,1} and
predicted probability p:

```
Brier = (1/n) × Σ (y_i - p_i)²
```

Penalizes confident wrong predictions most heavily. Note
that Brier and Recall are antithetical: minimizing loss can
actually lower recall.

### IFA (Initial False Alarms) — minimize

Commits are sorted by predicted defect probability. IFA
counts the false alarms encountered before the *first* real
defect is found. Based on Parnin & Orso's finding that
developers lose trust in analytics after many early false
alarms.

### MCC (Matthews Correlation Coefficient) — maximize

Uses all four cells of the confusion matrix:

```
MCC = (TP×TN - FP×FN)
      / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))
```

Returns [-1, +1]. Unlike accuracy, MCC is fair on heavily
imbalanced data. The paper uses it as a substitute for
precision/F-measure, which are unreliable on SE datasets.

### Summary table

| Measure | Direction | What it captures              |
|---------|-----------|-------------------------------|
| Recall  | maximize  | coverage of actual defects    |
| PF      | minimize  | false alarm burden             |
| AUC     | maximize  | threshold-free ROC summary    |
| D2H     | minimize  | distance from ideal (0,1)     |
| GM      | maximize  | recall + specificity balance  |
| Brier   | minimize  | probability calibration       |
| IFA     | minimize  | early false alarm trust       |
| MCC     | maximize  | balanced confusion summary    |

The paper deliberately **excludes precision**: "Prior work
has shown that precision has significant issues for
unbalanced data. We do not include that in our evaluation."
MCC draws from all four corners of the confusion matrix
without precision's instability — that is why it is there.

---

## 14. Why It Works: The Optimality Result (10 min)

Domingos & Pazzani (1997) ask: when is NB *optimal* even
when its independence assumption is false?[^dom]

**Zero-one loss** means we only care whether the predicted
class is correct or not. We don't care how wrong the
probability estimate is, as long as the right class wins.

**Theorem 1**: NB is optimal under zero-one loss for a
given example if and only if

```
(p ≥ ½  and  r ≥ s)   or   (p ≤ ½  and  r ≤ s)
```

where `p = P(+ | example)` is the true class probability,
`r = P(+) ∏ P(Aj | +)` is NB's discriminant for `+`,
and `s` is the same for `−`.

**Corollary 1**: This condition holds over exactly *half
the volume* of all possible (p, r, s) combinations. The
independence assumption is needed only on a second-order
infinitesimal fraction of that space. NB's true region of
optimality is vastly larger than previously thought.

Put plainly: NB only needs to get the *sign* right, not
the *magnitude*. Even if its probability estimates are
badly wrong, it picks the correct class as long as the
ranking is preserved.

**Conjunctions and disjunctions** (Theorems 7 & 8): NB is
provably globally optimal for learning conjunctive and
disjunctive concepts — even though these concepts
decisively violate the independence assumption.

**Small sample advantage**: Because NB has low variance
(O(features) parameters, not O(rows)), it often outperforms
C4.5 on datasets with fewer than ~1000 rows even when
C4.5's learning bias is more appropriate. At small sample
sizes, variance dominates bias, and NB wins.

---

## 15. When NB Struggles, and Fixes (10 min)

NB's independence assumption creates two systematic biases
that Rennie et al. (ICML 2003)[^ren03] identified for text
classification. Both have simple fixes.

[^ren03]: Jason D. M. Rennie, Lawrence Shih, Jaime Teevan, David R. Karger:
Tackling the Poor Assumptions of Naive Bayes Text Classifiers. ICML 2003: 616-623

### Problem 1: Skewed training data

If class A has 1000 training examples and class B has 10,
NB will produce weight estimates for class B that are
systematically too low (because log is concave and
E[log x] < log E[x] for small samples). The classifier
then unfairly prefers class A.

**Fix: Complement Naive Bayes (CNB)**. Estimate weights for
class C using all examples *not* in class C:

```
             N_{ci_complement} + α
θ̂_complement = ──────────────────────────
             N_{c_complement} + α × vocab
```

Each class now uses a roughly equal amount of training data
for its estimates. CNB's weights are more stable across
varying dataset sizes (see Rennie et al. Figure 1).

### Problem 2: Word dependencies inflate magnitudes

When two words always appear together ("San" and
"Francisco"), NB double-counts their evidence. The weight
vector for the dependent class grows artificially large,
biasing predictions toward it.

**Fix: Weight normalization**. Divide each weight by the
L1 norm of that class's weight vector:

```
              log P(word_i | class_c)
w[c,i] = ─────────────────────────────────────
          Σ_k | log P(word_k | class_c) |
```

This keeps classes with more dependencies from dominating.

### The result

| Classifier | Industry Sector accuracy |
|------------|--------------------------|
| Plain MNB  | 58%                      |
| TWCNB      | 92%                      |
| SVM        | 93%                      |

TWCNB approaches SVM accuracy while being far faster and
easier to implement. For the full transform pipeline (log
term frequency, IDF weighting, length normalization,
complement estimation, weight normalization) see Table 4
of Rennie et al.

The key lesson: NB's failures are not fundamental — they
are correctable with simple, motivated heuristics.

---

## 16. Summary

| Property           | Why it helps                                   |
|--------------------|------------------------------------------------|
| O(1) add/sub       | streaming, expiry, cross-validation            |
| O(features) mem    | no rows stored, model stays small              |
| Handles "?"        | just skip that column's likelihood term        |
| Log space          | avoids floating-point underflow                |
| Smoothing          | avoids zero probabilities for unseen values    |
| Ranking only       | doesn't need good probability estimates to win |
| Optimal for AND/OR | works despite independence assumption failure  |
| Low variance       | beats complex models on small datasets         |
| pd/pf not prec     | stable measures; precision is data-dependent   |
| MCC over F1        | fair on imbalanced data, uses all 4 cells      |

NB is not a toy. It is the right first model to try — fast
to implement, interpretable, incremental, and surprisingly
hard to beat at small to medium dataset sizes.

---

## 17. Another Advantage of Bayes: Fast Model Update in Active Learning

So far we have seen that NB is fast to train, incremental,
and surprisingly competitive. Here is one more place where
those properties really bite: **active learning**[^sett09]

[^sett09]: Settles, Burr. "Active learning literature survey." (2009).


### The Active Learning Loop

Active learning is the problem of deciding *which* unlabelled
example to label next, given a fixed labelling budget. At
each step you:

1. Train a model on the labelled examples seen so far.
2. Score every candidate in the unlabelled pool.
3. Pick the best candidate, label it, add it to the labelled set.
4. **Rebuild the model. Repeat.**

Step 4 is where learner complexity kills you. Every iteration
adds one row and requires a fresh model.

### SMAC: Powerful but Expensive

SMAC (Sequential Model-based Algorithm Configuration)[^hutt11] is one
of the most widely used active-learning optimizers in software
configuration research. Its surrogate model is a **random
forest** of decision trees. Such trees can offer multiple gusses
on any new example. From those guesses, we can decide to sample:

[^hutt11]: Hutter, Frank, Holger H. Hoos, and Kevin Leyton-Brown. "Sequential model-based optimization for general algorithm configuration." International conference on learning and intelligent optimization. Berlin, Heidelberg: Springer Berlin Heidelberg, 2011.

- Where most of the guesses say "this is good" (certainty sampling)
- Or where the guesses most disagree (uncertainty sampling)
- Or some adaptive strategy that first explores uncertainty, then
  as more and more labelled data actually arrives, switches
  to certainty sampling.

When a new labelled example
arrives, SMAC discards the old forest and rebuilds all trees
from scratch. For N labelled examples and T trees of depth d,
that is O(T × N log N) work per acquisition step. Over a full
run of B budget steps, total model-rebuild cost is:

```
O(T × B × B × log B)   ← grows super-linearly with budget
```

Experimentally (Menzies & Ganguly 2025), running SMAC for 20
seeds across the 63 MOOT tasks takes **days**.

### EZR's `guess`: Two-Class Bayes as the Surrogate

EZR's `guess` active  learner[^gang26] replaces the forest with a two-class Naive Bayes
classifier over the BEST / REST split. Because NB's `add` and
`sub` each touch one entry in O(1), the model update after
acquiring a new row is:

[^gang26]: Ganguly, Kishan Kumar, and Tim Menzies. "How Low Can You Go? The Data-Light SE Challenge." arXiv preprint arXiv:2512.13524 (2026).

```
O(features)   ← independent of how many rows you have seen
```

Here is the entire acquisition loop from `acquire_class.py`:

```python
def guess(d, rows, Any=4, Budget=None,
          scorer=nearer, eager=True, label=lambda r:r):
  Budget = Budget or the.Budget
  rows   = shuffle(rows[:])
  unseen = clone(d, rows[Any:][:the.Few])
  seen   = clone(d, rows[:Any]).sorty()
  n      = round(sqrt(Any))
  best   = clone(d, seen.rows[:n])    # ← the BEST class
  rest   = clone(d, seen.rows[n:])    # ← the REST class
  while len(unseen.rows) > 2 and len(seen.rows) < Budget:
    seen.add(    
      best.add(  # add/sub can be nessed since they return the thing added. 
        label(
          unseen.sub(
            acquire(seen, best, rest, unseen,
                    scorer=scorer, eager=eager)))))
    if len(best.rows) > sqrt(len(seen.rows)):
      rest.add(
        best.sub(
          best.sorty().rows[-1]))     # ← demote worst BEST → REST
  return seen.sorty().rows
```

There is no "rebuild" step. `best.add(row)` updates the NB
frequency counts for the BEST class in O(features). The
BEST/REST boundary is maintained dynamically: whenever BEST
grows too large (more than √N members), the worst BEST row is
demoted to REST via `best.sub` / `rest.add` — both O(1) per
column. The entire per-step update cost is O(features),
regardless of how many rows have been labelled so far.

### The Acquisition Function: Corrected

The
actual Bayesian acquisition function in `acquire_class.py` is:

```python
def likelier(seen, best, rest, r):
    return rest.like(r, len(seen.rows), 2) \
         - best.like(r, len(seen.rows), 2)
```

Because `Data.like` returns log-posteriors (see Section 4),
this computes:

```
score(r) = log P(r | REST) − log P(r | BEST)
         = log [ P(r | REST) / P(r | BEST) ]
```

The acquisition step then picks the row that **minimises**
this score — i.e., the candidate that looks as much like BEST
as possible while looking as little like REST as possible. This
is a log-likelihood ratio: a Bayes factor between the two
classes. It needs no discretisation, no kernel, no epsilon
guard, and no rebuilding. Each call is one pass over the
columns of one row: O(features).

### Eager vs. Lazy Acquisition

`acquire_class.py` offers two modes controlled by the `eager`
flag:

```python
def acquire(seen, best, rest, unseen,
            scorer=nearer, eager=True):
  if eager:
    return min(unseen.rows,          # scan whole pool
               key=lambda r: scorer(seen, best, rest, r))
  for _ in range(len(unseen.rows)):  # random walk until
    r = choice(unseen.rows)          # first promising candidate
    if scorer(seen, best, rest, r) < 0: break
  return r
```

**Eager** mode does a full linear scan of the unlabelled pool
(O(pool × features)) and always picks the best candidate.
**Lazy** mode samples at random and stops at the first row
whose score is already negative (better than REST), saving
work when the pool is large and many good candidates exist.
Both modes share the same O(1) model-update overhead.

### Experimental Payoff

Despite replacing SMAC's ensemble with a two-class Bayes
classifier, EZR matches or beats SMAC on all 63 MOOT tasks
at every budget level (see Figure 1 of Menzies & Ganguly
2026). The performance gap closes entirely by N = 32 samples.
The computational gap does not close: the same experiment
that finishes in **minutes** for EZR takes **days** for SMAC.

This is the punchline of the "simple ain't stupid" argument.
SMAC's forest encodes rich nonlinear interactions between
features — but software's Sparsity of Influence means those
interactions don't matter. Two classes, one log-likelihood
ratio, O(1) update. That is enough.

### Updated Summary Row

Add this to the table from Section 16:

| Property              | Why it helps                                       |
|-----------------------|----------------------------------------------------|
| O(1) per-step update  | active learning stays fast at any budget size      |
| 2-class Bayes factor  | acquisition = log P(REST\|r) − log P(BEST\|r)      |
| No forest rebuild     | minutes vs. days compared with SMAC ensembles      |


---

## 18. Lab Exercises

### A: Explore the likelihood scores

```bash
./ez_class.py --like path/to/weather.csv
```

Which rows get the highest log-likelihood? Which the lowest?
What does that tell you about the "typical" row?

### B: Sensitivity to smoothing

Edit `the.k` and `the.m` in `ez_class.py`.

- Set `k=0`. What happens to `Sym.like` when it encounters
  a value it has never seen for a given class?
- Set `m=0`. What happens to the prior for a very rare class?
- Restore defaults and re-run. Do the confusion matrix
  numbers change? By how much?

### C: Change the warmup

In `bayes_class.py`, change `warmup=10` to `warmup=1`.

- Does accuracy improve or degrade on soybean?
- Now try `warmup=50`. What happens on a small dataset?
- Why does warmup exist at all?

### D: add/sub consistency check

```bash
./ez_class.py --addsub path/to/diabetes.csv
```

The assert at the end checks that midpoints after deletion
equal midpoints after insertion. Read the code. Why does
the order of deletion not matter? What would break if `sub`
decremented `seen` but did not remove the value from the
list?

### E: Precision instability

On the diabetes output (Section 8), the two classes have
neg/pos ratios of roughly 496/262 ≈ 1.9 and 262/496 ≈ 0.5.
Using the formula from Section 12:

```
prec = 1 / (1 + (neg/pos) × pf/recall)
```

Plug in the actual pd and pf values from the table. Do you
recover the reported precision values? What would prec
become if pf dropped from 32% to 5% while pd held steady?

### F: Try complement NB (advanced)

Using `ez_class.py` primitives, implement Complement NB:
for each class, build a `Data` from all rows *not* in that
class, and use its negated `like` score for classification.
Compare pd, pf, prec, acc on `diabetes.csv` against
standard NB. Does CNB help on the imbalanced class?
