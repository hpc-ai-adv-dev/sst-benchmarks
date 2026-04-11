# componentsLoseParity

## Situation

A and B are expected to stay in matching state over time, but their scripted values diverge at cycle 40 when they become 5 and 7.

![componentsLoseParity flowchart](../story_flowcharts/componentsLoseParity.png)


## To try it out:

`sst --interactive-start componentsLoseParity.py`

-or-

`./doit componentsLoseParity`

## Approach 1 -- step and print

```
run 11ns   # Let's run to where we can observe the state of components after processing events from 10ns
p A        # A.value is 1
p B        # As is B.value
run 10ns   # Advance some more
p A        # A.value is 4
p B        # As is B.value
run 10ns   # Advance some more
p A        # A.value is 3
p B        # As is B.Value
run 10ns   # Advance some more
p A        # A.value is 5
p B        # But B.value mismatches as 7!
```

Let's now run this and observe the output from the SST debugger:

```
Entering interactive mode at time 0
Interactive start at 0
> run 11ns
Entering interactive mode at time 11000
Ran clock for 11000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 1 (int)
 visited = 0 (int)
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 1 (int)
 visited = 0 (int)
> run 10ns
Entering interactive mode at time 21000
Ran clock for 10000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 4 (int)
 visited = 0 (int)
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 4 (int)
 visited = 0 (int)
> run 10ns
Entering interactive mode at time 31000
Ran clock for 10000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 3 (int)
 visited = 0 (int)
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 3 (int)
 visited = 0 (int)
> run 10ns
Entering interactive mode at time 41000
Ran clock for 10000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 5 (int)
 visited = 0 (int)
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 7 (int)
 visited = 0 (int)
```

