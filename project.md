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

# Grad essay:
Hand in a research paper on the topics and methods of this class. 
## Due Mar 30 (6.0)

- To get "ok to go" approaval, show the lecturer the following:

### Find a question or make up your own. 

- Start [here](https://arxiv.org/pdf/2511.16882), Table2
- Poke around Google scholar
  - Focus mostly on these venues: [Top SE venues](https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=eng_softwaresystems)
  - Focus mostly on papers since 2015
  - But feel free to look elsewhere if you find something seminal or uber-cool
- Run queires in Google Scholar (remember your searchs trigns!)
- Write down the citation counts of the top 100 papers. Sort them. Find the knee (the bend in the graph fursthest from the line conencting first to last)
  - e.g. the knee of  [Fig2](syn.pdf) is 35 cites
- Read in detail all the papers above the knee (expect 10 to 30). Find a way to vidie them on four or five big properties
  - e.g. the papers of [Table2](syn.pdf) divide into five groups.
- Draw a venn diagram of the overlap of those groups. Gound the size of the groups and their overlaps
  - e.g. in  papers of [Table2](syn.pdf) divide into five groups, and their overlap in the middle is zero
- Write up some thing section 1 and section 2.3 pf [this paper](syn.pdf) 

### Explore some region that has not been explored before.

- Look at papers in your "above the knee" set. 
- Pick your focus

### Stand on the shoulder of giants

Get your stuff going, jumping off the work of others.

- In the papers you found, look for "reproduction prackages". Get them running.
  - Warning:
    - only a third will run 
    - And of those that run, only half will run fast enough to allow you tog et conclusions in a one semester project
- Show baseline results from the reproduction pages

## Due Apr20 (6a)

Pdf format genreted from latx (\documentclass[sigconf,nonacm]{a).
3-5 pages of text (+ 2 pages references).


- Introduction: clear Goal: Stated research questions/objectives.
  - Rsearch Questions
  - List of Contributions
- Background
  - Motivation: Validity of the problem itself.
  - Related work, Origin of data or participants.
- Methods
  -  Variables: Definitions of metrics and measures. 
  - Selection Strategy: Justification of selection of data sets or metrics or magic aprameters used in experiment
  - Methodology: Replicability of steps. For
  - Data Analysis: Definition. Discussion Appropriateness of techniques

## Due Apr27 (6b)
Same paper, now with more sections.

- Results:
  - Experimental rig
  - What was seen
  - Evaluation: Rigor of validation measures. For experimen-
tal papers, validation measures could be standard metrics
like recall, etc. For other kinds of paper, the appropriate
“evaluation” would have to reflect the nature of the argu-
ment. 
- Discussion
  -  Results and Implications
  -  Explicit validity sections. 
  - Future work
- Conclisopm
- Replication Artifacts: Poitners to a repo for all your scripts and data. e.g. https://github.com/KKGanguly/NEO
