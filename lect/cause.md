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

# From Black Boxes to Small Trees
## An 80-minute lecture on explainable optimization

---

## Part 1: Why Locality Matters (15 min)

### The distributed dogma

For decades, the orthodoxy was that neural network
knowledge is *distributed* — smeared across millions
of weights, impossible to localize. Dropout trains
networks to survive losing random neurons. Adversarial
examples show tiny input perturbations flip outputs.
The implication: no single neuron "knows" anything.

### The surprise

Three results broke this story:

**Elhage et al. (2022)** showed that polysemantic
neurons — neurons responding to unrelated concepts —
arise from *compression*, not true distribution.
Networks pack more features than they have neurons
via "superposition." The distributed look is an
encoding trick, not a fundamental property.

**Dai et al. (2022)** found that specific factual
knowledge in BERT ("The capital of Ireland is ___")
localizes to tiny subsets of FFN neurons. Suppressing
those neurons drops correct recall by ~29%. Suppressing
random neurons of the same count: ~1.5%. You can
surgically edit, update, or erase individual facts
without retraining.

**Voria et al. (2026)** extended this to social bias.
Gender, age, and race stereotypes similarly concentrate
in sparse neuron subsets. Zeroing them selectively
reduces bias while leaving unrelated fluency intact
(p < 0.0001, Cliff's delta = 1.0). And scaling the
model doesn't spread bias — it *concentrates* it
into fewer, more specialized neurons.

Knowledge is sparse. Knowledge is local. Surgery works.

---

## Part 2: Why Interpretable, Not Explainable (15 min)

### Rudin's argument (2019)

If knowledge is localizable, why not build models that
*are* the sparse structure from the start?

**The myth.** DARPA [published](https://ojs.aaai.org/aimagazine/index.php/aimagazine/article/view/2850/3419) a figure showing a smooth
accuracy-interpretability tradeoff. Rudin points out
it was generated from no data. The axes have no units.

**The evidence.** On structured data with meaningful
features, simple models routinely match complex ones.
Rudin's NYC power grid study: algorithms differed by
≤1% on static data, but the ability to *interpret and
reprocess* led to significant gains. The best models
were sparse.

**The logic.** If an explanation were perfectly faithful
to the black box, it *would be* the black box — and
you wouldn't need the black box. So every explanation
is, by definition, unfaithful somewhere.

**The poster child.** COMPAS: 130+ input factors,
proprietary, used for bail decisions across the U.S.
Typographical errors in the 130-factor survey sometimes
determine who goes free.

CORELS produces a 3-rule model matching COMPAS's
accuracy on the same Broward County data:
```text
IF age 18-20 AND male       → predict arrest
ELSE IF age 21-23 AND 2-3 priors → predict arrest
ELSE IF more than 3 priors  → predict arrest
ELSE → predict no arrest
```

Three rules. Computable on a napkin. No typos.

### Gigerenzer's heuristics (2008)

Why does simplicity *work*? Not just because the data
are easy — because simplicity is an *active advantage*
in uncertain environments.

**1/N beats the Nobel.** Markowitz won the Nobel for
optimal portfolio theory. For his *own* retirement he
used 1/N: split money equally. DeMiguel et al. tested
12 optimal strategies against 1/N. None beat it.
The optimizers overfit past data. 1/N estimates zero
parameters, so it *cannot* overfit. With 50 funds,
optimization needs ~500 years of data to catch up.

**Fast-and-frugal trees save lives.** Green and Mehr
built a 3-question tree for coronary care allocation
that beat logistic regression and the physicians
themselves. The hospital still uses it.

The principle: **the noisier the environment, the more
information you should ignore.** Heuristics aren't
second-best — they're ecologically rational. And they
produce *symbolic* outputs that humans can check,
debate, and override with domain knowledge.

---

## Part 3: The Simplest Useful Model (20 min)

### How the tree works

One file. ~700 lines. Here's the pipeline:

**Step 1: Header is schema.** No config files.
Column names encode everything:
```python
# [A-Z]* → Numeric    [a-z]* → Symbolic
# *+     → Maximize    *-     → Minimize
# *X     → Ignore      ?      → Missing value

class Cols:
  def __init__(i, names):
    i.names = names
    i.all = {at: col(s) for at,s in enumerate(names)}
    i.w = {at: s[-1]!="-"
           for at,s in enumerate(names)
           if s[-1] in "-+!"}
    i.x = {at:c for at,c in i.all.items()
            if at not in i.w
            and names[at][-1] != "X"}
    i.y = {at: i.all[at] for at in i.w}
```

So `EFFORT-` means "numeric, minimize." `Mpg+` means
"numeric, maximize." `origin` (lowercase) means
"symbolic, independent variable." The system figures
out X vs Y from the punctuation.

**Step 2: Distance to heaven.** Every row gets a
single score — how far is it from the ideal point
where all goals are simultaneously at their best?
```python
def disty(i, r):
  return minkowski(
    abs(c.norm(r[at]) - i.cols.w[at])
    for at,c in i.cols.y.items())
```

`i.cols.w[at]` is 1 for maximize columns, 0 for
minimize. `c.norm` squashes values to 0..1. The
result: 0 = perfect, 1 = worst possible. One number
per row. Now we can sort *anything*.

**Step 3: Split on median.** Here's the nonstandard
choice. Most trees split numerics at the point of
minimum expected variance, evaluating every possible
cut. We split on the **median**:

```python
def _treeCuts(c: Col, rs: Rows) -> Iterable[Any]:
  """Yield possible split points for a column."""
  vs = [r[c.at] for r in rs if r[c.at] != "?"]
  if not vs: return []
  return set(vs) if Sym == type(c) else [sorted(vs)[len(vs)//2]]
```

Symbolics: try every value. Numerics: one cut, the
median. Tested across 127 SE datasets — median splits
were as good or better, and far cheaper. No exhaustive
search over all possible thresholds.

**Step 4: Recurse, sorted best-to-worst.**

```python
def treeGrow(d: Data, rs: Rows) -> Tree:
  """Recursively grow a decision tree to minimize Y-distance variance."""
  t = Tree(d, rs)
  if len(rs) >= 2 * the.learn.leaf:
    splits = (
      _treeSplit(d, c, cut, rs)
      for c in t.d.cols.xs for cut in _treeCuts(c, rs)
    )
    if valid := [s for s in splits if min(len(s[3]), len(s[4])) >= the.learn.leaf]:
      _, t.col, t.cut, left, right = min(valid, key=lambda x: x[0])
      t.left, t.right = treeGrow(d, left), treeGrow(d, right)
  return t

def _treeSplit(d: Data, c: Col, cut: Any, rs: Rows) -> tuple:
  """Evaluate splitting rows on a specific column and cut point."""
  l_rs, r_rs, l_num, r_num = [], [], Num(), Num()
  for r in rs:
    v = r[c.at]
    go = v == "?" or (v == cut if Sym == type(c) else v <= cut)
    (l_rs if go else r_rs).append(r)
    add(l_num if go else r_num, disty(d, r))
  return (l_num.n * spread(l_num) + r_num.n * spread(r_num), c, cut, l_rs, r_rs)

```

Recurse until leaves have ≤ `leaf` rows. The tree
nodes are printed sorted by their `disty` score —
best regions first, worst last.

### Reading the output

Here's a real run on XOMO (a NASA software cost
model with 4 objectives: minimize effort, months,
defects, and risk):
```text
                         ,0.50 ,( 50), {EFFORT-=655, MONTHS-=24, ...}
KLOC <= 227              ,0.40 ,( 26), {EFFORT-=409, MONTHS-=21, ...}
|   KLOC <= 93           ,0.32 ,( 14), {EFFORT-=239, MONTHS-=18, ...}
|   |   RELY > 2.51      ,0.22 ,(  6), {EFFORT-=199, MONTHS-=17, ...}
|   |   RELY <= 2.51     ,0.39 ,(  8), {EFFORT-=270, MONTHS-=19, ...}
...
KLOC > 227               ,0.62 ,( 24), {EFFORT-=922, MONTHS-=28, ...}
...
|   |   SITE <= 3.63     ,0.78 ,(  7), {EFFORT-=1536,MONTHS-=34, ...}
|   |   |   CPLx > 1.99  ,0.83 ,(  3), {EFFORT-=1718,MONTHS-=36, ...}
```

Reading this:

- **First line**: root, all 50 rows, median disty 0.50.
- **Best leaf**: `KLOC <= 93 AND RELY > 2.51` — 6 rows,
  score 0.22. Small programs with higher reliability
  requirements yield the lowest effort (199), fewest
  months (17), and least defects.
- **Worst leaf**: `KLOC > 227 AND RESL <= 3.82 AND
  SITE <= 3.63 AND CPLx > 1.99` — 3 rows, score 0.83.
  Large, complex, poorly-resolved, co-located projects
  have 8.6x the effort and 2.1x the schedule.
- **The tree is the explanation.** Reading top-to-bottom
  tells you: keep programs small, demand reliability,
  and resolve risks early. No post-hoc explainer needed.

### What the tree *can't* do

The tree tells you what *is*. It doesn't tell you
what to *change* or what *would have happened* under
different conditions. For that, we need Pearl.

---

## Part 4: The Causal Ladder (15 min)

### Three rungs

**Rung 1 — See.** "What patterns exist?" Query the
joint distribution P(Y|X). Route nothing, just look
at the training data.

In tree terms: `build` + `showTree`. The output above.

**Rung 2 — Act.** "What does the model say about
*this* row?" Apply the model to new data. The model
itself is an intervention — without it, you'd just
be eyeballing the data (rung 1).

```python
def treeLeaf(t: Tree, r: Row) -> Tree:
  """Traverse the tree to find the leaf node for a given row."""
  if not t.left: return t
  v = r[t.col.at]
  go = (v != "?" and v <= t.cut) if Num == type(t.col) else (v != "?" and v == t.cut)
  return treeLeaf(t.left if go else t.right, r)
```

Route a test row. Compare actual score vs leaf score.
Flag anomalies (large gaps = alerts). That's `eg_act`.

**Rung 3 — Imagine.** "What *would have happened*
if this row were different?" Clone the row, force one
feature, re-route, see what changes:
```python
def whatif(t, r, at, val):
  r2 = r[:]; r2[at] = val
  return leaf(t, r2)
```

Two lines. But this is a genuine counterfactual:
the observed row contradicts the hypothetical, and
the model connects the two worlds.

For the worst XOMO row (score 0.83), a what-if sweep
might show: "if KLOC were 93 instead of 350, score
drops to 0.32 — biggest single improvement." That's
root cause analysis, forecasting, and simulation in
one report.


### Why walk up — not jump across?

A naive optimizer would say: "You're in the worst leaf
(0.83). The best leaf is 0.22. Just go there." But
going there means changing KLOC, RELY, and possibly
everything else. That's not advice — that's "be a
different project."

Counterfactuals are not optimization. Three constraints
separate them:

**Freeze the individual.** Pearl calls this U — the
unobserved background. In the tree, U is everything in
the row you don't change. When you ask "what if
SITE > 3.63?", the project's size, complexity,
personnel, and history stay frozen. You're asking about
*this* project, not some hypothetical ideal one.

**Minimal change.** Walking up one branch tests one
variable at a time. That's not a limitation — it's the
point. A manager can action one change. Two changes are
harder. Three are a reorg. The tree's branching
structure naturally decomposes the counterfactual into
single-variable interventions ranked by impact.

**Stay in observed territory.** Every sibling leaf
contains real rows — projects that actually existed.
You're not extrapolating to a fantasy configuration.
You're saying "projects like yours, but with better
site collocation, looked like *this*." The tree can't
send you somewhere the data hasn't been.

The `whatif` planning function encodes all three constraints
in six lines:

```python
def treePlan(t: Tree, here: Tree) -> Iterable[tuple]:
  """Yield plans (variable changes) to improve outcomes from current leaf."""
  eps = the.stats.eps * spread(t.ynum)
  for there, _, _, _, _ in treeNodes(t):
    if there.col is None and (dy := mid(here.ynum) - mid(there.ynum)) > eps:
      diff = [f"{c.txt}={o(mid(c))}" for c, h in zip(there.d.cols.xs, here.d.cols.xs)
              if mid(c) != mid(h)]
      if diff: yield dy, mid(there.ynum), diff
```

Output:

```python
./ezr.py -plan ~/gits/moot/optimize/misc/auto93.csv

now=0.94
    0.71 (dy=0.23) if Clndrs=7.33, Volume=286.33, Model=72.67
    0.58 (dy=0.35) if Clndrs=6.00, Volume=213.80, Model=73.80
    0.56 (dy=0.38) if Clndrs=4.00, Volume=121.80, Model=72.80, origin=3
    0.52 (dy=0.42) if Clndrs=5.67, Volume=215.33, Model=79.67
    0.43 (dy=0.51) if Clndrs=4.00, Volume=140.75, Model=78.50
    0.39 (dy=0.55) if Clndrs=4.00, Volume=104.67, Model=76.67, origin=2
    0.37 (dy=0.56) if Clndrs=4.00, Volume=129.50, Model=81.50
    0.31 (dy=0.63) if Clndrs=3.80, Volume=84.40, Model=78.60, origin=3
    0.29 (dy=0.65) if Clndrs=4.00, Volume=97.75, Model=77.50, origin=3
    0.21 (dy=0.73) if Clndrs=4.00, Volume=88.75, Model=75.25, origin=2
```

This is what distinguishes Rung 3 from Rung 2.
Intervention asks "what does the model predict for
new data?" Counterfactual asks "what would *this
specific individual* experience if *one thing* were
different — holding everything else fixed?"

### The 3×3 grid collapses

Buse and Zimmermann's analytics grid:
```text
           Past       Present     Future
Find     Trends      Alerts     Forecast
Explain  Summarize   Compare    Root cause
Compare  Model       Benchmark  Simulate
```

9 cells. Looks like 9 tools. But the columns are just
*which data you feed*:

- Past = training set → `build + showTree`
- Present = test set → `leaf` on new rows
- Future = perturbed test → `whatif` on mutated rows

And the rows are just *what you read* in the same
output. One report per column, three readings each.
9 cells, 3 functions:

| past   | pressent    | figure|
|--------------|--------------|---------------------|
| See (train)  | Act (test)   | Imagine (perturb) |
| showTree     | leaf → gap   | whatif → rank       |
| eg_see       | eg_act       | eg_imagine          |
| Rung 1       | Rung 2       | Rung 3              |


---

## Part 5: Wrap-up (5 min + 10 min Q&A)

Three threads, one conclusion:

**Locality**: knowledge in large models is sparser
than we thought. You can find it and edit it.

**Interpretability**: if you can explain a black box,
you can probably build a simple model that's just as
accurate — and more trustworthy.

**Ecological rationality**: simple models aren't just
easier to understand. In noisy environments, they're
*more accurate* on future data because they ignore
the noise that complex models overfit.

The synthesis: build small trees on small budgets.
They are inherently interpretable, ecologically
rational, and they produce symbolic outputs that
humans can check, debate, and extend — across all
three rungs of the causal ladder.

That's `ez.py`. 700 lines. One file. `pip install ezr`.

### References

- Dai et al. "Knowledge Neurons in Pretrained
  Transformers." ACL 2022.
- Elhage et al. "Toy Models of Superposition."
  Anthropic, 2022.
- Gigerenzer. "Why Heuristics Work." Perspectives
  on Psychological Science, 2008.
- Rudin. "Stop Explaining Black Box Models for High
  Stakes Decisions." Nature Machine Intelligence, 2019.
- Voria et al. "Tracing Stereotypes in Pre-trained
  Transformers." MSR 2026.