## Approach 1 -- tracepoints
```
Entering interactive mode at time 0
Interactive start at 0
> cd A
> trace value changed : 200 200 : value : printTrace
Added watchpoint #0
> cd ..
> cd B
> trace value changed : 200 200 : value : printTrace
Added watchpoint #1
> run 60ns
Entering interactive mode at time 60000
Ran clock for 60000 sim cycles
> printTrace 0
TriggerRecord:@cycle40000: samples lost = 0: A/value=5
buf[0] BC @1000 (-) A/value=0
buf[1] AC @1000 (-) A/value=0
buf[2] BC @2000 (-) A/value=0
buf[3] AC @2000 (-) A/value=0
buf[4] BC @3000 (-) A/value=0
buf[5] AC @3000 (-) A/value=0
buf[6] BC @4000 (-) A/value=0
buf[7] AC @4000 (-) A/value=0
buf[8] BC @5000 (-) A/value=0
buf[9] AC @5000 (-) A/value=0
buf[10] BC @6000 (-) A/value=0
buf[11] AC @6000 (-) A/value=0
buf[12] BC @7000 (-) A/value=0
buf[13] AC @7000 (-) A/value=0
buf[14] BC @8000 (-) A/value=0
buf[15] AC @8000 (-) A/value=0
buf[16] BC @9000 (-) A/value=0
buf[17] AC @9000 (-) A/value=0
buf[18] BC @10000 (-) A/value=0
buf[19] AC @10000 (!) A/value=1
buf[20] BC @11000 (+) A/value=1
buf[21] AC @11000 (+) A/value=1
buf[22] BC @12000 (+) A/value=1
buf[23] AC @12000 (+) A/value=1
buf[24] BC @13000 (+) A/value=1
buf[25] AC @13000 (+) A/value=1
buf[26] BC @14000 (+) A/value=1
buf[27] AC @14000 (+) A/value=1
buf[28] BC @15000 (+) A/value=1
buf[29] AC @15000 (+) A/value=1
buf[30] BC @16000 (+) A/value=1
buf[31] AC @16000 (+) A/value=1
buf[32] BC @17000 (+) A/value=1
buf[33] AC @17000 (+) A/value=1
buf[34] BC @18000 (+) A/value=1
buf[35] AC @18000 (+) A/value=1
buf[36] BC @19000 (+) A/value=1
buf[37] AC @19000 (+) A/value=1
buf[38] BC @20000 (+) A/value=1
buf[39] AC @20000 (+) A/value=4
buf[40] BC @21000 (+) A/value=4
buf[41] AC @21000 (+) A/value=4
buf[42] BC @22000 (+) A/value=4
buf[43] AC @22000 (+) A/value=4
buf[44] BC @23000 (+) A/value=4
buf[45] AC @23000 (+) A/value=4
buf[46] BC @24000 (+) A/value=4
buf[47] AC @24000 (+) A/value=4
buf[48] BC @25000 (+) A/value=4
buf[49] AC @25000 (+) A/value=4
buf[50] BC @26000 (+) A/value=4
buf[51] AC @26000 (+) A/value=4
buf[52] BC @27000 (+) A/value=4
buf[53] AC @27000 (+) A/value=4
buf[54] BC @28000 (+) A/value=4
buf[55] AC @28000 (+) A/value=4
buf[56] BC @29000 (+) A/value=4
buf[57] AC @29000 (+) A/value=4
buf[58] BC @30000 (+) A/value=4
buf[59] AC @30000 (+) A/value=3
buf[60] BC @31000 (+) A/value=3
buf[61] AC @31000 (+) A/value=3
buf[62] BC @32000 (+) A/value=3
buf[63] AC @32000 (+) A/value=3
buf[64] BC @33000 (+) A/value=3
buf[65] AC @33000 (+) A/value=3
buf[66] BC @34000 (+) A/value=3
buf[67] AC @34000 (+) A/value=3
buf[68] BC @35000 (+) A/value=3
buf[69] AC @35000 (+) A/value=3
buf[70] BC @36000 (+) A/value=3
buf[71] AC @36000 (+) A/value=3
buf[72] BC @37000 (+) A/value=3
buf[73] AC @37000 (+) A/value=3
buf[74] BC @38000 (+) A/value=3
buf[75] AC @38000 (+) A/value=3
buf[76] BC @39000 (+) A/value=3
buf[77] AC @39000 (+) A/value=3
buf[78] BC @40000 (+) A/value=3
buf[79] AC @40000 (+) A/value=5
buf[80] BC @41000 (+) A/value=5
buf[81] AC @41000 (+) A/value=5
buf[82] BC @42000 (+) A/value=5
buf[83] AC @42000 (+) A/value=5
buf[84] BC @43000 (+) A/value=5
buf[85] AC @43000 (+) A/value=5
buf[86] BC @44000 (+) A/value=5
buf[87] AC @44000 (+) A/value=5
buf[88] BC @45000 (+) A/value=5
buf[89] AC @45000 (+) A/value=5
buf[90] BC @46000 (+) A/value=5
buf[91] AC @46000 (+) A/value=5
buf[92] BC @47000 (+) A/value=5
buf[93] AC @47000 (+) A/value=5
buf[94] BC @48000 (+) A/value=5
buf[95] AC @48000 (+) A/value=5
buf[96] BC @49000 (+) A/value=5
buf[97] AC @49000 (+) A/value=5
buf[98] BC @50000 (+) A/value=5
buf[99] AC @50000 (+) A/value=5
buf[100] BC @51000 (+) A/value=5
buf[101] AC @51000 (+) A/value=5
buf[102] BC @52000 (+) A/value=5
buf[103] AC @52000 (+) A/value=5
buf[104] BC @53000 (+) A/value=5
buf[105] AC @53000 (+) A/value=5
buf[106] BC @54000 (+) A/value=5
buf[107] AC @54000 (+) A/value=5
buf[108] BC @55000 (+) A/value=5
buf[109] AC @55000 (+) A/value=5
buf[110] BC @56000 (+) A/value=5
buf[111] AC @56000 (+) A/value=5
buf[112] BC @57000 (+) A/value=5
buf[113] AC @57000 (+) A/value=5
buf[114] BC @58000 (+) A/value=5
buf[115] AC @58000 (+) A/value=5
buf[116] BC @59000 (+) A/value=5
buf[117] AC @59000 (+) A/value=5
> printTrace 1
TriggerRecord:@cycle40000: samples lost = 0: B/value=7
buf[0] BC @1000 (-) B/value=0
buf[1] AC @1000 (-) B/value=0
buf[2] BC @2000 (-) B/value=0
buf[3] AC @2000 (-) B/value=0
buf[4] BC @3000 (-) B/value=0
buf[5] AC @3000 (-) B/value=0
buf[6] BC @4000 (-) B/value=0
buf[7] AC @4000 (-) B/value=0
buf[8] BC @5000 (-) B/value=0
buf[9] AC @5000 (-) B/value=0
buf[10] BC @6000 (-) B/value=0
buf[11] AC @6000 (-) B/value=0
buf[12] BC @7000 (-) B/value=0
buf[13] AC @7000 (-) B/value=0
buf[14] BC @8000 (-) B/value=0
buf[15] AC @8000 (-) B/value=0
buf[16] BC @9000 (-) B/value=0
buf[17] AC @9000 (-) B/value=0
buf[18] BC @10000 (-) B/value=0
buf[19] AC @10000 (!) B/value=1
buf[20] BC @11000 (+) B/value=1
buf[21] AC @11000 (+) B/value=1
buf[22] BC @12000 (+) B/value=1
buf[23] AC @12000 (+) B/value=1
buf[24] BC @13000 (+) B/value=1
buf[25] AC @13000 (+) B/value=1
buf[26] BC @14000 (+) B/value=1
buf[27] AC @14000 (+) B/value=1
buf[28] BC @15000 (+) B/value=1
buf[29] AC @15000 (+) B/value=1
buf[30] BC @16000 (+) B/value=1
buf[31] AC @16000 (+) B/value=1
buf[32] BC @17000 (+) B/value=1
buf[33] AC @17000 (+) B/value=1
buf[34] BC @18000 (+) B/value=1
buf[35] AC @18000 (+) B/value=1
buf[36] BC @19000 (+) B/value=1
buf[37] AC @19000 (+) B/value=1
buf[38] BC @20000 (+) B/value=1
buf[39] AC @20000 (+) B/value=4
buf[40] BC @21000 (+) B/value=4
buf[41] AC @21000 (+) B/value=4
buf[42] BC @22000 (+) B/value=4
buf[43] AC @22000 (+) B/value=4
buf[44] BC @23000 (+) B/value=4
buf[45] AC @23000 (+) B/value=4
buf[46] BC @24000 (+) B/value=4
buf[47] AC @24000 (+) B/value=4
buf[48] BC @25000 (+) B/value=4
buf[49] AC @25000 (+) B/value=4
buf[50] BC @26000 (+) B/value=4
buf[51] AC @26000 (+) B/value=4
buf[52] BC @27000 (+) B/value=4
buf[53] AC @27000 (+) B/value=4
buf[54] BC @28000 (+) B/value=4
buf[55] AC @28000 (+) B/value=4
buf[56] BC @29000 (+) B/value=4
buf[57] AC @29000 (+) B/value=4
buf[58] BC @30000 (+) B/value=4
buf[59] AC @30000 (+) B/value=3
buf[60] BC @31000 (+) B/value=3
buf[61] AC @31000 (+) B/value=3
buf[62] BC @32000 (+) B/value=3
buf[63] AC @32000 (+) B/value=3
buf[64] BC @33000 (+) B/value=3
buf[65] AC @33000 (+) B/value=3
buf[66] BC @34000 (+) B/value=3
buf[67] AC @34000 (+) B/value=3
buf[68] BC @35000 (+) B/value=3
buf[69] AC @35000 (+) B/value=3
buf[70] BC @36000 (+) B/value=3
buf[71] AC @36000 (+) B/value=3
buf[72] BC @37000 (+) B/value=3
buf[73] AC @37000 (+) B/value=3
buf[74] BC @38000 (+) B/value=3
buf[75] AC @38000 (+) B/value=3
buf[76] BC @39000 (+) B/value=3
buf[77] AC @39000 (+) B/value=3
buf[78] BC @40000 (+) B/value=3
buf[79] AC @40000 (+) B/value=7
buf[80] BC @41000 (+) B/value=7
buf[81] AC @41000 (+) B/value=7
buf[82] BC @42000 (+) B/value=7
buf[83] AC @42000 (+) B/value=7
buf[84] BC @43000 (+) B/value=7
buf[85] AC @43000 (+) B/value=7
buf[86] BC @44000 (+) B/value=7
buf[87] AC @44000 (+) B/value=7
buf[88] BC @45000 (+) B/value=7
buf[89] AC @45000 (+) B/value=7
buf[90] BC @46000 (+) B/value=7
buf[91] AC @46000 (+) B/value=7
buf[92] BC @47000 (+) B/value=7
buf[93] AC @47000 (+) B/value=7
buf[94] BC @48000 (+) B/value=7
buf[95] AC @48000 (+) B/value=7
buf[96] BC @49000 (+) B/value=7
buf[97] AC @49000 (+) B/value=7
buf[98] BC @50000 (+) B/value=7
buf[99] AC @50000 (+) B/value=7
buf[100] BC @51000 (+) B/value=7
buf[101] AC @51000 (+) B/value=7
buf[102] BC @52000 (+) B/value=7
buf[103] AC @52000 (+) B/value=7
buf[104] BC @53000 (+) B/value=7
buf[105] AC @53000 (+) B/value=7
buf[106] BC @54000 (+) B/value=7
buf[107] AC @54000 (+) B/value=7
buf[108] BC @55000 (+) B/value=7
buf[109] AC @55000 (+) B/value=7
buf[110] BC @56000 (+) B/value=7
buf[111] AC @56000 (+) B/value=7
buf[112] BC @57000 (+) B/value=7
buf[113] AC @57000 (+) B/value=7
buf[114] BC @58000 (+) B/value=7
buf[115] AC @58000 (+) B/value=7
buf[116] BC @59000 (+) B/value=7
buf[117] AC @59000 (+) B/value=7
```

Notes:
- This approach is showing me more information than I want. Is there a way to only post to the tracepoint buffer when there is a change?