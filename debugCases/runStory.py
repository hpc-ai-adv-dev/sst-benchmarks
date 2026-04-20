# Builds SST topologies for each debug use case story.  The script is intended
# to be run by sst itself, not directly, but will be forwarded an argument
# indicating which story to run.  For information about the stories and how to
# run them, see README.md in this directory.

import argparse
import sst

# Maps each story name to whether it has been hand-verified.
# If the user runs a story that has not been hand-verified, they will get a warning message.
STORIES = {
    # --- Event Tracing ---
    "wrongPath":             True,
    "infiniteLoop":          False,
    "unexpectedDisappear":   False,
    "missedDeadline":        False,
    "outOfOrderReceipt":     False,
    "duplicateSepTimes":     False,
    "duplicateSameTime":     False,

    # --- Event Processing ---
    "broadcastStorm":        False,
    "badMerge":              False,

    # --- Incorrect Topology ---
    "missingLink":             False,
    "wrongLink":               False,
    "unexpectedDuplicateLink": False,

    # --- Deadlock ---
    "directDeadlock":        False,
    "indirectDeadlock":      False,

    # --- Fault Detection And Attribution ---
    "detectWhenComponentBecomesInvalid": False,
    "badInvariantBetweenComponents":     False,
    "componentsLoseParity":              False,
    "divergedModels_A":                  False,
    "divergedModels_B":                  False,
    "componentCausesSegfault":           False,
    "badInitialState":                   False,
    "badTerminatingState":               False,
    "findFirstToComplete":               False,
    "determineWhatNotComplete":          False,

    # --- Load Imbalances ---
    "findEventHeavyComponent":     False,
    "findSlowProcessingComponent": False,
    "findMemHeavyComponent":       False,
    "findMemHeavyEvent":           False,
    "findStarvedComponent":        False,
}

VALID_STORIES = list(STORIES.keys())

ASSESSMENT_BASE_URL = "https://github.com/hpc-ai-adv-dev/sst-benchmarks/blob/debugUseCases/debugCases/assessments"

def print_assessment_url(story_name):
    # The "divergedModels" story has two variants (A and B) (the point is that
    # we can run each individually through the debugger and compare). We
    # document the assessment in a single markdown file.
    if story_name in ("divergedModels_A", "divergedModels_B"):
        assessment_name = "divergedModels"
    else:
        assessment_name = story_name

    print(f"To read an assessment of how this story runs with the SST debugger go to")
    print(f"  {ASSESSMENT_BASE_URL}/{assessment_name}.md")
    print()


def warn_if_story_not_hand_verified(story_name):
    if not STORIES.get(story_name, False):
        print("* * * * * * * * * * * * * * * * * * * * *")
        print(f"WARNING: story '{story_name}' has not been hand-verified yet.")
        print("* * * * * * * * * * * * * * * * * * * * *")


def parse_story_arg():
    parser = argparse.ArgumentParser(description="Run a debug story")
    parser.add_argument(
        "story",
        choices=VALID_STORIES,
        help="Story name to run",
    )

    args, _ = parser.parse_known_args()
    return args.story

def error_story_not_yet_implemented():
    print("Story not yet implemented")
    raise SystemExit(1)


# --- Event Tracing ---
def story_wrongPath():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'wrongPath', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'wrongPath', 'name': 'B', 'numLinks': 3})
    comp_C.addParams({'story': 'wrongPath', 'name': 'C', 'numLinks': 1})
    comp_D.addParams({'story': 'wrongPath', 'name': 'D', 'numLinks': 1})

    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('b_c').connect((comp_B, "port1", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('b_d').connect((comp_B, "port2", "1ns"), (comp_D, "port0", "1ns"))


def story_infiniteLoop():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'infiniteLoop', 'name': 'A', 'numLinks': 2})
    comp_B.addParams({'story': 'infiniteLoop', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'infiniteLoop', 'name': 'C', 'numLinks': 3})
    comp_D.addParams({'story': 'infiniteLoop', 'name': 'D', 'numLinks': 1})

    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('b_c').connect((comp_B, "port1", "1ns"), (comp_C, "port1", "1ns"))
    sst.Link('a_c').connect((comp_A, "port1", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('c_d').connect((comp_C, "port2", "1ns"), (comp_D, "port0", "1ns"))


def story_unexpectedDisappear():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'unexpectedDisappear', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'unexpectedDisappear', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'unexpectedDisappear', 'name': 'C', 'numLinks': 2})
    comp_D.addParams({'story': 'unexpectedDisappear', 'name': 'D', 'numLinks': 1})

    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('b_c').connect((comp_B, "port1", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('c_d').connect((comp_C, "port1", "1ns"), (comp_D, "port0", "1ns"))


def story_missedDeadline():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'missedDeadline', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'missedDeadline', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'missedDeadline', 'name': 'C', 'numLinks': 2})
    comp_D.addParams({'story': 'missedDeadline', 'name': 'D', 'numLinks': 1})

    sst.Link('a_b').connect((comp_A, "port0", "10ns"), (comp_B, "port0", "10ns"))
    sst.Link('b_c').connect((comp_B, "port1", "15ns"), (comp_C, "port0", "15ns"))
    sst.Link('c_d').connect((comp_C, "port1", "10ns"), (comp_D, "port0", "10ns"))


