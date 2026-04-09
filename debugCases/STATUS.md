# SST Debug Story Status

This document tracks the status of verifying and assessing the implemented SST debug stories. We have initial implementations for all stories and are now hand-verifying that each implementation matches the intent of its use case. We also want to assess, for each story, how the SST debugger can be used today to address it.

## Hand Verification Status

This table is intended to track which implemented stories have been manually checked end-to-end.

| Story | Hand-verified? | Notes |
| --- | --- | --- |
| **Event Tracing** |  |  |
| wrongPath | ❌ Not started |  |
| infiniteLoop | ❌ Not started |  |
| unexpectedDisappear | ❌ Not started |  |
| missedDeadline | ❌ Not started |  |
| outOfOrderReceipt | ❌ Not started |  |
| duplicateSepTimes | ❌ Not started |  |
| duplicateSameTime | ❌ Not started |  |
| **Event Processing** |  |  |
| broadcastStorm | ❌ Not started |  |
| badMerge | ❌ Not started |  |
| **Incorrect Topology** |  |  |
| missingLink | ❌ Not started |  |
| wrongLink | ❌ Not started |  |
| unexpectedDuplicateLink | ❌ Not started |  |
| **Deadlock** |  |  |
| directDeadlock | ❌ Not started |  |
| indirectDeadlock | ❌ Not started |  |
| **Fault Detection And Attribution** |  |  |
| detectWhenComponentBecomesInvalid | ❌ Not started |  |
| badInvariantBetweenComponents | ❌ Not started |  |
| componentsLoseParity | ❌ Not started |  |
| divergedModels_A / divergedModels_B | ❌ Not started |  |
| componentCausesSegfault | ❌ Not started |  |
| badInitialState | ❌ Not started |  |
| badTerminatingState | ❌ Not started |  |
| findFirstToComplete | ❌ Not started |  |
| determineWhatNotComplete | ❌ Not started |  |
| **Load Imbalances** |  |  |
| findEventHeavyComponent | ❌ Not started |  |
| findSlowProcessingComponent | ❌ Not started |  |
| findMemHeavyComponent | ❌ Not started |  |
| findMemHeavyEvent | ❌ Not started |  |
| findStarvedComponent | ❌ Not started |  |

## SST Debugger Assessments

This table tracks which stories we have examined with the SST debugger. For each story, we want to document how the debugger can be used to identify or analyze the case, what worked well and what did not, and any wishlist features that would improve the workflow.

| Story | SST debugger assessment | Notes |
| --- | --- | --- |
| **Event Tracing** |  |  |
| [wrongPath](assessments/wrongPath.md) | ❌ Not started |  |
| [infiniteLoop](assessments/infiniteLoop.md) | ❌ Not started |  |
| [unexpectedDisappear](assessments/unexpectedDisappear.md) | ❌ Not started |  |
| [missedDeadline](assessments/missedDeadline.md) | ❌ Not started |  |
| [outOfOrderReceipt](assessments/outOfOrderReceipt.md) | ❌ Not started |  |
| [duplicateSepTimes](assessments/duplicateSepTimes.md) | ❌ Not started |  |
| [duplicateSameTime](assessments/duplicateSameTime.md) | ❌ Not started |  |
| **Event Processing** |  |  |
| [broadcastStorm](assessments/broadcastStorm.md) | ❌ Not started |  |
| [badMerge](assessments/badMerge.md) | ❌ Not started |  |
| **Incorrect Topology** |  |  |
| [missingLink](assessments/missingLink.md) | ❌ Not started |  |
| [wrongLink](assessments/wrongLink.md) | ❌ Not started |  |
| [unexpectedDuplicateLink](assessments/unexpectedDuplicateLink.md) | ❌ Not started |  |
| **Deadlock** |  |  |
| [directDeadlock](assessments/directDeadlock.md) | ❌ Not started |  |
| [indirectDeadlock](assessments/indirectDeadlock.md) | ❌ Not started |  |
| **Fault Detection And Attribution** |  |  |
| [detectWhenComponentBecomesInvalid](assessments/detectWhenComponentBecomesInvalid.md) | ❌ Not started |  |
| [badInvariantBetweenComponents](assessments/badInvariantBetweenComponents.md) | ❌ Not started |  |
| [componentsLoseParity](assessments/componentsLoseParity.md) | ❌ Not started |  |
| [divergedModels](assessments/divergedModels.md) | ❌ Not started |  |
| [componentCausesSegfault](assessments/componentCausesSegfault.md) | ❌ Not started |  |
| [badInitialState](assessments/badInitialState.md) | ❌ Not started |  |
| [badTerminatingState](assessments/badTerminatingState.md) | ❌ Not started |  |
| [findFirstToComplete](assessments/findFirstToComplete.md) | ❌ Not started |  |
| [determineWhatNotComplete](assessments/determineWhatNotComplete.md) | ❌ Not started |  |
| **Load Imbalances** |  |  |
| [findEventHeavyComponent](assessments/findEventHeavyComponent.md) | ❌ Not started |  |
| [findSlowProcessingComponent](assessments/findSlowProcessingComponent.md) | ❌ Not started |  |
| [findMemHeavyComponent](assessments/findMemHeavyComponent.md) | ❌ Not started |  |
| [findMemHeavyEvent](assessments/findMemHeavyEvent.md) | ❌ Not started |  |
| [findStarvedComponent](assessments/findStarvedComponent.md) | ❌ Not started |  |