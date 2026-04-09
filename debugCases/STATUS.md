# SST Debug Story Status

This document tracks the status of verifying and assessing the implemented SST debug stories. We have initial implementations for all stories and are now hand-verifying that each implementation matches the intent of its use case. We also want to assess, for each story, how the SST debugger can be used today to address it.

## Hand Verification Status

This table is intended to track which implemented stories have been manually checked end-to-end.

<table>
	<thead>
		<tr style="background-color: #1a3a52; color: #ffffff;">
			<th align="left">Story</th>
			<th align="left">Hand-verified?</th>
			<th align="left">Notes</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Event Tracing</strong></th>
		</tr>
		<tr><td><code>wrongPath</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>infiniteLoop</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>unexpectedDisappear</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>missedDeadline</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>outOfOrderReceipt</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>duplicateSepTimes</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>duplicateSameTime</code></td><td>❌ Not started</td><td></td></tr>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Event Processing</strong></th>
		</tr>
		<tr><td><code>broadcastStorm</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>badMerge</code></td><td>❌ Not started</td><td></td></tr>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Incorrect Topology</strong></th>
		</tr>
		<tr><td><code>missingLink</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>wrongLink</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>unexpectedDuplicateLink</code></td><td>❌ Not started</td><td></td></tr>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Deadlock</strong></th>
		</tr>
		<tr><td><code>directDeadlock</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>indirectDeadlock</code></td><td>❌ Not started</td><td></td></tr>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Fault Detection And Attribution</strong></th>
		</tr>
		<tr><td><code>detectWhenComponentBecomesInvalid</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>badInvariantBetweenComponents</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>componentsLoseParity</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>divergedModels_A</code> / <code>divergedModels_B</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>componentCausesSegfault</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>badInitialState</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>badTerminatingState</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>findFirstToComplete</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>determineWhatNotComplete</code></td><td>❌ Not started</td><td></td></tr>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Load Imbalances</strong></th>
		</tr>
		<tr><td><code>findEventHeavyComponent</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>findSlowProcessingComponent</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>findMemHeavyComponent</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>findMemHeavyEvent</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>findStarvedComponent</code></td><td>❌ Not started</td><td></td></tr>
	</tbody>
</table>

## SST Debugger Assessments

This table tracks which stories we have examined with the SST debugger. For each story, we want to document how the debugger can be used to identify or analyze the case, what worked well and what did not, and any wishlist features that would improve the workflow.

<table>
	<thead>
		<tr style="background-color: #1a3a52; color: #ffffff;">
			<th align="left">Story</th>
			<th align="left">SST debugger assessment</th>
			<th align="left">Notes</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Event Tracing</strong></th>
		</tr>
		<tr><td><code>wrongPath</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>infiniteLoop</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>unexpectedDisappear</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>missedDeadline</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>outOfOrderReceipt</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>duplicateSepTimes</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>duplicateSameTime</code></td><td>❌ Not started</td><td></td></tr>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Event Processing</strong></th>
		</tr>
		<tr><td><code>broadcastStorm</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>badMerge</code></td><td>❌ Not started</td><td></td></tr>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Incorrect Topology</strong></th>
		</tr>
		<tr><td><code>missingLink</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>wrongLink</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>unexpectedDuplicateLink</code></td><td>❌ Not started</td><td></td></tr>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Deadlock</strong></th>
		</tr>
		<tr><td><code>directDeadlock</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>indirectDeadlock</code></td><td>❌ Not started</td><td></td></tr>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Fault Detection And Attribution</strong></th>
		</tr>
		<tr><td><code>detectWhenComponentBecomesInvalid</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>badInvariantBetweenComponents</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>componentsLoseParity</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>divergedModels_A</code> / <code>divergedModels_B</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>componentCausesSegfault</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>badInitialState</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>badTerminatingState</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>findFirstToComplete</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>determineWhatNotComplete</code></td><td>❌ Not started</td><td></td></tr>
		<tr>
			<th colspan="3" align="left" style="background-color: #4a7298; color: #ffffff;"><strong>Load Imbalances</strong></th>
		</tr>
		<tr><td><code>findEventHeavyComponent</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>findSlowProcessingComponent</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>findMemHeavyComponent</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>findMemHeavyEvent</code></td><td>❌ Not started</td><td></td></tr>
		<tr><td><code>findStarvedComponent</code></td><td>❌ Not started</td><td></td></tr>
	</tbody>
</table>