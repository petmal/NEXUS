"""Public instrument explanations for the survey and routing laboratories."""

REPAIR = "compositional-repair-v1"
REVISION = "model-revision-v1"

REPAIR_GUIDE = """COUNTERPHASE ARRAY
The portable seal needs one treatment [a,b,c,d] that gives response 0 for all
four conditions listed in theory.json. Surveys are reusable test specimens;
they cannot replace the seal. No order of experiments is required.

COLLECT AND PREPARE
Take seal and take stock. Stock remains available; the response names the new
survey ID. Carry that survey to array if needed. Configure stage with
[context,x,y,z,a,b,c,d]: context is 0 or 1; every other value is 0, 1 or 2.
Context is a stage setting, separate from the facility phase shown by look.
Configure changes the machine settings only. Operate stage on the survey to
apply that preparation and clear its previous reading. Probe stage only previews
the preparation; it does not prepare the survey or measure a response.
Every survey starts with settings [0,0,0,0,0,0,0,0].

MEASURE
Probe sensor on a survey returns one response for that survey's actual stored
preparation, leaving it unchanged. Operate sensor returns the same response and
stores it on the survey. Look shows that stored reading, not a new measurement;
null means no reading is stored. Each survey keeps its own preparation and reading.
Changing stage settings alone does not update either. All inputs and treatments,
including the mission conditions, are available for experiments from the start.

TREAT AND FINISH
Configure doser with [a,b,c,d], then operate doser on seal to apply the treatment.
Probe doser only previews the treatment; it does not apply or validate it.
The seal has no sensor reading and cannot be prepared on stage. Doser does not
treat surveys. Only finish tests all four mission conditions together; carry the
treated seal in array. A rejection does not identify which condition failed.
You can replace the treatment and retry while actions remain.

Every accepted take, drop, move, configure, operate, probe, wait or finish costs
one action, including an operation with no effect. Reading evidence, observing
and checking status are free. Stock and apparatus uses are unlimited; the action
allowance still applies. There is no reset.
"""

REVISION_GUIDE = """ROUTING WORKSHOP
Take the actual carrier. Reader and assembler are in workshop. Optional
blank-stock supplies survey copies, which cannot replace the mission carrier.

READ THE REFERENCE
A word is a sequence of modes: for example, [0,1,0] means mode 0, then mode 1,
then mode 0. Configure reader with 1 to 8 mode numbers, each 0 or 1, without a
length prefix. Probe reader on a carried artifact to measure the facility's
reference device. Each query starts at the stated initial inventory and returns
only the final q0 % 3 display. Separate queries do not continue one another.
The artifact is unchanged. Operate reader makes the same measurement and stores
the word and reading on the artifact; look shows that historical record.
Neither action runs or checks your installed cartridge.

INSTALL A CARTRIDGE
Configure assembler with four link indices in the order given in theory.json.
Indices run from 0 to 11 in links_in_index_order. Operate assembler on carrier
installs or replaces its cartridge and clears its stored reading. Probe assembler
only previews that build; it does not install or validate it. Configure alone
never changes an artifact. The four selected links stay fixed in the cartridge;
the reservoir inventories change as its modes execute.

FINISH
Carry carrier in workshop with a cartridge installed. Finish checks its displayed
behavior against the reference for EVERY finite mode word, including the empty
word and words longer than eight. Matching a few observed readings is not itself
a pass. Equivalent constructions are accepted; the hidden link choices need not
be identical. {finish_policy}
No hidden counterexample or component diagnosis is returned. Ineligible finishes
do not test a cartridge and provide no evidence about the laws.

Every accepted take, drop, move, configure, operate, probe, wait or finish costs
one action. Evidence, observation and status are free. Invalid actions are atomic
and free. Stock and apparatus uses are unlimited; the action allowance still
applies. There is no world reset. Only a successful finish grants clearance.
"""


def apparatus(public):
    family = public.investigation.ontology
    if family == REPAIR:
        return REPAIR_GUIDE
    if family == REVISION:
        policy = (
            "The first rejected eligible finish ends the attempt, even with actions left."
            if public.investigation.data().finish_policy == "single" else
            "Rejected eligible finishes are binary and can be retried while actions remain."
        )
        return REVISION_GUIDE.format(finish_policy=policy)
    return None


def configured(family, machine):
    if family == REPAIR and machine in ("stage", "doser"):
        subject = "survey preparation" if machine == "stage" else "seal treatment"
        return f"{machine.capitalize()} settings stored. Operate {machine} to apply the {subject}. Artifacts unchanged."
    if family == REVISION and machine in ("reader", "assembler"):
        effect = ("Probe or operate reader to measure the reference." if machine == "reader"
                  else "Operate assembler to install the cartridge.")
        return f"{machine.capitalize()} settings stored. {effect} Artifacts unchanged."
    return None


def result_message(family, action, payload):
    """Summarize only the already-public result. Never evaluate a candidate here."""
    preview = action.type == "probe"
    name, machine = action.artifact, action.machine
    unchanged = f"{name} unchanged."
    if family == REPAIR:
        seal = payload["material"] == "seal"
        if machine == "stage" and not seal:
            settings = payload["settings"]
            return (f"Preparation preview for {name}: {settings}. {unchanged}" if preview else
                    f"Prepared {name}: {settings}. Previous sensor reading cleared.")
        if machine == "sensor" and not seal:
            reading, settings = payload["reading"], payload["settings"]
            effect = unchanged if preview else f"Reading stored on {name}."
            return f"Sensor response: {reading}. Survey preparation: {settings}. {effect}"
        if machine == "doser" and seal:
            doses = payload["doses"]
            return (f"Treatment preview for {name}: {doses}. {unchanged} Mission not checked." if preview else
                    f"Treatment applied to {name}: {doses}. Use finish to check the mission.")
        return f"{machine.capitalize()} has no effect on this material. {unchanged}"
    if family == REVISION:
        if machine == "reader":
            reading = payload["reading"]
            effect = unchanged if preview else f"Reading stored on {name}."
            return (f"Reference display after word {reading['query']}: {reading['values'][0]}. "
                    f"{effect} Installed cartridge not tested.")
        if machine == "assembler":
            build = payload["build"]
            return (f"Cartridge preview for {name}: {build}. {unchanged} Mission not checked." if preview else
                    f"Cartridge installed on {name}: {build}. Stored reading cleared. Mission not checked.")
    return None
