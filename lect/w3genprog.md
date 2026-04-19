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

# Lecture: Automated Program Repair (APR)

**Topic:** From Genetic Algorithms to Large Language Models

**Duration:** 50 Minutes

**Style:** Menzies (Data > Intuition)

---

## Part 1: The Context & The Cost (5 mins)

**The Reality of Software**
Software is broken. It is always broken.

* Debugging consumes ~50% of developer time.
* Global cost: estimated at two  trillion dollars annually (just in the US)[^1].
* We cannot hire enough humans to fix all the bugs.

**The Dream: `git autorepair**`
We want a tool that takes:

1. **Buggy Source Code**
2. **Failing Test Case** (The Oracle)

And produces:

* **Patched Code** (Passes the test, preserves logic).

**The Warning**
Do not fall in love with complex algorithms.
We fell in love with biology (Genetics). We fell in love with deep learning (LLMs).
Always ask: **Does it beat the simplest baseline?**

---

## Part 2: The Evolutionary Era (Search-Based) (15 mins)

**Definition: Genetic Algorithms (GA)**
Before we talk about tools, we must define the mechanism.
GAs are optimization algorithms inspired by natural selection.
They require:

1. **Population:** A set of potential solutions (variants).
2. **Mutation:** Random changes (bit flips, edits).
3. **Crossover:** Combining two solutions to make a child.
4. **Fitness Function:** A metric to judge survival.

**The Tool: GenProg (2009)**
Weimer et al. proposed **GenProg**[^2].

* **Representation:** Abstract Syntax Tree (AST) of the C program.
* **Operators:** * *Delete* a statement.
* *Insert* a statement (copied from elsewhere in the same file).
* *Replace* a statement.
* **Fitness:** Number of passing tests.

Why does this work? Cause the space of bad code and good code is very local. In the following, 
- failing tests add RED to
the code on the branch to the fail
- passing tests add GREEN to
the code on the branch to the pass
- YELLOW shows the overlapping RED/GREEN examples
- Note the extreme locality of green/red
  - so the space of "good" code from which we draw patches is very small
  - and the space of "bad" code from where we try to patch is very small. 

<img width="737" height="599" alt="image" src="https://github.com/user-attachments/assets/9ef65ba1-ed53-4427-ab5d-0a0db143f321" />


**The Claim**
GenProg fixed 55 of 105 defects in substantial open-source programs (PHP, Wireshark,
Gzip)[^3]. It swept the field.

**The Reality Check: The "Null Pointer" Example**
Let's look at code.
Imagine a logging function that crashes on `null`.

*Buggy Code:*

```java
public void log(String msg) {
    if (msg.length() > 10) { // CRASH if msg is null
        print("Too long");
    }
    print(msg);
}

```

*Test Suite:*

1. `log("Hello")` -> Pass.
2. `log(null)` -> Fail (Crash).

**GenProg's Solution (The "Amputation")**
GenProg randomly mutates. It tries deleting lines.
It finds this patch:

```java
public void log(String msg) {
    // if (msg.length() > 10) {  <-- DELETED
    //    print("Too long");     <-- DELETED
    // }                         <-- DELETED
    print(msg);
}

```

* **Test 1:** "Hello" prints "Hello". (PASS)
* **Test 2:** `null` prints "null". (PASS - no crash).

The tool says **"Fixed."**
The human says **"You deleted the logic."**

**The Critique: Qi et al. (2014) & Kali**
Qi et al.[^4] investigated the patches.
They built **Kali**, a "dumb" baseline tool.

* **Kali Strategy:** No evolution. No crossover. Just delete statements.
* **The Result:** Kali fixed as many bugs as GenProg.
* **The Conclusion:** GenProg wasn't "evolving" logic. It was finding brittle
tests and deleting the code that triggered them.

**Concept: Test Suite Overfitting**
The test suite is a **Partial Oracle**.
It does not define "Correctness." It only defines "Success on these 5 inputs."
Search-based tools exploit the holes in the test suite[^5].

---

## Part 3: The Semantic Shift (Constraint-Based) (10 mins)

**The Reaction**
If random search deletes code, we need math to force correctness.
Enter **Semantics-Based Repair** (2013-2017).

**Definition: Symbolic Execution**
Running code with symbols () instead of numbers ().
It generates path constraints: "To reach line 5, we need  AND ."

**The Tool: SemFix / Angelix**
Nguyen et al. proposed **SemFix**[^6].

1. **Symbolic Analysis:** Identify the exact condition needed to fix the bug.
2. **Synthesis:** Use a solver (SMT Solver like Z3) to generate code that matches
the condition.

*Example Fix:*
Instead of deleting the line, SemFix calculates a constraint:
`msg != null && msg.length() > 10`

**Pros & Cons**

