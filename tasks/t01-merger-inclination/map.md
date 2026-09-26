# Map: Orbital inclination at peak strain from NRSur7dq4v2

<!-- The internal structure of this task, edited in place by the main agent after every
finished subtask: one node per subtask or line of attack, arrows for what depends on what,
and the status of each (active, done, failed, abandoned). A task with no internal structure
keeps a single node. The project graph is map/graph.md; this map shows what is inside the
task. -->

```mermaid
flowchart LR
  S1["S1: inputs: GW231123 C00:NRSur7dq4 ML sample, LAL data (done)"]
  S2["S2: iota_Q, iota_E code; convention gate vs LAL, rel. L2 6.4e-5; must-fail controls (done)"]
  S3["S3: apply to the ML sample with v1 and v2; three near-equal peaks of |h| found (done)"]
  S1 --> S2 --> S3
  classDef done fill:#dcfce7,stroke:#15803d
  class S1,S2,S3 done
```
