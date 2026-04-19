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


# ez_class.py — Tutorial

---

# Part 1: Idioms

---

## 1. Walrus Operator `:=` mid-expression

Assigns a variable *and* uses it in the same expression.

```python
return -sum(p*log(p,2) for k in i if (p:=i[k]/n)>0)
```

`p` is assigned `i[k]/n`, tested `>0`, then used in `p*log(p,2)` —
all in one pass. Equivalent longhand:

```python
total = 0
for k in i:
    p = i[k] / n
    if p > 0:
        total += p * log(p, 2)
return -total
```

---

## 2. Docstring as Config Store

```python
the = o(**{k:cast(v) for k,v in re.findall(r"(\S+)=(\S+)", __doc__)})
```

The module docstring contains lines like `  -s seed=1`. The regex
finds every `key=value` pair, casts them to int/float/str, and builds
a config namespace. So `the.seed == 1`. To change a default, edit
the docstring — the code follows automatically.

---

## 3. Reservoir Sampling in `Num.add`

Keeps a fixed-size random sample of a stream without storing all of it.

```python
if len(i) < i.mx:
    insort(i, v)
elif r() < i.mx/i.seen:
    i.pop(int(r()*len(i)))
    insort(i, v)
```

Once the buffer is full, each new value has probability `mx/seen` of
replacing a random existing value. The result is a sorted uniform
random sample of at most `mx` items, regardless of stream length.

---

## 4. `next(items := iter(items))`

```python
i.cols = Cols(next(items := iter(items)))
[i.add(row) for row in items]
```

- `iter(items)` wraps the input as an iterator (harmless if already one)
- `:=` rebinds `items` to that iterator
- `next(...)` pops the *header row* for `Cols`
- The remaining rows are still in `items` for the list comp below

One expression consumes the header and advances the cursor.

---

## 5. Lambda as `__repr__`

```python
__repr__ = lambda i: str(i.names)
```

Equivalent to `def __repr__(self): return str(self.names)`. Python
just needs a callable bound to the dunder name. The parameter is
`i` not `self` — a consistent style choice throughout the file.

---

## 6. `col()` — Naming Convention as Type Dispatch

```python
def col(s:str): return (Num if s[0].isupper() else Sym)()
```

Column *names* encode their type: `"Weight"` → `Num`, `"color"` → `Sym`.
The `()` at the end calls whichever class was chosen, returning a
fresh instance. Convention doing the work of a type annotation.

---

## 7. Annotations as Runtime Coercers in `main()`

```python
def eg_s(n:int): the.seed=n; random.seed(n)

f(*[make(args.pop(0)) for make in f.__annotations__.values()])
```

`f.__annotations__` returns `{'n': int}`. The code uses `int` (the
type hint) *as a function* to cast the raw `sys.argv` string.
Type hints here do double duty: documentation *and* arg parsing.

---

# Part 2: Concepts Newbies Find Confusing

---

## Column Naming Conventions

Column names are not just labels — they control behavior:

| Suffix | Meaning                          | Goes into    |
|--------|----------------------------------|--------------|
| `+`    | y-goal, maximize                 | `cols.y`     |
| `-`    | y-goal, minimize                 | `cols.y`     |
| `!`    | class label (for Bayes etc.)     | `cols.klass` |
| `X`    | ignore this column               | neither      |
| upper  | numeric (`Num`)                  | `cols.x`     |
| lower  | symbolic (`Sym`)                 | `cols.x`     |

Everything without a special suffix goes into `cols.x` as a predictor.

---

## "Heaven" and `disty`

"Heaven" is the ideal point: all goals simultaneously at their best.
`disty` measures how far a row falls short of heaven:

```python
def disty(i, r:Row) -> float:
    return minkowski(c.norm(r[at]) - i.cols.w[at]
                     for at,c in i.cols.y.items())
```

`cols.w[at]` is `True` (1.0) for maximize (`+`) and `False` (0.0)
for minimize (`-`). After `norm`, a maximized column wants to be
near 1, so `norm(v) - 1` is near 0 when good. A minimized column
wants to be near 0, so `norm(v) - 0` is near 0 when good.
`sorty` floats the best rows to the top by sorting on `disty`.

---

## x cols vs y cols

