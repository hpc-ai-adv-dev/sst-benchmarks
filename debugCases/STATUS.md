# SST Debug Story Status

This document tracks the status of verifying and assessing the implemented SST debug stories. We have initial implementations for all stories and are now hand-verifying that each implementation matches the intent of its use case. We are also assessing how the SST debugger, as it exists today, can address each story.

## Hand Verification

This table is intended to track which implemented stories have been manually checked end-to-end.

In the done column we use ❓ to indicate that although reading the code, the implementation looks correct it hasn't been hand verified and I'm unsure how we could verify it or at-least it would be difficult to do so.

| Story | Done? | Notes |
| --- | --- | --- |
| **Event Tracing** |  |  |
| [wrongPath](assessments/wrongPath.md) | ✅ |  |
| [infiniteLoop](assessments/infiniteLoop.md) | ✅ |  |
| [unexpectedDisappear](assessments/unexpectedDisappear.md) | ✅ |  |
| [missedDeadline](assessments/missedDeadline.md) | ✅ |  |
| [outOfOrderReceipt](assessments/outOfOrderReceipt.md) | ❌ |  |
| [duplicateSepTimes](assessments/duplicateSepTimes.md) | ✅ |  |
| [duplicateSameTime](assessments/duplicateSameTime.md) | ✅ |  |
| **Event Processing** |  |  |
| [broadcastStorm](assessments/broadcastStorm.md) | ✅ |  |
| [badMerge](assessments/badMerge.md) | ✅ |  |
| **Incorrect Topology** |  |  |
| [missingLink](assessments/missingLink.md) | ✅ |  |
| [wrongLink](assessments/wrongLink.md) | ✅ |  |
| [unexpectedDuplicateLink](assessments/unexpectedDuplicateLink.md) | ✅ |  |
| **Deadlock** |  |  |
| [directDeadlock](assessments/directDeadlock.md) | ❓ |  |
| [indirectDeadlock](assessments/indirectDeadlock.md) | ❓ |  |
| **Fault Detection And Attribution** |  |  |
| [detectWhenComponentBecomesInvalid](assessments/detectWhenComponentBecomesInvalid.md) | ✅ |  |
| [badInvariantBetweenComponents](assessments/badInvariantBetweenComponents.md) | ✅ |  |
| [componentsLoseParity](assessments/componentsLoseParity.md) | ✅ |  |
| [divergedModels](assessments/divergedModels.md) | ✅ |  |
| [componentCausesSegfault](assessments/componentCausesSegfault.md) | ✅ |  |
| [badInitialState](assessments/badInitialState.md) | ✅ |  |
| [badTerminatingState](assessments/badTerminatingState.md) | ✅ |  |
| [findFirstToComplete](assessments/findFirstToComplete.md) | ❓ |  |
| [determineWhatNotComplete](assessments/determineWhatNotComplete.md) | ❓ |  |
| **Load Imbalances** |  |  |
| [findEventHeavyComponent](assessments/findEventHeavyComponent.md) | ✅ |  |
| [findSlowProcessingComponent](assessments/findSlowProcessingComponent.md) | ❓ |  |
| [findMemHeavyComponent](assessments/findMemHeavyComponent.md) | ❓ |  |
| [findMemHeavyEvent](assessments/findMemHeavyEvent.md) | ❓ |  |
| [findStarvedComponent](assessments/findStarvedComponent.md) | ✅ |  |

## SST Debugger Assessments

This table tracks which stories we have examined with the SST debugger. For each story, we want to document how the debugger can be used to identify or analyze the case, what worked well and what did not, and any wishlist features that would improve the workflow.

In the done column we use 🚧 to indicate 'in progress'.

| Story | Done? | Notes |
| --- | --- | --- |
| **Event Tracing** |  |  |
| [wrongPath](assessments/wrongPath.md) | 🚧 | works in debugger but requires advanced topology knowlege and the event to set a side effect on components |
| [infiniteLoop](assessments/infiniteLoop.md) | ❌ |  |
| [unexpectedDisappear](assessments/unexpectedDisappear.md) | ❌ |  |
| [missedDeadline](assessments/missedDeadline.md) | ❌ |  |
| [outOfOrderReceipt](assessments/outOfOrderReceipt.md) | ❌ |  |
| [duplicateSepTimes](assessments/duplicateSepTimes.md) | ❌ |  |
| [duplicateSameTime](assessments/duplicateSameTime.md) | ❌ |  |
| **Event Processing** |  |  |
| [broadcastStorm](assessments/broadcastStorm.md) | ❌ |  |
| [badMerge](assessments/badMerge.md) | ❌ |  |
| **Incorrect Topology** |  |  |
| [missingLink](assessments/missingLink.md) | ❌ |  |
| [wrongLink](assessments/wrongLink.md) | ❌ |  |
| [unexpectedDuplicateLink](assessments/unexpectedDuplicateLink.md) | ❌ |  |
| **Deadlock** |  |  |
| [directDeadlock](assessments/directDeadlock.md) | ❌ |  |
| [indirectDeadlock](assessments/indirectDeadlock.md) | ❌ |  |
| **Fault Detection And Attribution** |  |  |
| [detectWhenComponentBecomesInvalid](assessments/detectWhenComponentBecomesInvalid.md) | ❌ |  |
| [badInvariantBetweenComponents](assessments/badInvariantBetweenComponents.md) | ❌ |  |
| [componentsLoseParity](assessments/componentsLoseParity.md) | ❌ |  |
| [divergedModels](assessments/divergedModels.md) | ❌ |  |
| [componentCausesSegfault](assessments/componentCausesSegfault.md) | ❌ |  |
| [badInitialState](assessments/badInitialState.md) | ❌ |  |
| [badTerminatingState](assessments/badTerminatingState.md) | ❌ |  |
| [findFirstToComplete](assessments/findFirstToComplete.md) | ❌ |  |
| [determineWhatNotComplete](assessments/determineWhatNotComplete.md) | ❌ |  |
| **Load Imbalances** |  |  |
| [findEventHeavyComponent](assessments/findEventHeavyComponent.md) | ❌ |  |
| [findSlowProcessingComponent](assessments/findSlowProcessingComponent.md) | ❌ |  |
| [findMemHeavyComponent](assessments/findMemHeavyComponent.md) | ❌ |  |
| [findMemHeavyEvent](assessments/findMemHeavyEvent.md) | ❌ |  |
| [findStarvedComponent](assessments/findStarvedComponent.md) | ❌ |  |