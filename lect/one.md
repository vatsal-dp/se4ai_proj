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


start: hstory of science

end: list of algorothms. starting at random sarch and hillclimbing

Here is the complete **TinyTutorial** merged into a single Github Flavored Markdown document.

# TinyTutorial: Data Mining & Optimization with `xai.py`

## 1. The Core Philosophy

Data science asks two main questions:

### A. Data Mining (Structure)

* **Goal:** Find naturally occurring **groups** within data.
* **Question:** "What is similar within this group? What is different between groups?"
* **Technique:** Clustering (Unsupervised Learning).

### B. Optimization (Improvement)

* **Goal:** Find **differences** that guide us to a better state.
* **Question:** "How do I move from a heavy, low-MPG car to a lighter, high-efficiency car?"
* **Technique:** Multi-Objective Optimization (finding the Pareto Frontier).

---

## 2. The Anatomy of Data (`Sym` & `Num`)

Data is a grid of **Rows** (examples) and **Columns** (features). `xai.py` simplifies the standard "NOIR" hierarchy into two types based on column names.

### A. Symbolic Data (`Sym`)

Used for **Nominal** (Labels) and **Ordinal** (Ranked) data.

* **Detection:** Column name starts with **lowercase**.
* **Storage:** Counts frequencies in a dictionary (`has`).
* **Stats:** The `mid` is the **Mode** (most frequent value).

```python
def Sym(): return obj(it=Sym, n=0, has={})

```

### B. Numeric Data (`Num`)

Used for **Interval** (Dates) and **Ratio** (Quantities) data.

* **Detection:** Column name starts with **Uppercase**.
* **Storage:** Tracks mean (`mu`) and variance (`m2`) incrementally.
* **Stats:** The `mid` is the **Mean** (μ).

```python
def Num(): return obj(it=Num, n=0, mu=0, m2=0)

```

---

## 3. Managing Data: `Cols` & `Data`

### A. The Column Factory (`Cols`)

Organizes raw names into objects and defines roles.

* **`x` (Inputs):** Independent features (e.g., `Clndrs`).
* **`y` (Goals):** Targets to minimize (`-`) or maximize (`+`).
* **`X` (Ignored):** Columns skipped (end in `X`).

```python
def Cols(names): 
  # ... creates Col objects ...
  return obj(..., x=[...], y=[...])

```

### B. The Container (`Data`)

Holds the rows and summarizes them.

* **Logic:** The first row creates `Cols`; subsequent rows update stats via `add()`.
* **Centroids:** It calculates the "average row" (`mids`) used for clustering.

```python
def mids(data):
  data._centroid = ... [mid(col) for col in data.cols.all]
  return data._centroid

```

---

## 4. Distributions & Statistics

### A. The Normal Distribution

`Num` assumes data follows a bell curve defined by Mean (μ) and Standard Deviation (σ).

```
         Probability Density
              |
              |      _--_
              |    -      -
              |   /        \ 
              |  |    mu    |
              | * *
              |* *
        ------+-----------------------
             Low              High

```

* **Calculation:** Uses Welford's algorithm to calculate σ in one pass (streaming).

```python
def sd(num): 
  return 1/BIG + (0 if num.n<2 else sqrt(max(0,num.m2)/(num.n-1)))

```

### B. Simulation (Irwin-Hall)

To simulate Gaussian data cheaply, we sum three uniform random numbers.

```python
def gauss(mid,div):
  return mid + 2 * div * (sum(random.random() for _ in range(3)) - 1.5)

```

### C. Discretization

Continuous distributions can be noisy. We "bin" them into chunks (converting `Num` → `Ord`) using `cutsAll`. This simplifies complex curves into rules like `if x < 0.5`.

---

## 5. Distance & Normalization

### A. Normalization (`norm`)

Distance metrics fail if units differ (e.g., Weight 4000 vs MPG 20). We scale all `Num` values to `0..1` using a sigmoid-like curve.

