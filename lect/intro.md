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


# Software Engineering as Choice: A Multi-Objective Perspective
## Act 1: The Challenge
### 1.1 Your Lecturer's Insane Claim

<img align=right width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/a5211fef-c05c-442d-be99-98a8d87b04dd" />

> **Has your lecturer lost it?  He thinks LLMs might not be the greatest
thing since sliced toast. **

He says: 

- **LLMS have some interesting application areas"
- but industrially, **LLMs are economically failing (see below) and we need simpler approaches.**
 - not for generative tasks
 - but for everything else we want to do with AI (e.g. see below:  multi-objective choice)

#### The Evidence: "Cause we need a better AI"

[Dells CES 2026 chat was the most pleasingly un-AI briefing I've had in maybe 5 years](https://www.pcgamer.com/hardware/dells-ces-2026-chat-was-the-most-pleasingly-un-ai-briefing-ive-had-in-maybe-5-years).

**Bubble bursting in "big data" AI?**

- Unlike standard software, **exponential costs per new user**
- Unless usage rate limited (bad for keeping new users)
- **ChatGPT**: A mere 2% to 8% conversion free to paid users
  [2]
- Established companies: **95% of AI apps not returning
  revenue** [3]
- **Microsoft**: Copilot costing Msoft $X00 per user [1]

**What's failing?** [3]

- Support tools for groups, for negotiation
- Integration into organizational workflows

**What's working:** Support tools for individuals (e.g.
Copilot)

- But the improvements are **modest: +/-20%** [5] or
  **negative** [4][6]

**References for this slide:**

- [1] AI Startups Are Bad Businesses, Sept 2025
- [2] McKinsey report, 2025
- [3] MIT NANDA, July 2025
- [4] GitClear, 2024
- [5] Does AI Boost Productivity? 2025
- [6] METR July 2025

### 1.2 The Hypothesis

**Your lecturer's claim:** "Maybe simpler is better than
bigger, more complex AI."

> **But is he just a cranky old professor who doesn't get modern AI?**

### 1.3 Course Framing

**Let's check empirically.**

We'll look at a particular SE problem—**CHOICE**—and
systematically study every major algorithm for exploring
choices, including:

- His ultra-simple tools
- The fancy modern stuff
- Everything in between

> **By semester's end, YOU decide what works.**

---

## Act 2: The Problem Space

### 2.1 Software Engineering as Multi-Objective Choice

MOOT enables data mining research for trading off multiple
user goals such as:

- **Better, faster, cheaper**: fewer bugs, less time, less
  cost
- **Performance vs. sustainability**: faster response, less
  energy
- **Hyperparameter optimization**: finding learner parameters
  that minimize false alarms and maximize recall

Formally, these are **multi-objective configuration
optimization tasks** [49].

**Problem Statement**: Configuration optimization seeks
<tt>c* &isin; C</tt> optimizing multiple objectives (e.g.,
maximize database throughput, minimize energy). Given
<tt>f : C &rarr; R<sup>M</sup></tt> mapping configurations to
performance metrics:

<pre>
c* = argmax<sub>c &isin; C</sub> f(c)
</pre>

### 2.2 The Three Core Obstacles

Modern software has extensive configurability, but tuning
parameters critically affect performance [18]. For example,
Storm's defaults yield **480× performance degradation** vs.
optimal parameters [34].

Such poor performance is hardly surprising since industrial
optimization faces major obstacles:

**1. Exponential Explosion**

Configuration spaces explode exponentially. In 7z: 14
parameters with one million possible configurations.

**2. Rugged Landscapes**

Performance landscapes are rugged and sparse [15, 27, 45],
creating local optima traps that mislead simple search
strategies.

**3. Costly Evaluation**

Evaluation is expensive: x264's 11 parameters need 1,536 hours
to explore [67], limiting budgets to dozens of evaluations
[14, 54].

Krishna et al. report that these obstacles result in the
delivery of suboptimal products [43].

