# Map: Inclination vs time over the GW231123 NRSur posterior and prior

<!-- The internal structure of this task, edited in place by the main agent after every
finished subtask: one node per subtask or line of attack, arrows for what depends on what,
and the status of each (active, done, failed, abandoned). A task with no internal structure
keeps a single node. The project graph is map/graph.md; this map shows what is inside the
task. -->

```mermaid
flowchart LR
  S1["S1: batch module; t_ref from identity quaternion; gate passes (done)"]
  S2["S2: job array 20907281, 156 chunks, 18185 posterior + 5000 prior, 0 failures (done)"]
  S3["S3: aggregate, bands, t = 0 histograms, folded |iota - 90| plot (done)"]
  S1 --> S2 --> S3
  classDef done fill:#dcfce7,stroke:#15803d
  class S1,S2,S3 done
```
