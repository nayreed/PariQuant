# PariQuant

Rezwan Ahmad Nayreed (ORCID 0009-0005-4256-3068)
Oulun Yliopisto, Oulu, Finland · RezwanAhmad.Nayreed@student.oulu.fi

*Revised after the review of 2 October 2026 (comments by S. Adhikari). Passages that changed in response to a review comment carry a marker such as ⟨R3⟩, which refers to the issue of that number; see [`../review-response.md`](../review-response.md). The markers are for review only and are removed in the submitted text.*

---

**Abstract.** Quantum processors based on different hardware technologies can implement the same logical computation using substantially different native gates, connectivity, routing, execution times and measurement requirements. Existing cross-platform benchmarks compare workloads and performance, but they do not directly establish when the physical implementations of the same computation have used comparable resources.

This research proposes PariQuant, a framework for translating common logical quantum workloads into architecture-specific native implementations and comparing the resulting resource use without assuming a universal conversion between heterogeneous gates. The initial study uses four physical QPUs in a 2 × 2 design: IBM Berlin and IQM Emerald as superconducting systems, and AQT IBEX-Q1 and IonQ Forte-1 as trapped-ion systems. Each translated circuit is first checked to preserve the intended logical computation. PariQuant then records observable quantities including native operations, occupied qubits, routing or transport, execution timing and the requested number of shots ⟨R6⟩, while provider-reported calibration and characterization information is retained separately as execution context rather than as a model of the hardware's noise ⟨R2⟩.

Explicit, researcher-defined comparison rules, frozen before held-out evaluation ⟨R3⟩, classify implementation pairs as resource-matched, different, or insufficiently characterized. The framework will be developed through controlled compilation and simulation and evaluated, subject to access, on the four selected QPUs. Its usefulness will be tested against simpler circuit metrics and existing feature-based benchmarking approaches on held-out workloads and calibration periods.

**Keywords:** Heterogeneous QPUs · Quantum resource accounting · Cross-platform benchmarking · Quantum compilation

---

## 1  Background and Motivation

A quantum circuit is an abstract computation. Before execution, it must be translated into the operations supported by a particular quantum processing unit (QPU), mapped to physical qubits, routed through the available connectivity and scheduled subject to hardware constraints. Consequently, two processors may receive the same logical workload while executing very different physical implementations. Real-system architectural studies have shown that native gates, connectivity, mapping and calibration-aware compilation can materially change the resulting circuit and its performance [10]. Direct experiments comparing superconducting and trapped-ion systems likewise demonstrate that architectural differences influence how the same algorithms are realized and executed [8, 2].

This direction also follows experimental work at the University of Oulu. Herajärvi conducted six controlled experiments on IBM's 127-qubit superconducting Brisbane processor, studying how neighboring gate activity, circuit distance, parallel execution and circuit duration affect quantum computation [6]. The results showed both distance-dependent crosstalk and non-linear hardware behavior, and the thesis identified experiments on longer circuits and different quantum hardware platforms as future work. PariQuant addresses a different question, but adopts the same controlled experimental philosophy while moving from one superconducting processor to cross-architecture comparison.

The broader Oulu hardware-security review by Adhikari and Halunen similarly emphasizes that hardware effects depend on the underlying qubit technology and that results cannot automatically be generalized from one architecture to another [1]. These studies motivate PariQuant's experimental question: if hardware architecture changes the implementation itself, what evidence is required before two implementations can be called resource-comparable?

Raw gate count, qubit count or circuit depth are useful descriptions, but none alone provides such evidence. A superconducting implementation may require additional routing operations because of limited connectivity, while a trapped-ion implementation may expose different native interactions, operation durations and scheduling constraints. Even apparently dimensionless quantities, such as execution time normalized by a coherence time, remain conditional on a specific physical and noise model. A useful comparison therefore needs an auditable accounting boundary rather than an assumed universal conversion between hardware technologies.

## 2  Prior Work and Research Gap

Cross-platform quantum benchmarking already spans compact capability measures and richer workload descriptions. Quantum Volume summarizes random model circuits [4], volumetric benchmarking retains performance across a width–depth region [3], and QED-C application-oriented benchmarking defines common application workloads and reference-circuit procedures while combining output quality with execution-related measurements [9]. SupermarQ and QASMBench add structural descriptors for heterogeneous systems [16, 7].

Featuremetric is the closest representational overlap: it maps circuits into a multidimensional feature space and demonstrates capability models using IBM superconducting and IonQ trapped-ion systems [12]. PariQuant therefore does not claim novelty from circuit vectors. Hardware-aware compilation captures native decomposition, topology, routing and reliability information [10]; the Metric–Noise–Resource framework relates resources, noise and performance at the full-stack level [5]; and recent QUOPS work strengthens cross-platform capability comparison [13]. Together, these approaches make a broad claim that heterogeneous processors lack common benchmarks untenable.

At the same time, these approaches answer different questions. A common workload does not imply a common physical expenditure; a feature-space coordinate does not by itself certify a resource match; and equal output quality does not imply equal resource use. Simple predictors can also miss important circuit structure and context. Proctor et al. showed experimentally that structured programs can fail at substantially smaller sizes than disordered programs, demonstrating that circuit structure matters beyond a coarse size description [11]. Similarly, a reported average gate fidelity does not uniquely determine the operational error of a gate [14].