### 2.3 The Scale Challenge

The space of possible configurations seems too large to
explore. For example, MySQL's 460 binary options generate
<tt>2<sup>460</sup></tt> configurations—more than the
<tt>2<sup>80</sup></tt> stars in the observable universe [17].

### 2.4 Understanding MOOT Data Format

> **Before we see if simplicity works, you need to understand
the data you'll work with all semester.**

#### What is MOOT?

[http://tiny.cc/moot](http://tiny.cc/moot)

To the best of our knowledge, MOOT is the largest and most
varied collection of real multi-objective optimization tasks
in SE [49].

MOOT's datasets come from:

- Published SE studies
- Real performance logs
- Cloud systems
- Defect predictors
- Tuning tasks where bad configurations cost time, money, and
  credibility

#### Example: The xomo_flight Dataset

**First, the raw data structure:**

```
PREC, FLEX, RESL, TEAM, PMAT, rely, ..., PCAP, ... | Effort-, Months-, Defects-, Risks-
3.72, 4.05, 4.38, 3.29, 4.68, 3.52, ..., 4.18, ... | 1287.3,  32.4,    143,     2.8
2.48, 3.52, 5.48, 4.05, 3.18, 4.96, ..., 3.29, ... | 892.1,   28.9,    98,      1.9
4.24, 5.07, 3.84, 2.76, 5.32, 2.95, ..., 5.43, ... | 2103.6,  38.7,    287,     4.2
...  (9,997 more rows)
```

**Key properties:**

- **24 input variables** (x): PREC (precedentness: experience with silimar projects), FLEX, RESL, TEAM, PMAT (process maturity),
  rely (required reliability), data, cplx, time, stor, virt, turn, acap, aexp, PCAP (prograppmer capability),
  vexp, lexp, modp, tool, sced, site, FLEx, RUSE, PVOL
- **4 goal variables** (y): Effort-, Months-, Defects-, Risks-
- **10,000 scenarios** of flight software development
- Goals marked with `-` means minimize (lower is better)

**The challenge:** 24 variables = massive configuration space.
How do we find the best settings?

#### Six Key Properties of MOOT Format

As seen in that figure:

1. **MOOT datasets are tables** with <tt>x</tt> inputs and
   <tt>y</tt> goals.

2. **The first row** shows the column names.

3. **The other rows** show examples of a <tt>y = f(x)</tt>
   relation.

4. **Numerics start with uppercase** letters, all else are
   symbolic.

5. **Goal columns** (e.g. `Throughput+`, `Latency-`) use
   `+`/`-` to denote maximize and minimize.

6. **Columns with uppercase "X"** at the end of their names
   are to be ignored by the inference.

> **This format is intentionally simple - you can read it,
process it, and reason about it without complex tooling.**

#### MOOT Dataset Characteristics

Table 1 of [49] shows the current 120+ tasks in MOOT. Each
task has:

- **One to 11 goals** (median = 3)
- **3 to 10,044 input variables** (median = 11)
- **100 to over 100,000 instances** (median = 10,000)

The last few rows of Table 1 show non-SE datasets. These are
useful for explaining MOOT to visitors from other fields of
research.

---

## Act 3: Evidence for Simplicity

### 3.1 Humans Overlook Simplicity

**From Nature journal (2021):**

> People systematically overlook subtractive changes.

**The  experiment:**

- Task: Design a logo (make symmetrical). Could be done by
   -  adding green to other corners.
   -  subtracting green from top left

<img width="425" height="421" alt="image" src="https://github.com/user-attachments/assets/25fbb7d7-3608-427d-ad4d-5b95a23b6109" />
  
- Task: Keep a block height "I" above ground. Could be done by
  - adding 3 copies of the existing tower, then  building a table with 4 legs (one leg per tower)
  - subtracting that tiny decorative collat underneath the top train.

<img width="473" height="442" alt="image" src="https://github.com/user-attachments/assets/8fbc8528-26e2-41e0-94e6-6f6fbcf224a5" />

- Result: **1155 additive ideas and only 297 subtractive**

**We're cognitively biased toward adding, not simplifying.**

<img width="1200" height="630" alt="image" src="https://github.com/user-attachments/assets/eaddd164-5358-4a0f-b13a-f2a47d0e75f6" />


This matters because engineering is about finding elegant
solutions, not just functional ones.

### 3.2 Why Simpler Matters

**Why is simpler important?**

- **Reduce** CPU
- Reduce the cost of model building (cost of local hardware
  or cloud)
- Less **energy** consumption
- Less cost to buy that energy
- Less **pollution** to make energy
- Simpler explanation
- Simpler customization of **system**
- Quicker more effective training
- Easier **maintenance**
- Solution being more trustable
- Quicker **experimentation**
- Faster, more easier reproducibility
- **Cause it is possible** (see next slide)

### 3.3 Simplicity Has a Long History

**"Simplicity is possible"**

A timeline of simplification techniques:

**Early Foundations:**

- **1902, PCA**: reduce data to a few principal components
- **1960s, Narrows**: guide search via a few key variables
- **1974, Prototypes**: speed up k-NN by reducing rows to a
  few exemplars
- **1984, JL lemma**: random projection to <tt>k = O(&epsilon; <sup>-2</sup> log n)</tt> dimensions can preserve pairwise
  distances to within some error <tt>(&plusmn; &epsilon;)
  </tt>

**The 1980s-1990s:**

- **1986, ATMS**: only focus diagnosis on core assumptions
- **1994, ISAMP**: a few restarts explore large problems
- **1996, Sparse coding**: learn efficient, sparse
  representations from data which inspired dictionary learning
  and sparse autoencoders

**Modern Era:**

- **1997, Feature selection**: ignore 80%+ features
- **2005, Semi-supervised learning**: data can be
  approximated on a much lower-dimensional manifold
- **2009, Active learning**: use just most informative rows
- **2003–2021, SE "keys"**: a few parameters govern many SE
  models

**Recent Advances:**

- **2010+, Surrogates**: first, build small models to label
  the rest of the data
- **2020s, Distillation**: compress large LLM models with
  little performance loss

> **The pattern:** For over a century, researchers have found
that complex problems often have simple structure hiding
inside them.

---

## Act 4: Does Simplicity Actually Work?

### 4.1 Example 1: Drastic Simplification

**"Let's run a simple explainable AI tool on xomo_flight:"**

Consider the `xomo_flight` dataset:

- 10,000 scenarios of flight software development
- 24 independent variables (inputs)
- 4 conflicting objectives (Minimize Effort, Months, Defects,
  Risks)

```bash
./xai.py -l 4 --tree ~/gits/moot/optimize/process/xomo_flight.csv
```

**Output:**

```
                                 score   N    EFFORT-, MONTHS-...
                                 -----   ---  -------------------
.                              : 0.5   : 25 : 1119.0, 30.6, ...
FLEx >= 4.428                  : 0.27  :  4 : 786.7, 27.5, ...
FLEx < 4.428                   : 0.55  : 21 : 1182.3, 31.2, ...
| 2.67 <= RUSE < 3.19          : 0.29  :  4 : 819.6, 28.3, ...
| RUSE < 2.67 or RUSE >= 3.19  : 0.61  : 17 : 1267.7, 31.8, ...
| | PCAP >= 4.805              : 0.36  :  5 : 893.1, 28.1, ...
| | PCAP < 4.805               : 0.71  : 12 : 1423.7, 33.4, ...
| | | RELY >= 4.82             : 0.5   :  4 : 1170.8, 31.2, ...
| | | RELY < 4.82              : 0.79  :  8 : 1550.2, 34.5, ...
{:uses 4 :x 24 :y 4 :rows 10_000 :lo 0.15 :mid 0.48 :win 84}
```

#### The Mic Drop Moment

**Drastic Simplification**: Despite having 24 variables to
choose from, the algorithm found that only 4 mattered:

- `FLEx` (Flexibility)
- `RUSE` (Reusability)
- `PCAP` (Programmer Capability)
- `RELY` (Required Reliability)

**High Performance**: By controlling just these 4 variables,
we achieve **84% of the optimal score** (`:win 84`).

**Understanding the output:**

- `:uses 4` = only 4 variables used (out of 24)
- `:x 24` = 24 input variables available
- `:y 4` = 4 goal variables
- `:rows 10_000` = 10,000 examples
- `:lo 0.15` = best possible score
- `:mid 0.48` = median score across all data
- `:win 84` = this tree achieves 84% of optimal

**The tree structure:**

- Root (`.`): baseline score 0.5
- Best path: FLEx >= 4.428 &rarr; score 0.27 (better is lower)
- Worst path: RELY < 4.82 &rarr; score 0.79 (needs
  improvement)

**The bottom line:**

- From 24 &rarr; 4 variables (**83% reduction**)
- While maintaining **84% performance**
- We don't need to manage 24 complex factors
- **We only need to manage the 4 "keys"**


---

## Act 5: Your Semester Roadmap

### 5.1 The Optimization Algorithm Timeline

> **Here's what we'll study, chronologically. Each represents a
different philosophy about how to explore the space of
choices.**

#### The Foundations (1950s-1970s)

**Random Search (1950s):** The essential baseline "sanity
check" to prove complex methods are actually adding value.
Despite its simplicity, random search remains surprisingly
competitive for high-dimensional problems.

**Hill Climbing (1950s):** The fundamental local search
strategy that iteratively moves to better neighbors. Simple
but gets trapped in local optima.

**Genetic Algorithms / GA (1975):** The grandfather of
evolutionary computation, using selection, crossover, and
mutation on bitstrings to evolve populations of solutions.

#### The Metaheuristic Era (1980s-1990s)

**Simulated Annealing / SA (1983):** A probabilistic technique
using "temperature" to accept worse solutions early on to
escape local optima. Inspired by metallurgy.

**Tabu Search (1986):** A metaheuristic using memory
structures (forbidden lists) to force exploration and avoid
cycling back to previously visited solutions.

**Genetic Programming / GP (1992):** Evolves actual parse
trees or source code (e.g., automated bug fixing) rather than
parameter vectors.

**Ant Colony Optimization / ACO (1992):** Uses pheromone
trails to solve path-based problems like test sequence
generation. Inspired by foraging ants.

**Particle Swarm Optimization / PSO (1995):** Simulates
flocking behavior (birds/fish) to move candidates through
continuous search spaces. Simple and effective.

**MaxWalkSat (1996):** A stochastic local search algorithm
combining greedy moves with random walks, essential for SAT
solving and constraint satisfaction.

**Differential Evolution / DE (1997):** A vector-based
evolutionary algorithm that optimizes continuous problems
using vector differences for mutation.

#### The Multi-Objective Revolution (2000s)

**SPEA2 (2001):** An early modern multi-objective algorithm
using "strength" values and nearest-neighbor density
estimation to maintain diversity.

**NSGA-II (2002):** The "gold standard" for multi-objective
optimization using non-dominated sorting and crowding distance
to find the Pareto frontier.

**IBEA (2004):** Optimizes quality indicators (like
Hypervolume) directly rather than relying solely on dominance
ranking.

**MOEA/D (2007):** Decomposes a multi-objective problem into
many scalar sub-problems and optimizes them simultaneously
using weight vectors.

#### The Modern Era: Model-Based Optimization (2010s-Present)

**GPM (2010s):** Gaussian Process Models, used within SMBO to
provide probabilistic predictions (mean and variance) for
expensive functions.

**TPE (2011):** Tree-structured Parzen Estimator, a Bayesian
approach for hyperparameter tuning that models <tt>p(x|y)</tt>
rather than <tt>p(y|x)</tt>.

**SMBO (2011):** Sequential Model-Based Optimization, a broad
class (including SMAC) that builds surrogates to choose the
next sample intelligently.

**FLASH (2017):** A sequential model-based optimizer that uses
decision trees (CART) to quickly find solutions with very few
evaluations [54]. Specifically designed for SE configuration.

**SWAY (2018):** A recursive spectral clustering method that
samples data to approximate the Pareto frontier [51]. Uses
eigenvalue analysis to find structure.

### 5.2 Course Structure

**Each week, we'll:**

1. Srudy the above algorithmS
2. Run some of them on the MOOT data
3. Compare it to baselines and prior methods
4. Build intuition for when each approach works

**By semester's end:**

- You'll have run experience on 120+ real problems
- You'll understand the trade-offs between simple and complex
- **You decide: does your lecturer's "simplicity" claim hold
  water?**

 
---

## Act 6: Research Directions from MOOT

### 6.1 Six Research Categories

Table 2 from [this paper](https://arxiv.org/pdf/2511.16882) presents a roadmap for future work using
MOOT data. Here are the six major categories.

All of you are invited to reflect on all of these. Grad students ahve a month at end of semester, with no other homework, to
work on any of these (or anything else they want, if they clear it with the professor first).

#### A. Core Optimization Strategies & Performance

How best to find good solutions?

**Key questions:**

- Sample size: What is the minimum budget for reliable
  optimization?
- Surprising Simplicity: What makes SE problems unique and so
  simple?
- Algorithms: Which AI optimization algorithms are best for
  MOOT data?
- Metrics: How do distance metrics (Euclidean, Hamming) affect
  performance?
- Causality: Does using causality (rather than just
  correlation) improve optimization?

#### B. Human Factors & Interpretability

Making solutions understandable and usable.

**Key questions:**

- Explanation: How can we (visually or otherwise) explain
  opaque optimization results?
- Trade-offs: What analytics best help humans understand the
  decision space (especially for 5+ objectives)?
- Bias: Does optimization routinely disadvantage certain
  social groups?
- Human Acceptance: Will humans accept recommendations, and do
  explanations change their minds?

#### C. Industrial Deployment & Adoption

Bridging the gap between research and practice.

**Key questions:**

- Problem Identification: How can we identify and validate
  high-impact industrial problems?
- Case Studies: What are the main barriers to applying these
  methods to real-world industrial systems?
- Data Collection: How can we incentivize and manage the
  collection of new industrial optimization datasets?
- Education: How to introduce newbies (in industry and
  academia) to these methods?

#### D. LLMs & Emerging AI Technologies

Foundation models and optimization.

**Key questions:**

- Distillation: Can few-labels approach guide LLM
  distillation?
- Configuration Generation: Can LLMs generate effective
  initial configurations?
- Explanation Translation: Can LLMs translate technical
  optimization results into domain-specific recommendations?
- Prompt Engineering as Configuration: Can MOOT techniques
  optimize LLM prompts as multi-objective configuration
  problems?
- LLM-Generated Surrogates: Can LLMs learn to approximate
  expensive evaluation functions?
- Meta-Learning: Can LLMs identify which optimization
  strategies work best for new problems?

#### E. Solution Quality & Generalizability

Understand solution reliability.

**Key questions:**

- Generalization: Any commonalities in MOOT-generated
  solutions?
- Transferability: Can we transfer knowledge between tasks, or
  must we start fresh?
- Stability: How stable are conclusions across stochastic
  multi-objective algorithms?
- Robustness: Robustness of results to noise, incomplete data,
  changing conditions?
- Uncertainty: Can we learn confidence intervals around our
  conclusions?

#### F. Future Directions

Exploring new domains and advanced concepts.

**Key questions:**

- Temporal: Reasoning across time. How to leverage the past?
  How (and when) to unlearn?
- Philosophical: Is solution space "flat" (many "near-maxima")
  so no single "truth"?
- Artificial General Intelligence: If we can learn, optimize,
  trade off goals, transfer knowledge to new domains—when does
  this become AGI?

### 6.2 Your Opportunities

**What MOOT enables:**

- 120+ datasets enable answering these questions **at scale**
- Move from toy problems to credible case studies
- Replicate and verify prior work
- Discover more general principles

**Community involvement:**

- MOOT is open source (MIT license)
- New datasets welcome via pull request
- Annual ICSE research events planned
- Expedited publication in Automated Software Engineering
  journal

**Your contribution:**

- Pick a research question from Table 2
- Test it across multiple MOOT datasets
- Publish results that generalize, not just work on 1-2
  examples

---

## Epilogue: Three Takeaways

### Key Messages

**1. SE is choice**

- Every configuration decision represents a point in a
  multi-dimensional space of competing objectives
- There's no single "right" answer, only trade-offs
- Optimization helps us understand those trade-offs

**2. Simple often beats complex (but not always)**

- xomo_flight: 4/24 variables achieve 84% optimal
- BASELINE: 40 labels &asymp; 160+ labels
- But we'll discover when simplicity fails
- That's why we test 20+ algorithms on 120+ problems

**3. You'll have the tools to decide**

- By semester end, you'll understand:
  * When to use random search vs. NSGA-II vs. FLASH
  * When more data helps vs. when it doesn't
  * How to apply these techniques to LLMs and beyond
- **Most importantly: you'll decide if your lecturer is insane
  or insightful**

### Practical Next Steps

**Get started today:**

Three levels of engagement:

1. **Basic**: Run existing scripts, explore results
2. **Intermediate**: Implement one algorithm, compare to
   baselines
3. **Advanced**: (Required for the grad students) Pick a research question from Table 2, test
   at scale

### The Meta-Question

This semester is an empirical investigation:

- Not about believing your lecturer
- Not about dismissing modern AI
- About **testing claims systematically**

Software engineering has always been about making informed
choices under uncertainty. Now you have 120+ real problems and
20+ algorithms to explore those choices.

> **Welcome to the laboratory. Let's find out what actually
works.**

---

## References

[1] https://www.youtube.com/watch?v=OYlQyPo-L4o AI Startups
    Are Bad Businesses, Sept 2025

[2] https://www.mckinsey.com/capabilities/quantumblack/our-
    insights/seizing-the-agentic-ai-advantage McKinsey report,
    2025

[3] https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_
    Business_2025_Report.pdf MIT NANDA, July 2025

[4] https://www.gitclear.com/coding_on_copilot_data_shows_ais_
    downward_pressure_on_code_quality GitClear, 2024

[5] https://www.youtube.com/watch?v=tbDDYKRFjhk Does AI Boost
    Productivity? 2025

[6] https://metr.org/blog/2025-07-10-early-2025-ai-
    experienced-os-dev-study/ METR July 2025

[14] Chen, J., Xu, N., Chen, P., & Zhang, H. (2021). Efficient
     compiler autotuning via bayesian optimization. In 43rd
     IEEE/ACM Int. Conf. Softw. Eng. ICSE 2021, Madrid, Spain,
     22-30 May 2021, pages 1198–1209.

[15] Chen, P., & Chen, T. (2026). PromiseTune: Unveiling
     causally promising and explainable configuration tuning.
     In Proc. of the 48th IEEE/ACM Int. Conf. Softw. Eng.

[17] Chen, T. (2025). Personal communication with author, at
     ICSE'25, Ottawa, Canada, May 2025. Regarding the results
     of the K-means++ experiment.

[18] Chen, T., & Li, M. (2023). Do performance aspirations
     matter for guiding software configuration tuning? an
     empirical investigation under dual performance
     objectives. ACM Trans. Softw. Eng. Methodol.,
     32(3):68:1–68:41.

[23] Easterby-Smith, M. (1980). The design, analysis and
     interpretation of repertory grids. International Journal
     of Man-Machine Studies, 13(1):3–24.

[27] Gong, J., & Chen, T. (2025). Deep configuration
     performance learning: A systematic survey and taxonomy.
     ACM Trans. Softw. Eng. Methodol.

[32] Herbold, S., Trautsch, A., Trautsch, F., & Ledel, B.
     (2022). Problems with szz and features: An empirical
     study of the state of practice of defect prediction data
     collection. Empir. Softw. Eng., 27(2):42.

[34] Jamshidi, P., & Casale, G. (2016). An uncertainty-aware
     approach to optimal configuration of stream processing
     systems. In Proc. 24th IEEE Int. Symp. Modeling, Analysis
     and Simulation of Computer and Telecommunication Systems.

[39] Kamei, Y., Shihab, E., Adams, B., Hassan, A. E., Mockus,
     A., Sinha, A., & Ubayashi, N. (2012). A large-scale
     empirical study of just-in-time quality assurance. IEEE
     Trans. Softw. Eng., 39(6):757–773.

[40] Kang, H. J., Aw, K. L., & Lo, D. (2022). Detecting false
     alarms from automatic static analysis tools: How far are
     we? In 44th Int. Conf. Softw. Eng.

[41] Kington, A. (2009). Defining Teachers' Classroom
     Relationships.

[43] Krishna, R., Yu, Z., Agrawal, A., Dominguez, M., & Wolf,
     D. (2016). The "BigSE" project: lessons learned from
     validating industrial text mining. In Workshop on BIG
     Data SE, page 65–71.

[45] Lustosa, A., & Menzies, T. (2024). Learning from very
     little data: On the value of landscape analysis. ACM
     TOSEM, 33(3):1–22.

[49] Menzies, T., Chen, T., Ganguly, K., Rayegan, A.,
     Srinivasan, S., Lustosa, A., & Vilkomir, K. (2025).
     MOOT: A repository of many multi-objective optimization
     tasks. arXiv:2511.16882. DOI:
     https://doi.org/10.5281/zenodo.17354083

[51] Nair, V., Menzies, T., Siegmund, N., & Apel, S. (2017).
     Using bad learners to find good configurations. In FSE,
     pages 257–267.

[54] Nair, V., Yu, Z., Menzies, T., Siegmund, N., & Apel, S.
     (2020). Finding faster configurations using FLASH. IEEE
     Trans. Software Eng., 46(7):794–811.

[61] Shepperd, M., Song, Q., Sun, Z., & Mair, C. (2013). Data
     quality: Some comments on the nasa software defect
     datasets. IEEE Trans. Softw. Eng., 39(9):1208–1215.

[64] Tu, H., & Menzies, T. (2019). Better data labelling with
     emblem (and how that impacts defect prediction). IEEE
     TSE.

[65] Tu, H., & Menzies, T. (2021). Frugal: Unlocking semi-
     supervised learning for software analytics. In ASE, pages
     394–406.

[66] Valerdi, R. (2010). Heuristics for systems engineering
     cost estimation. IEEE Systems Journal, 5(1):91–98.

[67] Valov, P., Petkovich, J., Guo, J., Fischmeister, S., &
     Czarnecki, K. (2017). Transferring performance prediction
     models across different hardware platforms. In Proc. of
     the 8th ACM/SPEC on Int. Conf. Perf. Eng., pages 39–50.

[69] Wu, X., Zheng, W., Xia, X., & Lo, D. (2021). Data quality
     matters: A case study on data label correctness for
     security bug report prediction. TSE, 48(7):2541–2556.

[74] Yu, Z., Theisen, C., Williams, L., & Menzies, T. (2019).
     Improving vulnerability inspection efficiency using
     active learning. IEEE Trans. Softw. Eng., 47:2401–2420.

[75] Yu, Z., Fahid, F. M., Tu, H., & Menzies, T. (2021).
     Identifying self-admitted technical debts with
     jitterbug: A two-step approach. IEEE Trans. Softw. Eng.
