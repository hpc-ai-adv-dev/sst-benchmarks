import argparse
import sst

VALID_STORIES = [
    "wrongPath",
    "infiniteLoop",
    "unexpectedDisappear",
    "missedDeadline",
    "outOfOrderReceipt",
    "duplicateSepTimes",
    "duplicateSameTime",
    "broadcastStorm",
    "badMerge",
    "missingLink",
    "wrongLink",
    "unexpectedDuplicateLink",
    "directDeadlock",
    "indirectDeadlock",
    "detectWhenComponentBecomesInvalid",
    "badInvariantBetweenComponents",
    "componentsLoseParity",
    "divergedModels_A",
    "divergedModels_B",
    "componentCausesSegfault",
    "badInitialState",
    "badTerminatingState",
    "findFirstToComplete",
    "determineWhatNotComplete",
    "findEventHeavyComponent",
    "findSlowProcessingComponent",
    "findMemHeavyComponent",
    "findMemHeavyEvent",
    "findStarvedComponent",
]


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


def story_broadcastStorm():
    error_story_not_yet_implemented()


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
    comp_E.addParams({'story': 'outOfOrderReceipt', 'name': 'D', 'numLinks': 2})

    sst.Link('a_b').connect((comp_A, "port0", "2ns"), (comp_B, "port0", "2ns"))
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



def story_badMerge():
    error_story_not_yet_implemented()


def story_missingLink():
    error_story_not_yet_implemented()


def story_wrongLink():
    error_story_not_yet_implemented()


def story_unexpectedDuplicateLink():
    error_story_not_yet_implemented()


def story_directDeadlock():
    error_story_not_yet_implemented()


def story_indirectDeadlock():
    error_story_not_yet_implemented()


def story_detectWhenComponentBecomesInvalid():
    error_story_not_yet_implemented()


def story_badInvariantBetweenComponents():
    error_story_not_yet_implemented()


def story_componentsLoseParity():
    error_story_not_yet_implemented()


def story_divergedModels_A():
    error_story_not_yet_implemented()


def story_divergedModels_B():
    error_story_not_yet_implemented()


def story_componentCausesSegfault():
    error_story_not_yet_implemented()


def story_badInitialState():
    error_story_not_yet_implemented()


def story_badTerminatingState():
    error_story_not_yet_implemented()


def story_findFirstToComplete():
    error_story_not_yet_implemented()


def story_determineWhatNotComplete():
    error_story_not_yet_implemented()


def story_findEventHeavyComponent():
    error_story_not_yet_implemented()


def story_findSlowProcessingComponent():
    error_story_not_yet_implemented()


def story_findMemHeavyComponent():
    error_story_not_yet_implemented()


def story_findMemHeavyEvent():
    error_story_not_yet_implemented()


def story_findStarvedComponent():
    error_story_not_yet_implemented()


def main():
    story = parse_story_arg()

    for valid_story in VALID_STORIES:
        if story == valid_story:
            builder = globals().get(f"story_{valid_story}")
            if builder is None:
                raise ValueError(f"No builder defined for story: {valid_story}")
            builder()
            return


main()
