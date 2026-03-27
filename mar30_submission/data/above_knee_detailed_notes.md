# Above-Knee Detailed Reading Notes

Source set: `data/above_knee_set.csv`
Rows: all papers above knee threshold, each with explicit classification rationale.

## 1. Reinforcement learning for automatic test case prioritization and selection in continuous integration
- Year/Venue/Citations: 2017 / Proceedings of the 26th ACM SIGSOFT International Symposium on Software Testing and Analysis / 252
- Input artifact: `mixed_artifacts`
- Model family: `reinforcement_learning`
- Task: `optimization`
- Prediction timing: `early_or_online`
- Evaluation metric(s): `apfd,napfd,fault_detection_rate`
- Detailed reading note: RL-based policy for CI test prioritization/selection using historical execution outcomes and change context.
- Abstract evidence excerpt: Testing in Continuous Integration (CI) involves test case prioritization, selection, and execution at each cycle. Selecting the most promising test cases to detect bugs is hard if there are uncertainties on the impact of committed code changes or, if traceability links between code and tests are not available. This paper introduces Retecs, a new method for automatically learning test case selection and prioritizatio…

## 2. Oops, My Tests Broke the Build: An Explorative Analysis of Travis CI with GitHub
- Year/Venue/Citations: 2017 / 2017 IEEE/ACM 14th International Conference on Mining Software Repositories (MSR) / 164
- Input artifact: `log_text`
- Model family: `statistical_empirical`
- Task: `diagnosis_or_rca`
- Prediction timing: `post_failure_or_rca`
- Evaluation metric(s): `failure_rate,category_proportions,descriptive_statistics`
- Detailed reading note: Empirical characterization of CI failures/testing behavior in Travis+GitHub workflows.
- Abstract evidence excerpt: Continuous Integration (CI) has become a best practice of modern software development. Yet, at present, we have a shortfall of insight into the testing practices that are common in CI-based software development. In particular, we seek quantifiable evidence on how central testing is to the CI process, how strongly the project language influences testing, whether different integration environments are valuable and if…

## 3. iDFlakies: A Framework for Detecting and Partially Classifying Flaky Tests
- Year/Venue/Citations: 2019 / 2019 12th IEEE Conference on Software Testing, Validation and Verification (ICST) / 156
- Input artifact: `log_text`
- Model family: `rule_or_statistical`
- Task: `diagnosis_or_rca`
- Prediction timing: `post_failure_or_rca`
- Evaluation metric(s): `flaky_detection_rate,classification_precision`
- Detailed reading note: Detects order-dependent flaky tests via controlled reordering/reruns and partial flake classification.
- Abstract evidence excerpt: Regression testing is increasingly important with the wide use of continuous integration. A desirable requirement for regression testing is that a test failure reliably indicates a problem in the code under test and not a false alarm from the test code or the testing infrastructure. However, some test failures are unreliable, stemming from flaky tests that can nondeterministically pass or fail for the same code unde…

## 4. Test case selection and prioritization using machine learning: a systematic literature review
- Year/Venue/Citations: 2021 / Empirical Software Engineering / 149
- Input artifact: `mixed_artifacts`
- Model family: `traditional_ml`
- Task: `optimization`
- Prediction timing: `early_or_online`
- Evaluation metric(s): `study_counts,taxonomy_coverage`
- Detailed reading note: SLR summarizing ML methods for test selection/prioritization in CI-like settings.
- Abstract evidence excerpt: Not available in retrieved metadata.

