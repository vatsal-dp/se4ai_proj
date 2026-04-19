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

# Python Idioms in ez.py: A Tutorial

A walk through some of the lower-level details of [ez.py](../submit/two/ez.py)
Some tricks from `ez.py`, ordered from
"you probably know this" to "wait, what just
happened?"

> Warning: my code is not "industrial standard" (no classes, not type hints, no doc strings,  not "PEP8" complient).
But when I rewrite to those standarards, my 200 lines becoems 1000 lines. And since
I write code to show code to other people.... 

This used to be a big issues. But in this new era of LLMs, you can
ask an automatic friend to add classes, format to PEP8, add the type hints. add the doc strings, etc etc.

---

## SETUP

Before you begin down these two files into an empty directory:

- [ez.py](../submit/two/ez.py)
- [auto93.csv](../submit/two/auto93.csv)
- [FFM-1000-200-0.50-SAT-1.csv](../submit/two/FFM-1000-200-0.50-SAT-1.csv)
- [xomo_ground.csv](../submit/two/xomo_ground.csv)
  - For an explanation of the xomo attributes, search for (e.g.) Team in [this doc](https://rose-hulman.edu/class/cs/csse372/201310/Homework/CII_modelman2000.pdf).
- [smells.csv](../submit/two/smells.csv)
  - For an explanation of the small attributes, search for (e.g.) WOC in [this doc](https://essere.disco.unimib.it/wp-content/uploads/sites/71/2019/04/metric-definitions.pdf)

```
┌─ TRY THIS ────────────────────────────────────────────────────┐
│ 1. look at first row of the .csv files                        │
│ 2. Then, in Python....                                        │
│                                                               │
│ from ez import *                                              │
│ eg__tree("auto93.csv")    #1                                  │
│ eg__tree("xomo_ground.csv") #2                                │
│ eg__tree("smells.csv")    #3                                  │
│ eg__tree("FFM-1000-200-0.50-SAT-1.csv")  #4                   │
│                                                               │
│ #1 What is best volume for a car with more than 4 cylinders?   │
│ #2 In small projects, does analyst capability trump experience?│
│ #3 How to find ieature Envy (FE) (excess calls to other classes) │
│ #4 How many attributes are needed for effective optimization ? │
└───────────────────────────────────────────────────────────────┘
```


---

## 1. Ternary Expressions

One-line if/else that returns a value.

```python
def mid(col):
  return mode(col) if SYM is col.it else col.mu
```

Read it as: "return mode if symbolic, else mu."

---

## 2. Unpacking with `*` and `**`

The `*` splat expands a list into separate arguments.

```python
print(*data.cols.names)
# same as print("Clndrs","Volume","HpX", ...)
```

Also used to accept variable positional args:

```python
def furthest(*args): return order(*args)[-1]
def nearest(*args):  return order(*args)[0]

def order(data,r1,rows): return sorted(rows,key=lambda r2:distx(data,r1,r2))
```

Q:  if `order`  changes its arguments, what changes are requird in `furthest, nearest`?    
A: None! (Tee hee)

The `**` double-splat does the same for dicts.
It unpacks key=value pairs:

```python
def NUM(**d): return OBJ(it=NUM, **d, n=0, mu=0, m2=0)
```

Here `**d` carries keyword args through — so
`NUM(at=3, txt="Mpg+", goal=True)` passes those
fields straight into the `OBJ` constructor along
with the defaults `n=0, mu=0, m2=0`.

---

## 3. Multiple Assignment

Assign several variables at once.

```python
i.n, i.mu, i.m2 = 0, 0, 0
```

Also used to unpack tuples:

```python
n, d = 0, 0
c, cut, left, right = best
```

---

## 4. List Comprehensions

Build a list in one expression.

```python
def what(s):
  return NUM if s[0].isupper() else SYM

def COL(at=0, txt=" "):
  return what(txt)(at=at, txt=txt, goal=txt[-1]!="-")

names = ["origin","Volume"]
cols = [COL(at=n, txt=s) for n,s in enumerate(names)]
```

`enumerate` yields `(index, value)` pairs. Each name
becomes a `COL`. `what` checks if the name starts
uppercase (→ `NUM`) or lowercase (→ `SYM`). So
`"Volume"` creates a `NUM`, `"origin"` creates a
`SYM`, and `COL` wraps the decision.

With a filter, we can find all the x columns (the independent
input variables).

```python
x = [c for c in cols if c.txt[-1] not in "-+!X"]
```

---

## 5. Dict Comprehensions

Same idea, but builds a dictionary.

The module docstring doubles as a settings spec:

```python
"""
OPTIONS:
  -b bins=7    Number of bins for discretization
  -p p=2       Minkowski distance power
  -s seed=1    Random number seed
  -S Show=30   Tree display width
"""
```

One line parses that into a config object:

```python
the = OBJ(**{
  k: cast(v)
  for k, v in re.findall(r"(\S+)=(\S+)", __doc__)
})
# the.bins=7, the.p=2, the.seed=1, the.Show=30
```

The regex `(\S+)=(\S+)` finds every `key=value`
pair in `__doc__` (the module's docstring). `cast`
converts strings to ints/floats. The `**{...}`
unpacks the dict into keyword arguments for `OBJ`.

One source of truth: the docstring both documents
and initializes all settings.

```
┌─ Reading Guide ──────────────────────── ──────┐
│ __doc__         module's docstring            │
│ re.findall()    all regex matches in a string │
│ (\S+)=(\S+)    capture nonwhitespace=nonws    │
│ cast(v)         "7"→7, "2"→2 (string→number)  │
│ OBJ(**{...})    dict → object with dot access │
└────────────────────────────────────────────-──┘
```

```
┌─ TRY THIS ───────────────────────────────────┐
│ from ez import *                             │
│ print(the)                                   │
│ print(the.bins, the.seed)                    │
│                                              │
│ # What fields does 'the' have?               │
│ # Where did those values come from?          │
└──────────────────────────────────────────────┘
```

---

## 6. Generator Expressions

Like list comprehensions but lazy — values computed
one at a time, never all stored in memory.

```python
adds(gauss(10, 1) for _ in range(1000))
```

No square brackets means it yields on demand.
Critical when data is large or streaming.

---

## 7. First-Class Functions

Functions are values. Store them in variables,
pass them as arguments, return them from other
functions.

```python
# Store a function in a variable
Y = lambda r: disty(data, r)

# Pass a function as a sort key
sorted(rows, key=Y)

# what() returns a function (NUM or SYM)
def what(s): return NUM if s[0].isupper() else SYM
```

In `what`, the return value is a function — either
the `NUM` factory or the `SYM` factory. The caller
can then *call* the result:

```python
def COL(at=0, txt=" "):
  return what(txt)(at=at, txt=txt, goal=txt[-1]!="-")
```

`what(txt)` returns `NUM` or `SYM`, then `(at=...)`
calls whichever was returned. Two function calls
in one expression.

---

## 8. Lambda Functions

Small anonymous functions, often used as sort keys.

```python
sorted(rows, key=lambda r2: distx(data, r1, r2))
```

Can also be stored in variables:

```python
Y = lambda r: disty(data, r)
```

Lambdas are limited to one expression. For anything
more complex, use a regular `def`.

---

## 9. The Walrus Operator `:=`

Assign and use a value in the same expression.
Added in Python 3.8.

```python
if (v := r[at]) != "?":
  (left if fn(v) else right).append(r)
```

Without it, you'd need a separate line:

```python
v = r[at]
if v != "?": ...
```

Also used inside comprehensions:

```python
-sum(p*log(p,2)
     for n in sym.has.values()
     if (p := n/sym.n) > 0)
```

---

## 10. Chained Comparisons

Python lets you chain comparisons naturally.

```python
if u == v == "?": return 1
```

This tests `u == v` *and* `v == "?"` in one shot.
Equivalent to `if u == "?" and v == "?"`.

---

## 11. Short-Circuit Defaults with `or`

Use `or` to provide a fallback value.

```python
it = it or NUM()
```

If `it` is `None` (falsy), create a fresh `NUM`.
Same pattern:

```python
rows or []
```

Returns `rows` if non-empty, else an empty list.

---

## 12. `.get()` with Fallback

Safe dictionary access that never throws `KeyError`.

```python
i.has[v] = w + i.has.get(v, 0)
```

If `v` isn't in `i.has`, return `0` instead of
crashing.

---

## 13. Conditional Method Selection

Pick *which method* to call at runtime.

```python
(i.rows.append if w > 0 else i.rows.remove)(v)
```

The ternary picks `append` or `remove`, then the
trailing `(v)` calls whichever was chosen.

Same pattern for selecting other *which function*:

```python
(ent if SYM is col.it else sd)(col)
```

---

## 14. `is` for Identity Checks

`is` checks if two names point to the *same object
in memory*, not just equal values. It compiles down
to a single pointer comparison — about as fast as
any operation can be.

```python
if SYM is col.it: ...
```

Here `SYM` is a function object. The `.it` field
stores a reference to that same function. So `is`
acts like a type tag without needing classes or
enums — and it's faster than string comparison or
`isinstance()`.

---

## 15. List Comprehensions for Side Effects

Sometimes we build a list we never use, just to
run `add` on each item.

```python
[add(it, item) for item in (items or [])]
```

The list is thrown away. We only care about the
side effects of `add`. Compact but controversial —
some prefer a plain `for` loop.

---

## 16. `try`/`except` as Control Flow

`cast` tries each converter in turn. Failure is
expected and handled gracefully.

```python
CASTS = [int, float,
  lambda s: {"true":1,"false":0}.get(s.lower(), s)]

def cast(s):
  for f in CASTS:
    try: return f(s)
    except ValueError: ...
```

**Why `ValueError`, not `Exception`?** Catching
`Exception` would swallow real bugs (`TypeError`,
`AttributeError`, etc.). `ValueError` is the
*specific* error `int()` and `float()` raise on
bad input. The `...` (Ellipsis) is a do-nothing
placeholder.

---

## 17. `with` and File Generators

`with` ensures the file closes even if we crash.
`yield` makes this a generator — rows produced
lazily, one at a time.

```python
def csv(f):
  with open(f, encoding="utf-8") as file:
    for s in file:
      if s := s.partition("#")[0].strip():
        yield [cast(x.strip()) for x in s.split(",")]
```

`partition("#")` splits on the first `#`, so
everything after it (comments) is discarded.
Callers iterate with `for row in csv("data.csv")`.
Only one row is in memory at a time.

```
┌─ TRY THIS ───────────────────────────────────┐
│ from ez import *                             │
│ for i,row in enumerate(csv('auto93.csv')):   │
│   if i % 100 == 0: print(row)                │
│                                              │
│ # Which row is the header? Which are data?   │
│ # What types did cast() produce?             │
└──────────────────────────────────────────────┘
```

---

## 18. `iter()` and `next()`

The iterator protocol. `iter()` wraps a list
so `next()` can pull items one at a time.

Note that, under the hood, Python's for loops
also use `iter,next`.

```python
def main(settings, funs):
  args = iter(sys.argv[1:])
  for s in args:
    if f := funs.get(f"eg_{s[1:].replace('-','_')}"):
      run(f, *[t(next(args))
               for t in f.__annotations__.values()])
    else:
      for k in settings:
        if k[0] == s[1]:
          settings[k] = cast(next(args, ""))

if __name__ == "__main__": main(the,globals())
```

The key trick: `next(args)` advances the *same*
iterator that the `for` loop uses. So when we
consume an extra arg (the value after a flag), the
loop skips it automatically.

To say that another way, this code queries the functions
to as "how many arguments do you need"? For example, in the follow `eg__the` needs zeo and `eg_s` needs one.

```python
ef eg__the():
  "Show config."
  print(the)

def eg_s(n:int):
  "Set random number seed."
  the.seed=n; random.seed(n)
```

Walk through `python3 ez.py -s 42 --tree auto93.csv`:

1. `args = iter(["-s","42","--tree","auto93.csv"])`
2. `s = "-s"` → `funs["eg_s"]` exists, has 1
   annotation (`int`), so `next(args)` eats `"42"`,
   casts to `int`, runs `eg_s(42)`
3. `s = "--tree"` → `funs["eg__tree"]` exists,
   has 1 annotation, eats `"auto93.csv"`, runs
   `eg__tree("auto93.csv")`

`next(args, "")` provides a default if exhausted.

---

## 19. `match`/`case` (Structural Pattern Matching)

Python 3.10+. Like a `switch` but matches on type
and structure.

```python
def o(t):
  match t:
    case _ if type(t) is type(o): return t.__name__
    case dict():  return "{" + ... + "}"
    case float(): return f"{t:.{the.decs}f}"
    case list():  return "[" + ... + "]"
    case _:       return str(t)
```

`case dict()` matches any dict. `case _` is the
default. The guard `if type(t) is type(o)` matches
function objects.

---

## 20. F-String Formatting Tricks

F-strings can nest expressions inside format specs.

```python
f"{s:{the.Show}}"   # pad to width from a variable
f"{o(mid(n.y)):>6}" # right-align to width 6
f"{t:.{the.decs}f}" # decimal places from a variable
```

The `{x:{width}}` syntax means "format x using a
width that is itself computed at runtime."

---

## 21. `yield from` (Generator Delegation)

Delegates to a sub-generator, forwarding all its
values.

```python
def treeNodes(tree, lvl=0, pre=""):
  if tree:
    yield tree, lvl, pre
    if "col" in tree:
      for kid, txt in ...:
        yield from treeNodes(kid, lvl+1, ...)
```

Without `yield from`, you'd need:

```python
for item in treeNodes(kid, lvl+1, ...):
  yield item
```

---

## 22. The OBJ Class

One line wires three magic methods to make dicts
behave like objects.

```python
class OBJ(dict):
  __getattr__  = dict.__getitem__  # obj.x  → obj["x"]
  __setattr__  = dict.__setitem__  # obj.x=1→ obj["x"]=1
  __repr__     = o                 # print  → o(obj)
```

Now `obj.mu` and `obj["mu"]` are the same thing.
You get dot notation *and* all dict methods
(`.keys()`, `.update()`, `in` operator).

---

## 23. Duck Typing for Polymorphism

No class hierarchy. The `.it` field tags what kind
of thing an object is:

```python
if SYM  is col.it: ...  # symbolic column
if NUM  is col.it: ...  # numeric column
if DATA is i.it:   ...  # dataset
```

And structural checks on dict keys:

```python
if "col" in tree:  # internal node (has a split)
```

This replaces inheritance with simple identity
checks and key lookups.

---

## 24. Factory Functions (not Classes)

Capitalized functions return configured `OBJ`s.

```python
def NUM(**d):
  return OBJ(it=NUM, **d, n=0, mu=0, m2=0)

def SYM(**d):
  return OBJ(it=SYM, **d, n=0, has={})
```

The `**d` splat carries keyword arguments straight
through. So when `COL` calls:

```python
def COL(at=0, txt=" "):
  return what(txt)(at=at, txt=txt, goal=txt[-1]!="-")
```

...the `at=`, `txt=`, `goal=` keywords arrive in
`NUM` (or `SYM`) as `**d` and get merged with the
defaults like `n=0, mu=0`.

Note that if we just calle `NUM()` or `SYM()` the `**d` would be `{}` so we would get
get a simple struct that could be used to sumamrize any stream of numbers or symbols:

- and that simpler struct does not worry about things it needs not, like  column header or column position.


`COLS` decodes a full header row to decide which
columns are x (independent) vs y (dependent):

```python
x = [c for c in cols if c.txt[-1] not in "-+!X"]
y = [c for c in cols if c.txt[-1]     in "-+!"]
```

Column name suffixes drive everything: `Lbs-`
means minimize, `Mpg+` means maximize, `HpX`
means ignore.

```
┌─ TRY THIS ───────────────────────────────────┐
│ from ez import *                             │
│ data = DATA(csv('auto93.csv'))               │
│ for c in data.cols.x: print('x:', c.txt)     │
│ for c in data.cols.y: print('y:', c.txt)     │
│                                              │
│ # Why is HpX not in either list?             │
│ # Why is Lbs- in y but not x?                │
└──────────────────────────────────────────────┘
```

---

## 25. Function Metadata

Python functions carry inspectable attributes.

```python
fun.__doc__           # docstring
fun.__name__          # "eg__csv"
fun.__annotations__   # {"f": <function filename>}
```

`ez.py` uses all three to build its CLI:

```python
# __doc__ for help text
print(f"  -{s:<12}{fun.__doc__.strip()}")

# __annotations__ to count and type args
run(f, *[t(next(args))
         for t in f.__annotations__.values()])

# __name__ via globals() to find eg_* functions
for k, fun in globals().items():
  if k.startswith("eg_"): ...
```

A function with one annotation eats one CLI arg.
Zero annotations means no args needed.

---

## 26. `__name__ == "__main__"`

The standard Python guard.

```python
if __name__ == "__main__": main(the, globals())
```

When you `import ez`, `__name__` is `"ez"` and
`main()` doesn't run — the file is a library.
When you `python3 ez.py`, `__name__` is
`"__main__"` and the CLI activates.

---

## 27. Separation of Concerns: Data Pipeline

`DATA` doesn't know where rows come from.

```python
# From a file (lazy, streaming):
data = DATA(csv("auto93.csv"))

# From memory (list of rows):
data = DATA([headers] + rows)
```

The chain: `DATA` → `adds` → `add` → column
updates. Each layer only talks to the next.
`DATA` never opens a file. `csv` never touches
columns. `add` never knows about files or lists.

---

## 28. Incremental Update and Undo

`add` updates column stats one value at a time.
`sub` reverses it by passing `w=-1`.

```python
def sub(i, v): return add(i, v, -1)

def add(i, v, w=1):
  if v != "?":
    i.n += w
    if NUM is i.it:
      d = v - i.mu
      i.mu += w * d / i.n
      i.m2 += w * d * (v - i.mu)
```

Add rows to a dataset, then remove them, and the
statistics stay correct. Essential for streaming
and cross-validation.

---

## 29. Composite Pattern

Functions that recurse over their parts. The outer
function handles collections; the inner function
handles one element.

| Outer       | Inner    | Does what?             |
|-------------|----------|------------------------|
| `adds`      | `add`    | update stats           |
| `likes`     | `like`   | log-likelihood         |
| `distx`     | `aha`    | feature-space distance |
| `mids`      | `mid`    | central tendency       |
| `o` (lists) | `o`(atom)| pretty print           |

Example — `likes` loops over columns, `like` scores
one column:

```python
def likes(data, row, nall, nh):
  prior = (len(data.rows)+the.m) / (nall+the.m*nh)
  out = log(prior)
  for col in data.cols.x:
    if (v := row[col.at]) != "?":
      out += log(like(col, v, prior))
  return out
```

---

## 30. Coercion Pipeline: csv and cast

Raw CSV data is all strings. `cast` tries converters
in order until one works.

```python
CASTS = [int, float,
  lambda s: {"true":1,"false":0}.get(s.lower(), s)]

def cast(s):
  for f in CASTS:
    try: return f(s)
    except ValueError: ...
```

`"42"` → tries `int("42")` → succeeds → `42`.
`"3.14"` → `int` fails, `float` succeeds → `3.14`.
`"red"` → `int` fails, `float` fails, lambda
returns `"red"` unchanged.

---

## 31. Welford's Online Algorithm

Single-pass incremental mean and variance. No need
to store all values.

```python
d = v - i.mu             # deviation from OLD mean
i.mu += w * d / i.n      # update mean
i.m2 += w * d * (v - i.mu)  # uses NEW mean
```

`i.m2` tracks the sum of squared deviations.
Standard deviation:

```python
def sd(num):
  return 0 if num.n < 2 else sqrt(num.m2/(num.n-1))
```

The `n-1` is Bessel's correction (unbiased estimate
from a sample).

```
┌─ TRY THIS ───────────────────────────────────┐
│ from ez import *                             │
│ nums = adds(gauss(10,1) for _ in range(1000))│
│ print('mu:', round(nums.mu, 2))              │
│ print('sd:', round(sd(nums), 2))             │
│                                              │
│ # mu should be near 10, sd near 1.           │
│ # Try changing gauss(10,1) to gauss(50,5).   │
└──────────────────────────────────────────────┘
```

---

## 32. Entropy (Shannon)

Measures the "surprise" in symbolic data.

```python
def ent(sym):
  return -sum(p*log(p,2)
    for n in sym.has.values()
    if (p := n/sym.n) > 0)
```

If one symbol dominates, entropy → 0 (predictable).
If all symbols equally likely, entropy is maximized
(maximum uncertainty). Units are bits.

---

## 33. CDF-Based Normalization

A common need: map raw values to the range 0..1.
Min/max scaling is fragile — one outlier at 99999
squashes everything else near zero. `ez.py` uses
a smarter approach based on how likely a value is.

**Background: PDF and CDF.** A probability density
function (PDF) gives the *shape* of a bell curve —
tall near the mean, low at the tails. But we don't
need the shape. We need the *cumulative* probability:
"what fraction of the data is below this value?"
That's the CDF (cumulative distribution function).

The CDF maps any value to a number between 0 and 1:
a value at the mean → 0.5 (half the data is below).
A value 2 standard deviations above → ~0.98.
Two standard deviations below → ~0.02.

`ez.py` approximates the Gaussian CDF in two steps.

Step 1 — z-score (how many SDs from the mean):

```python
def z(num, v):
  return max(-3, min(3,
    (v - num.mu) / (sd(num) + 1/BIG)))
```

Clamped to [-3, 3] because values beyond 3 standard
deviations are extreme outliers (less than 0.3% of
normal data).

Step 2 — sigmoid maps z-score to (0, 1):

```python
def norm(num, v):
  return 1 / (1 + exp(-1.7 * z(num, v)))
```

This is a logistic curve that approximates the
Gaussian CDF. The 1.7 stretches it so ±3σ maps
close to 0 and 1:

```
  z   | norm(z)
 -----+--------
  -3  |  0.006   ← very low value → near 0
  -1  |  0.154
   0  |  0.500   ← mean → exactly 0.5
  +1  |  0.846
  +3  |  0.994   ← very high value → near 1
```

**Why not min/max?** If `Lbs` ranges from 1600 to
5000 but one car weighs 9999, min/max scaling
squashes the useful range. CDF-based normalization
uses the *distribution*, so outliers barely matter.

---

## 34. Aha Distance (Heterogeneous)

Real data mixes numbers and symbols. The `aha`
function (named after David Aha's instance-based
learning) handles both, under two key assumptions:

**Assumption 1:** Everything is mapped to 0..1
first, so numeric and symbolic distances are
comparable.

**Assumption 2:** Missing values assume the worst
case — if we don't know something, assume
maximum distance.

```python
def aha(col, u, v):
  if u == v == "?": return 1       # both unknown
  if SYM is col.it: return u != v  # 0 or 1
  u, v = norm(col, u), norm(col, v)
  u = u if u != "?" else (0 if v > 0.5 else 1)
  v = v if v != "?" else (0 if u > 0.5 else 1)
  return abs(u - v)
```

For symbolics: same = 0, different = 1.
For numerics: normalize both to 0..1 via `norm`,
then take the absolute difference.
For missing values: if the known value is high
(> 0.5), assume the unknown is 0 — maximizing the
gap. Conservative: don't pretend to know what you
don't.

---

## 35. Minkowski Distance

Generalized distance that unifies Manhattan (p=1),
Euclidean (p=2), and Chebyshev (p→∞).

```python
def minkowski(items):
  n, d = 0, 0
  for item in items:
    n, d = n+1, d + item ** the.p
  return 0 if n == 0 else (d / n) ** (1 / the.p)
```

Dividing by `n` makes distance independent of how
many features exist — fair comparison across
datasets with different dimensionality.

---

## 36. Distance to Heaven (Multi-Objective)

Combines multiple goals into one score.

```python
def disty(data, row):
  return minkowski(
    (norm(y, row[y.at]) - y.goal)
    for y in data.cols.y)
```

Each y-column has `.goal`: `True` (=1) for maximize
(`+` suffix), `False` (=0) for minimize (`-`). The
"heaven point" is where every goal is met. `disty`
measures how far a row is from heaven.
**Lower = better.**

Example with `auto93.csv` (goals: `Lbs-`, `Acc+`,
`Mpg+`):

```
A heavy gas-guzzler:  disty ≈ 0.79 (far from heaven)
A light efficient car: disty ≈ 0.20 (close to heaven)
```

The `nearest`, `furthest`, and `order` functions
use feature-space distance (`distx`) to find
similar rows:

```python
def order(data, r1, rows):
  return sorted(rows,
                key=lambda r2: distx(data, r1, r2))

def nearest(*args):  return order(*args)[0]
def furthest(*args): return order(*args)[-1]
```

`order` sorts all `rows` by distance from `r1`.
`nearest` takes the front (closest).
`furthest` takes the end (most distant).

```
┌─ TRY THIS ─────────────────────────────────--──┐
│ from ez import *                               │
│ data = DATA(csv('auto93.csv'))                 │
│ r = data.rows[0]                               │
│ print('row:', r[:3], '...')                    │
│ print('disty:', round(disty(data, r), 3))      │
│ best = min(data.rows,                          │
│            key=lambda r: disty(data, r))       │
│ print('best:', best)                           │
│ print('disty:', round(disty(data,best), 3))    │
│                                                │
│ # What makes the best row 'best'?              │
│ # Look at Lbs, Acc, Mpg — does it make sense?  │
└────────────────────────────────--──────────────┘
```

---

## 37. Sampling: `gauss` and `pick`

`gauss` approximates a normal distribution via the
Central Limit Theorem — sum 3 uniforms, shift,
scale.

```python
def gauss(mu, sd1):
  return mu + 2*sd1*(sum(random.random()
                         for _ in range(3)) - 1.5)
```

`pick` does weighted random selection from a dict.
Given `{"a": 4, "b": 2, "c": 1}` with total 7,
it picks `"a"` about 4/7 of the time, `"b"` about
2/7, `"c"` about 1/7.

```python
def pick(d, n):
  n *= random.random()
  for k, v in d.items():
    if (n := n - v) <= 0: return k
```

Walk through: say `n=7`, `random()=0.3`, so
`n = 7*0.3 = 2.1`. Subtract `a`'s count (4):
`2.1 - 4 = -1.9 ≤ 0` → pick `"a"`.
If `random()=0.8`, `n = 5.6`. Subtract 4 → 1.6.
Subtract 2 → -0.4 ≤ 0 → pick `"b"`.

---

## 38. Bayesian Classification

`like` computes the likelihood of a value given a
column's distribution.

For numerics — Gaussian probability density:

```python
var = sd(col)**2 + 1/BIG
return (1/sqrt(2*3.14159*var)) * exp(
       -((v - col.mu)**2) / (2*var))
```

For symbolics — frequency with Laplace smoothing:

```python
n = col.has.get(v, 0) + the.k * prior
return max(1/BIG, n / (col.n + the.k))
```

**What are `the.k` and `the.m`?** These are
smoothing hacks that prevent zero probabilities
from killing the entire calculation.

`the.k` (default 1) is the attribute smoother.
Without it, a symbol never seen in training data
has frequency 0, and since `likes` multiplies
probabilities across columns, one zero wipes out
everything. Adding `the.k * prior` gives unseen
values a tiny non-zero probability proportional to
the class size.

`the.m` (default 2) is the class prior smoother,
used in `likes`:

```python
prior = (len(data.rows) + the.m) / (nall + the.m*nh)
```

Here `nh` is the number of hypothesis classes.
`the.m` nudges small classes away from zero
probability. With `the.m = 2` and 3 classes, even
an empty class gets prior ≈ 2/(n+6) instead of 0.

`likes` combines column likelihoods via log-sums
(adding logs instead of multiplying tiny floats
avoids underflow to zero):

```python
out = log(prior)
for col in data.cols.x:
  if (v := row[col.at]) != "?":
    out += log(like(col, v, prior))
```

---

## 39. Spread Trees

`TREE` builds a decision tree that minimizes the expected
value of the 
**spread** in the leaves.

- Aside: expected value means ``weeighted sum``.
- So a pair of divisions of size 10 and 100 with spreads 0.9 and 0.1 have an expected value of 
  - (10\*0.9 + 100\*0.1)/110
- When considering multiple pairts divisions of the same thing, we can forget the denominator (since that will be a constant for all pairs of divisions)

Spread is measured by
`sd` for numeric targets and `ent` (entropy) for
symbolic targets — whichever `spread()` returns
for the column type.

```python
w = sum(
  len(s) * spread(adds(disty(data,r) for r in s))
  for s in [left, right])
```

For each candidate split, compute the weighted
spread of both sides. Pick the split with smallest
total.

This is *not* limited to classification or
regression. Since `spread()` dispatches on column
type, the same tree code works for any target:
class labels, continuous values, or `disty` scores
(a continuous score combining multiple goals into
one number). The tree doesn't care what it's
minimizing the spread of.

Recursion stops when a node has fewer than
`2 * the.leaf` rows. Each leaf stores `mids`
(central tendency of y-columns), enabling prediction
via `treeLeaf`.

```
┌─ TRY THIS ───────────────────────────────────┐
│ from ez import *                             │
│ random.seed(1)                               │
│ data = DATA(csv('auto93.csv'))               │
│ rows = shuffle(data.rows)[:50]               │
│ tree = TREE(clone(data, rows), rows)         │
│ treeShow(tree)                               │
│ print('features used:', treeUsed(tree))      │
│                                              │
│ # How many of the 4 x-columns get used?      │
│ # Which branch has the lowest disty (= best)?│
│ # What do the Lbs/Acc/Mpg values look like   │
│   for the best leaf vs the worst?            │
└──────────────────────────────────────────────┘
```
