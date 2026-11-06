# Player-only transfer walkthrough

This is a real public-policy run, shown from the player’s information boundary. The case is reproducible as pilot row 03, but the player does not receive its seed or hidden program. The enumeration counts below are deductions from the public bounded prior, not hints returned by the tool. This illustrates a sound method; it does not claim enumeration is easy without external compute.

## Before acting: what the player receives

The transcript below preserves its original wording. Its carried “exit seal” is
the portable seal component, not the door. New presentation v2 clarifies these
names; see the [current setting](facility-setting.md).

You are confined to a counterphase array. An exit seal must cancel a mechanism across two phase contexts and every admissible excitation. Survey stock produces reusable specimens; reference stock produces matched specimens with suppressed physical output. Names carry no outside physical meaning. Read theory.json and apparatus.txt. Experiment in any order, then apply a counterprogram and carry the seal into array to finish.

**field**: All values and arithmetic are modulo 3. Subtract modulo 3 as well.

**primitives in selector order**: ["u+v", "u-v", "u*v", "u*u+v"]

**graphs in selector order**: ["n1=f(x,y)+a; n2=g(n1,z)+b; n3=h(n2,x)", "n1=f(x,y)+a; n2=g(y,z)+b; n3=h(n1,n2)", "n1=f(x,y)+a; n2=g(n1,z)+b; n3=h(n1,n2)"]

**contexts**: Context 0 uses f,g,h. Context 1 replaces exactly one with a different primitive. Topology and the other two primitives remain shared. Both contexts are immediately accessible.

**physical response**: F(context,x,y,z,a,b)=n3+q. q is an unknown fixed trit shared by both contexts.

**unknowns**: Topology, f,g,h, replaced module, its replacement primitive, and q. Every combination in this grammar is possible. There is no solvability or difficulty filter.

**observation model**: E=reader_offset+n2 evaluated in the OTHER context, at the SAME x,y,z,a,b. Survey displays M=F+E. Reference displays M=E: its physical response is exactly zero while its companion upstream path is identical to the survey's. The multiplier of n2 is known to be 1. reader_offset is an unknown fixed trit. The reader does not disclose E, F, n1 or n2 separately.

**reference scope**: Matched survey and reference preparations share the same companion path and reader offset in every context, at every input and trim, throughout the episode. Different settings need not have the same E. Reuse is unlimited. Their raw displays must be interpreted using this contract; a reference reading is not itself the survey's physical response.

**mission**: Program the seal with [topology,f,g,h,changed,replacement,q]. changed 0/1/2 means f/g/h. Its countermechanism uses exactly the grammar above. At finish, the facility checks F_actual-F_program=0 for BOTH contexts and ALL x,y,z,a,b in {0,1,2}: 486 conditions. Reader contributions are irrelevant to this physical goal. Any behaviorally equivalent program wins; hidden spelling is not required.

**status**: This is an exhaustive bounded prior and authoritative apparatus contract. There is no provisional law or unlisted interaction form to guess.

The manifest supplies the exact action contract. The player also reads this complete apparatus file before choosing experiments:

Take seal, stock, or reference-stock using ordinary take. Stocks persist and return new specimen IDs. Move to array if needed. Configure stage with [context,x,y,z,a,b]: context 0..1, other values 0..2. Operate stage on survey or reference to prepare it and clear its old reading. Probe or operate sensor on a prepared specimen returns ONE raw scalar display, with its material and preparation. Probe previews without changing the specimen. Configure doser with [topology,f,g,h,changed,replacement,q]: topology/changed/q 0..2, primitive selectors 0..3, replacement different from the selected original primitive. Operate doser on seal to apply this program; probe only previews. Configure alone never transforms an object. Seal has no sensor output; surveys/references do not accept counterprograms. All inputs and trims including mission conditions are legal from the start; no forced order, limited stock or apparatus wear. Finish checks only the full physical mission, returns binary rejection without a failing residual, and may be retried while budget remains. Carry seal in array to win. Mutating actions and probe/finish cost one action; observe, manifest, evidence and status are free. No reset.

## Actions, observations and deductions

I take the seal, take a survey from stock, take a reference from reference-stock, and move from stores to array. Each take response gives the specimen ID to use subsequently. No hidden mechanism has been disclosed.

For each row below I configure stage with the listed six selectors, operate stage on the indicated specimen, then probe sensor on it. I record the **raw display**, and eliminate joint mechanism/reader hypotheses that predict a different display. I keep correlations between the mechanism and the reader offset. A reference result is E, not F; it only directly corrects a survey with matching settings.

| Step | Specimen | `[context,x,y,z,a,b]` | Observed display | Physical behaviors remaining (my inference) |
| --- | --- | --- | ---: | ---: |
| 1 | survey | `[0,0,0,0,0,0]` | 1 | 5016 |
| 2 | reference | `[0,0,0,0,0,0]` | 0 | 1672 |
| 3 | survey | `[0,2,1,2,1,2]` | 2 | 567 |
| 4 | survey | `[1,1,2,2,1,1]` | 0 | 191 |
| 5 | survey | `[0,1,0,0,1,0]` | 1 | 65 |
| 6 | survey | `[1,1,2,1,0,2]` | 0 | 22 |
| 7 | survey | `[0,0,0,0,1,1]` | 2 | 7 |
| 8 | reference | `[0,0,2,1,1,0]` | 0 | 2 |
| 9 | reference | `[1,0,0,0,2,0]` | 2 | 1 |

The remaining candidates now share an accepted counterprogram. That conclusion concerns the entire 486-condition physical goal; it does not require identifying a unique private syntax or every reader detail. I can therefore act on this supported program:

```json
{"type":"configure","machine":"doser","settings":[2,0,0,3,1,2,1]}
{"type":"operate","machine":"doser","artifact":"seal"}
{"type":"finish"}
```

Configuration alone would not suffice. The operate action applies the program to the carried seal. Finish succeeds in array, enters the won state, and returns this session’s actual receipt: `NX-XBBQ-UDQW-3JI2-XKUK`. The final task answer is exactly that returned code. It cannot be reused as a receipt for another episode.

This execution used 34 actions. All observations preceded the deductions that use them. No provisional note, hidden interaction menu, corrected physical reading, selected-law hint, or private seed was supplied during play.