## 5. Root causing flaky tests in a large-scale industrial setting
- Year/Venue/Citations: 2019 / Proceedings of the 28th ACM SIGSOFT International Symposium on Software Testing and Analysis / 129
- Input artifact: `log_text`
- Model family: `rule_or_statistical`
- Task: `diagnosis_or_rca`
- Prediction timing: `post_failure_or_rca`
- Evaluation metric(s): `diagnosis_precision,time_to_diagnosis`
- Detailed reading note: Industrial flaky-test root-cause localization pipeline integrated into CI troubleshooting.
- Abstract evidence excerpt: In today’s agile world, developers often rely on continuous integration pipelines to help build and validate their changes by executing tests in an efficient manner. One of the significant factors that hinder developers’ productivity is flaky tests—tests that may pass and fail with the same version of code. Since flaky test failures are not deterministically reproducible, developers often have to spend hours only to…

## 6. How Open Source Projects Use Static Code Analysis Tools in Continuous Integration Pipelines
- Year/Venue/Citations: 2017 / 2017 IEEE/ACM 14th International Conference on Mining Software Repositories (MSR) / 117
- Input artifact: `code_or_commit`
- Model family: `statistical_empirical`
- Task: `explanation`
- Prediction timing: `early_or_online`
- Evaluation metric(s): `adoption_rate,warning_density,usage_patterns`
- Detailed reading note: Studies integration and usage patterns of static analysis in CI pipelines.
- Abstract evidence excerpt: Static analysis tools are often used by software developers to entail early detection of potential faults, vulnerabilities, code smells, or to assess the source code adherence to coding standards and guidelines. Also, their adoption within Continuous Integration (CI) pipelines has been advocated by researchers and practitioners. This paper studies the usage of static analysis tools in 20 Java open source projects ho…

## 7. An Empirical Analysis of Build Failures in the Continuous Integration Workflows of Java-Based Open-Source Software
- Year/Venue/Citations: 2017 / 2017 IEEE/ACM 14th International Conference on Mining Software Repositories (MSR) / 114
- Input artifact: `log_text`
- Model family: `statistical_empirical`
- Task: `diagnosis_or_rca`
- Prediction timing: `post_failure_or_rca`
- Evaluation metric(s): `failure_category_distribution,failure_frequency`
- Detailed reading note: Empirical taxonomy and frequency analysis of build failures in Java OSS CI workflows.
- Abstract evidence excerpt: Continuous Integration (CI) has become a common practice in both industrial and open-source software development. While CI has evidently improved aspects of the software development process, errors during CI builds pose a threat to development efficiency. As an increasing amount of time goes into fixing such errors, failing builds can significantly impair the development process and become very costly. We perform an…

## 8. Test Case Prioritization in Continuous Integration environments: A systematic mapping study
- Year/Venue/Citations: 2020 / Information and Software Technology / 96
- Input artifact: `mixed_artifacts`
- Model family: `traditional_ml`
- Task: `optimization`
- Prediction timing: `early_or_online`
- Evaluation metric(s): `study_counts,taxonomy_coverage`
- Detailed reading note: Mapping study of CI test prioritization strategies and evidence trends.
- Abstract evidence excerpt: Not available in retrieved metadata.

## 9. An empirical characterization of bad practices in continuous integration
- Year/Venue/Citations: 2020 / Empirical Software Engineering / 81
- Input artifact: `code_or_commit`
- Model family: `statistical_empirical`
- Task: `explanation`
- Prediction timing: `post_failure_or_rca`
- Evaluation metric(s): `anti_pattern_frequency,association_statistics`
- Detailed reading note: Characterizes CI anti-patterns and links them to quality/process degradation.
- Abstract evidence excerpt: Not available in retrieved metadata.

## 10. HireBuild
- Year/Venue/Citations: 2018 / Proceedings of the 40th International Conference on Software Engineering / 79
- Input artifact: `code_or_commit`
- Model family: `deep_learning`
- Task: `optimization`
- Prediction timing: `early_or_online`
- Evaluation metric(s): `build_success_rate,time_saved`
- Detailed reading note: AI-assisted build maintenance/repair direction targeting developer productivity in build workflows.
- Abstract evidence excerpt: Advancements in software build tools such as Maven reduce build management effort, but developers still need specialized knowledge and long time to maintain build scripts and resolve build failures. More recent build tools such as Gradle give developers greater extent of customization flexibility, but can be even more difficult to maintain. According to the TravisTorrent dataset of open-source software continuous in…