The research gap investigated here is therefore deliberately limited:

> Can the actual compiled implementations of the same logical workload on superconducting and trapped-ion physical QPUs be converted into an auditable consumption-and-context record, compared using pre-specified practical tolerances and uncertainty, and validated independently of the task-output scores used to assess performance?

The literature reviewed for this proposal establishes the components of this problem, including common workloads, feature spaces, compilation models, resource analysis and cross-platform experiments, but does not establish that a particular small set of observable descriptors is sufficient for the above comparison. PariQuant is therefore an empirical method and falsification study, not a claim of a universal quantum resource unit.

## 3  Research Questions and Objectives

The primary research question is:

> **RQ.** Under what conditions can compiled implementations of the same logical workload across the four selected physical QPUs, comprising two superconducting and two trapped-ion systems from different providers, be considered resource-comparable using observable execution properties and explicitly stated assumptions?

Three supporting questions guide the study:

- **RQ1.** Which descriptors of resource consumption and hardware context are measurable, non-redundant and interpretable both within and between the two selected hardware modalities?
- **RQ2.** How can the same logical workload be translated into architecture-specific native gate sets, and how can the resulting operations, routing or transport, timing and sampling requirements be compared without pretending that physically different operations have a universal exchange rate?
- **RQ3.** Do explicit, pre-specified descriptor-level matching rules remain reproducible across providers, compiler variants, workloads and calibration periods, how sensitive are their verdicts to the chosen tolerances ⟨R3⟩, and do they provide information beyond simpler metrics and feature-based baselines?

The corresponding objectives are to (O1) define a versioned accounting specification, (O2) implement a semantics-preserving cross-architecture translation layer together with backend-specific extraction software, (O3) define explicit match/difference/insufficient-evidence rules, and (O4) evaluate their validity, limitations and added information through simulation and hardware experiments.

## 4  Proposed PariQuant Method

### 4.0  Terminology

Several terms are used in a fixed sense throughout.

| Term | Meaning in this proposal |
|---|---|
| **Circuit qubit** ⟨R7⟩ | A qubit of the circuit before hardware mapping, including ancillas the circuit itself requires. Used instead of "logical qubit", which would suggest error-corrected encoding; no encoding is part of the study. |
| **Circuit width** | Total number of circuit qubits (data qubits plus ancillas). |
| **Physical qubit** | A hardware qubit. A physical qubit is *occupied* if it carries at least one operation or measurement in the compiled program; unused wires of a full-device circuit representation are not counted. |
| **Circuit-qubit order** ⟨R4⟩ | Which abstract circuit qubit each index names. |
| **Physical layout** ⟨R4⟩ | Which physical qubit implements each circuit qubit, including the final layout after routing. |
| **Measurement mapping** ⟨R4⟩ | Which classical bit receives the measurement of each measured circuit qubit. |
| **Bitstring convention** ⟨R4⟩ | The direction in which a returned string lists classical bits (for example, Qiskit lists the highest classical bit leftmost [28]). |
| **Requested shots** ⟨R6⟩ | The sampling budget submitted for a circuit; an experiment setting chosen and recorded by the experimenter. |
| **Provider-reported executed repetitions** ⟨R6⟩ | The actual execution count, only where the provider explicitly exposes it; otherwise unavailable. |
| **Returned / retained samples** ⟨R6⟩ | Samples present in the returned measurement data / samples remaining after any filtering or postselection. |
| **Approximation error** ⟨R5⟩ | Deviation introduced by an explicitly permitted approximate translation or synthesis step, measured between noiseless reference and translated objects (Sec. 4.1). Not hardware noise and not sampling uncertainty. |
| **Execution context** ⟨R2⟩ | Provider-reported calibration and characterization information with its provenance (Sec. 4.4). Not a model of the full physical noise channel. |

### 4.1  Cross-Architecture Translation Layer

Translation is a core part of PariQuant rather than an implicit compiler step. The same logical workload $W$ is first expressed in a reference circuit form whose semantics are fixed independently of the target hardware. For each target processor $H_i$, a translator $T_i$ then synthesizes that workload into the native operation family supported by the architecture:

$$C_i^{\text{native}} = T_i(W;\, H_i,\, \Gamma_i). \tag{1}$$

Focusing on the architecture-dependent two-qubit interaction used in the translation, the four target paths can be summarized as

$$W \longrightarrow \begin{cases} C_{\text{IBM}}^{\text{CZ/RZZ}},\\ C_{\text{IQM}}^{\text{CZ}},\\ C_{\text{AQT}}^{\text{RXX/MS}},\\ C_{\text{IonQ}}^{\text{ZZ}}. \end{cases}$$

Each $C_i$ must implement the same logical semantics before its resource record is compared with another implementation. The device-reported native instruction set and compiler configuration are frozen for each experimental campaign [20, 24].

Here $\Gamma_i$ records the native gate definitions, synthesis conventions, approximation limits and translator version. The translator is a contract, not necessarily a new compiler: it may invoke Qiskit, Amazon Braket or provider-native synthesis, provided that the native program and visible transformations are retained. Layout, routing and scheduling then produce the implementation that would actually be submitted or executed:

$$P_i = \text{MapSchedule}(C_i^{\text{native}},\, H_i,\, \Theta_i). \tag{2}$$

