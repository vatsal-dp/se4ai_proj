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

# Search-Based Software Engineering: From Theory to Cloud

In this lecture we motivate the value of this subject's algorithms for software engineering.


## 1. Motivation and Theory

We start with a provocation from the father of this field's
underlying theory, Vilfredo Pareto (1848, 1923):

> "Give me the fruitful error any time, full of seeds, bursting
> with its own corrections. You can keep your sterile truth for
> yourself."

In Software Engineering (SE), we often seek a "sterile
truth"—the single best algorithm, the perfect architecture.
But real-world SE is messy. It is defined by **competing
goals** that cannot all be satisfied simultaneously.

### The Pareto Frontier

This is where Search-Based Software Engineering (SBSE) shines.
Instead of looking for one "perfect" answer, we look for the
**Pareto Frontier**.

Imagine plotting every possible system configuration on a
graph with two objectives:
* **X-axis:** Cost (Lower is better)
* **Y-axis:** Performance (Higher is better)

Let's see what this looks like with a simple example. 

<img width="346" height="271" alt="image" src="https://github.com/user-attachments/assets/d64d338d-3b10-438f-9070-440da66d7abc" />



Points A, B, ...H  are **non-dominated** solutions (the Pareto
frontier). Point N and K are  **dominated**.

**The Dominance Rule:** Solution X dominates solution Y if X
is better than Y in *all* objectives, or better in some and
equal in others.

The following examle is not from SE, buts its sooooo cool

> Schmidt, Michael, and Hod Lipson. "Distilling free-form natural laws from experimental data." science 324, no. 5923 (2009): 81-85.

<img width="974" height="390" alt="image" src="https://github.com/user-attachments/assets/1722f4d0-a280-4bbf-9458-5d9a9a96a5b6" />


<img   height="300" alt="image" src="https://github.com/user-attachments/assets/5843b446-8ab2-46d9-bf01-0ece4e613694" /><img 
  height="400" alt="image" src="https://github.com/user-attachments/assets/900d5a39-264c-4822-86d6-20554fcd1abc" />


**The Inference Rule:**
1.  **Forget everything not on the frontier.** If a solution
    is dominated (there exists another solution that is better
    in *all* dimensions), throw it away.
2.  **Look for cool combinations in the rest.** The frontier
    represents the "fruitful errors"—the intelligent
    trade-offs.

But here's the challenge: **Why can't we just pick one?**
* Different stakeholders prefer different trade-offs
* The "best" depends on context we can't formalize
* We need to show decision-makers their *options*

**Why Search?** Because the space is enormous:
* Ambulance problem: 2^(locations) possible deployments
* Cloud refactoring: 2^(classes) possible partitions
* We cannot enumerate all possibilities
* We need smart algorithms to find the frontier

---

## 2. Application I: Ambulance Services (Physical Intuition)

> Veerappa, Varsha, and Emmanuel Letier. "Understanding Clusters of Optimal Solutions in Multi-Objective Decision Problems." 2011 IEEE 19th International Requirements Engineering Conference, 2011, pp. 89-98.

Let's apply this to a life-or-death problem: **Ambulance
Location Planning**.

**Real Impact:** This approach has been deployed in cities
worldwide. In one case, it reduced average response times by
4 minutes—directly saving lives.

### The Competing Goals

The city planner faces a fundamental conflict between two
stakeholders:
1.  **The Taxpayer (Minimize Cost):** Wants fewer ambulances
    to save money.
2.  **The Patient (Minimize Response Time):** Wants an
    ambulance on every corner.

You cannot satisfy both. If you optimize purely for cost,
response times skyrocket. If you optimize for time, you
bankrupt the city.

### The Search & The Dense Frontier

**The Search Space:** For a city with 50 potential
locations, there are 2^50 ≈ 1 quadrillion possible
deployment maps. Clearly, we cannot check them all.

An evolutionary algorithm explores this space intelligently.
It returns a Pareto frontier of **10,000 valid solutions**.

* **Solution A:** Fast response in city center, slow in
  suburbs.
* **Solution B:** Balanced response, medium cost.
* **Solution C:** Low cost, high risk areas underserved.

This creates **Analysis Paralysis**. The human decision-maker
cannot review 10,000 maps manually. We need a way to
summarize these trade-offs. (We'll return to this in
Section 6.)

---

## 3. Application II: Cloud Services (The SE Case)

> Carvalho, Luiz,  Assuncao, Wesley, et al. "On the Usefulness of Automatically Generated Microservice Architectures." IEEE Transactions on Software Engineering, vol. 50, no. 3, Mar. 2024, pp. 651-667.
Veerappa, Varsha, and Emmanuel Letier. "Understanding Clusters of Optimal Solutions in Multi-Objective Decision Problems." 2011 IEEE 19th International Requirements Engineering Conference, 2011, pp. 89-98.

> Yedida, Rahul, Menzies, Tim, et al. "An Expert System for Redesigning Software for Cloud Applications." Expert Systems with Applications, 2022.