## 11. A Tale of CI Build Failures: An Open Source and a Financial Organization Perspective
- Year/Venue/Citations: 2017 / 2017 IEEE International Conference on Software Maintenance and Evolution (ICSME) / 79
- Input artifact: `log_text`
- Model family: `statistical_empirical`
- Task: `diagnosis_or_rca`
- Prediction timing: `post_failure_or_rca`
- Evaluation metric(s): `failure_category_distribution,cross_context_comparison`
- Detailed reading note: Comparative build-failure characterization across OSS and industrial financial CI contexts.
- Abstract evidence excerpt: Continuous Integration (CI) and Continuous Delivery (CD) are widespread in both industrial and open-source software (OSS) projects. Recent research characterized build failures in CI and identified factors potentially correlated to them. However, most observations and findings of previous work are exclusively based on OSS projects or data from a single industrial organization. This paper provides a first attempt to…

## 12. Improving the prediction of continuous integration build failures using deep learning
- Year/Venue/Citations: 2022 / Automated Software Engineering / 60
- Input artifact: `mixed_artifacts`
- Model family: `deep_learning`
- Task: `prediction`
- Prediction timing: `early_or_online`
- Evaluation metric(s): `precision,recall,f1,auc`
- Detailed reading note: Deep-learning model for CI build-failure prediction from historical CI artifacts.
- Abstract evidence excerpt: Not available in retrieved metadata.

## 13. Test prioritization in continuous integration environments
- Year/Venue/Citations: 2018 / Journal of Systems and Software / 55
- Input artifact: `mixed_artifacts`
- Model family: `traditional_ml`
- Task: `optimization`
- Prediction timing: `early_or_online`
- Evaluation metric(s): `apfd,time_to_first_failure`
- Detailed reading note: Prioritization strategy for CI test suites to detect failures earlier under time budget.
- Abstract evidence excerpt: Not available in retrieved metadata.

## 14. A Study on the Interplay between Pull Request Review and Continuous Integration Builds
- Year/Venue/Citations: 2019 / 2019 IEEE 26th International Conference on Software Analysis, Evolution and Reengineering (SANER) / 52
- Input artifact: `code_or_commit`
- Model family: `statistical_empirical`
- Task: `explanation`
- Prediction timing: `post_failure_or_rca`
- Evaluation metric(s): `correlation_effect_size,descriptive_statistics`
- Detailed reading note: Examines relationship between PR review dynamics and CI build outcomes.
- Abstract evidence excerpt: Modern code review (MCR) is nowadays well-adopted in industrial and open source projects. Recent studies have investigated how developers perceive its ability to foster code quality, developers' code ownership, and team building. MCR is often being used with automated quality checks through static analysis tools, testing or, ultimately, through automated builds on a Continuous Integration (CI) infrastructure. With t…

## 15. Who broke the build? Automatically identifying changes that induce test failures in continuous integration at Google Scale
- Year/Venue/Citations: 2017 / 2017 IEEE/ACM 39th International Conference on Software Engineering: Software Engineering in Practice Track (ICSE-SEIP) / 52
- Input artifact: `code_or_commit`
- Model family: `rule_or_statistical`
- Task: `diagnosis_or_rca`
- Prediction timing: `post_failure_or_rca`
- Evaluation metric(s): `topk_accuracy,precision,recall`
- Detailed reading note: At-scale culprit-change localization for CI test failures in fast development cycles.
- Abstract evidence excerpt: Quickly identifying and fixing code changes that introduce regressions is critical to keep the momentum on software development, especially in very large scale software repositories with rapid development cycles, such as at Google. Identifying and fixing such regressions is one of the most expensive, tedious, and time consuming tasks in the software development life-cycle. Therefore, there is a high demand for autom…