PariQuant does not assume relations such as 1 CNOT = 1 XX. KAK/Weyl analysis can identify the ideal nonlocal content of two-qubit operations up to local transformations, but physical interaction cost remains dependent on the available Hamiltonian and control assumptions [18, 17]. Small translated circuits will therefore be verified by unitary or statevector equivalence before resource comparison. The corresponding canonical nonlocal content may also be retained as an interaction-equivalence descriptor, allowing candidate cross-architecture "equivalence budgets" to be tested experimentally rather than assumed.

**Preserving qubit identity and output meaning.** ⟨R4⟩ Translation validation checks three related records separately: the circuit-qubit order, the physical layout (including the final layout after routing), and the measurement mapping together with the bitstring convention of the returned data. A reversed bit order is not a physical remapping and a correct execution can look wrong if a string is read in the opposite direction. For example, for a two-qubit circuit that applies X to circuit qubit $q_0$ only and measures $q_0 \to c_0$, $q_1 \to c_1$, a Qiskit-style string reads `01` ($c_1$ left, $c_0$ right) [28], whereas a convention that lists $c_0$ first reads `10`. Every result is therefore converted to one documented common ordering — a tuple indexed by circuit qubit — before any comparison. Validation circuits must be asymmetric (X on $q_0$ only, X on $q_1$ only, and a circuit with a nontrivial measurement mapping), because symmetric outputs such as equal weight on `00` and `11` cannot expose a bit-order reversal.

**Approximation error.** ⟨R5⟩ A translation may change the gate sequence without introducing any approximation (for example, a CNOT written as a CZ between two Hadamards). Exact transformations are preferred and are validated as exact. Where approximate synthesis is explicitly permitted, each such transformation is identified, its settings and compiler version are retained as provenance, and its *approximation error* is the deviation of the translated computation from the ideal reference computation, both evaluated noiselessly and expressed in the same qubit ordering after layout and measurement mappings are normalised. The validation target is declared before evaluation, and it selects the metric:

| Declared target | Metric (noiseless reference vs. translated) |
|---|---|
| Fixed-input output state $\lvert\psi\rangle$ | $\varepsilon_{\text{state}} = 1 - \lvert\langle\psi_{\text{ref}}\vert\psi_{\text{tr}}\rangle\rvert^{2}$ |
| Output distribution | total variation distance $\tfrac12\sum_x \lvert p_{\text{ref}}(x)-p_{\text{tr}}(x)\rvert$ |
| Full operation (unitary) | $\varepsilon_{\text{op}} = 1 - \lvert\operatorname{Tr}(U_{\text{ref}}^{\dagger}U_{\text{tr}})\rvert^{2}/d^{2}$ |

Both fidelity-type metrics ignore global phase, and $\varepsilon_{\text{op}}$ is the process infidelity, related to average gate fidelity by $F_{\text{avg}} = (d(1-\varepsilon_{\text{op}})+1)/(d+1)$. Agreement on one input does not establish equivalence for every input: a fixed-input comparison supports only the declared workload and input scope, and equivalence of the whole operation needs the operator-level metric. For the small circuits of Phase 1 (at most 12 circuit qubits, so $d\le 4096$) the operator-level check is feasible and is the default; fixed-input or distribution-level checks are used where ancillas, mixed outputs or mid-circuit measurements make the unitary comparison inapplicable. The metric, tolerance, observed deviation, validation scope and verdict are stored in the provenance record. Floating-point residuals (of order $10^{-12}$) are recorded separately and are not evidence of approximate synthesis. The reference implementation is `pariquant/validation.py`.

### 4.2  From Translated Workload to Accounting Record

Let $W$ denote the fixed logical workload, $H_i$ a target QPU, $\Gamma_i$ the translation configuration and $\Theta_i$ the mapping and scheduling configuration. PariQuant compares the resulting physical implementations after the semantics-preserving translation above rather than assigning a fixed cost to logical gates before compilation. The translator, compiler and version, optimization level, qubit mapping policy, random seed, target description and permitted approximation are all retained as provenance.

For each implementation, the framework constructs

$$A_i = (\mathbf r_i,\, \mathbf n_i,\, \mathbf u_i,\, \mathbf p_i), \tag{3}$$

where $\mathbf r_i$ is the consumption record, $\mathbf n_i$ the available execution context (Sec. 4.4), $\mathbf u_i$ uncertainty and missing-information metadata, and $\mathbf p_i$ provenance.

The initial consumption record will investigate the following quantities: occupied physical qubits and ancillas; native one- and multi-qubit operation profiles; routing, movement or transport where observable; scheduled duration and qubit-time where available; initialization/reset/readout overhead; and the sampling budget. ⟨R6⟩ The sampling budget is accounted as four separate quantities — requested shots, provider-reported executed repetitions (where exposed), returned samples and retained samples — plus the number of repeated whole-job submissions, which is distinct from shots per circuit and serves to assess run-to-run variability and drift. The requested shot count is an experiment setting that the study chooses explicitly and archives; it is not treated as an intrinsic property of a QPU or as an unexplained provider default, and it is either held fixed across compared implementations or varied as a declared controlled resource. A request field is never read as proof of the number of physical executions: retries, expanded execution circuits and mitigation-related sampling overhead are recorded where observable and otherwise marked unknown. For simple unfiltered count data, the sum of returned counts documents the returned sample count; requesting 1000 shots and retaining 900 after postselection does not mean that only 900 executions were consumed. The reference implementation is `pariquant/shots.py`.

