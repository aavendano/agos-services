# STD-GOV-001: Corporate Governance, Authority, and Continuous Verification Guidelines

**Status:** Approved & Enforced  
**Standard ID:** STD-GOV-001  
**Authority:** CEO (`05c05fac-bda2-48ae-8284-ebed265cc4dc`) & Governance & Verification Lead (`9ecf20b0-d942-4a22-adec-992f9af3b5d7`)  
**Normative Substrate:** `agents-os-core` (`https://github.com/aavendano/agents-os-core.git`)  
**Governed Platforms:** `agos-services`, `commercial-tech-analyzer`, `paperclip`  
**Date:** 2026-08-30  

---

## 1. Executive Summary & Purpose

**AA Digital Business** operates an autonomous, multi-agent organization designed to execute digital products, commercial software evaluation, and service infrastructure with high rigor, predictability, and safety.

The fundamental premise of **STD-GOV-001** is:
> **"Governance is achieved when human intent is converted into verifiable computational behavior."**

This standard establishes the binding governance guidelines across all agents, repositories, workflows, and automated pipelines, defining the authority models, execution boundaries, operational single source of truth (SSoT), and continuous compliance verification mechanisms.

---

## 2. Foundational Constitutional Principles

Derived directly from `agents-os-core/.agent/constitution/foundational-principles.qms`:

1. **Verifiable Computational Behavior (`principle governance`)**  
   Human strategic intent must be mapped to deterministic, verifiable code, contracts, tests, and evidence records.
2. **Cognitive Autonomy (`principle cognitive-autonomy`)**  
   Agents have full autonomy to reason, plan, delegate, and execute tasks within their explicitly authorized operational scope.
3. **Normative Boundary (`principle normative-boundary`)**  
   Governed agents SHALL-NOT modify governance sources, policy files, or constitution definitions (`.agent/**`) without explicit human ratification.
4. **Escalation Protocol (`principle escalation`)**  
   When a required operational authority exceeds an agent's effective authority (e.g. financial budget, security policy exception, deployment to live customer production), the agent SHALL halt and submit an explicit escalation request.
5. **Delegation Invariant (`principle delegation`)**  
   Delegated authority MUST NOT exceed delegator authority. No agent can confer capabilities or permissions it does not possess.
6. **Runtime Separation (`principle runtime-separation`)**  
   Operational agents consume published APIs, contracts, and tools. They do not require source-code modification access to the core framework to execute work.
7. **Governed Interface (`principle governed-interface`)**  
   Operational actions MUST use authorized public capabilities, MCP servers, and verified endpoints rather than ad-hoc workarounds.
8. **Provider Neutrality (`principle provider-neutrality`)**  
   External service providers (e.g. OpenAI, Anthropic, Google DeepMind, Hetzner, AWS) are execution substrates and SHALL NOT define normative governance semantics.
9. **AI-First Artifact Rule (`principle ai-first-artifact`)**  
   Agents must produce a complete, reviewable draft or deliverable artifact before requesting human review or approval.
10. **Capability-Based Assignment (`principle capability-assignment`)**  
    Task dispatch and issue assignment MUST match the verified technical capability profile, budget, and toolset of the assignee.

---

## 3. Repository Topology & Authority Boundaries

The software ecosystem of **AA Digital Business** is organized into four distinct authority domains:

```mermaid
graph TD
    subgraph "Normative Governance Substrate"
        CORE["agents-os-core<br/>(Semantics, Grammar, IR, Contracts, PDCA)"]
    end

    subgraph "Operational Orchestration (SSoT)"
        CLIP["Paperclip Orchestration Engine<br/>(Issues, Heartbeats, State Machine, Artifacts)"]
    end

    subgraph "Execution & Platform Workloads"
        AGOS["agos-services<br/>(hi-bel, analyzer service, docker-compose)"]
        CTA["commercial-tech-analyzer<br/>(CPI Scoring, Valuation, Portfolios)"]
    end

    CORE -->|Normative Standards| CLIP
    CORE -->|Contracts & Boundaries| AGOS
    CORE -->|Compliance Models| CTA
    CLIP -->|Issue-Driven Dispatch| AGOS
    CLIP -->|Expansion Work Orders| CTA
```

### 3.1 Repository Roles & Boundaries
- **`agents-os-core` (Normative Core)**:
  - *Authority:* Canonical semantics, EBNF grammar, AST/IR compiler, PDCA cycle checks, and distribution contracts.
  - *Immutability:* `.agent/` is human-owned; changes to normative semantics require formal versioning.
- **`agos-services` (Execution Monorepo)**:
  - *Authority:* Containerized microservices runtime, Shopify MCP gateway (`hi-bel`), commercial analyzer service, and deployment profiles.
  - *Compliance:* Must adhere to zero-trust container isolation and standard health probe paths (`/healthz`, `/health/`, `/api/health/`).
