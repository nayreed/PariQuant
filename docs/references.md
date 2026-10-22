# Reference and link check (22 October 2026)

Every reference and link of the proposal, of the review issues (#1–#8), of the supervisor e-mails and of the Slack screenshot was checked on 22 October 2026. Direct HTTPS from the working environment is blocked by its network policy, so pages were read through the web-fetch tool, and bibliographic data of DOIs were read from the Crossref registry (`api.crossref.org`) where the publisher site refuses automated access.

**Status key.** ✅ resolves and the content matches the citation · ◐ resolves but part of the claim could not be confirmed · ❌ could not be read · 📄 PDF is among the project files.

## A. Proposal references [1]–[26]

| # | Reference | Link status | PDF available |
|---|---|---|---|
| 1 | Adhikari & Halunen, *Review of vulnerabilities in quantum hardware*, J. Phys. Commun. 9, 112001 (2025) | ✅ Crossref metadata matches; publisher page refuses automated access | 📄 `Review of vulnerabilities in quantum hardware.pdf` |
| 2 | Blinov, Wu, Monroe, *Comparison of cloud-based ion trap and superconducting quantum computer architectures*, AVS Quantum Sci. 3, 033801 (2021) | ✅ Crossref | missing |
| 3 | Blume-Kohout & Young, *A volumetric framework for quantum computer benchmarks*, Quantum 4, 362 (2020) | ✅ journal page found by search (Crossref lookup failed) | missing |
| 4 | Cross et al., *Validating quantum computers using randomized model circuits*, PRA 100, 032328 (2019) | ✅ Crossref | missing |
| 5 | Fellous-Asiani et al., *Optimizing Resource Efficiencies for Scalable Full-Stack Quantum Computers*, PRX Quantum 4, 040319 (2023) | ✅ Crossref | missing |
| 6 | Herajärvi, *Security of Quantum Computing*, MSc thesis, Oulu (2025) | ✅ repository handle `oulurepo.oulu.fi/handle/10024/56040` loads and lists `urn:nbn:fi:oulu-202505163553`; `urn.fi` itself could not be fetched | 📄 `Security of quantum computing.pdf` |
| 7 | Li et al., *QASMBench*, ACM TQC 4(2) (2023) | ✅ Crossref (pages 1–26; article number 10 not shown by Crossref) | missing |
| 8 | Linke et al., *Experimental comparison of two quantum computing architectures*, PNAS 114(13), 3305–3310 (2017) | ◐ DOI landing page and Crossref lookup both failed; the paper exists (arXiv:1702.01852, PMC5380037 found by search) but volume/pages were not read from a registry | missing |
| 9 | Lubinski et al., *Application-Oriented Performance Benchmarks for Quantum Computing*, IEEE TQE 4, 1–32 (2023) | ✅ Crossref | missing |
| 10 | Murali et al., *Full-Stack, Real-System Quantum Computer Studies*, ISCA 2019, pp. 527–540 | ✅ Crossref | missing |
| 11 | Proctor et al., *Measuring the capabilities of quantum computers*, Nat. Phys. 18, 75–79 (2022) | ✅ Crossref (online Dec 2021, print Jan 2022) | missing |
| 12 | Proctor et al., *Featuremetric benchmarking*, arXiv:2504.12575 | ✅ arXiv abstract page | missing |
| 13 | Proctor et al., *Benchmarking the computational power of quantum computers*, arXiv:2609.12146 (2026) | ✅ arXiv abstract page (submitted 10 Sep 2026) | missing |
| 14 | Sanders, Wallman, Sanders, *Bounding quantum gate error rate based on reported average fidelity*, NJP 18, 012002 (2016) | ✅ Crossref. Crossref dates it 2015 (online); volume 18 is the 2016 volume, so "2016" in the proposal is defensible, **please confirm which year you want** | missing |
| 15 | Schuirmann, J. Pharmacokinet. Biopharm. 15(6), 657–680 (1987) | ✅ Crossref | missing |
| 16 | Tomesh et al., *SupermarQ*, HPCA 2022 | ✅ Crossref | missing |
| 17 | Vidal, Hammerer, Cirac, *Interaction cost of nonlocal gates*, PRL 88, 237902 (2002) | ✅ Crossref | missing |
| 18 | Zhang, Vala, Sastry, Whaley, *Geometric theory of nonlocal two-qubit operations*, PRA 67, 042313 (2003) | ✅ Crossref (the original PDF text breaks the DOI as `0.0423 / 13`, the DOI is correct) | missing |
| 19 | IBM Quantum, *Compute resources: Nighthawk processors* | ✅ loads; lists `ibm_phoenix`, `ibm_miami`, `ibm_berlin` (120 programmable qubits). **`ibm_berlin` is "only available for use in the eu-de region"**, relevant for access | n/a (web) |
| 20 | IBM Quantum, *Monitoring, calibrations, and benchmarking* | ✅ loads | n/a |
| 21 | IQM, *New on IQM Resonance: IQM Emerald* (5 Aug 2025) | ✅ loads: 54 qubits, square lattice | n/a |
| 22 | AQT, *IBEX Q1* | ✅ loads: 12 fully connected qubits (supports the 12-qubit bound) | n/a |
| 23 | IonQ, *Forte* | ◐ loads: 36 qubits; the page does **not** name the native gate, so "ZZ" in Table 1 rests on [24] | n/a |
| 24 | AWS, *Submitting quantum tasks to QPUs* | ✅ loads; native gates for verbatim compilation: IQM `cz`, `prx`; IonQ `gpi`, `gpi2`, `zz` (supports Table 1 for IQM/IonQ). Compiled-circuit inspection is on a separate page ("Inspecting compiled circuits") that was **not** opened, so the IQM-yes/IonQ-no claim is unconfirmed | n/a |
| 25 | AWS, *Amazon Braket supported regions and devices* | ✅ loads; lists AQT `Ibex-Q1`, IonQ `Forte-1`, IQM `Emerald` (device ARNs are case sensitive) | n/a |
| 26 | AWS, *Amazon Braket list of result types* | ✅ loads; confirms that for devices returning probabilities (IonQ) the `measurements` are post-computed (`measurements_copied_from_device`) | n/a |

Not verifiable from the cited pages: the native interactions of **IBM Berlin** ("CZ/RZZ class") and **AQT IBEX-Q1** ("RXX/MS") in Table 1. The proposal already says that backend capabilities are re-verified before evaluation.

## B. References added in the revision [27]–[35]

| # | Source | Link status |
|---|---|---|
| 27 | Wallman et al., *Estimating the Coherence of Noise*, arXiv:1503.07865 | ✅ arXiv abstract page (v4, Jan 2019); not in project files |
| 28 | IBM, *Bit-ordering in the Qiskit SDK* | ✅ loads; confirms little-endian: qubit 0 is the least significant bit, rightmost character of a string |
| 29 | IBM, *Get QPU information* | ✅ loads |
| 30 | IBM, `RuntimeJobV2` API | ✅ loads; `properties()` returns `BackendProperties | None` ("None if properties are not available") |
| 31 | AWS, `GetDevice` | ✅ loads |
| 32 | AWS, `GetQuantumTask` | ✅ loads; response contains `shots`, `numSuccessfulShots`, `createdAt`, `endedAt`, `deviceArn`, `deviceParameters` |
| 33 | IQM, *Qiskit on IQM* user guide | ✅ loads; `calibration_set_id` can be set on the backend and is reported in `result.parameters.calibration_set_id` |
| 34 | IonQ, characterizations API | ✅ loads |
| 35 | IonQ, *Quantum Cloud Resource Estimator* (from Subarna's e-mail) | ✅ loads. Note that it estimates **price** per iteration from qubits, gate counts and shots; it is useful for sizing and budgeting, not a physical-resource estimator |

## C. Links that appear only in the issues, e-mails or Slack

| Link | Where | Status | PDF available |
|---|---|---|---|
| `quantum.cloud.ibm.com/docs/en/guides/monitor-job` | issue #2 | ✅ loads | n/a |
| `docs.aws.amazon.com/braket/.../braket-local-emulator.html` | issue #2 | ✅ loads | n/a |
| `docs.ionq.com/.../get-the-most-recent-backend-characterization` | issue #2 | ✅ loads | n/a |
| `docs.iqm.tech/iqm-client/api/...IQMClient.html` | issue #2 | ✅ loads | n/a |
| `iqm-finland.github.io/QDMI-on-IQM/usage.html` | issue #2 | ✅ loads | n/a |
| `arnica.aqt.eu/api/v1/docs` | issue #2 | ◐ the page loads but shows only a title and logos (the API documentation is rendered by JavaScript). **The claim "AQT documents its T1 entry as a literature value" could not be confirmed** and is therefore not stated in the proposal | n/a |
| arXiv:2104.05899 *Qubit Sensing: A New Attack Model for Multi-programming Quantum Computing* (Saki & Ghosh) | Slack, Subarna | ✅ abstract page | 📄 `Qubit Sensing A New Attack Model ….pdf` |
| `iopscience.iop.org/article/10.1088/2399-6528/ae1652` | Slack / e-mail | = reference [1] | 📄 |
| `oulurepo.oulu.fi/handle/10024/56040` (Herajärvi thesis) | e-mail, Juuso | ✅ | 📄 `Security of quantum computing.pdf` |
| Nielsen & Chuang, *Quantum Computation and Quantum Information* (Cambridge page) | e-mail, Juuso | ✅ loads (10th Anniversary Edition; the page's metadata also says "1st Edition") | 📄 `Quantum Computation and Quantum Information.pdf` |
| `qubithub.org/platforms.html` | e-mail, Juuso | ✅ loads (list of quantum platforms) | n/a (web) |
| *Towards a distributed quantum computing ecosystem* (IET Quantum Commun., doi 10.1049/iet-qtc.2020.0002) | e-mail, Kimmo | n/a (not fetched) | 📄 |
| *The Path to Scalable Distributed Quantum Computing* (Van Meter & Devitt) | e-mail, Kimmo | n/a (not fetched) | 📄 |
| *Distributed Quantum Computing: Applications and Challenges* (arXiv:2410.00609) | e-mail, Kimmo | n/a (not fetched) | 📄 `Distributed Quantum Computing.pdf` |
| `sciencedirect.com/science/article/pii/S0164121226001172`, "Classification of security challenges and mitigation approaches in the quantum software engineering" | e-mail, Zeeshan | ❌ the publisher blocks automated access, title/authors/journal not confirmed | **missing** |
| arXiv:2605.26528 *Crosstalk In Contemporary Quantum Devices* (Gicev et al.) | e-mail, Zeeshan | ✅ abstract page. **The e-mail lists this ID twice (first and fourth link); one of them is probably a typo for a different paper** | **missing** |
| arXiv:2603.11018 *Mitigating crosstalk errors for simultaneous single-qubit gates on a superconducting quantum processor* (Wesdorp et al.) | e-mail, Zeeshan | ✅ abstract page | **missing** |
| arXiv:2503.23846 *Mitigation of exchange cross-talk in dense quantum dot arrays* (Jirovec et al.) | e-mail, Zeeshan | ✅ abstract page | **missing** |

## D. The zip file of PDFs

The repository contained only `LICENSE` and the project files contained no zip archive. The PDFs available are the loose files in the project folder, listed in the "PDF available" columns above. No PDF has been added to the repository (several are copyrighted and the repository visibility matters); a zip can be assembled from the items marked 📄 once it is decided where it should live.

**Papers still needed as PDFs** (not available to the working environment, which cannot download files from arXiv or publishers): references [2]–[5], [7]–[18]; [27] (Wallman et al.); the three crosstalk arXiv papers and the ScienceDirect paper from Zeeshan's e-mail.
