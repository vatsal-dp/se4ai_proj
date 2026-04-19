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


# K-Means and K-Means++

---

## 1. The Core Idea

K-means partitions rows into k groups such that each row
belongs to the group whose centre is closest to it. "Centre"
means the representative row of that group — its `mid()`.

The algorithm alternates two steps until nothing changes:

1. **Assign** every row to its nearest centroid.
2. **Update** each centroid to be the mid of its assigned
   rows.

That is the whole algorithm. Here it is in code:

```python
def kmeans(d:Data, rows=None, k=10, n=10, cents=None):
  rows  = rows or d.rows
  cents = cents or choices(rows, k=k)   # random start
  for _ in range(n):
    kids = [Data([d.cols.names]) for _ in cents]
    err  = 0
    for r in rows:
      i    = min(range(len(cents)),
                 key=lambda j: d.distx(cents[j], r))
      err += d.distx(cents[i], r)
      kids[i].add(r)
    yield err/len(rows), kids
    cents = [choice(c.rows) for c in kids if c.rows]
```

Walk through each part:

- `cents = cents or choices(rows, k=k)` — pick k random
  rows as starting centroids (overrideable, used by k-means++
  later).
- Inner loop assigns each row `r` to the nearest centroid
  index `i`, accumulates distance error, and adds the row
  to that centroid's `Data` bucket.
- `yield err/len(rows), kids` — returns the average
  per-row error and the k sub-datasets. Because it is a
  generator, the caller controls convergence.
- `cents = [choice(c.rows) for c in kids if c.rows]` —
  new centroids are a random row from each bucket (not the
  mean, since `Data` uses medians and `choice` samples from
  the stored reservoir).

**Try this:** run it on a CSV and watch the error fall:

```bash
./kmeans_class.py --data path/to/diabetes.csv
```

```
err=0.412
err=0.387
err=0.371
err=0.371    ← converged (change ≤ 0.01)
```

---

## 2. Why Random Starts Fail

Random initialisation has a serious flaw: if you happen to
place two centroids in the same dense region, one cluster
will "own" half of a natural group while the other cluster
sits uselessly nearby. The remaining natural groups get
split across the leftover centroids.

This is not rare. With k=10 and random starts, poor
initialisations happen often enough to matter. The clusters
you get depend heavily on the random seed.

**Try this:** run vanilla k-means 20 times and look at the
spread of final errors. Large variance = bad seed
sensitivity.

```python
errs = []
for _ in range(20):
    last = 1e32
    for err, _ in kmeans(d):
        if abs(last - err) <= 0.01: break
        last = err
    errs.append(int(100 * err))
print(sorted(errs))
# [31, 31, 33, 35, 35, 37, 39, 41, 41, 44, ...]
#  ↑ wide spread = seed-sensitive
```

---

## 3. K-Means++ Seeding

K-means++ (Arthur & Vassilvitskii, 2007) fixes this with a
smarter initialisation. Instead of picking k random rows,
it picks rows that are spread far apart:

1. Pick the **first centroid** uniformly at random.
2. For each remaining centroid, pick a new row with
   probability proportional to its **squared distance to
   the nearest centroid already chosen**.

Rows far from any existing centroid are more likely to be
picked next. This pushes centroids apart by construction,
covering the space rather than clumping.

```python
def kpp(d:Data, rows=None, k=10, few=256):
  rows = rows or d.rows
  out  = [choice(rows)]                 # step 1: random first
  while len(out) < k:
    tmp  = sample(rows, min(few, len(rows)))   # subsample
    out += [tmp[pick({i: min(d.distx(r,c)**2  # step 2: weighted
                      for c in out)
                      for i,r in enumerate(tmp)})]]
  return out
```

Key details:

- `out = [choice(rows)]` — first centroid is uniform random.
- `sample(rows, min(few, len(rows)))` — we don't score every
  row; we draw a random subset of size `few=256`. This keeps
  the seeding fast even on large datasets.
- `min(d.distx(r,c)**2 for c in out)` — for each candidate
  row `r`, compute its squared distance to the **nearest**
  centroid already chosen.
- `pick({i: dist² ...})` — `pick` does a weighted random
  draw proportional to the distances. High distance = high
  probability of being selected next.

Then `kmeansp` just passes these seeds into the standard
`kmeans` loop:

```python
def kmeansp(data, k=10, **kw):
  return kmeans(data, k=k, cents=kpp(data, k=k), **kw)
```

Same loop, better start.

---

## 4. Does It Help? (The Comparison)

```python
def eg__data(f:filename):
  d0   = Data(csv(f))
  seen = {kmeans: [], kmeansp: []}
  for _ in range(20):
    d1 = Data([d0.cols.names] + shuffle(d0.rows)[:50])
    for algo in seen:
      last = 1e32
      for err,_ in algo(d1):
        if abs(last - err) <= 0.01: break
        last = err
      seen[algo] += [int(100*err)]
  for algo, errs in seen.items():
    says(sorted(errs) + [sum(errs)/len(errs), algo.__name__], w=3)
```

