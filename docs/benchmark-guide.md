# Design a benchmark you can interpret

Suppose a model fails to repair a device. Did it misunderstand the machine, choose a poor route, or simply run out of tool calls? NEXUS lets you change one condition, replay the attempt and narrow that question. Start with a world the model can operate, then decide what you want to learn.

## Where NEXUS fits

[ARC-AGI-3](https://arcprize.org/arc-agi/3) asks agents to explore unfamiliar interactive environments and discover their goals, with human action efficiency as a reference. [DiscoveryWorld](https://github.com/allenai/discoveryworld) puts agents in scientific investigations. [Alchemy](https://arxiv.org/abs/2102.02926) is a closer precedent for one design choice: causal structure can change from episode to episode, so learning the local rules matters.

In NEXUS, **the player knows the mission and the controls**. What you can withhold is a law of the world, or you can disclose everything and ask for a plan. The useful feature is the pairing: change the information or action budget, keep the rest fixed, and examine the decision at which the outcomes diverged. These projects measure different things; their scores cannot be converted into each other.

## Pick the experimental unit

An **ontology** is a family of worlds: it defines objects, legal mechanisms, observations and what counts as success. A **compiled episode** is one instance with a particular law, layout, goal and budget. A **run** is one player's attempt on that episode. Repeating a model call on the same world tests consistency; generating a different seed tests a different question.

| If you want to study… | Start here | Change | Hold fixed or check |
|---|---|---|---|
| Learning a mechanism | [Model revision](model-revision-guide.md) | Supplied vs hidden routing law | Same behavior, mission, accessible instruments and model settings |
| Building a solution from evidence | [Compositional repair](compositional-pilot-guide.md) | Supplied treatment vs one the player must infer | Same acceptance rule; record whether the evidence supports the treatment |
| Planning with known laws | [Interference](interference-guide.md) | Action allowance on the same target; separately, subgoal coupling or horizon | Same kernel and target for a budget comparison. Changing coupling or horizon can also change the minimum cost. |

The family checks (**qualification**) say what an instance actually requires. Its **certificate** records the scope and results of those checks. Neither proves that a given model finds the world difficult. Use the supported profiles in the family guide or [fresh matrix](fresh-world-guide.md), not arbitrary combinations of four axis numbers.

## Worked comparison: what changes when the budget has slack?

Fresh rows F11 and F12 are the same short, independent planning problem, with disclosed laws and a 12-action minimum including `take` and `finish`. R2 gives exactly 12 actions. R1 gives 18. Generate the pair locally from the NEXUS root (Bash, new output directories):

```bash
for r in 2 1; do
  uv run --frozen nexus generate "../nexus-pair-r$r" --seed 107 \
    --axis-version 2 --science-family stateful-interference-v1 \
    --theory-level 0 --discovery-level 0 --planning-level 0 --resource-pressure "$r" \
    --ontology-options '{"coupling":"independent","horizon":"short"}' || break
  uv run --frozen nexus qualify "../nexus-pair-r$r/private.json" || break
done
```

A legal preview costs an action. If the player has already taken the seal, a preview that leaves the physical task unchanged uses one of the actions still needed by the tight plan. The same preview can fit in the relaxed budget. That is an interpretable difference even if both attempts end at the target. `finish` still costs its own action.

For a first comparison:

1. **Choose conditions before looking at outcomes.** Fix the model endpoint and settings, harness, tool descriptions, presentation version, budgets outside the world, and a repetition rule. Reserve fresh worlds for confirmation.
2. **Run a disclosed control first.** Confirm the tool works and the receipt can be submitted. In the maintained panel, pass all four controls for the same model/settings before attempting challenges. The [single-model tutorial](first-model.md) is independent of that gate.
3. **Run both members of each pair.** Give each attempt a new service. Keep failed attempts, provider stops and reruns. Save the configs, raw records and private audit exports where available.
4. **Report the paired outcomes.** Count both won, tight-only, relaxed-only and neither. Also show unassessed pairs. For each loss, distinguish a bad physical plan, an unsupported choice, a missing receipt and an interrupted provider. Use the [evaluation guide](evaluation-guide.md) to run the service or build the maintained panel.

## Compile the results

In the maintained panel package, each launched group has its own directory and run manifest. After the run, refresh the derived summaries:

```bash
python3 summarize_results.py results/*/
```

Each directory gets a `readout.json`. Check `expected_attempts`, `recorded_attempts` and `matrix_complete` before calculating rates; a recorded provider error still occupies a row. Use `rows[].reported_kind` for the harness verdict and `rows[].diagnostics.world_win_observed` for the world outcome. Keep nulls unassessed. Match by provider, model **and settings**, task ID and repetition, retaining the group manifest to distinguish reruns. Join task IDs to the matrix: F11/F12 are one pair, not two independent worlds. Report the numerator, denominator and missing cases for every contrast. A readout summarizes captured logs; it does not re-verify the original receipt or replay the world. This command requires the panel's run manifests and does not apply to the standalone tutorial directory.

## What earlier experiments show

The original [T/D experiments](td-experiments-and-next-directions.md) did not establish a repeatable failure of the strongest tested configuration from hidden laws or deeper investigation alone. A world can require several pieces of evidence and still be tractable. A physical win can also leave an alternative explanation unresolved.

In the [fresh-world study](research/fresh-world-results-2026-11-04.md), Luna medium won **2/8** tight planning cases and **6/8** relaxed counterparts: five losses became wins, one win became a loss, and two pairs were unchanged. On the common first 16 conditions, Astra medium and Flash high each won 16; evidence supported **16** of Astra's wins and **13** of Flash's. These comparisons answer different questions. They used selected worlds, one attempt per condition and historical presentation; they are not general rankings or estimates for a new model.

## Going further

To integrate another harness, expose the player API and reserve validation for the evaluator; [service setup](evaluation-guide.md) includes a minimal request. To add a family, implement its laws and public observations, then demonstrate a working policy and check the certificate. Start with the [operator example](../examples/ontologies/revision_example.py), then the [ontology author guide](ontology-author-guide.md). For a publishable comparison, use the [research guide](research-guide.md) and [metric reference](reference/metrics.md).