Routing is treated as an attribution of operations and time, not charged a second time if it is already present in native-operation and timing totals.

Execution context is stored separately because resource consumption and error exposure are related but not identical. Missing information is recorded as unknown rather than replaced by a fabricated estimate. This is important because providers expose different levels of detail and may perform compilation or scheduling steps that are not visible to the user.

### 4.3  Comparison Decision

**Who defines the rules.** ⟨R3⟩ In the first version the comparison rules are *researcher-defined*; they are not generated by a learning or rule-induction algorithm, which is outside the initial scope. The rules are recorded in a versioned rule table (`rules/rule_table_v0.1.json`). For each descriptor the table states its name and definition, units and source; the platforms to which it applies and any semantic prerequisites (equal native gate counts of different technologies are not comparable by default, and calibration quantities of different scope or characterization method are not matched against each other); whether it is compared exactly or numerically; the absolute or relative tolerance and its justification; the treatment of uncertainty and of missing data; and its role as required comparison evidence or supplementary context.

**How the rules are frozen.** Pilot workloads and held-out evaluation workloads are separate partitions. Pilot data may inform the tolerances, but those choices are documented, the table is frozen under a version identifier and a content hash, and only then are held-out outcomes examined. The reference implementation refuses to apply a table that is not frozen or that has an unset tolerance on a required numerical descriptor. The tolerances are practical comparison margins, not parameters chosen after seeing which values make two devices look similar.

**Robustness.** Sensitivity of the verdicts to the tolerances is evaluated under predeclared tighter and looser versions (by default 0.5× and 2× of every tolerance). The primary result is the 1× verdict and is not redefined after the sensitivity analysis.

**Decision procedure.** For a pair of semantically valid implementations, each descriptor is compared through the difference between the two implementations and an uncertainty interval for that difference, against an equivalence region around zero fixed by its tolerance. The distinction follows the logic of statistical equivalence testing: failing to detect a difference is not the same as establishing closeness within a specified margin [15]. PariQuant reports per descriptor:

- *Matched*: the uncertainty interval lies wholly inside the tolerance region (equivalence shown);
- *Different*: the interval lies wholly outside the region (mismatch shown);
- *Insufficient evidence*: the interval crosses a boundary, or required evidence is missing.

Exact quantities such as counts are compared directly, without inventing sampling uncertainty. The overall decision uses the required descriptors only, and the per-descriptor results are always preserved: any *Different* required descriptor yields **Different**; otherwise, if all required descriptors are *Matched*, the pair is **Matched**; otherwise it is **Insufficient evidence**. Because *Matched* requires every required descriptor to be equivalent, it is an intersection–union test and needs no multiplicity correction per descriptor, whereas a *Different* verdict triggered by any one of several descriptors is a union of rejections and must use a corrected interval (for example Bonferroni). The interval construction, confidence level and repeated-run design are fixed in the pre-specification of Month 3. Approximate matching is treated as a conditional, pairwise statement; no transitive "equivalence class" is assumed. The reference implementation is `pariquant/decision.py`.

**What a match means.** A resource match is conditional on a named descriptor set, a tolerance policy, a rule version and an evidence standard. It means that, under those criteria, the implementations consumed observably comparable resources. It does not imply equal output quality, identical physical noise, or general equivalence of the processors. Task-output quality is deliberately excluded from this decision and is evaluated later as an independent outcome. Thus, equal resources may coexist with different performance, and equal performance may be achieved with different resources.

### 4.4  Collecting Execution Context

⟨R2⟩ PariQuant does **not** claim to reconstruct the physical noise model of a QPU. The information available through cloud interfaces is normally a set of provider-reported calibration and characterization quantities — T1/T2, gate and readout fidelities or errors, operation durations, reported uncertainties and timestamps — which are partial observations of the hardware. They do not uniquely determine coherent error, correlated error, crosstalk, leakage or a complete stochastic noise channel. They are therefore called *provider-reported calibration and characterization context* and are retained for interpretation and reproducibility.

Noise and calibration data are treated as provider-reported execution context rather than as a complete model of physical hardware noise. For every run, PariQuant archives the calibration or characterization information exposed by the execution platform together with its retrieval time, provider timestamp or calibration identifier where available, hardware scope, reported uncertainty and characterization method. IBM runs use job-linked backend properties where available [29, 30]; Braket runs archive the device-capability payload immediately before submission and after completion, together with quantum-task metadata [31, 32]. Provider-specific fields are classified as directly observed, derived under a stated model, or unavailable. Static or literature-derived values are identified separately, and missing fields are not imputed. These context variables are not assumed to define the full noise channel of the QPU.

The procedure for each run is:

1. Identify the exact backend or device and the execution path.
2. Retrieve the available calibration or characterization state as close to execution as the platform allows.
3. Preserve the raw provider payload with its retrieval time and any provider timestamp or calibration identifier; hash it.
4. Record task or job identifiers and execution timestamps.
5. Where the calibration state cannot be linked directly to the job, take a pre-execution and a post-execution device snapshot. If their identifiers or timestamps differ, the run is marked as crossing a characterization change. Unchanged snapshots do not rule out unreported drift, and queueing means that even a snapshot bracket does not prove which calibration governed execution; such context is labelled *near-run/current provider characterization*, never "calibration at execution".
6. Extract fields (T1/T2, gate and readout fidelity or error, durations, provider-reported uncertainty) only when the provider exposes them, with their characterization method (for example randomized benchmarking or Ramsey) when documented, and their scope: device, qubit, qubit pair or operation.
7. Tag every field with an *evidence status* (observed, derived, unavailable) and, separately, a *provenance kind* (job-linked, calibration-set-linked, near-run/current, static provider-published, researcher-measured). A derived quantity, such as $1-\text{fidelity}$ or an emulator noise parameter, is stored separately with its equation or model and version and never overwrites the provider value; a separate experiment run by PariQuant is labelled researcher-measured. A model generated from calibration data is derived from it and is not the hardware's true noise model.
8. Never impute a missing field or silently substitute a product specification for a measured calibration quantity. Equal field names do not guarantee comparable definitions, and a device-wide mean must not silently become a per-qubit value.

The record layout is given by `schemas/context_record.schema.json` and `pariquant/context.py`. The four targets expose different information, so an availability matrix is built per provider rather than a universal "noise vector":

| Target | Primary collection path | Execution linkage | Limitation to record |
|---|---|---|---|
| IBM Berlin | IBM Quantum / Qiskit Runtime backend and job properties [29, 30] | Job-linked properties where available (the call may return nothing), plus job and calibration timestamps | Values are characterization estimates and drift |
| IQM Emerald | IQM client calibration-set and quality-metric interfaces if direct access is used [33]; otherwise Braket device capabilities [31] | Direct runs can be tied to a `calibration_set_id`; Braket runs use pre/post snapshots | The direct-IQM field set is not assumed to equal the Braket payload |
| AQT IBEX-Q1 | Braket device properties [31] | Near-run snapshots and provider update timestamps | Static or literature-derived entries must be separated from live measurements |
| IonQ Forte-1 | IonQ characterization interface if authorized [34]; otherwise Braket [31] | Characterization identifiers and dates; Braket tasks need explicit snapshot provenance | System-level means are not automatically per-qubit or job-specific |

Public schemas show what a platform *can* expose, not which optional fields the selected live backend populates. The exact current backends and accounts are therefore queried and representative raw payloads archived in the Month-1 feasibility audit (Sec. 5.2); that audit is still to be performed.

## 5  Experimental Plan

### 5.1  Target QPUs and Experimental Design

The experimental design separates hardware modality from provider-specific variation using two independent QPUs from each architecture:

| | Provider 1 | Provider 2 |
|---|---|---|
| **Superconducting** | IBM Berlin | IQM Emerald |
| **Trapped ion** | AQT IBEX-Q1 | IonQ Forte-1 |

IBM–IQM and AQT–IonQ provide within-modality controls, while the four cross-modality pairs test superconducting–trapped-ion differences. The study reports device-pair results first and does not treat two devices as representative of an entire hardware technology.

| QPU | Native interaction | Connectivity |
|---|---|---|
| IBM Berlin | CZ/RZZ class | square grid |
| IQM Emerald | CZ | square lattice |
| AQT IBEX-Q1 | RXX/MS | all-to-all |
| IonQ Forte-1 | ZZ | all-to-all |

*Table 1. Technical characteristics of the current target QPUs [19, 20, 21, 24, 22, 23]. Exact backend identities and capabilities will be re-verified before evaluation.*

### 5.2  Phase 1: Data-Availability and Reproducibility Pilot

The first milestone is a feasibility audit, not immediate commitment to a fixed five-dimensional vector. The feasibility audit will be performed separately on all four target QPUs. For each backend, the study will determine what can actually be recovered from the user-visible stack: native instructions, physical mapping, operation parameters, routing or transport, timing/schedule information, calibration metadata, measurement settings, result provenance and execution identifiers. Each field will be classified as directly observed, derived under a stated model, or unavailable. ⟨R2⟩ The audit queries the exact accessible accounts and backends, archives representative raw properties/characterization payloads, and produces the availability-and-provenance table of Sec. 4.4, including the fields that turn out to be missing and the runs whose calibration linkage is ambiguous.

Provider-side compilation, mitigation, debiasing and result reconstruction will also be recorded. Optional mitigation will be disabled in the primary experiment where possible; unavoidable processing will be treated explicitly as part of the execution/provenance boundary.

IQM Emerald, AQT IBEX-Q1 and IonQ Forte-1 are currently available through Amazon Braket [25], but the common adapter does not make their evidence formats identical. IonQ devices return probabilities through Braket, and apparent per-shot measurements may be post-computed because device-level per-shot measurements are unavailable [26]. PariQuant will preserve this distinction in its measurement-resource accounting (Sec. 4.2). Provider visibility will also be audited: Braket currently permits compiled-circuit inspection for IQM but not IonQ, so submitted native programs and provider-reported compiled representations will be distinguished explicitly [24].

The software pipeline will then be tested on small circuits whose semantic equivalence can be checked in noiseless simulation. This includes explicit translation tests across native gate families: the same reference two-qubit operations will be synthesized to the selected superconducting and trapped-ion native bases, and the resulting unitaries will be checked before any resource comparison is performed. ⟨R4, R5⟩ This stage verifies circuit-qubit identity, the mapping to physical qubits and the correspondence between measured qubits and returned classical bits, using the asymmetric known-output circuits of Sec. 4.1; it also measures the approximation error of every permitted approximate synthesis against the declared target, metric and tolerance of Sec. 4.1, and verifies translator/compiler provenance.