This runs both algorithms 20 times on random 50-row
subsamples and prints sorted final errors plus the mean.
Typical output:

```bash
▶ ./cluster.py --data ~/gits/moot/optimize/misc/auto93.csv
  8  10  11  11  11  11  11  11  11  12  12  12  12  12  12  13  13  13  13  14 11.65 kmeans
  6   6   8   8   8   8   8   8   8   8   9   9   9   9   9  10  10  10  11  12 8.70 kmeansp
```

K-means++ consistently gets lower error and has a tighter
spread — fewer bad runs. The subsample size (`[:50]`) keeps
both fast while making seed quality easy to see.

**Try this:** change the subsample size from 50 to 200.
Does k-means++ still win? Does the gap shrink?

**Try this:** change `few=256` in `kpp` to `few=10`. Watch
the seed quality degrade. At what value of `few` does
k-means++ stop outperforming random starts?

---

## 5. Beyond Clustering: Classification and Regression

K-means is often presented as an unsupervised method, but
the cluster structure it finds can drive both supervised
tasks.

### Classification

Once you have k clusters, label each cluster by the
majority class of its training rows. To classify a new row:
find its nearest centroid, return that centroid's label.

```python
# after kmeans converges, kids = [Data, Data, ...]
labels = {i: max(set(r[-1] for r in k.rows),
                 key=lambda v: sum(r[-1]==v for r in k.rows))
          for i, k in enumerate(kids)}

def classify(new_row):
    i = min(range(len(cents)),
            key=lambda j: d.distx(cents[j], new_row))
    return labels[i]
```

This is essentially a 1-nearest-centroid classifier. It is
fast at prediction time (k distance computations instead of
n), and the clusters naturally summarise the training data.

### Regression

For a numeric target, replace majority vote with the median
of the target column in each cluster:

```python
medians = {i: k.cols.y[target_col].mid()
           for i, k in enumerate(kids)}

def predict(new_row):
    i = min(range(len(cents)),
            key=lambda j: d.distx(cents[j], new_row))
    return medians[i]
```

The model is a piecewise-constant approximation of the
target surface: k flat regions, each with its own median
prediction.

**Why this matters:** both supervised tasks inherit k-means'
speed and incrementality. You can re-cluster as new data
arrives and update centroid labels/medians in O(k) time.

---

## 6. Convergence and Stopping

The `kmeans` generator yields after every iteration. The
caller decides when to stop. The standard criterion is
plateau detection:

```python
last = 1e32
for err, kids in kmeans(d):
    if abs(last - err) <= 0.01: break
    last = err
```

`abs(last - err) <= 0.01` stops when improvement drops
below 1%. Other options:

- Fixed iterations: `for err, kids in kmeans(d, n=5)` —
  just let the loop run out.
- Relative improvement: `if (last-err)/last < 0.001: break`
- Hard limit + plateau: use both, stop on whichever comes
  first.

K-means is guaranteed to converge (error never increases),
but not to a global optimum. It finds a local minimum that
depends on initialisation — which is exactly why k-means++
seeding matters.

---

## 7. Summary

| Concept        | Detail                                          |
|----------------|-------------------------------------------------|
| Assign step    | each row → nearest centroid by `distx`          |
| Update step    | centroid ← `choice` from bucket rows            |
| Error          | mean per-row distance to assigned centroid      |
| Convergence    | stop when `abs(last - err) <= threshold`        |
| Random start   | fast but seed-sensitive, high variance          |
| k-means++ seed | weighted draw by squared distance, low variance |
| Classification | label each centroid by majority class           |
| Regression     | predict each centroid by target column median   |

K-means is small code with wide applicability. K-means++
makes it reliable. Together they are a strong first tool
before reaching for anything more complex.

---

## 8. Lab Exercises

### A: Watch convergence

```bash
./kmeans_class.py --data path/to/diabetes.csv
```

How many iterations before convergence? Rerun with a
different seed (`-s 42`). Does it take more or fewer
iterations?

### B: Seed sensitivity

Edit `kmeans_class.py`: replace `choices(rows, k=k)` with
a fixed bad seed — pick 10 rows from only the first quarter
of the data. How does final error change?

### C: k-means++ subsample size

In `cluster.py`, change `few=256` to `few=5`, `few=20`,
`few=100`. Run `eg__data` each time. At what value does
k-means++ stop beating random initialisation?

### D: Classification with clusters

After `kmeans` converges, `kids` is a list of `Data`
objects. Pick the class column from each kid's rows and
find the majority label. How does centroid-based
classification compare to the Bayes classifier from
`bayes_class.py` on the same dataset?

### E: Vary k

Change `k=10` to `k=3`, `k=20`, `k=50` in the comparison
run. How does the gap between k-means and k-means++ change
as k grows? Why would larger k make seeding matter more?
