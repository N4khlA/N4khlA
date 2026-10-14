```text
SEC-ASSESSMENT // GUERFI-A-Y                         CLASSIFICATION: PUBLIC
-----------------------------------------------------------------------------
SUBJECT      Guerfi Ahmed Yacine
INSTITUTION  ESI Sidi Bel Abbès (ESI-SBA)
PROGRAMME    State Engineering degree, Cyber Security + Master's (final year)
GRADUATION   2027
STATUS       [ AVAILABLE ]  open to internships: pentest · AppSec · SOC/detection
```

I learn security by building the vulnerable system, exploiting it, instrumenting it, and proving that the fix works.

## Findings

| ID | Project | Area | Evidence |
|---|---|---|---|
| F-01 | **[Race Condition Exploiter](https://github.com/N4khlA/Race_condition_exploiter)** | Offensive / Web | 5 TOCTOU bugs · 4 attack strategies · 3 detectors · 7 labs |
| F-02 | **[ML Network Intrusion Detection](https://github.com/N4khlA/AI-_threat_hunting)** | Defensive / ML | RF macro-F1 0.948 · LSTM AUC 0.998 · 49 tests |
| F-03 | **[masa: Mobile App Security Analyzer](https://github.com/N4khlA/MobileApp_SecAnalyzer)** | AppSec / Mobile | OWASP Mobile M1–M10 · APK + IPA · 0 dependencies |

<details>
<summary><b>F-01 · Race Condition Exploiter</b>: details</summary>

A full-stack TOCTOU lab: a deliberately vulnerable shop with five real race bugs (double-spend, coupon reuse, oversell, duplicate signup, reset-token reuse). The exploit harness uses asyncio, barrier-synced threads, raw TCP sockets and HTTP/2 multiplexing. Detection comes from PostgreSQL invariant triggers (`LISTEN/NOTIFY`) and burst fingerprinting. Fixes (CAS, row locks, serializable, Redis locks) are toggleable and benchmarked for exploit rate against latency.
`FastAPI` `PostgreSQL` `Redis` `React/TS` `Docker`
</details>

<details>
<summary><b>F-02 · ML Network Intrusion Detection</b>: details</summary>

Trained on UNSW-NB15: a grid-searched Random Forest compared with a bidirectional LSTM, using a McNemar significance test. It includes a leakage scan, per-attack-family recall, a FastAPI inference endpoint, a live Streamlit monitor, and a retraining pipeline that refuses to replace the current model with a worse one.
`scikit-learn` `TensorFlow` `FastAPI` `Streamlit` `pytest`
</details>

<details>
<summary><b>F-03 · masa</b>: details</summary>

A static scanner for Android and iOS apps, written with only the Python standard library. It has hand-written parsers for binary AXML, bplist, DEX, ELF and Mach-O, checks binary hardening (PIE, RELRO, NX), detects secrets, TrustAll managers, ATS bypasses and weak crypto, and produces HTML, Markdown and JSON reports.
`Python stdlib` `OWASP MASVS` `ELF / Mach-O`
</details>

## Capability matrix

| Recon & analysis | Exploitation | Detection | Hardening | Engineering |
|---|---|---|---|---|
| Binary format parsing | Race conditions / TOCTOU | ML intrusion detection | Concurrency-safe DB fixes | Python |
| Static analysis | Custom exploit harnesses | DB invariant triggers | OWASP Mobile Top 10 | FastAPI · React · TS |
| Traffic & flow analysis | HTTP/2 & raw-socket attacks | Request fingerprinting | ELF / Mach-O hardening | PostgreSQL · Redis |
| Network enumeration | Web injection & auth flaws | Model drift monitoring | OWASP Top 10 (web) | Docker · pytest · Git |

## Disclosure channel

[![Email](https://img.shields.io/badge/Email-ay.guerfi%40esi--sba.dz-0f0f10?style=flat-square&logo=maildotru&logoColor=white)](mailto:ay.guerfi@esi-sba.dz)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Guerfi%20Ahmed%20Yacine-d93a12?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/guerfi-ahmed-yacine-6831b32b8/)
[![Portfolio](https://img.shields.io/badge/Portfolio-n4khla.github.io-0f0f10?style=flat-square&logo=googlechrome&logoColor=white)](https://n4khla.github.io)

Open to internship offers, projects and hard problems.

<sub>All offensive tooling here is for authorised education and research, run in isolated environments.</sub>
