# Map: Density of distinguishable waveforms vs inclination at merger

<!-- The internal structure of this task, edited in place by the main agent after every
finished subtask: one node per subtask or line of attack, arrows for what depends on what,
and the status of each (active, done, failed, abandoned). A task with no internal structure
keeps a single node. The project graph is map/graph.md; this map shows what is inside the
task. -->

```mermaid
flowchart LR
  S1["S1 metric code and controls (done)"]
  J["LAL waveform jumps with the parameters: start taper at a sample index, abrupt end (found in S1; fixed by continuous-time tapers)"]
  C["(c) literal check fails at 1e-3 from cubic terms (confirmed by scaling; symmetric test passes)"]
  S2["S2 job array 20909319: 10 001 points, 0 failures (done)"]
  S3["S3 aggregate, figures, result (done): R_edge median ratio 18, not rising with chi_p"]
  T["heavy tail: 10 of 8000 points hold 91 % of the edge-on sum; ratio of means not converged"]
  F["milestone figure: s vs |cos iota_Q(t_peak)|; median s rises with chi_p at every inclination (2.2-2.8 decades)"]
  N["mechanism: det g grows as the network signal weakens (psi-only test, slope near -9/2)"]
  S1 --> J
  S1 --> C
  S1 --> S2 --> S3
  S3 --> T --> N
  S3 --> F
```