def story_outOfOrderReceipt():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")
    comp_E = sst.Component("E", "debugUseCases.Node")

    comp_A.addParams({'story': 'outOfOrderReceipt', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'outOfOrderReceipt', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'outOfOrderReceipt', 'name': 'C', 'numLinks': 1})
    comp_D.addParams({'story': 'outOfOrderReceipt', 'name': 'D', 'numLinks': 2})
    comp_E.addParams({'story': 'outOfOrderReceipt', 'name': 'E', 'numLinks': 2})

    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('b_e').connect((comp_B, "port1", "1ns"), (comp_E, "port0", "1ns"))
    sst.Link('c_d').connect((comp_C, "port0", "1ns"), (comp_D, "port0", "1ns"))
    sst.Link('d_e').connect((comp_D, "port1", "1ns"), (comp_E, "port1", "1ns"))


def story_duplicateSepTimes():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'duplicateSepTimes', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'duplicateSepTimes', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'duplicateSepTimes', 'name': 'C', 'numLinks': 2})
    comp_D.addParams({'story': 'duplicateSepTimes', 'name': 'D', 'numLinks': 1})

    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('b_c').connect((comp_B, "port1", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('c_d').connect((comp_C, "port1", "1ns"), (comp_D, "port0", "1ns"))


def story_duplicateSameTime():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'duplicateSameTime', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'duplicateSameTime', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'duplicateSameTime', 'name': 'C', 'numLinks': 2})
    comp_D.addParams({'story': 'duplicateSameTime', 'name': 'D', 'numLinks': 1})

    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('b_c').connect((comp_B, "port1", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('c_d').connect((comp_C, "port1", "1ns"), (comp_D, "port0", "1ns"))


# --- Event Processing ---
def story_broadcastStorm():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")
    comp_E = sst.Component("E", "debugUseCases.Node")
    comp_F = sst.Component("F", "debugUseCases.Node")
    comp_G = sst.Component("G", "debugUseCases.Node")

    comp_A.addParams({'story': 'broadcastStorm', 'name': 'A', 'numLinks': 6})
    comp_B.addParams({'story': 'broadcastStorm', 'name': 'B', 'numLinks': 1})
    comp_C.addParams({'story': 'broadcastStorm', 'name': 'C', 'numLinks': 1})
    comp_D.addParams({'story': 'broadcastStorm', 'name': 'D', 'numLinks': 1})
    comp_E.addParams({'story': 'broadcastStorm', 'name': 'E', 'numLinks': 1})
    comp_F.addParams({'story': 'broadcastStorm', 'name': 'F', 'numLinks': 1})
    comp_G.addParams({'story': 'broadcastStorm', 'name': 'G', 'numLinks': 1})

    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('a_c').connect((comp_A, "port1", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('a_d').connect((comp_A, "port2", "1ns"), (comp_D, "port0", "1ns"))
    sst.Link('a_e').connect((comp_A, "port3", "1ns"), (comp_E, "port0", "1ns"))
    sst.Link('a_f').connect((comp_A, "port4", "1ns"), (comp_F, "port0", "1ns"))
    sst.Link('a_g').connect((comp_A, "port5", "1ns"), (comp_G, "port0", "1ns"))



def story_badMerge():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'badMerge', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'badMerge', 'name': 'B', 'numLinks': 1})
    comp_C.addParams({'story': 'badMerge', 'name': 'C', 'numLinks': 3})
    comp_D.addParams({'story': 'badMerge', 'name': 'D', 'numLinks': 1})

    sst.Link('a_c').connect((comp_A, "port0", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('b_c').connect((comp_B, "port0", "1ns"), (comp_C, "port1", "1ns"))
    sst.Link('c_d').connect((comp_C, "port2", "1ns"), (comp_D, "port0", "1ns"))


# --- Incorrect Topology ---


def story_missingLink():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'missingLink', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'missingLink', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'missingLink', 'name': 'C', 'numLinks': 2})
    comp_D.addParams({'story': 'missingLink', 'name': 'D', 'numLinks': 1})

    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('c_d').connect((comp_C, "port1", "1ns"), (comp_D, "port0", "1ns"))



def story_wrongLink():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")

    comp_A.addParams({'story': 'wrongLink', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'wrongLink', 'name': 'B', 'numLinks': 1})
    comp_C.addParams({'story': 'wrongLink', 'name': 'C', 'numLinks': 1})

    # Intentionally connect A to C instead of A to B
    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_C, "port0", "1ns"))


