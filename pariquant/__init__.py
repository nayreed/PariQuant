"""PariQuant: auditable resource accounting and comparison across heterogeneous QPUs.

The modules mirror the definitions in docs/proposal/PariQuant.md:

- ``bitorder``   circuit-qubit / measured-bit conventions (wire ordering)
- ``validation`` noiseless translation-validation metrics (approximation error)
- ``shots``      requested / executed / returned / retained sample accounting
- ``context``    provider-reported calibration context with provenance
- ``decision``   frozen rule tables and the matched / different / insufficient decision
"""

__version__ = "0.1.0"