```python
def norm(num,n):
  z = (n - num.mu) / sd(num)
  return 1 / (1 + exp(-1.7 * z))

```

### B. Input Distance (`distx`)

Used for **Clustering**. Measures how different the features (`x`) are between two rows (e.g., Row 1 vs Row 2).

* **Logic:** Euclidean distance of normalized attributes.

```python
def distx(data,row1,row2):
  xs = data.cols.x
  return sqrt(sum(_aha(x, row1, row2)**2 for x in xs) / len(xs))

```

### C. Output Distance (`disty`)

Used for **Optimization**. Measures the gap between a row's outcomes and "Heaven."

* **Heaven:** Target is `1` for `+` columns, `0` for `-` columns.
* **Goal:** Minimize `disty`.

**Example:**
Given goals `Lbs-`, `Acc+`, `Mpg+` and normalized values `.59`, `.33`, `0`:

* Formula: `d = sqrt( ((.59 - 0)^2 + (.33 - 1)^2 + (0 - 1)^2) / 3 )`
* Math: `sqrt( 0.34 + 0.44 + 1 ) = sqrt(1.79/3)`
* Result: `~0.77`

**Conclusion:** Smaller distances are better. 0.77 is far from heaven (0.0). We want to find rows with smaller distances.

---

## 6. Summary Table

| Concept | Implemented By | Role |
| --- | --- | --- |
| **Data Mining** | `distx`, `mids` | Find structure/clusters |
| **Optimization** | `disty`, `norm` | Find better solutions |
| **Categories** | `Sym` | Nominal/Ordinal data |
| **Quantities** | `Num` | Interval/Ratio data |
| **Scaling** | `norm` | Compare Apples to Oranges |
| **Streaming** | `add` | One-pass statistics |
-----------------


Here is the tutorial formatted as requested.

# TinyTutorial: Data Mining & Optimization

## 1. The Anatomy of Data

Data is a grid. **Rows** are examples (cars); **Columns** are
features.

### Data Types: The "NOIR" Hierarchy

Columns dictate the "language" of the data.

**1. Nominal (Labels)**
No inherent order. Just names.

* *Ex:* `origin`. Value 1 vs 2. One is not "greater" than the
other.

**2. Ordinal (Ranked)**
Order matters, but differences are uneven or unknown.

* *Ex:* Safety ratings (Low, Med, High).

**3. Interval (Equal Spacing)**
Order matters, distances are equal, but **no true zero**. You
can subtract, but not divide.

* *Ex:* `Model` (Year). The gap between '70 and '71 is 1 year.
But "Year 0" isn't "no time," so '70 isn't "twice" '35.

**4. Ratio (True Zero)**
True zero exists. All math works.

* *Ex:* `Lbs-`, `Mpg+`. 4000lbs is exactly 2x 2000lbs.


## 2. The Relationship: y = f(x)

We find how inputs (x) predict outputs (y).

### A. Supervised Learning (|y| = 1)

One target column.

* **Regression:** y is a number (Ratio/Interval).
* *Goal:* Predict `Mpg+`.


* **Classification:** y is a class (Nominal/Ordinal).
* *Goal:* Predict `origin`.



### B. Optimization (|y| > 1)

Multiple outputs.

* *Goal:* Maximize `Mpg+` AND minimize `Lbs-`.
* *Result:* Finds trade-offs (Pareto frontier).


## 3. Special Structures

### Text Mining (Sparse Data)

* *Condition:* |x| is huge (every word in English).
* *Sparsity:* Rows (docs) are mostly empty (zeros).

### Unsupervised Learning (y is missing)

No labels. We only have x.

* **Clustering:** Group data by similarity.
* *Within Group:* "What is similar?" (e.g., all V8s).

### Semi-Supervised (y is rare)

Labels are expensive; raw data is cheap.