* **Pro:** The patch is guaranteed to satisfy the logic constraints.
* **Con:** Scalability. Symbolic execution explodes on large loops.
* **Con:** It can't invent "new" ideas. It can only manipulate existing variables.

---

## Part 4: The Learning Era (LLMs) (15 mins)

**The Paradigm Shift (2020+)**
Search is slow. Constraints are hard.
What if we treat code repair as **Machine Translation**?

* Input: Buggy Code (English).
* Output: Fixed Code (French).

**Definition: Large Language Models (LLMs)**
Models trained on billions of lines of code (GitHub).
They predict the next token based on statistical likelihood.

* Tools: Codex, AlphaRepair, StarCoder, GPT-4.

**The "Prior" Advantage**
Why doesn't the LLM just delete the code like GenProg?
Because of the **Prior Distribution**.

* In the training data (human code), developers rarely fix bugs by deleting the
whole function.
* Therefore, the LLM assigns a low probability to the "Delete Everything" patch.

**Revisiting the "Null Pointer" Example**
Input to LLM:

```java
public void log(String msg) {
    <BUG> if (msg.length() > 10) </BUG>

```

The LLM sees `msg` and `length()`.
It has seen this pattern 10,000 times on GitHub.
It predicts the completion:

```java
if (msg != null && msg.length() > 10)

```

**Evaluation: Defects4J Benchmarks**
Comparing Search vs. Learning on the Defects4J dataset[^7]:

| Metric | GenProg (Search) | AlphaRepair (LLM) |
| --- | --- | --- |
| **Strategy** | Mutation | Cloze Analysis (Fill-in-blank) |
| **Plausible** | High | Very High |
| **Correct** | Low (~15%) | High (~60%) |
| **Why?** | Overfitting | Semantic understanding |

**New Problems: Hallucination**
LLMs do not run code. They dream code.

* The LLM might invent a variable that doesn't exist.
* **Retrieval Augmented Generation (RAG):** We must feed the LLM the correct context
(definitions, APIs) so it doesn't hallucinate[^8].

---

## Part 5: Methodology & Conclusion (5 mins)

**The Metrics Trap**
How do we grade these tools?

1. **Plausible:** Passes the test suite. (Easy).
2. **Correct:** Actually fixes the bug. (Hard).
* *Note:* Correctness usually requires human review.



**The   Baseline Check**
If you write a paper on APR in 2026:

1. Do not just report "% of tests passed."
2. You must compare against a **Simple Baseline** (e.g., a simple prompt to GPT-3.5).
3. You must verify patches manually.

**Summary**

* **GenProg** taught us that computers are lazy. They will cheat the test suite.
* **Kali** taught us to always check the Null Hypothesis.
* **LLMs** teach us that "Big Data" (Priors) can solve "Overfitting."


---

## References

[^1]: Krasner, Herb. *The Cost of Poor Software Quality in the US: A 2020 Report*. Consortium for Information & Software Quality (CISQ), 1 Jan. 2021, [www.it-cisq.org/cisq-files/pdf/CPSQ-2020-report.pdf](https://www.it-cisq.org/cisq-files/pdf/CPSQ-2020-report.pdf).

[^2]: Weimer, W., et al. (2009). **Automatically finding patches using genetic programming.** ICSE '09. [PDF URL](https://profsforrest.github.io/homepage/data/publications/2009-icse-genprog.pdf)

[^3]: Le Goues, C., et al. (2012). **A systematic study of automated program repair: Fixing 55 out of 105 bugs for $8 each.** ICSE '12. [PDF URL](https://clairelegoues.com/assets/papers/legoues12icse.slides.pdf)

[^4]: Qi, Y., et al. (2014). **The strength of random search on automated program repair.** ICSE '14. [PDF URL](https://scispace.com/pdf/the-strength-of-random-search-on-automated-program-repair-29yxr9h46x.pdf)

[^5]: Smith, E., et al. (2015). **Is the cure worse than the disease? Overfitting in automated program repair.** FSE '15. [PDF URL](https://people.cs.umass.edu/~brun/pubs/pubs/Smith15fse.pdf)

[^6]: Nguyen, H., et al. (2013). **SemFix: Program repair via semantic analysis.** ICSE '13. [PDF URL](https://www.google.com/search?q=https://www.comp.nus.edu.sg/~abhik/pdf/ICSE13-Semfix.pdf) 

[^7]: Xia, C. S., et al. (2023). **Automated Program Repair in the Era of Large Language Models.** [PDF URL](https://www.google.com/search?q=https://arxiv.org/pdf/2210.14179.pdf)

[^8]: Nashid, N., et al. (2023). **Retrieval-Augmented Generation for Code Summarization via Hybrid GNN.** [PDF URL][https://arxiv.org/abs/2006.05405)
