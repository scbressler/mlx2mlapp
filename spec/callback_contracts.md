# Callback Contracts

This document defines the contract between layout XML callback declarations
and MATLAB code implementations.

---

## XML Side (Declaration)

- Callbacks are declared as component properties in layout XML.
- The value of a callback property MUST be a MATLAB method name.
- Callback names are case‑sensitive.
- Layout XML MUST NOT contain inline executable code.

Example:
```xml
<ButtonPushedFcn>RunButtonPushed</ButtonPushedFcn>