* *Method:* Cluster all data. If one row in Cluster A has a
label, assume all of Cluster A shares it.


## 4. Summary

| Role | Goal |
| --- | --- |
| **Miner** | Finds **groups**. "These are similar." |
| **Optimizer** | Finds **differences**. "Moving here is better." |


-----

# TinyTutorial: The `xai.py` Data Model

## 1. The Core Philosophy

Your code simplifies the NOIR hierarchy into just two types based on
column names:

* **Sym (Symbolic):** Nominal & Ordinal data.
* **Num (Numeric):** Interval & Ratio data.

---

## 2. Parsing Logic (`Col`)

The function `Col` decides the type by looking at the **first
letter** of the column name.

### A. The Constructor

`col = (Num if txt[0].isupper() else Sym)()`

* **Uppercase Start** → `Num` class (Ratio/Interval).
* *Ex:* `Volume`, `HpX`, `Lbs-`, `Acc+`, `Mpg+`.
* *Stats kept:* `mu` (mean), `m2` (for variance).


* **Lowercase Start** → `Sym` class (Nominal/Ordinal).
* *Ex:* `origin`, `model` (if lowercase), `name`.
* *Stats kept:* `has` (counts of each symbol).



### B. Goals (`x` vs `y`)

The suffix of the column name determines its role.

* **Dependent Goals (y):** Ends in `+` or `-`.
* `+` → Maximize (weight = 1).
* `-` → Minimize (weight = 0).


* **Ignored (X):** Ends in `X`.
* Used for comments or non-predictive features (e.g., ID).


* **Independent (x):** Everything else.
* The features used to predict `y`.



---

## 3. Data Loading Pipeline

### Step 1: `csv(fileName)`

Reads text, handles comments (`%`), and type inference (`coerce`).

* Strings → Integers → Floats → Booleans.

### Step 2: `Cols(names)`

The factory that organizes columns.

1. Creates all `Col` objects.
2. Splits them into `x` (inputs) and `y` (goals).
* `x`: `Clndrs`, `Volume`, `HpX`, `Model`, `origin`
* `y`: `Lbs-`, `Acc+`, `Mpg+`



### Step 3: `Data(rows)`

The container.

* **First row:** Passed to `Cols()` to define structure.
* **Data rows:** Stored in `rows[]` list.
* *Note:* `adds()` (implied helper) updates column stats (`mu`,
`has`) as rows are added.

---

## 4. Example Output Analysis

Given your car data and `csv()` loop:

`8, 304, 193, 70, 1, 4732, 18.5, 10`

| Value | Name | Type | Role | Why? |
| --- | --- | --- | --- | --- |
| `8` | `Clndrs` | **Num** | `x` | Starts with 'C', no +/- |
| `304` | `Volume` | **Num** | `x` | Starts with 'V' |
| `1` | `origin` | **Sym** | `x` | Starts with 'o' |
| `4732` | `Lbs-` | **Num** | `y` | Ends with `-` (Min) |
| `18.5` | `Acc+` | **Num** | `y` | Ends with `+` (Max) |

### Stats Calculation

* **Num** columns update `mu` (mean) incrementally.
* **Sym** columns update `has` (frequency dictionary).

---

## 5. Summary

| `xai.py` Type | NOIR Equivalents | Detected By |
| --- | --- | --- |
| **Sym** | Nominal, Ordinal | **Lowercase** name |
| **Num** | Interval, Ratio | **Uppercase** name |


-----

which NOIR type each column specifically belongs to?

Here is a **TinyTutorial** on statistical distributions, tailored to the specific algorithms used in `xai.py`.

# TinyTutorial: Distributions in `xai.py`

## 1. The Normal Distribution (Gaussian)

In `xai.py`, we often assume numeric data follows a "bell curve" or
Normal Distribution. This curve is defined by two numbers:

* **Mean (μ):** The center/average.
* **Standard Deviation (σ):** The spread.

In the code, the `Num` class captures these:

```python
def Num(): return obj(it=Num, n=0, mu=0, m2=0)

```

---

## 2. PDF vs. CDF

* **PDF (Probability Density Function):** The height of the curve
at a specific point. It shows how likely a value is near that
point.
* **CDF (Cumulative Distribution Function):** The area under the
curve up to a point. It shows the probability of a value being
**less than or equal to** that point.

### In `xai.py`

The function `norm` acts like a sigmoid-based CDF. It converts a raw
number into a score between 0 and 1 using μ and σ.

```python
def norm(num,n):
  z = (n - num.mu) / sd(num)      # Standardize (Z-score)
  z = max(-3, min(3, z))          # Clip outliers
  return 1 / (1 + exp(-1.7 * z))  # Sigmoid compression

```

*Note: This specific curve approximates the error function (Erf) used
in Gaussian CDFs.*

---

## 3. The Irwin-Hall Distribution

True Gaussian generation is computationally expensive. `xai.py` uses
a "hack" called the **Irwin-Hall Distribution**. By summing multiple
Uniform (flat) distributions, you get a bell curve.

### The Code: `gauss`

The code sums 3 random numbers to approximate a Normal distribution
.

```python
def gauss(mid,div):
  # Summing 3 uniform randoms creates a bell-like curve
  return mid + 2 * div * (sum(random.random() for _ in range(3)) - 1.5)

```

* `random.random()` is Uniform (0 to 1).
* Summing them pushes values toward the center (Central Limit
Theorem).


## 4. Incremental Calculation (Welford's Algorithm)

Calculating μ and σ usually requires looping over all data
twice (once for mean, once for variance). `xai.py` does it in **one
pass**, updating as data arrives.

This is critical for "streaming" data where you can't hold everything
in memory.

### The Code: `add`

It updates the mean (`mu`) and the second moment (`m2`) incrementally
.

```python
def add(i, v, inc=1):
  ...
  d = v - i.mu
  i.mu += inc * d / i.n           # Update Mean
  i.m2 += inc * d * (v - i.mu)    # Update Variance Helper

```

To get the final Standard Deviation (σ):

```python
def sd(num): return ... sqrt(max(0,num.m2)/(num.n-1))

```


## 5. Discretization

Sometimes continuous distributions are too noisy. We "bin" them into
chunks (Ordinal data).

### The Code: `cutsAll`

The code converts continuous numbers into integer bins.

```python
k = floor(the.bins * norm(col, x)) # Scale 0..1 to 0..Bins

```

If two adjacent bins predict the target (`y`) similarly, they are
merged. This simplifies the complex distribution into simple rules
like:
`if x < 0.5 then ...`

### Summary Table

| Concept | `xai.py` Implementation | Role |
| --- | --- | --- |
| **Normal** | `Num` class | Tracks data shape |
| **CDF** | `norm()` | Standardizes data (0..1) |
| **Simulate** | `gauss()` | Fake Gaussian (Irwin-Hall) |
| **One-Pass** | `add()` | Updates μ/σ live |


Here is a **TinyTutorial** on how `xai.py` calculates distance, strictly following your formatting and citation constraints.

# TinyTutorial: Distance in `xai.py`

## 1. Why Measure Distance?