### 5.3  Phase 2: Controlled Compilation and Simulation

Controlled workloads will vary one implementation pressure at a time: interaction graph, circuit depth, idle time, two-qubit content at the circuit level, native translation/decomposition and requested shots. ⟨R6⟩ Workload families will include BV circuits, small QFT circuits and fixed-parameter variational blocks. BV is included partly because it provides continuity with Herajärvi's Brisbane experiments, while the other families introduce different interaction and rotation structures.

⟨R7⟩ The primary four-QPU workload suite is bounded by the smallest selected processor, AQT IBEX-Q1, which offers 12 qubits [22]. The common paired workloads will therefore use **at most 12 circuit qubits, including required ancillas**, subject to confirmed feasibility on all selected backends. Twelve is an upper bound on circuit width, not a minimum workload size and not a statement that every experiment occupies 12 physical qubits: a workload with six data qubits and two ancillas has width eight and is not padded to twelve. Three quantities are kept distinct and recorded separately: the number of data qubits, the total circuit width, and the physical qubits actually occupied by the compiled implementation. For unencoded execution each simultaneously live circuit qubit needs a physical realization, but the occupied count is read from the compiled implementation and not inferred from the width cap (routing may pass through otherwise unused qubits), and device capacity alone does not show that a circuit fits a backend's connectivity, operations and compilation requirements. Each workload is therefore checked against every backend's actual capabilities and restricted if it exceeds them. Larger circuits may be used as secondary within-device or within-modality scaling experiments, but they will not enter the four-QPU matching analysis.

⟨R8⟩ Simulation creates reference cases whose noise is known **by construction**. The channels, parameters, spatial and temporal scope and assumptions of each noise model are specified; exact model calculations are kept apart from finite-shot simulated observations; and the cases test the accounting code and the behaviour of descriptors and comparison decisions, without claiming that any chosen model is the noise of a real device. The cases intentionally include situations where scalar summaries are expected to fail: circuits with equal gate count but different routing, equal depth but different scheduled duration, and noise models with a precisely defined, matched average-error metric but different structure. A simple instance is a coherent over-rotation by angle $\theta$ versus a stochastic channel with the same per-gate process infidelity $r=\sin^2(\theta/2)\approx\theta^2/4$: after $N$ repetitions the coherent error accumulates as $\sin^2(N\theta/2)\approx N^2\theta^2/4$, whereas the stochastic one grows approximately as $Nr$. Coherent noise is a systematic unitary deviation, whereas correlated noise denotes dependence across qubits, operations or time and the kind of correlation is specified for each case; the two are not mutually exclusive.

### 5.4  Phase 3: Cross-Architecture Hardware Study

Subject to access, the frozen workload suite will be executed on all four target QPUs using the translation and accounting procedures defined above. Multiple compiler seeds or mappings and repeated calibration sessions will be retained as separate implementation records. Analysis will preserve the pre-defined 2 × 2 experimental structure. If one target is unavailable, the result will be reported as a reduced pilot rather than a complete four-QPU study.

⟨R8⟩ On hardware the study reports resource comparisons and observable task performance, with compilation, mapping, timing, execution context and sampling settings preserved. Different outputs from two circuits on the same QPU do not by themselves establish different coherent or correlated noise: they can also arise from the intended circuit difference, different gate sequences or mappings, drift, state-preparation and readout effects, or finite sampling, and the same underlying noise process affects different circuits differently. Provider calibration context does not identify these mechanisms either, and repetition reduces some uncertainty without identifying its physical cause. The evidentiary standard is therefore:

- comparable experiments are repeated and, where feasible, interleaved or randomized to limit order and drift confounding;
- effect sizes and uncertainty are reported under a prespecified analysis that respects the repeated-run structure;
- a difference is attributed to a particular noise mechanism only if a dedicated characterization protocol supports that interpretation. Unitarity benchmarking is an example for studying the coherence of noise [27]; its assumptions must be checked and it does not by itself establish every form of correlated noise. A correlation claim requires an experiment and analysis targeting the specific spatial or temporal dependence.

Mechanism-specific coherent/correlated-noise examples are therefore confined to controlled simulation in the first study; dedicated hardware characterization is added only if the research question, access and experimental budget justify it.

### 5.5  Baselines and Validation

PariQuant will be compared with simpler baselines using the same workload pairs: physical qubit count, total gate count, two-qubit gate count, circuit depth and QED-C-style reference normalization [9]. Featuremetric descriptors will provide the closest multidimensional baseline [12]. The goal is not to make PariQuant "win" a benchmark, but to test whether its additional accounting fields identify implementation differences that simpler representations miss.

Validation will use development and held-out partitions at the workload-family or calibration-session level rather than random splits of nearly identical circuits. Descriptor ablation will test whether routing, timing, sampling and context fields add distinct information. The frozen resource-matching policy will be applied before examining held-out task-output results. Output success probability or distribution distance will then be analyzed separately to ask what a resource match does and does not explain.

## 6  Expected Contributions and Limitations

The expected contributions are:

