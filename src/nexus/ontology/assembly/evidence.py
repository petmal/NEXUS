"""Complete bounded prior and construction contract, shared by all episode profiles."""

import json


def files(spec):
    theory = {
        "specification": spec.model_dump(mode="json"),
        "arithmetic": "All values and arithmetic are modulo 3. Gains s,t are 1 or 2; phases a,b and reader offset r are 0,1,2.",
        "laws": "U(x)=s*x+a; V(y)=t*y+b; F(x,y)=H(U(x),V(y)). Each hidden value is fixed for this episode. Every combination allowed by the disclosed prior is possible, with no noise or hidden exceptions.",
        "kernel_menu": {"0": "u+v", "1": "u-v", "2": "u*v", "3": "u*u+v"},
        "disclosure": "T3 hides which kernel and all constants; T2 supplies H's selector in known_kernel but leaves gains/phases/offset unknown; T0 supplies resolved laws. The full kernel menu above is exhaustive.",
        "reader": {
            "settings": "[channel,x,y]; channel,x,y each 0,1,2. Channel 0 uses x only; channel 1 uses y only; channel 2 uses both.",
            "displayed": ["U(x)+r", "V(y)-r", "F(x,y)+r"]
            if spec.coupled_reader
            else ["U(x)", "V(y)", "F(x,y)"],
            "scope": "Reader interrogates an isolated facility reference fixture using the carrier as its sampling interface. It does NOT measure the prepared carrier, its residual error, local validity, or the assembled compensator. All settings work before or after preparation. There is no separate known-zero offset reference. In the coupled profile, displayed value and physical response are different; the same r enters the channels with the signs shown.",
            "probe_and_operate": "Both return exactly one displayed trit. Operate caches that reading; probe leaves the carrier unchanged. Cached values are historical readings, not fresh measurements.",
        },
        "component_contract": "A prepared B component has gain S and phase A, response S*x+A. C has gain T and phase B, response T*y+B. Local functional validity requires S=s and T=t. All three phases are locally valid; local validity alone does not establish compatibility with the assembled mission. There is no local pass/fail test action.",
        "forge": {
            "settings": "[slot,gain,phase]; slot 0=B or 1=C, gain 1 or 2, phase 0,1,2.",
            "operate": "Replace the chosen slot with exactly the selected gain and phase. If the other slot already exists, rotate its stored phase by ADDING the newly selected phase modulo 3; its gain stays unchanged. This happens on EVERY operation, including repeats. An existing assembly kernel remains installed. Clear the cached reader value.",
            "scope": "The cross-slot rotation is a known mounting effect. Stored component fields are actual committed settings. Preparing or repairing one component can change the other and invalidate a previously correct device. Probe previews exactly this public change without applying it or testing hidden validity.",
        },
        "assembler": "Configure [kernel] with selector 0..3. Operate installs/replaces this kernel on a carrier with BOTH components already prepared. It does not rotate components, test correctness or change gains/phases. Probe previews without committing. Missing components are a public precondition error, independent of hidden laws.",
        "mission": "Carry the actual artifact carrier in workshop, with both components prepared and a kernel installed. Its gains must satisfy S=s and T=t AND its output H_installed(S*x+A,T*y+B) must equal F(x,y) for EVERY one of the nine x,y pairs in {0,1,2}^2. Any complete build satisfying this predicate is valid, including equivalent phase assignments. Call finish to evaluate the complete predicate.",
        "finish_feedback": "A rejected finish reveals only that the complete eligible build failed, never which component/point failed. It can be retried while actions remain. A missing carrier, wrong room or incomplete assembly is ineligible and provides no law evidence. Successful finish ends play with the actual victory_code.",
        "recovery": "Components can be replaced and the kernel changed repeatedly using forge and assembler. Survey stock provides blank carriers for experiments, but copies cannot replace the actual mission carrier. There is no reset, replenish or fatal activation action.",
        "profiles": "D3 has calibrated readings; D4 has the opposite local offsets and joint offset described above. Physical laws, construction effects and goal are unchanged. T0/D0 is the supplied-law execution control. Labels are family-specific experimental profiles, not claims about model failure rates.",
    }
    return {
        "facility.txt": "You are confined to an alien phase workshop. The exit's compensator is missing. Prepare components B and C on the carrier, install a coupling kernel, and reproduce the facility's complete response. A component can meet its local contract yet be incompatible with the final device. Read theory.json and apparatus.txt. The names imply no real-world physics.",
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "apparatus.txt": "Take carrier from its visible location. Reader, forge and assembler are in workshop. Optional blank-stock supplies survey copies. Configure stores settings; operate applies them to the carried artifact; probe previews without committing. Every take/drop, move, configure, operate, probe, wait and finish costs one action. Manifest, evidence, observe and status are free. Invalid actions are atomic and free. Stock and apparatus uses are unlimited; observe reports remaining action budget (null means unlimited inside NEXUS, subject to harness limits). Only the actual carrier can fulfill the mission. Re-read its committed fields after preparation as needed. Finish successfully and return only the actual victory_code.",
    }