- **`commercial-tech-analyzer` (Domain Strategy Engine)**:
  - *Authority:* Standalone technology commercial valuation, CPI scoring engine, and financial modeling (TAM/SAM/SOM, NPV).
- **`Paperclip` (Operational SSoT)**:
  - *Authority:* Master issue queue, state tracking, agent heartbeats, delegation ledger, and company document registry.

---

## 4. Operational SSoT & Traceability Rules

Every engineering and operational action must satisfy the **Triple Representation Rule**:
$$\text{Documental Definition} \iff \text{Semantic / Contractual Model} \iff \text{Executable Code \& Tests}$$

### 4.1 Traceability Mandates
1. **Issue-Driven Origin:** No autonomous work may begin without an assigned Paperclip Issue (e.g. `AADA-51`).
2. **Commit & PR Traceability:** Every git commit message and Pull Request title/description MUST reference the originating Issue identifier (`AADA-XX` or `AAD-XX`).
3. **Evidence-Based Completion:** Issues cannot transition to `done` without durable evidence:
   - Automated test execution logs.
   - Verified documentation or work products.
   - Remote repository synchronization (pushed commits).

---

## 5. Organizational Squad Structure & Roles

As established in `STD-PRJ-001`, the organization is structured into specialized execution squads:

| Squad / Body | Lead Agent | Scope & Responsibilities |
| :--- | :--- | :--- |
| **Executive Leadership** | [CEO](/AADA/agents/ceo) | Strategy, capital allocation, governance promulgation, cross-squad alignment. |
| **PMO & Operations** | [Operations Lead](/AADA/agents/operations-lead) | WIP limits, issue triage, cadence tracking, cross-agent coordination. |
| **Quality & Compliance Gate** | [Governance & Verification Lead](/AADA/agents/governance-verification-lead) | Independent code review, zero-secrets audit, health check verification, PDCA cycle checks. |
| **Platform & Microservices** | [Agent Platform Engineer](/AADA/agents/agent-platform-engineer) | `agos-services` core architecture, API design, debugger integration. |
| **Infra & MCP Services** | [Infra Manager](/AADA/agents/infra-manager) | Docker container runtime, cloud deployment profiles, reverse proxy (Caddy/Traefik). |
| **Commercial Strategy** | [Business Manager](/AADA/agents/business-manager) | Commercial Tech Analyzer, CPI asset evaluation, GTM investment prioritization. |

---

## 6. Security, Zero-Trust, and Secrets Management

1. **Zero Secrets in Code:** Hardcoded API keys, JWT secrets, passwords, or private keys in any repository is a Critical Nonconformity (`NC-SECURITY-SECRET-LEAK`).
2. **Environment Isolation:** All sensitive credentials must be injected at runtime via `.env` or secure vault mechanisms.
3. **MCP Gateway Isolation:** MCP servers must run in sandboxed Docker containers with restricted network access and explicit tool whitelisting.
4. **Service Health Probes:** Every deployed service must implement unambiguous health endpoints returning HTTP 200:
   - `GET /healthz` (Kubernetes / Docker container liveness)
   - `GET /health/` or `GET /api/health/` (Application service readiness)

---

## 7. Continuous Compliance & PDCA Verification Protocol

Compliance is verified through automated test suites and continuous cycle checks:
1. **Repository Test Suites:**
   - `agents-os-core`: 100% pass on compiler, language, and governance tests (`uv run pytest tests/`).
   - `agos-services`: 100% pass on unit, integration, and MCP tests (`pytest agos-services/tests/`).
   - `commercial-tech-analyzer`: 100% pass on scoring and valuation tests (`pytest tests/`).
2. **Automated Governance Compliance Suite (`test_corporate_governance_compliance.py`):**
   - Validates git commit traceability format across all repos.
   - Scans repos for zero-secret compliance.
   - Verifies health endpoint contracts.
   - Verifies agent role allocations in Paperclip database.
3. **Nonconformity & Inactivity Protocol:**
   - When an agent or provider fails to produce observable evidence within the inactivity threshold, a Nonconformity record (`NC-*`) is generated, the provider is disabled, and containment is triggered.

---

## 8. Summary Checklist for All Agents

Before marking any task or issue as `done`, every agent must verify:
- [x] Code adheres to the repository boundary and constitutional principles.
- [x] All unit/integration tests pass with 0 errors.
- [x] Zero secrets or sensitive credentials are committed.
- [x] Git commits include the originating issue identifier (`AADA-XX`).
- [x] Durable documentation or work product is stored and synchronized.
- [x] Changes are pushed to remote repositories.