1. a versioned, auditable schema for recording observable resource consumption, context, uncertainty and missingness from compiled quantum implementations;
2. a reference software workflow containing an explicit semantics-preserving translator from common logical workloads to selected superconducting and trapped-ion native gate sets, followed by extraction and comparison of the resulting implementation records;
3. an explicit three-way decision procedure for resource comparison under pre-specified tolerances; and
4. an empirical evaluation showing where the representation adds useful information, where it is redundant with existing approaches, and where the available evidence is insufficient.

A negative result is scientifically meaningful. If a compact descriptor set cannot support stable comparisons, PariQuant can instead identify which architecture-specific information is lost and which additional descriptors are required. Likewise, if Featuremetric or simpler baselines explain the observed differences equally well, the evidence would not support presenting PariQuant as a separate general framework.

The first study is restricted to physical gate-model superconducting and trapped-ion systems, static circuits with terminal measurement, and observable cloud-accessible information. The selected devices do not justify technology-wide causal or population-level claims. The study excludes fault-tolerant resource estimation, error-corrected logical-qubit encoding, distributed inter-QPU operations, pulse-level optimization, energy consumption and financial cost. Provider-side hidden compilation, unavailable schedules, drift, leakage and correlated errors may limit what can be concluded; provider-reported calibration context is not a complete noise description, and no hardware noise-mechanism claim is made without dedicated characterization (Sec. 5.4). These limitations are part of the result rather than values to be filled with unsupported assumptions.

## 7  Initial Six-Month Work Plan

The first decision point occurs after the Month 3 falsification pilot. The project proceeds to a stronger framework claim only if the selected descriptors are observable, non-redundant and empirically useful. Otherwise the research question is narrowed to documenting the limits of cross-architecture resource comparison with presently accessible evidence.

| Month | Main work |
|---|---|
| 1 | Re-verify and freeze the target QPUs; create provider accounts and check student credit programs; use provider resource estimators (for example [35]) to size the intended circuits; complete the per-backend data/provenance audit with archived raw payloads; freeze the first accounting schema. |
| 2 | Implement the translation/backend adapters, provenance capture and semantic checks; construct the common ≤ 12-circuit-qubit diagnostic workload suite and check it against every backend's capabilities. |
| 3 | Controlled simulation and compilation study; verify accounting; refine descriptor set; set tolerances from the pilot partition only, specify the interval/multiplicity procedure and sensitivity analysis, and freeze the comparison rule table. |
| 4 | Execute the hardware pilot; repeat compiler variants and initial sessions. |
| 5 | Repeat selected calibration epochs; perform pairwise validation, baseline comparison and descriptor ablation. |
| 6 | Analyze results, document failure cases, prepare reproducibility package and draft the research paper. |

*Table 2. Initial work plan.*

---

## References

References 1–26 are those of the submitted proposal. Their bibliographic data and links were re-checked on 22 October 2026 (see [`../references.md`](../references.md)). References 27–35 are new in this revision.