`cols.x` are the *inputs* (predictors). `cols.y` are the *outputs*
(goals). Most methods that compute distance or likelihood use only
`cols.x` — because at prediction time you may not know the y values.
`disty` uses only `cols.y` — because it measures outcome quality.

---

## Why `log` in `like`

Naive Bayes multiplies many small probabilities:

```
P(class) * P(col1|class) * P(col2|class) * ...
```

Each factor may be 0.01 or smaller. With enough columns the product
underflows to zero (floating point can't represent it). Taking logs
converts multiplication to addition, which stays numerically stable:

```python
return log(prior) + sum(log(v) for v in ls if v>0)
```

The result is a log-likelihood. To compare classes you only need to
know which is *largest*, so the log transform is harmless.

---

## Laplace Smoothing (`the.m` and `the.k`)

What if a class has only 2 rows? Or a symbol value was never seen
in training? Raw frequency gives 0, and `log(0)` is undefined.

Smoothing adds a small pseudocount to avoid zeros:

```python
# Sym.like
return (i.get(v,0) + the.k*prior) / (n + the.k)

# Data.like
prior = (len(i.rows)+the.m) / (n_all+the.m*n_h)
```

`the.k=1` and `the.m=2` are classic defaults. They pull sparse
estimates gently toward the prior rather than leaving them at zero.

---

## Minkowski Distance and `p=2`

```python
def minkowski(items:Iterable) -> float:
    n=d=0
    for x in items: n,d = n+1, d+x**the.p
    return 0 if n==0 else (d/n)**(1/the.p)
```

With `the.p=2` this is Euclidean distance, averaged over columns
(the `d/n` normalizes for varying column counts). With `p=1` it
becomes Manhattan distance. Averaging not summing means distance
stays in `[0,1]` regardless of how many columns exist.

---

## `_mid` Cache with `or`

```python
def mid(i) -> Row:
    i._mid = i._mid or [c.mid() for c in i.cols.all.values()]
    return i._mid
```

`None or expr` evaluates `expr` only when `_mid` is `None`.
`add` and `sub` reset it to `None`, so the cache is invalidated
whenever the data changes. A cheap lazy-evaluation pattern.

---

## `pick`: Num vs Sym, and the Wrap-Around Trick

`pick` generates a mutated neighbor of a row — used in optimization
to explore nearby solutions.

**`Sym.pick`** samples uniformly from values already seen:

```python
def pick(i, _:Val=None) -> Val: return pick(i)   # weighted sample
```

Any seen symbol is a valid mutation. No notion of "nearby."

**`Num.pick`** perturbs the current value using random differences
drawn from existing samples:

```python
def pick(i, v:Qty=None) -> Val:
    result = (i.mid() if v is None or v=="?" else v) \
             + choice(i) - choice(i)
    lo, hi = i[0], i[-1]
    return lo + ((result - lo) % (hi - lo + 1E-32))
```

`choice(i) - choice(i)` is a symmetric random step whose size is
drawn from the actual data distribution — so large-range columns
take large steps and tight-range columns take small ones.

The **wrap-around** is the key safety device:
`(result - lo) % (hi - lo)` keeps the result inside `[lo, hi]`
by wrapping overshoots back from the other end. Without this,
repeated perturbations drift toward the boundaries and accumulate
there — the optimizer spends all its time "bumping into walls."
The tiny `1E-32` prevents division by zero when `lo == hi`.

---

# Part 3: Code Walkthrough

---

## Sorting and Searching

**`sorty`** — sort rows by distance to heaven (best possible y values)

```python
def sorty(i) -> "Data":
    i.rows.sort(key=lambda row: i.disty(row)); return i
```
Rows closest to ideal y values float to the top.

---

**`sortx`** — sort rows by distance to a reference row in x space

```python
def sortx(i, r:Row, rows:list[Row]) -> list[Row]:
    return sorted(rows, key=lambda r2: i.distx(r,r2))
```
Returns `rows` ordered nearest-to-furthest from `r`.

---

**`nearest` / `furthest`** — first and last of `sortx`

```python
def nearest(i,  r:Row, rows:list[Row]) -> Row: return i.sortx(r,rows)[0]
def furthest(i, r:Row, rows:list[Row]) -> Row: return i.sortx(r,rows)[-1]
```
Convenience wrappers. `nearest` is used heavily in active learning.

---

## Summarizing Columns: `mid`, `spread`, `norm`

**`mid`** — central tendency. Median for `Num`, mode for `Sym`.

```python
def mid(i) -> float: return i[len(i)//2] if i else 0   # Num
def mid(i) -> Val:   return max(i, key=i.get)           # Sym
```

---

**`spread`** — diversity. IQR-like range for `Num`, entropy for `Sym`.

```python
# Num: robust spread via 10th-90th percentile range
return (i[a]-i[b])/2.56

# Sym: entropy
return -sum(p*log(p,2) for k in i if (p:=i[k]/n)>0)
```
Both measure "how spread out" without being thrown off by outliers.

---

**`norm`** — rescale a `Num` value to `[0,1]`

```python
a,b = i[int(.05*len(i))], i[int(.95*len(i))]
return 0 if a==b else max(0, min(1, (v-a)/(b-a)))
```
Uses 5th–95th percentile as lo/hi to resist outlier distortion.

---

## Delegation: `Data` → `Num`/`Sym`

Each `Data` method loops over columns and calls the same-named
method on each col. `Num` and `Sym` share the protocol.

---

**`add` / `sub`**

```python
def add(i, row:Row) -> Row:
    for at,c in i.cols.all.items(): c.add(row[at])
    i.rows.append(row); return row
```
`Num.add` does reservoir sampling. `Sym.add` increments a count dict.
`sub` is the mirror — enables incremental delete.

---

**`mid` (Data level)**

```python
def mid(i) -> Row:
    i._mid = i._mid or [c.mid() for c in i.cols.all.values()]
    return i._mid
```
Lazily cached. Returns one representative value per column.
Cache invalidated by `add`/`sub` setting `i._mid = None`.

---

**`distx`** — x-space distance between two rows

```python
def distx(i, r1:Row, r2:Row) -> float:
    return minkowski(c.distx(r1[at],r2[at]) for at,c in i.cols.x.items())
```
Delegates per-column distance to `Num.distx` or `Sym.distx`,
then combines via Minkowski (default: Euclidean, `p=2`).

---

**`disty`** — distance from a row to heaven

```python
def disty(i, r:Row) -> float:
    return minkowski(c.norm(r[at]) - i.cols.w[at]
                     for at,c in i.cols.y.items())
```
`cols.w[at]` is `1` (maximize) or `0` (minimize). See concept note
on "Heaven" above.

---

**`like`** — naive Bayes log-likelihood of a row belonging to this Data

```python
def like(i, row:Row, n_all:int, n_h:int) -> float:
    prior = (len(i.rows)+the.m) / (n_all+the.m*n_h)
    ls = [c.like(v,prior) for at,c in i.cols.x.items()
          if (v:=row[at])!="?"]
    return log(prior) + sum(log(v) for v in ls if v>0)
```
Delegates to `Num.like` (Gaussian) or `Sym.like` (frequency).
Uses log to avoid underflow. `the.m` smooths sparse class counts.

---

**`pick`** — mutate a row by randomly perturbing some x columns

```python
def pick(i, row=None, n=1) -> Row:
    if not row: return [c.pick() for c in i.cols.all.values()]
    s, k = row[:], n if n > 0 else len(i.cols.x)
    for at, c in random.sample(list(i.cols.x.items()),
                                min(k, len(i.cols.x))):
      s[at] = c.pick(s[at])
    return s
```
`Num.pick` perturbs with wrap-around to stay in range.
`Sym.pick` samples from seen values. See concept note above.

---

## Factory: `col()` and `Cols`

**`col()`** — name convention dispatches to `Num` or `Sym`

```python
def col(s:str): return (Num if s[0].isupper() else Sym)()
```
Uppercase first letter → `Num`. Lowercase → `Sym`.

**`Cols`** — organizes all columns into roles

```python
i.x  = {at:c for at,c in i.all.items() if at not in i.w ...}
i.y  = {at:i.all[at] for at in i.w}
i.klass = next((at for at,s in enumerate(names) if s[-1]=="!"), None)
```
`x` = independent cols, `y` = goal cols (marked `+`, `-`),
`klass` = classification target (marked `!`).