def story_unexpectedDuplicateLink():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")

    comp_A.addParams({'story': 'unexpectedDuplicateLink', 'name': 'A', 'numLinks': 2})
    comp_B.addParams({'story': 'unexpectedDuplicateLink', 'name': 'B', 'numLinks': 2})

    sst.Link('a_b'    ).connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('a_b_dup').connect((comp_A, "port1", "1ns"), (comp_B, "port1", "1ns"))



# --- Deadlock ---


def story_directDeadlock():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")

    comp_A.addParams({'story': 'directDeadlock', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'directDeadlock', 'name': 'B', 'numLinks': 1})

    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))


def story_indirectDeadlock():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")

    comp_A.addParams({'story': 'indirectDeadlock', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'indirectDeadlock', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'indirectDeadlock', 'name': 'C', 'numLinks': 1})

    sst.Link('a_b').connect((comp_A, "port0", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('b_c').connect((comp_B, "port1", "1ns"), (comp_C, "port0", "1ns"))


# --- Fault Detection And Attribution ---


def story_detectWhenComponentBecomesInvalid():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_A.addParams({'story': 'detectWhenComponentBecomesInvalid', 'name': 'A', 'numLinks': 0})


def story_badInvariantBetweenComponents():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")

    comp_A.addParams({'story': 'badInvariantBetweenComponents', 'name': 'A', 'numLinks': 1})
    comp_B.addParams({'story': 'badInvariantBetweenComponents', 'name': 'B', 'numLinks': 1})
    comp_C.addParams({'story': 'badInvariantBetweenComponents', 'name': 'C', 'numLinks': 2})

    sst.Link('a_c').connect((comp_A, "port0", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('b_c').connect((comp_B, "port0", "1ns"), (comp_C, "port1", "1ns"))


def story_componentsLoseParity():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")

    comp_A.addParams({'story': 'componentsLoseParity', 'name': 'A', 'numLinks': 0})
    comp_B.addParams({'story': 'componentsLoseParity', 'name': 'B', 'numLinks': 0})


def story_divergedModels_A():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_A.addParams({'story': 'divergedModels_A', 'name': 'A', 'numLinks': 0})


def story_divergedModels_B():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_A.addParams({'story': 'divergedModels_B', 'name': 'A', 'numLinks': 0})


def story_componentCausesSegfault():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'componentCausesSegfault', 'name': 'A', 'numLinks': 0})
    comp_B.addParams({'story': 'componentCausesSegfault', 'name': 'B', 'numLinks': 0})
    comp_C.addParams({'story': 'componentCausesSegfault', 'name': 'C', 'numLinks': 0})
    comp_D.addParams({'story': 'componentCausesSegfault', 'name': 'D', 'numLinks': 0})


def story_badInitialState():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'badInitialState', 'name': 'A', 'numLinks': 0})
    comp_B.addParams({'story': 'badInitialState', 'name': 'B', 'numLinks': 0})
    comp_C.addParams({'story': 'badInitialState', 'name': 'C', 'numLinks': 0})
    comp_D.addParams({'story': 'badInitialState', 'name': 'D', 'numLinks': 0})


def story_badTerminatingState():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'badTerminatingState', 'name': 'A', 'numLinks': 0})
    comp_B.addParams({'story': 'badTerminatingState', 'name': 'B', 'numLinks': 0})
    comp_C.addParams({'story': 'badTerminatingState', 'name': 'C', 'numLinks': 0})
    comp_D.addParams({'story': 'badTerminatingState', 'name': 'D', 'numLinks': 0})


def story_findFirstToComplete():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'findFirstToComplete', 'name': 'A', 'numLinks': 0})
    comp_B.addParams({'story': 'findFirstToComplete', 'name': 'B', 'numLinks': 0})
    comp_C.addParams({'story': 'findFirstToComplete', 'name': 'C', 'numLinks': 0})
    comp_D.addParams({'story': 'findFirstToComplete', 'name': 'D', 'numLinks': 0})


def story_determineWhatNotComplete():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")
    comp_E = sst.Component("E", "debugUseCases.Node")

    comp_A.addParams({'story': 'determineWhatNotComplete', 'name': 'A', 'numLinks': 0})
    comp_B.addParams({'story': 'determineWhatNotComplete', 'name': 'B', 'numLinks': 0})
    comp_C.addParams({'story': 'determineWhatNotComplete', 'name': 'C', 'numLinks': 0})
    comp_D.addParams({'story': 'determineWhatNotComplete', 'name': 'D', 'numLinks': 0})
    comp_E.addParams({'story': 'determineWhatNotComplete', 'name': 'E', 'numLinks': 0})