> Yedida, Rahul, Menzies, Tim et al. "Lessons Learned from Hyper-Parameter Tuning for Microservice Candidate Identification." 2021 36th IEEE/ACM International Conference on Automated Software Engineering (ASE), 2021, pp. 1141-1145.


Now, let's translate this to code: **Refactoring Monoliths to
Microservices**.

**Like the ambulance problem, we have competing goals.** But
now it's about code, not geography.

### The Problem: Tangled Legacy Code

Companies have monolithic applications running on their local machines with:
* **180+ classes** with 1,000+ methods (e.g., daytrader system)
* **Poor modularization:** Features scattered everywhere
* **Years of technical debt:** Hard to maintain, harder to
  innovate

If we can move this to cloud, we get many advantages:

- Scalability (if we refactor the code into loosely coupled parts that can run on different microservices on different cloud nodes)
- Maintainability (easier to update something with small parts than one big monolith(

But manual refactoring takes *months* of expert time. We need
automation.

### The Competing Goals

> "Architectural refactoring is a war between
conflicting objectives."

1.  **Maximize Cohesion (Stakeholder: Developer):**
    * *Goal:* Keep related code together so it's easy to
        understand and maintain.
    * *Metric:* Business Context Sensitivity (BCS).
2.  **Minimize Coupling (Stakeholder: Operations/Cloud
    Architect):**
    * *Goal:* Minimize the "chatter" (network calls) between
        services to reduce latency and cost.
    * *Metric:* Inter-Partition Call Percentage (ICP).

<img width="300" height="297" alt="image" src="https://github.com/user-attachments/assets/55774335-0a9c-42e5-b4ad-408634b008b4" />

**The Conflict:** 
- To minimize coupling, you might lump
 everything into one giant service (the "God Class"
or "Boulder" ). But this destroys cohesion.
-  To maximize cohesion, you might split every class into its
 own service (the "Dust" anti-pattern ),
causing network traffic to explode.

### The Search Space

For a system with 180 classes:
* **2^180 possible partitions** (more atoms than in the
  observable universe)
* Each partition defines which classes go into which
  microservice
* We need algorithms to explore this space intelligently

---

## 4. How the Search Works (Just Enough Theory)

So how do we search a space of 2^180 possibilities? We use
**genetic algorithms**, specifically NSGA-II (Non-dominated
Sorting Genetic Algorithm).

### The Genetic Algorithm Approach

Think of evolution:

1.  **Population:** Start with 100 random partitions
    (microservice architectures)
2.  **Evaluation:** Measure each one on our objectives
    (cohesion, coupling, etc.)
3.  **Selection:** Keep the non-dominated solutions (the
    Pareto frontier)
4.  **Breeding:** Create new solutions by combining good ones
    * **Crossover:** Take half the microservices from Parent
      A, half from Parent B
    * **Mutation:** Randomly move some classes between
      microservices
5.  **Repeat:** Run for 10,000 iterations

**Why Genetic Algorithms?**
* Good at exploring huge spaces with multiple objectives
* Don't get stuck in local optima (like hill-climbing would)
* Naturally generate diverse solutions (the whole frontier,
  not just one point)

After 10,000 iterations: We have a Pareto frontier of ~100
candidate architectures.
 

---

## 5. But Wait... There's a Catch (Actually Two)

The story so far sounds great: Press button, get optimal
microservices. But reality is messier.

### Catch #1: Brittleness (The Yedida Problem)


Researchers tested multiple optimization algorithms on the same
problems. **Surprising finding:** Different algorithms won on
different metrics and datasets.

* **Algorithm A** produces the best cohesion but worst
  coupling
* **Algorithm B** produces the best coupling but worst
  cohesion
* **Algorithm C** is mediocre on everything

**And it gets worse:** The same algorithm performs differently
with different hyperparameter settings:
* Population size: 30 vs 100 vs 200?
* Mutation rate: 10% vs 50%?
* These choices *dramatically* affect results

<img height="400" alt="image" src="https://github.com/user-attachments/assets/dd36c116-80e1-4d52-adf7-4a80626c1af1" />


<img  height="500" alt="image" src="https://github.com/user-attachments/assets/e822c548-1336-42a2-86c4-af62a45413e6" />

<img   height="500" alt="image" src="https://github.com/user-attachments/assets/4df53cce-e95e-458d-9fb2-bd666dd5ab41" />


**Implication:** There is **no silver bullet**. The "best"
approach depends on:
* Which objectives you care most about
* The structure of your specific system
* How you tune the algorithm

This brittleness suggests **the problem is even harder than it
looks**. We're not just optimizing; we're choosing *which*
optimization to trust.

### Catch #2: Maintainer Profiles (The Carvalho Problem)


Researchers showed automatically generated microservice
architectures to 8 industrial maintainers. They asked: "Would
you adopt this?"

**Surprising finding:** Maintainers disagreed—not on quality,
but on **granularity preferences**.

**Fine-Grained Profile (4 maintainers):**
* "I want 10 small microservices"
* "Each should do exactly one thing"
* Valued: High cohesion, clear boundaries
* Worried about: Maintaining many small services

**Coarse-Grained Profile (3 maintainers):**
* "I want 5 larger microservices"
* "Each can handle a related set of features"
* Valued: Lower network overhead, fewer services
* Worried about: Services becoming mini-monoliths

<img width="1159" height="791" alt="image" src="https://github.com/user-attachments/assets/a1b3b250-e4ee-44e8-9580-de908e1eb8ec" />

**Same optimal solution, opposite reactions.**

One maintainer rated a microservice as "clearly adoptable"
(5/5). Another rated the *same* microservice as "not
adoptable at all" (1/5). The difference? Their profile.

**Implication:** The "optimal" architecture depends on *who*
you ask. This is not a bug—it's fundamental. Different teams
have different operational constraints, different expertise,
different risk tolerances.

 

---

## 6. The Solution: Clustering the Frontier


So we have TWO problems:
1.  **Too many solutions:** 10,000 ambulance maps or 100
    microservice architectures
2.  **Solutions depend on who you ask:** Different
    stakeholders, different profiles

How do we help decision-makers navigate this?

### The "Understanding" Approach

The key insight: **Don't cluster by objective values** (e.g.,
"these all have cohesion ≈ 0.8"). Instead, **cluster by design
decisions** (e.g., "these all group authentication classes
together").

Algorithm"

1.  **Generate** the full Pareto frontier (10,000 solutions)
2.  **Cluster** solutions based on *which decisions they make*
     rather than just objective values 
    * For ambulances: "Where are stations placed?"
    * For cloud: "Which classes are grouped?"
3.  **Select** one representative solution from each cluster


<img width="500" height="408" alt="image" src="https://github.com/user-attachments/assets/7525d744-0989-4f00-b2ec-dc80d1b92f38" />

### The Result

Instead of 10,000 points, the user sees **5-7 distinct
strategic choices**:

**For Ambulances:**
* **Cluster 1:** "Urban focus" (fast downtown, slow suburbs)
* **Cluster 2:** "Balanced coverage" (medium everywhere)
* **Cluster 3:** "Budget conscious" (minimal stations,
  acceptable times)

**For Cloud Microservices:**
* **Cluster 1:** "High Cohesion / High Latency" (10 fine-
  grained services, many network calls)
* **Cluster 2:** "Balanced Middleware" (5 medium services)
* **Cluster 3:** "Monolith-ish" (3 coarse services, low
  latency but harder to maintain)
 

**Why This Works:**

Each cluster represents a *different architectural vision*:
* Fine-grained vs coarse-grained
* Developer-friendly vs ops-friendly
* Innovation-focused vs stability-focused

Now maintainers can:
1.  **First:** Choose a cluster that matches their profile and
    priorities
2.  **Then:** Pick one solution within that cluster (or adapt
    it slightly)

This turns a mathematical optimization problem back into a
**human decision problem**—which is what it always was.

### The Carvalho Validation


When maintainers were shown clustered solutions:

- The maintainers said: *"The automatically generated
architectures are a good starting point."*
- But maintainers would not adopt
the solution generated by the search-based approach without
modifications.
- Regarding the methods in each microservice,
both groups made limited modifications, predominantly merging pairs of microservices


**Critically:** Different profile groups picked different
clusters. Fine-grained maintainers adopted Cluster 1.
Coarse-grained maintainers adopted Cluster 3. Same frontier,
different choices—**as it should be**.


Value of these methods: not to remove discussion, but to focus it and make it more time effecient.

---

## 7. Closing the Loop: Fruitful Errors

Let's return to Pareto's provocation:

> "Give me the fruitful error any time, full of seeds, bursting
> with its own corrections."

**The clusters ARE the fruitful errors.**

Each cluster represents an architectural hypothesis:
* "What if we prioritize developer productivity?"
* "What if we prioritize operational simplicity?"
* "What if we balance between them?"

Each is "wrong" in some dimension (that's why they're on the
frontier, not dominating everything). But each is **fertile**:
* It seeds a conversation among stakeholders
* It bursts with its own corrections (maintainers adapt it)
* It reveals trade-offs that were previously hidden

The "sterile truth" would be: "Here is THE optimal
architecture." But that truth doesn't exist—not because our
algorithms are weak, but because **the problem itself has no
single answer**.

Search-based SE embraces this reality. It generates the
frontier of possibilities, clusters them into strategic
choices, and hands them to humans who understand context,
risk, and organizational reality.

---

## 8. Future Work

We have shown how to:
1.  **Define** the conflicting goals (Pareto)
2.  **Search** the space (Genetic algorithms)
3.  **Navigate** the results (Clustering)

The next frontier is **Explainable AI (XAI)**:
* *Why* did the algorithm cluster these classes together?
* *What* makes this cluster "developer-friendly"?
* *How* sensitive is this solution to small changes?

If we can answer these questions, we turn black-box
optimization into **transparent decision support**. That's
when SBSE becomes truly practical.

For now: The tools exist. The theory is sound. The validation
is real. Search-based refactoring is ready for industrial
adoption—with human judgment in the loop, where it belongs.