1. Adhikari, S., Halunen, K.: Review of vulnerabilities in quantum hardware. Journal of Physics Communications 9, 112001 (2025). https://doi.org/10.1088/2399-6528/ae1652
2. Blinov, S., Wu, B., Monroe, C.: Comparison of cloud-based ion trap and superconducting quantum computer architectures. AVS Quantum Science 3, 033801 (2021). https://doi.org/10.1116/5.0058187
3. Blume-Kohout, R., Young, K.C.: A volumetric framework for quantum computer benchmarks. Quantum 4, 362 (2020). https://doi.org/10.22331/q-2020-11-15-362
4. Cross, A.W., Bishop, L.S., Sheldon, S., Nation, P.D., Gambetta, J.M.: Validating quantum computers using randomized model circuits. Physical Review A 100, 032328 (2019). https://doi.org/10.1103/PhysRevA.100.032328
5. Fellous-Asiani, M., Chai, J.H., Thonnart, Y., Ng, H.K., Whitney, R.S., Auffèves, A.: Optimizing Resource Efficiencies for Scalable Full-Stack Quantum Computers. PRX Quantum 4, 040319 (2023). https://doi.org/10.1103/PRXQuantum.4.040319
6. Herajärvi, J.: Security of Quantum Computing. Master's thesis, University of Oulu, Degree Programme in Computer Science and Engineering (2025). https://urn.fi/URN:NBN:fi:oulu-202505163553
7. Li, A., Stein, S., Krishnamoorthy, S., Ang, J.: QASMBench: A Low-Level Quantum Benchmark Suite for NISQ Evaluation and Simulation. ACM Transactions on Quantum Computing 4(2), Article 10 (2023). https://doi.org/10.1145/3550488
8. Linke, N.M., Maslov, D., Roetteler, M., Debnath, S., Figgatt, C., Landsman, K.A., Wright, K., Monroe, C.: Experimental comparison of two quantum computing architectures. Proceedings of the National Academy of Sciences 114(13), 3305–3310 (2017). https://doi.org/10.1073/pnas.1618020114
9. Lubinski, T., Johri, S., Varosy, P., Coleman, J., Zhao, L., Necaise, J., et al.: Application-Oriented Performance Benchmarks for Quantum Computing. IEEE Transactions on Quantum Engineering 4, 1–32 (2023). https://doi.org/10.1109/TQE.2023.3253761
10. Murali, P., Linke, N.M., Martonosi, M., Javadi-Abhari, A., Nguyen, N.H., Huerta Alderete, C.: Full-Stack, Real-System Quantum Computer Studies: Architectural Comparisons and Design Insights. In: Proceedings of the 46th International Symposium on Computer Architecture, pp. 527–540. ACM (2019). https://doi.org/10.1145/3307650.3322273
11. Proctor, T., Rudinger, K., Young, K., Nielsen, E., Blume-Kohout, R.: Measuring the capabilities of quantum computers. Nature Physics 18, 75–79 (2022). https://doi.org/10.1038/s41567-021-01409-7
12. Proctor, T., Tran, A., Liu, X., Dhumuntarao, A., Seritan, S., Green, A., Linke, N.M.: Featuremetric benchmarking: Quantum computer benchmarks based on circuit features. arXiv preprint arXiv:2504.12575 (2025). https://arxiv.org/abs/2504.12575
13. Proctor, T., Hart, O., Widzowski Maupin, O., et al.: Benchmarking the computational power of quantum computers. arXiv preprint arXiv:2609.12146 (2026). https://arxiv.org/abs/2609.12146
14. Sanders, Y.R., Wallman, J.J., Sanders, B.C.: Bounding quantum gate error rate based on reported average fidelity. New Journal of Physics 18, 012002 (2016). https://doi.org/10.1088/1367-2630/18/1/012002
15. Schuirmann, D.J.: A comparison of the Two One-Sided Tests Procedure and the Power Approach for assessing the equivalence of average bioavailability. Journal of Pharmacokinetics and Biopharmaceutics 15(6), 657–680 (1987). https://doi.org/10.1007/BF01068419
16. Tomesh, T., Gokhale, P., Omole, V., Ravi, G.S., Smith, K.N., Viszlai, J., Wu, X.-C., Hardavellas, N., Martonosi, M.R., Chong, F.T.: SupermarQ: A Scalable Quantum Benchmark Suite. In: 2022 IEEE International Symposium on High-Performance Computer Architecture (HPCA) (2022). https://doi.org/10.1109/HPCA53966.2022.00050
17. Vidal, G., Hammerer, K., Cirac, J.I.: Interaction cost of nonlocal gates. Physical Review Letters 88, 237902 (2002). https://doi.org/10.1103/PhysRevLett.88.237902
18. Zhang, J., Vala, J., Sastry, S., Whaley, K.B.: Geometric theory of nonlocal two-qubit operations. Physical Review A 67, 042313 (2003). https://doi.org/10.1103/PhysRevA.67.042313
19. IBM Quantum: Compute resources: Nighthawk processors. https://quantum.cloud.ibm.com/computers?processorType=Nighthawk (accessed 25 September 2026).
20. IBM Quantum: Monitoring, calibrations, and benchmarking. https://quantum.cloud.ibm.com/docs/en/guides/calibration-jobs (accessed 25 September 2026).
21. IQM Quantum Computers: New on IQM Resonance: IQM Emerald, almost 3x qubits for the same reliable quality (2025). https://iqm.tech/blog/new-on-iqm-resonance-iqm-emerald-almost-3x-qubits-for-the-same-reliable-quality/
22. Alpine Quantum Technologies: IBEX Q1 quantum computer. https://www.aqt.eu/products/ibex-q1/ (accessed 25 September 2026).
23. IonQ: Forte quantum system. https://ionq.com/quantum-systems/forte (accessed 25 September 2026).
24. Amazon Web Services: Submitting quantum tasks to QPUs. https://docs.aws.amazon.com/braket/latest/developerguide/braket-submit-tasks.html (accessed 25 September 2026).
25. Amazon Web Services: Amazon Braket supported regions and devices. https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html (accessed 25 September 2026).
26. Amazon Web Services: Amazon Braket list of result types. https://docs.aws.amazon.com/braket/latest/developerguide/braket-result-types.html (accessed 25 September 2026).
27. Wallman, J.J., Granade, C., Harper, R., Flammia, S.T.: Estimating the Coherence of Noise. arXiv preprint arXiv:1503.07865. https://arxiv.org/abs/1503.07865
28. IBM Quantum: Bit-ordering in the Qiskit SDK. https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering (accessed 22 October 2026).
29. IBM Quantum: Get QPU information. https://quantum.cloud.ibm.com/docs/en/guides/qpu-information (accessed 22 October 2026).
30. IBM Quantum: RuntimeJobV2 (qiskit-ibm-runtime API reference). https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/runtime-job-v2 (accessed 22 October 2026).
31. Amazon Web Services: Amazon Braket API Reference, GetDevice. https://docs.aws.amazon.com/braket/latest/APIReference/API_GetDevice.html (accessed 22 October 2026).
32. Amazon Web Services: Amazon Braket API Reference, GetQuantumTask. https://docs.aws.amazon.com/braket/latest/APIReference/API_GetQuantumTask.html (accessed 22 October 2026).
33. IQM: Qiskit on IQM user guide (IQM client). https://docs.iqm.tech/iqm-client/user_guide_qiskit.html (accessed 22 October 2026).
34. IonQ: API reference, characterizations (Get a characterization). https://docs.ionq.com/api-reference/v0.3/characterizations/get-a-characterization (accessed 22 October 2026).
35. IonQ: Quantum Cloud Resource Estimator. https://www.ionq.com/programs/research-credits/resource-estimator (accessed 22 October 2026).