# --- Load Imbalances ---


def story_findEventHeavyComponent():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'findEventHeavyComponent', 'name': 'A', 'numLinks': 2})
    comp_B.addParams({'story': 'findEventHeavyComponent', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'findEventHeavyComponent', 'name': 'C', 'numLinks': 2})
    comp_D.addParams({'story': 'findEventHeavyComponent', 'name': 'D', 'numLinks': 2})

    # Ring A-B-C-D-A (clockwise); port0=left link, port1=right link
    sst.Link('link_AB').connect((comp_A, "port1", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('link_BC').connect((comp_B, "port1", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('link_CD').connect((comp_C, "port1", "1ns"), (comp_D, "port0", "1ns"))
    sst.Link('link_DA').connect((comp_D, "port1", "1ns"), (comp_A, "port0", "1ns"))


def story_findSlowProcessingComponent():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'findSlowProcessingComponent', 'name': 'A', 'numLinks': 2})
    comp_B.addParams({'story': 'findSlowProcessingComponent', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'findSlowProcessingComponent', 'name': 'C', 'numLinks': 2})
    comp_D.addParams({'story': 'findSlowProcessingComponent', 'name': 'D', 'numLinks': 2})

    # Ring A-B-C-D-A (clockwise); port0=left link, port1=right link
    sst.Link('link_AB').connect((comp_A, "port1", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('link_BC').connect((comp_B, "port1", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('link_CD').connect((comp_C, "port1", "1ns"), (comp_D, "port0", "1ns"))
    sst.Link('link_DA').connect((comp_D, "port1", "1ns"), (comp_A, "port0", "1ns"))


def story_findMemHeavyComponent():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'findMemHeavyComponent', 'name': 'A', 'numLinks': 0})
    comp_B.addParams({'story': 'findMemHeavyComponent', 'name': 'B', 'numLinks': 0})
    comp_C.addParams({'story': 'findMemHeavyComponent', 'name': 'C', 'numLinks': 0})
    comp_D.addParams({'story': 'findMemHeavyComponent', 'name': 'D', 'numLinks': 0})


def story_findMemHeavyEvent():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'findMemHeavyEvent', 'name': 'A', 'numLinks': 2})
    comp_B.addParams({'story': 'findMemHeavyEvent', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'findMemHeavyEvent', 'name': 'C', 'numLinks': 2})
    comp_D.addParams({'story': 'findMemHeavyEvent', 'name': 'D', 'numLinks': 2})

    # Ring A-B-C-D-A (clockwise); port0=left link, port1=right link
    sst.Link('link_AB').connect((comp_A, "port1", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('link_BC').connect((comp_B, "port1", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('link_CD').connect((comp_C, "port1", "1ns"), (comp_D, "port0", "1ns"))
    sst.Link('link_DA').connect((comp_D, "port1", "1ns"), (comp_A, "port0", "1ns"))


def story_findStarvedComponent():
    comp_A = sst.Component("A", "debugUseCases.Node")
    comp_B = sst.Component("B", "debugUseCases.Node")
    comp_C = sst.Component("C", "debugUseCases.Node")
    comp_D = sst.Component("D", "debugUseCases.Node")

    comp_A.addParams({'story': 'findStarvedComponent', 'name': 'A', 'numLinks': 2})
    comp_B.addParams({'story': 'findStarvedComponent', 'name': 'B', 'numLinks': 2})
    comp_C.addParams({'story': 'findStarvedComponent', 'name': 'C', 'numLinks': 2})
    comp_D.addParams({'story': 'findStarvedComponent', 'name': 'D', 'numLinks': 2})

    # Ring A-B-C-D-A (clockwise); port0=left link, port1=right link
    sst.Link('link_AB').connect((comp_A, "port1", "1ns"), (comp_B, "port0", "1ns"))
    sst.Link('link_BC').connect((comp_B, "port1", "1ns"), (comp_C, "port0", "1ns"))
    sst.Link('link_CD').connect((comp_C, "port1", "1ns"), (comp_D, "port0", "1ns"))
    sst.Link('link_DA').connect((comp_D, "port1", "1ns"), (comp_A, "port0", "1ns"))


def main():
    story = parse_story_arg()

    for valid_story in VALID_STORIES:
        if story == valid_story:
            builder = globals().get(f"story_{valid_story}")
            if builder is None:
                raise ValueError(f"No builder defined for story: {valid_story}")
            warn_if_story_not_hand_verified(valid_story)
            print_assessment_url(valid_story)
            builder()
            return


main()