To cluster data ("find similar cars") or optimize it ("find better
cars"), we must mathematically quantify the "gap" between two rows.

`xai.py` splits this into two specific questions:

1. **`distx`**: How different are the inputs (features)?
2. **`disty`**: How far is the output from perfection?

---

## 2. The Foundation: Normalization (`norm`)

Distance fails if units differ (e.g., "Weight 4000" vs "MPG 20").
One large number dominates the math.

We scale everything to `0..1` using the `norm` function:

```python
def norm(num,n):
  z = (n - num.mu) / sd(num)      # Get Z-score
  return 1 / (1 + exp(-1.7 * z))  # Compress to 0..1

```

* **Result:** A heavy car (4732 lbs) becomes `~0.9`; a light car
becomes `~0.1`. Now it is comparable to MPG.

---

## 3. Comparing Single Attributes (`_aha`)

The function `_aha` (as in "Aha! I see the difference") measures the
gap between two specific values `u` and `v` in a single column
.

### A. Symbolic Data (`Sym`)

Simple boolean logic.

* **Same:** `("USA", "USA")` → 0
* **Different:** `("USA", "Europe")` → 1

```python
if Sym is col.it : return u != v

```

### B. Numeric Data (`Num`)

Absolute difference of the normalized values.

* **Gap:** `abs(norm(u) - norm(v))`

### C. Missing Data (`?`)

If data is missing, we assume the **maximum possible distance** (1) to
be safe.

```python
if u==v=="?": return 1

```

---

## 4. Distance Between Examples (`distx`)

To measure the gap between two cars (Row 1 vs Row 2), we combine the
`_aha` scores of all **x** columns (features like `Clndrs`,
`Volume`).

It uses a variation of **Euclidean Distance**:

```python
def distx(data,row1,row2):
  xs = data.cols.x
  # Average of squared differences
  return sqrt(sum(_aha(x, row1, row2)**2 for x in xs) / len(xs))

```

* **Why `/ len(xs)`?** It normalizes for the number of columns, so
adding more columns doesn't automatically increase the distance.

---

## 5. Distance to "Heaven" (`disty`)

This is for **Optimization**. We don't compare two cars; we compare
one car to a hypothetical "perfect" car.

* **The Target:** Defined in `Col`.
* `Mpg+` → Target is **1** (Maximize).
* `Lbs-` → Target is **0** (Minimize).



The code calculates the gap between the *actual* value and the
*target*:

```python
def disty(data,row):
  ys = data.cols.y
  # Gap between norm(value) and ideal target (0 or 1)
  return sqrt(sum(abs(norm(y,row) - y.target)**2 for y in ys) / len(ys))

```

* **Low `disty**` = Good car (Close to heaven).
* **High `disty**` = Bad car.

---

## 6. Summary

| Function | Measures... | Used For... |
| --- | --- | --- |
| **`norm`** | Scale (0..1) | Preparing raw numbers |
| **`_aha`** | Attribute Gap | Single column difference |
| **`distx`** | Feature Gap | Clustering, finding neighbors |
| **`disty`** | Performance Gap | Optimization, ranking |


----------

Here is the complete, comprehensive **TinyTutorial** merging all
concepts, structures, and algorithms discussed.

# TinyTutorial: Data Mining & Optimization with `xai.py`

## 1. The Core Philosophy

Data science asks two main questions:

### A. Data Mining (Structure)

* **Goal:** Find naturally occurring **groups** within data.
* **Question:** "What is similar within this group? What is
different between groups?"
* **Technique:** Clustering (Unsupervised Learning).

### B. Optimization (Improvement)

* **Goal:** Find **differences** that guide us to a better state.
* **Question:** "How do I move from a heavy, low-MPG car to a
lighter, high-efficiency car?"
* **Technique:** Multi-Objective Optimization (finding the Pareto
Frontier).

---

## 2. The Anatomy of Data (`Sym` & `Num`)

Data is a grid of **Rows** (examples) and **Columns** (features).
`xai.py` simplifies the standard "NOIR" hierarchy into two types
based on column names.

### A. Symbolic Data (`Sym`)

Used for **Nominal** (Labels) and **Ordinal** (Ranked) data.

* **Detection:** Column name starts with **lowercase**.
* **Storage:** Counts frequencies in a dictionary (`has`).
* **Stats:** The `mid` is the **Mode** (most frequent value).

```python
def Sym(): return obj(it=Sym, n=0, has={})

```

### B. Numeric Data (`Num`)

Used for **Interval** (Dates) and **Ratio** (Quantities) data.

* **Detection:** Column name starts with **Uppercase**.
* **Storage:** Tracks mean (`mu`) and variance (`m2`)
incrementally.
* **Stats:** The `mid` is the **Mean** (μ).

```python
def Num(): return obj(it=Num, n=0, mu=0, m2=0)

```

---

## 3. Managing Data: `Cols` & `Data`

### A. The Column Factory (`Cols`)

Organizes raw names into objects and defines roles.

* **`x` (Inputs):** Independent features (e.g., `Clndrs`).
* **`y` (Goals):** Targets to minimize (`-`) or maximize (`+`).
* **`X` (Ignored):** Columns skipped (end in `X`).

```python
def Cols(names): 
  # ... creates Col objects ...
  return obj(..., x=[...], y=[...])

```

### B. The Container (`Data`)

Holds the rows and summarizes them.

* **Logic:** The first row creates `Cols`; subsequent rows update
stats via `add()`.
* **Centroids:** It calculates the "average row" (`mids`) used for
clustering.

```python
def mids(data):
  data._centroid = ... [mid(col) for col in data.cols.all]
  return data._centroid

```

---

## 4. Distributions & Statistics

### A. The Normal Distribution

`Num` assumes data follows a bell curve defined by Mean (μ) and
Standard Deviation (σ).

* **Calculation:** Uses Welford's algorithm to calculate σ in
one pass (streaming).

```python
def sd(num): 
  return 1/BIG + (0 if num.n<2 else sqrt(max(0,num.m2)/(num.n-1)))

```

### B. Simulation (Irwin-Hall)

To simulate Gaussian data cheaply, we sum three uniform random
numbers.

```python
def gauss(mid,div):
  return mid + 2 * div * (sum(random.random() for _ in range(3)) - 1.5)

```

### C. Discretization

Continuous distributions can be noisy. We "bin" them into chunks
(converting `Num` → `Ord`) using `cutsAll`. This simplifies
complex curves into rules like `if x < 0.5`.

---

## 5. Distance & Normalization

### A. Normalization (`norm`)

Distance metrics fail if units differ (e.g., Weight 4000 vs MPG 20).
We scale all `Num` values to `0..1` using a sigmoid-like curve
.

```python
def norm(num,n):
  z = (n - num.mu) / sd(num)
  return 1 / (1 + exp(-1.7 * z))

```

### B. Input Distance (`distx`)

Used for **Clustering**. Measures how different the features (`x`)
are between two rows (e.g., Row 1 vs Row 2).

* **Logic:** Euclidean distance of normalized attributes
.

```python
def distx(data,row1,row2):
  xs = data.cols.x
  return sqrt(sum(_aha(x, row1, row2)**2 for x in xs) / len(xs))

```

### C. Output Distance (`disty`)

Used for **Optimization**. Measures the gap between a row's outcomes
and "Heaven."

* **Heaven:** Target is `1` for `+` columns, `0` for `-` columns.
* **Goal:** Minimize `disty`.

**Example:**
Given goals `Lbs-`, `Acc+`, `Mpg+` and normalized values `.59`,
`.33`, `0`:

*Result:* 0.77 is far from heaven (0.0). We want to find rows with
smaller distances.

---

## 6. Summary Table

| Concept | Implemented By | Role |
| --- | --- | --- |
| **Data Mining** | `distx`, `mids` | Find structure/clusters |
| **Optimization** | `disty`, `norm` | Find better solutions |
| **Categories** | `Sym` | Nominal/Ordinal data |
| **Quantities** | `Num` | Interval/Ratio data |
| **Scaling** | `norm` | Compare Apples to Oranges |
| **Streaming** | `add` | One-pass statistics |


Optimization via Landscape analusis

data minign:divine data into regions

optimization: play snales and ladders. find 

spread hv igd gd

promisetine 

disty

distxo

number tipes oranlial nonoaml ration etc. but who cares.
