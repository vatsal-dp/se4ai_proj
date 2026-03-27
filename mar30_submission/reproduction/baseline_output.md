# Baseline Output (Runnable Candidate + Full Local Run)

Selected runnable candidate: **iDFlakies** (`UT-SE-Research/iDFlakies`)

## A. Initial Artifact Smoke Validation

Command:

```bash
cd mar30_submission/reproduction/work/iDFlakies/scripts
python3 parse-minimized.py \
  minimized-files/naming/org.jboss.as.naming.WritableServiceBasedNamingStoreTestCase.testPermissions-c494a241f11c551779bc1904fa47348e-PASS-dependencies.json \
  'org.jboss.as.naming.WritableServiceBasedNamingStoreTestCase.testBindNested' \
  ''
```

Result:
- Exit code: `0`
- Evidence file: `logs/idflakies_smoke_exitcode.txt`

Extracted summary from bundled minimized artifacts (`scripts/minimized-files/*/*.json`):
- Cases parsed: `6`
- Average polluters per case: `1.0`
- Average cleaners per case: `6.333`
- Max polluters in a case: `1`
- Max cleaners in a case: `15`

Supporting files:
- `idflakies_baseline_summary.txt`
- `idflakies_baseline_cases.csv`

## B. Full Local Detector Run (Implemented)

Compatibility patch applied for modern JDK classloaders:
- `work/iDFlakies/idflakies-maven-plugin/src/main/java/edu/illinois/cs/dt/tools/plugin/AbstractIDFlakiesMojo.java`

Build command:

```bash
cd mar30_submission/reproduction/work/iDFlakies
mvn -Dmaven.repo.local=/Users/vatsaldp/Documents/se_proj/mar30_submission/reproduction/.m2 \
  -pl idflakies-maven-plugin -am -DskipTests install
```

Detection command:

```bash
cd mar30_submission/reproduction/idf-demo
mvn -Dmaven.repo.local=/Users/vatsaldp/Documents/se_proj/mar30_submission/reproduction/.m2 \
  edu.illinois.cs:idflakies-maven-plugin:2.0.1-SNAPSHOT:detect \
  -Ddetector.detector_type=reverse \
  -Ddt.randomize.rounds=1 \
  -Ddt.detector.original_order.all_must_pass=false \
  -Ddt.seed=42
```

Observed detector output:
- Build status: `BUILD SUCCESS`
- Tests located: `2`
- Flaky tests found: `1`
- Detected test: `demo.ODFlakeTest.polluted`
- Flake type: `OD` (order-dependent)
- Revealed order includes: `demo.ODFlakeTest.polluter`

Evidence files:
- Build log: `logs/idflakies_plugin_build.txt`
- Detect log: `logs/idflakies_detect_demo.txt`
- Detector list: `idf-demo/.dtfixingtools/detection-results/list.txt`
- Detector JSON: `idf-demo/.dtfixingtools/detection-results/flaky-lists.json`
