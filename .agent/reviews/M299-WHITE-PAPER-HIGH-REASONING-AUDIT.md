# M299 high-reasoning audit of the GSP white paper

Audit date: 2026-07-28  
Paper audited: `whitepaper/gsp-whitepaper.tex` and the 17-page rendered PDF committed at
`f43c2416d8905cfae3970dd03ffe36db8d3bf24f` on 2026-07-02  
Current product evidence:

- GSP `fd20c94264bf8893eed6c27e35966ff0397f14cb`
- VisPy2 `c51ca4cb4d97b72ce6207c35a3d2be8b191f2073`
- Datoviz adapter in the GSP commit above
- Datoviz HEAD observed at the audit-start evidence snapshot:
  `4e0076602a4f4b1294d5d5ddd6f3f1329cb61129`; concurrent work advanced that checkout after it was
  inspected, and its working tree was materially dirty during this audit, so later commits and
  uncommitted Datoviz files were not treated as audit evidence

## Executive verdict

**Verdict: strong position-paper foundation; not yet ready for external circulation as a current,
evidence-backed technical white paper.**

The paper has a clear and worthwhile central thesis: a semantic protocol boundary below diverse
scientific plotting APIs and above concrete renderers. Its best material is the explanation of
semantic visual families, explicit capability negotiation, query/readback as scientific
interpretation, and the separation between VisPy2, GSP, adapters, and renderers.

The draft currently falls short in three ways:

1. **Correctness and freshness.** It predates the current 11-family 2D/3D surface, bounded mesh
   materials and lighting, exact canvas work, experimental live navigation, and the latest query
   and backend limits. Its three exact-looking examples no longer match the current record or API
   shapes. Its review-pack figure is S030-era evidence rather than the current M292/M297 evidence.
2. **Protocol-versus-implementation clarity.** It presents the target command/session protocol
   persuasively but does not disclose prominently that the current Python adapters render immutable
   `Scene` snapshots through a backend-session interface and do not yet execute every protocol
   command category end to end. Binary IPC and production remote transports are reserved, not
   implemented profiles.
3. **White-paper evidence.** The conclusion says the implementation suggests the boundary is
   practical, but the paper presents no reproducible evaluation, performance/overhead measurement,
   semantic coverage table, negative capability tests, or adoption evidence. The six small S030
   screenshots are useful development artifacts, not sufficient evaluation.

The right revision is not a larger API manual. It is a tighter white paper with an explicit
contribution statement, a precise “target architecture versus implemented prototype” boundary, a
current capability/evidence table, and a modest but reproducible evaluation. The paper should
remain conceptual; detailed API documentation should stay in GSP and VisPy2.

## Evidence labels used below

- **Observed fact** means directly established from an inspected source, PDF, figure, capability
  declaration, or current public implementation.
- **Interpretation** is the auditor’s assessment of the effect on a technical reader.
- **Recommendation** is a proposed change and does not alter project authority.

## Authority contradiction that must be resolved before revision

### P0-AUTH — Two “current” specification copies disagree

**Observed fact.** GSP_API’s `SPEC_INDEX.md` declares its local `spec/current/` reading path
authoritative. Its local `spec/current/scene.md:68-70` still lists seven visual families: point,
marker, segment, path, image, text, and mesh. The fresh GSP repository’s
`specs/current/scene.md:60-70` and `specs/current/registries.md` list eleven families, adding pixel,
sphere, vector, and bounded primitive. The fresh GSP `AGENTS.md` also says material in GSP_API is
not authoritative merely because it exists. This is not a simple old-copy/new-copy relationship:
the GSP_API chapter contains later viewport semantics at `spec/current/scene.md:45-58` that are
absent from the fresh GSP chapter, while fresh GSP contains the later visual families.

**Interpretation.** The white paper currently agrees with the stale seven-family copy, while the
fresh product, producer, adapters, tests, and registry agree on eleven. This is not an editorial
choice; it is a source-of-truth contradiction.

**Recommendation.** Before editing the paper, the owner should designate the fresh `gsp` repository
as the canonical protocol/specification source (or explicitly choose another authority), then
either archive, synchronize, or label the GSP_API copy. This audit uses fresh GSP as current product
evidence because M299 explicitly requested comparison against the fresh-root repositories. It does
not silently resolve the governance contradiction.

## Audience and thesis assessment

### Intended audience

The current notes name “a technically sophisticated scientific visualization library developer.”
That is the right primary audience. The paper will also be read by:

- renderer/backend authors evaluating whether GSP is implementable;
- plotting and domain-tool authors evaluating producer value;
- visualization researchers evaluating novelty and evidence;
- project or standards maintainers evaluating governance and versioning.

The paper currently serves the first group best. It gives backend-minded readers a convincing
semantic boundary, but gives producer authors too little concrete value analysis and gives
research/standards readers too little evaluation and comparison.

### Thesis

**Observed fact.** The most concise thesis is at `gsp-whitepaper.tex:109-123`, especially
lines 113-116: GSP is below plotting APIs and above renderers and describes scenes, resources,
views, queries, capabilities, and diagnostics in backend-independent terms.

**Interpretation.** This is clear, differentiated, and durable. “A shared semantic rendering
layer” is accurate, but the more powerful contribution is not merely shared rendering; it is
**portable semantic execution with explicit capability truth and scientific readback**.

**Recommendation.** State one primary thesis and three contributions near the end of the
introduction:

1. a transport-independent semantic session boundary with a fast in-process profile;
2. capability- and diagnostic-driven portability rather than lowest-common-denominator claims;
3. snapshot-coherent query/readback as part of the visualization contract.

Then state the prototype evidence separately: one producer, two deliberately different adapters,
and a bounded conformance corpus.

### Does it work as a white paper?

Partly. It already works as a thoughtful position paper. It does not yet work as a comprehensive
technical white paper because target design, accepted specification, current implementation,
experimental paths, and future direction are interleaved without a consistent visual/status
vocabulary. “Current status” is too stale and too qualitative to repair that ambiguity.

## P0 — Factual, obsolescence, and boundary findings

### P0-1 — The visual-family inventory is obsolete

**Observed fact.** The paper’s baseline table at `gsp-whitepaper.tex:294-330` and current-status
list at `:613-625` cover point, marker, segment, path, image, text, and mesh. Fresh GSP
`specs/current/scene.md:60-70`, `specs/current/registries.md`, and
`gsp/scene.py:33-45` also include pixel, sphere, vector, and bounded primitive. VisPy2 exposes these
families through `Axes`/`Axes3D` methods and its public guide identifies them as priority 2D/3D
families.

**Interpretation.** A reader receives an incorrect picture of the current core vocabulary and
misses most of the newly qualified 3D product story.

**Recommendation.** Replace the family table with all eleven core families, grouping related
families without erasing their separate semantics. Add a compact status column: protocol accepted,
VisPy2 exposed, Matplotlib strict/adapted, Datoviz runtime-gated.

### P0-2 — The implementation boundary is overstated by omission

**Observed fact.** The paper describes a six-step initialized command/session protocol at
`gsp-whitepaper.tex:206-224` and later says the repository contains command batches and adapters
at `:609-625`. Fresh GSP’s normative lifecycle is indeed a command protocol, but
`gsp/specs/current/protocol.md:168-169` explicitly says the Python package does not yet ship a
complete Matplotlib or Datoviz server executing every command category end to end. The current
public adapter interface is `BackendSession.render(scene)`, `display(scene)`, and `query(...)`
(`gsp/backends.py:70-97`), and the current producer emits immutable `gsp.Scene` snapshots.

**Interpretation.** The target architecture is valid, but the paper makes it too easy to infer that
the complete command server already drives both adapters.

**Recommendation.** Add a boxed “GSP 0.2 target versus current Python prototype” table. Explicitly
say that protocol records and in-process transport exist, while current first-party rendering is a
scene-snapshot/backend-session slice and full command-category execution remains incomplete.

### P0-3 — Remote, IPC, and web targets are not separated from implemented profiles

**Observed fact.** The abstract and architecture table mention remote renderers and future web
paths (`gsp-whitepaper.tex:59-72`, `:185-212`), while the transport section calls four classes
“current design discussions” (`:278-292`). Fresh GSP
`specs/current/transports-extensions.md:46-50` states that binary IPC and production remote
transports are reserved until implementation profiles and conformance tests exist. Current
capability snapshots advertise only `INPROC`. Datoviz’s WebGPU path is an experimental Datoviz
runtime subset, not a proven GSP web transport/backend.

**Interpretation.** Most wording is aspirational, but the paper never gives the reader one
unambiguous implementation-status statement. “Renderers” in the architecture table reads like a
current list.

**Recommendation.** Mark each transport/target as **implemented**, **specified/reserved**, or
**future research**. Do not use the Datoviz WebGPU subset as evidence of a GSP browser path until a
GSP profile and conformance evidence exist.

### P0-4 — All three protocol examples are stale and exact-looking

**Observed fact.**

- The Python-shaped sketch at `gsp-whitepaper.tex:230-248` uses nonexistent current surfaces such
  as `gsp.connect`, `gsp.Canvas`, `scene.add_panel`, `gsp.Array`, `gsp.ScalarColor`, and
  `gsp.plan`; it also embeds `panel` in the visual rather than showing explicit attachment.
- The capability example at `:418-432` uses a diagnostic code
  `GSP_QUERY_CAPABILITY_UNSUPPORTED`, while the current stable diagnostic namespace includes
  values such as `pick.unsupported.no_public_primitive_map`. The current Datoviz declaration calls
  flat Lambert “CPU-resolved strict” and explicitly says native Datoviz lighting is not used
  (`gsp_datoviz/capabilities.py:741-755`).
- The query example at `:467-487` omits the current required request identity and coordinate-space
  vocabulary and uses `item_id` rather than the current `item_index`/typed payload model. Compare
  `vispy2/docs/producer-and-backends.md:35-71` and fresh GSP’s current query chapter.

**Interpretation.** The disclaimer “not a Python API commitment” protects syntax, but not the
conceptual mismatch. These blocks look authoritative enough to be copied and they obscure explicit
attachments, typed payload planning, and the actual producer/session boundary.

**Recommendation.** Choose one of two honest forms:

- executable, tested current VisPy2/GSP examples, versioned to the paper evidence snapshot; or
- language-neutral protocol records using the exact normative field vocabulary, labelled
  pseudocode and checked against the registry.

Do not mix Python syntax with invented API names.

### P0-5 — The conformance figure is no longer current evidence

**Observed fact.** Figure 3 (`gsp-whitepaper.tex:538-558`) embeds six S030-era 960×480 comparison
images. `whitepaper/capability_matrix_s030.md` records that run and reports no query evidence.
Current VisPy2 evidence is M292’s fourteen exact-wheel 800×600 artifacts across priority 2D,
perspective 3D, orthographic 3D, and camera states, plus M297 flat-Lambert live presentation.
The current capability matrix itself records GSP `fd20c94` and VisPy2 `7d2eb41`, so it also
predates current VisPy2 `c51ca4c` and needs a small evidence refresh before being quoted.

**Interpretation.** Calling Figure 3 representative “current implementation work” without date,
commit, run ID, or scope makes old evidence look current. At printed size, labels and differences
are difficult to read.

**Recommendation.** Replace it with two figures:

1. a legible 2D pair and a legible 3D pair selected from a newly qualified current-head run;
2. a compact evidence table with exact commits, dimensions, strict/adapted labels, and links to the
   full artifact manifest.

### P0-6 — Current 3D semantics and limitations are missing

**Observed fact.** Current GSP and adapters include perspective and orthographic View3D,
programmatic fit/orbit/pan/zoom/reset, retained Datoviz mesh depth, flat-Lambert face-normal
shading, ambient plus one directional light, Texture2D-unlit mesh support on qualified Datoviz,
raycast spheres with analytic depth, 3D vectors, primitives, pixels, and billboard text. The paper
only says “static View3D ... and View3D navigation review paths” and “broad material, lighting,
texture ... models remain bounded” (`gsp-whitepaper.tex:621-635`).

**Interpretation.** This is too vague to be correct as a current status account. It also misses the
most instructive example of GSP’s philosophy: Matplotlib’s deterministic projected adaptations
versus Datoviz’s qualified retained/depth paths.

**Recommendation.** Add one bounded 3D case study. Explain strict versus adapted depth, native
sphere shading versus Matplotlib projected circles, CPU-resolved strict flat Lambert, billboard
non-occlusion, capability-gated Texture2D, and experimental opt-in live navigation. Avoid implying
pixel parity or a general material system.

### P0-7 — Query rhetoric is much broader than current implementation disclosure

**Observed fact.** Query/readback is correctly presented as a core protocol principle at
`gsp-whitepaper.tex:438-491`. Current public integration evidence is bounded: point identity is
the qualified common path; Datoviz’s declared live payload parity is point identity, not image
texel/color/value (`gsp_datoviz/capabilities.py:502-512`); sphere, vector, primitive, billboard,
general 3D occlusion, per-glyph, and native Datoviz triangle picking are not claimed. Matplotlib
has broader reference query code, but producer documentation intentionally presents a bounded
public path.

**Interpretation.** The protocol ambition is legitimate, but the limitations list mentions only
Datoviz mesh triangle picking. Readers cannot tell which query statements are normative goals and
which are proven implementation.

**Recommendation.** Add a query coverage matrix with separate columns for protocol payload,
Matplotlib reference evidence, Datoviz evidence, and VisPy2 public integration. Preserve the
first-class thesis while stating the current narrowness plainly.

### P0-8 — The architecture figure contains misleading labels

**Observed fact.** `figures/gsp-architecture.pdf` labels the layer “Graphic Server Protocol”
instead of “Graphics Server Protocol,” uses “WGPU,” and groups “Vulkan / OpenGL / Skia / ...”
inside the protocol box. The paper’s own text says GSP does not require a graphics API, while
current Datoviz is Vulkan-first with an experimental WebGPU subset. The figure also omits sessions,
capabilities, adapters, queries, and the control/data split that distinguish GSP from a generic
renderer abstraction.

**Interpretation.** The main architecture figure weakens rather than clarifies the paper’s central
claim.

**Recommendation.** Redraw it around producer → protocol/session → adapter → renderer, with
capabilities/diagnostics and query/readback shown as bidirectional channels. Put graphics APIs
below renderers, not inside GSP.

### P0-9 — Release and reproducibility status is absent

**Observed fact.** GSP and VisPy2 are `0.2.0a1`, unpublished, multi-wheel/local-bootstrap projects.
Fresh GSP `README.md:28-35` says the required RC3-compatible Datoviz artifact is not published and
development uses `GSP_DATOVIZ_SOURCE`; VisPy2 `README.md:53-60` likewise says it is unpublished.
The paper has only “Draft for discussion — July 2026” and no evidence snapshot.

**Interpretation.** An external reader cannot reproduce or properly discount current-status
claims.

**Recommendation.** Add a small version/evidence box: paper revision, GSP/VisPy2 versions and
commits, Datoviz compatibility boundary, implemented transport, package publication state, and
artifact manifest. This is not release marketing; it is scientific traceability.

## P1 — Narrative and completeness findings

### P1-1 — No explicit contribution statement

The introduction motivates duplication well but never says “This paper contributes...” As a
result, semantic families, capability truth, query coherence, and transport independence compete
for attention. Add three contributions and one prototype/evaluation statement.

### P1-2 — The motivating problem lacks concrete failure stories

The motivation is broad and plausible, but abstract. Add two short cases:

- one scene that needs Matplotlib publication output and Datoviz interaction without changing
  scientific meaning;
- one capability-dependent interaction where rendering is available but picking is not, and the
  producer disables the tool explicitly.

These cases can organize the rest of the paper and demonstrate why a conventional backend flag is
insufficient.

### P1-3 — “Primitive decomposition” is useful but overweights one scatter plot

The decomposition figure is attractive, but the argument should progress from primitive reuse to
semantic commitments. Condense the cataloging prose and add one counterexample showing why draw
calls alone fail: logical-pixel size, image origin, scalar normalization, or query identity.

### P1-4 — Lifecycle and ownership deserve a first-class subsection

The current paper barely discusses ownership, shutdown, failure, and snapshot lifecycle, even
though these are central protocol concerns and were consequential in native Datoviz qualification.
Fresh GSP specifies NEW/ACTIVE/CLOSED/FAILED state, atomic initialization, monotonic revisions,
deterministic cleanup, and failure taxonomy. Add a compact state diagram and explain caller-owned
sessions, immutable producer state, adapter-private native objects, and crash/timeout classification.

### P1-5 — Versioning and conformance language are missing

GSP is an experimental pre-1.0 0.2 protocol with independent protocol, producer, renderer, query,
and transport conformance claims. The paper should state this. A reader otherwise cannot know what
“strict,” “adapted,” or “current baseline” binds to.

### P1-6 — Capability model needs typed granularity, not only a four-outcome table

The accept/simplify/deactivate/reject table is strong. It should be complemented by one current
example separating ordinary provider discovery (`visual.mesh`) from versioned semantic
capabilities (projection, depth, material, lighting, query). This is one of GSP’s most distinctive
and implemented ideas.

### P1-7 — Security is policy prose without a threat model

The no-network posture at `gsp-whitepaper.tex:582-605` is directionally correct and matches current
specification. It should distinguish:

- current accepted no-network profile;
- inert descriptors and redaction guarantees;
- reserved future server fetch;
- out-of-scope authentication, multitenancy, arbitrary code, and credential handling.

Without this, “security-conscious” risks reading as assurance rather than bounded policy.

### P1-8 — Large data is mostly architectural aspiration

The paper devotes a full section to large data, virtual sources, cache policy, and remote services,
but evaluation does not demonstrate large-data performance, zero-copy behavior, streaming, or live
remote access. Reframe as an accepted architectural direction plus bounded no-network source work,
or add evidence. “May carry NumPy/memoryview without mandatory serialization” must not be upgraded
to a zero-copy claim.

### P1-9 — Related work is too short for the novelty claim

Five paragraphs do not adequately locate GSP among:

- VisPy and other cross-backend scientific rendering layers;
- ParaView/VTK and remote scientific-visualization client/server systems;
- ANARI’s device-independent rendering contract;
- Vega/Vega-Lite and higher-level declarative grammars;
- scene/file interchange such as glTF/USD;
- browser/GPU execution layers such as WebGPU;
- multi-backend plotting ecosystems and adapter layers.

The revision should compare boundary, semantic level, transport, capability negotiation, query
contract, 2D/guides, and local zero-serialization intent. Avoid claiming “broader” or “lower” without
a comparison table and citations.

### P1-10 — The paper has no evaluation section

“Conformance as a design tool” explains methodology but presents no results. Add a bounded
evaluation with:

- semantic coverage across all eleven families;
- strict/adapted/unsupported counts by backend and feature scope;
- positive and negative capability tests;
- exact-wheel, exact-commit artifact provenance;
- canvas/viewport geometry checks;
- lifecycle stress evidence;
- query HIT/MISS/UNSUPPORTED evidence;
- in-process overhead benchmarks against direct Datoviz for scene creation, first render, repeated
  camera update, and large-array update;
- limitations of the measurements.

Do not claim general performance from screenshots or native Datoviz’s reputation.

### P1-11 — Community/governance comes before sufficient technical evidence

The community section is thoughtful, but a consortium discussion feels premature without a stable
specification authority, versioning policy, external implementation, and reproducible evaluation.
Condense it into “Governance and adoption questions” after limitations/future work.

### P1-12 — Producer value is underdeveloped

VisPy2 is described as the place for convenience, but the paper does not show what code a producer
author writes, what it does not own, how explicit backend selection works, or how capabilities
change user experience. One executable VisPy2 example and one architecture trace would make the
producer/backend separation tangible without turning the paper into an API guide.

## P2 — Figures, citations, examples, and editorial improvements

| Finding | Observed fact | Recommendation |
|---|---|---|
| P2-1 Figure legibility | The six-panel review figure is small on page 13; labels and raster differences are hard to inspect. | Use at most two comparisons per printed figure; move the full contact sheet to supplemental artifacts. |
| P2-2 Float layout | The 17-page PDF has conspicuous whitespace around floating code/figures and a dense final bibliography page. | Use non-floating code blocks where practical, revisit float placement, and balance page breaks after the content revision. |
| P2-3 Accessibility | `pdfinfo` reports `Tagged: no`; figures have captions but no accessible descriptions. | Produce a tagged PDF if the toolchain permits and include meaningful text descriptions in source/supplement. |
| P2-4 Architecture art | The architecture figure is visually simple but conceptually outdated and contains naming errors. | Redraw as vector art from the current architecture and include a legend for target/implemented/experimental. |
| P2-5 Decomposition art | The plot-decomposition figure is visually useful but its right-side component inventory is small. | Simplify labels or split into a main visual and a readable callout. |
| P2-6 Unused figure | `figures/visualization-pipeline.pdf` is present but not referenced. | Delete from the paper asset set later or deliberately reuse after verifying its model; it currently introduces different terminology. |
| P2-7 Citation integrity | All 12 bibliography keys are cited and no cited key is missing. | Preserve this hygiene, but broaden the bibliography before external circulation. |
| P2-8 Web references | ANARI, LSP, WebGPU, and Datoviz are cited as mutable web resources with year only. | Cite exact specification/release versions and access dates; use Datoviz’s archival citation/DOI when available. |
| P2-9 Terminology | “Renderer/server,” “renderer,” “backend,” and “adapter” occasionally blur. | Add a terminology box and use each role consistently. |
| P2-10 Status vocabulary | “Strict,” “accepted,” “adapted,” “current,” “proven,” and “supported” are not formally introduced together. | Define them once and bind them to capability snapshots and evidence scopes. |
| P2-11 Quantitative adjectives | Terms such as “substantial,” “high-performance,” and “high-quality” are not quantified in the paper. | Either attach bounded evidence or rewrite as design goals / properties of the underlying renderer. |
| P2-12 Repository link | The paper does not give a stable repository, specification, artifact, or reproducibility URL. | Add a versioned artifact/repository pointer and evidence manifest. |

## Section-by-section assessment

| Current section | Assessment | Required direction |
|---|---|---|
| Abstract | Clear problem and thesis; over-broad target list lacks implemented/reserved distinction. | Add contribution and prototype-status sentence; distinguish remote/web targets from current in-process evidence. |
| Motivation | Persuasive but generic. | Add two concrete cross-backend/query failure stories and one falsifiable claim. |
| Primitive decomposition | Good bridge from plotting to semantics. | Condense and add one “draw calls are insufficient” semantic counterexample. |
| What GSP is not | Strong and memorable. | Retain, but move after a positive contribution/model statement. |
| Protocol boundary | Correct target architecture, incomplete implementation disclosure, stale pseudocode. | Add target/current table, lifecycle, ownership, explicit attachment, and executable or language-neutral example. |
| Control/data plane | Sound architectural principle. | State implemented copy/borrow evidence and avoid implying zero-copy or remote materialization exists. |
| Transport independence | Correct goal. | Label in-process implemented; debug JSON bounded; binary IPC/network reserved. |
| Semantic visual families | Core conceptual section, but stale family list. | Update to eleven families and add logical-pixel, color, depth, identity, and adaptation examples. |
| Capabilities and adaptation | One of the strongest sections. | Replace stale YAML with a current typed capability example and define evidence/status vocabulary. |
| Query and readback | Strong scientific argument; current coverage not disclosed. | Separate normative contract from current backend/producer evidence; add coverage table. |
| Reference and flagship backends | Roles are clear but too promotional and non-quantitative. | Add exact backend profile table: strict/adapted/unsupported and runtime gates. |
| VisPy2 producer | Correct role, insufficient concrete value. | Add one tested producer example and explicit ownership/session behavior. |
| Conformance as a design tool | Good methodology, old evidence, no measured results. | Turn into evaluation methodology plus current results and provenance. |
| Large data/extensions/remote | Ambitious and security-aware, mostly future. | Bound claims to no-network/source validation; move broader remote/LOD discussion to future work unless evaluated. |
| Current status | Materially stale and not reproducible. | Replace with versioned implementation matrix and explicit limitations. |
| Relation to existing systems | Correct high-level distinctions, insufficient breadth/depth. | Expand into a structured comparison with stronger citations. |
| Community shape | Reasonable discussion, premature as a full section. | Condense and move after limitations/future work. |
| Conclusion | Restates thesis well; “practical” is not yet demonstrated in-paper. | Tie conclusion to actual bounded evaluation and name remaining falsification/adoption work. |

## Coverage matrix against the current product

Legend: **good** = paper covers the concept accurately; **partial** = concept present but current
scope/evidence missing; **missing** = absent or materially stale; **future-labelled** = accurately
described as outside current implementation.

| Topic | Paper coverage | Current product/evidence boundary | Revision need |
|---|---|---|---|
| Protocol thesis | good | Charter and fresh GSP agree | Preserve and sharpen contributions |
| Producer/session/adapter/renderer split | partial | Current VisPy2 → immutable Scene → BackendSession → adapter | Show target/current split |
| GSP 0.2 versioning | missing | Protocol 0.2, packages 0.2.0a1, pre-1.0 | Add version/conformance box |
| Session lifecycle | missing | Caller-owned sessions; deterministic close; lifecycle errors | Add state/ownership subsection |
| Command batches/full server | partial/over-broad | Records exist; full end-to-end command server incomplete | Disclose explicitly |
| In-process transport | good concept | Implemented; no mandatory JSON; no blanket zero-copy claim | Add evidence and ownership limits |
| Debug JSON | partial | Fixture/replay profile | Bound it precisely |
| Binary IPC | partial | Reserved, not implemented | Label reserved |
| Network/remote renderer | partial | No production GSP remote profile | Label future |
| Web/browser | partial | Future GSP path; Datoviz has separate experimental subset | Do not conflate |
| Point/marker | good | Both providers; backend raster differs | Current artifacts |
| Segment/path | good | Both providers | Current artifacts/coverage |
| Image/scalar color | good | Both providers; Matplotlib broader query | Current artifacts/query limits |
| Pixel | missing | 2D/3D API; Datoviz runtime-gated; Matplotlib adaptation | Add family/status |
| Sphere | missing | Matplotlib projected circle; Datoviz analytic-depth impostor | Add case study |
| Vector | missing | 2D/3D; Matplotlib adapted; Datoviz dense vector | Add family/status |
| Bounded primitive | missing | Five topologies; Matplotlib adapted; Datoviz public primitive | Add family/status |
| Text and billboard text | partial | Backend fonts/metrics differ; 3D overlay lacks strict occlusion | Add limitations |
| Mesh 2D/3D | partial | Depth/culling/material scopes capability-gated | Add exact scopes |
| Flat Lambert/lighting | missing | Face normals; scalar ambient + one directional; CPU-resolved strict Datoviz | Add bounded material case |
| Texture2D unlit | missing | Qualified Datoviz; Matplotlib unsupported | Add status, not broad material claim |
| Smooth/Phong/general materials | future-labelled | Unsupported/outside bounded GSP 0.2 | Preserve limit |
| Volume/surface visual families | future-labelled | Not public GSP families | Preserve limit |
| View2D/navigation | partial | Deterministic client actions; backend realization differs | Add current status |
| View3D/cameras | partial | Perspective/orthographic/fit/orbit/pan/zoom/reset | Add current evidence |
| Live Datoviz navigation | missing | Experimental opt-in, lifecycle/manual evidence | Add experimental label |
| Guides/layout/titles | partial | Matplotlib native; Datoviz partial/adapted, title unsupported | Add exact backend split |
| Canvas/logical pixels | partial | Exact 800×600 gallery; logical/device distinction | Add semantic/evaluation result |
| Capabilities/diagnostics | good concept | Ordinary + typed/versioned capabilities; runtime probe | Add current exact example |
| Query/readback model | good concept | Bounded implementation; common point identity path | Add coverage matrix |
| Mesh triangle picking | good/current | Datoviz unadvertised; Matplotlib bounded reference work | Keep exact diagnostic/status |
| Extensions/manifests | partial | Accepted typed/no-network policy | Separate validated model from execution |
| Virtual/large data | partial | Bounded sources; no general remote/streaming proof | Reduce or evaluate |
| Security/redaction | partial | Explicit no-network and inert-descriptor rules | Add threat/scope table |
| Packaging/discovery | missing | Multi-distribution, lazy entry points, unpublished bootstrap | Add reproducibility boundary |
| Conformance evidence | partial/stale | M292/M297 newer than paper; current-head refresh needed | Replace S030 evidence |
| Performance evidence | missing | No evidence presented in paper | Benchmark or soften claims |
| External adoption | missing | One producer and two first-party adapters | State prototype limitation |
| Governance | partial | Open, with current authority duplication | Resolve authority before external paper |

## Proposed revised outline

1. **Abstract**
   - problem, thesis, three contributions, exact prototype scope
2. **Introduction: why renderer portability currently fails**
   - publication/GPU use case
   - render-without-query use case
   - contribution statement
3. **Design goals and non-goals**
   - semantic, capability-honest, query-coherent, transport-independent, fast local profile
   - not a plotting API, renderer, file format, or universal feature promise
4. **Protocol model**
   - roles and terminology
   - session lifecycle and ownership
   - scene/resources/views/attachments
   - control versus data plane
   - target protocol versus current prototype
5. **Semantic visual contracts**
   - eleven accepted families
   - cross-cutting units, coordinates, color, depth, identity
   - one point example and one bounded 3D example
6. **Capabilities, adaptation, and diagnostics**
   - ordinary versus typed/versioned capability
   - accept/adapt/deactivate/reject
   - runtime-gated Datoviz example
7. **Query and readback**
   - snapshot coherence and payloads
   - current bounded query coverage
8. **Implementations**
   - GSP core/package boundary
   - VisPy2 producer
   - Matplotlib reference profile
   - Datoviz flagship profile
   - strict/adapted/experimental/unsupported matrix
9. **Evaluation**
   - method and exact commits/wheels
   - semantic and negative capability tests
   - 2D/3D artifact results
   - lifecycle/query results
   - local overhead/performance measurements
10. **Security, large data, and transport roadmap**
    - current no-network profile
    - reserved IPC/remote/browser profiles
11. **Related work**
    - structured comparison by abstraction boundary and semantics
12. **Limitations and threats to validity**
    - one producer, two first-party adapters
    - unpublished alpha packaging
    - bounded queries/materials/layout
    - no production remote profile
    - platform/runtime scope
13. **Future work, adoption, and governance**
14. **Conclusion**

This order makes the paper’s argument linear: problem → contribution → model → differentiators →
implementation → evidence → limitations.

## Prioritized improvement directions

| Priority | Direction | Expected impact | Effort | Dependency |
|---|---|---:|---:|---|
| P0 | Resolve canonical spec/repository authority | Very high: prevents contradictory revision | Small decision, medium cleanup | Owner decision |
| P0 | Freeze a paper evidence snapshot and regenerate current-head artifacts | Very high: makes every status claim traceable | Medium | M298/manual review findings |
| P0 | Replace stale family/status material | Very high: restores factual accuracy | Medium | Canonical authority |
| P0 | Replace all three stale examples | High: removes copyable misinformation | Medium | Current protocol/API freeze |
| P0 | Add target-versus-implemented table | Very high: prevents architecture overclaim | Small | None |
| P0 | Redraw architecture figure | High: clarifies central contribution | Medium | Terminology/outline |
| P0 | Add exact query, transport, packaging, and experimental limitations | High: honest scope | Small | Current evidence snapshot |
| P1 | Add explicit contributions and two running use cases | Very high: improves persuasion and coherence | Small | Owner thesis choice |
| P1 | Add bounded evaluation section | Very high: converts position draft into technical white paper | Large | Benchmark/evidence mission |
| P1 | Add lifecycle/ownership section | High: strengthens protocol character | Medium | None |
| P1 | Expand structured related work | High: supports novelty positioning | Medium/large | Literature review |
| P1 | Add security threat/scope table | Medium/high: bounds assurance | Medium | Security-owner review |
| P1 | Rebalance large-data/community sections | Medium: reduces speculative weight | Small | Revised outline |
| P2 | Improve figure legibility, PDF layout, accessibility, and artifact links | Medium: publication quality | Medium | Content stable |
| P2 | Broaden/version bibliography | Medium: scholarly credibility | Medium | Related-work revision |

### Suggested implementation sequence

1. Resolve authority and freeze exact evidence commits.
2. Complete the human API/backend review and turn findings into the current capability matrix.
3. Rewrite only the factual/status tables and examples.
4. Agree on thesis/contributions and revised outline.
5. Add evaluation and related work.
6. Redraw figures.
7. Perform technical, scientific, editorial, and accessibility reviews separately.

## Questions requiring owner or scientific judgment

1. Is the primary external artifact intended to be a **position white paper**, a
   **specification overview**, or a **research paper with evaluation**? This audit recommends a
   white paper with bounded evaluation.
2. Which repository owns the canonical GSP 0.2 specification now: fresh `gsp`, GSP_API, or a future
   specification-only repository?
3. Is the strongest claim “one semantic scene can target publication and GPU rendering,” or the
   broader “multiple producer ecosystems can share GSP”? The latter is not yet supported by an
   independent producer.
4. Should “query/readback is first-class” be framed as a normative design commitment despite
   deliberately narrow current picking coverage? This audit recommends yes, with an explicit
   implementation matrix.
5. What minimum evidence justifies the conclusion that the boundary is “practical”: current
   conformance and galleries, measured adapter overhead, an external producer/backend, or all
   three?
6. Is performance a core paper contribution? If yes, define workloads and success thresholds
   before benchmarking. If not, replace unqualified “high-performance” claims with “targets a
   high-performance renderer through a no-mandatory-serialization local profile.”
7. Should Datoviz remain the “flagship” backend in an ecosystem-facing paper, or be described as
   the first GPU implementation and stress test of the protocol boundary?
8. How much of experimental live View3D navigation belongs in the paper versus supplemental
   evidence?
9. Should Texture2D-unlit and flat Lambert appear as case studies of capability granularity, or
   remain only in the status matrix?
10. Is a production remote renderer a near-term commitment or a motivating architectural target?
    The paper should use one status consistently.
11. Which external systems are essential comparators for novelty: VisPy, ParaView/VTK client-server,
    ANARI, Vega/Vega-Lite, glTF/USD, WebGPU, HoloViews/Bokeh/Plotly, or others?
12. What governance statement is appropriate before an external implementation or independent
    adopter exists?
13. Should the paper retain the current authorship and “invitation to discuss” tone, or target a
    citable version with a frozen DOI and artifact archive?

## Claims explicitly checked

| Claim or claim family | Result |
|---|---|
| GSP sits below plotting APIs and above renderers | Consistent with charter, architecture, fresh GSP, and VisPy2 |
| GSP is not itself a plotting API, renderer, or file format | Consistent |
| Fast in-process path without mandatory JSON/base64 | Specified and implemented as a profile; not a general zero-copy guarantee |
| Four transport classes | Architectural model; only in-process is implemented, debug JSON bounded, IPC/network reserved |
| Session initialization/capabilities/commands/queries lifecycle | Normatively specified; complete adapter execution of every command category is not implemented |
| Current visual-family list | Paper obsolete: 7 shown versus 11 current |
| Logical-pixel point diameter | Consistent with current protocol |
| Capability accept/adapt/deactivate/reject philosophy | Consistent; exact example vocabulary stale |
| Datoviz flat Lambert CPU resolution | Current and strict within bounded contract; native Datoviz lighting is not used |
| Datoviz mesh triangle picking unadvertised | Current and correctly stated |
| Query tied to snapshots | Normatively current; example fields stale |
| Matplotlib as reference/publication backend | Current project role |
| Matplotlib PNG/PDF/SVG output | Advertised current capability |
| Datoviz as flagship retained GPU backend | Current project role; performance not measured in paper |
| VisPy2 as high-level producer | Current |
| Figure/Axes do not own backend resources | Current |
| Cross-backend conformance/review packs exist | True; embedded paper evidence is stale |
| Datoviz guide/layout behavior partly adapted | Current |
| Volume and surface visual families remain future work | Current |
| Broad material/light/shader system remains bounded | Current, but narrow flat Lambert/lighting and Texture2D-unlit now exist |
| Datoviz capability gating depends on binding/runtime evidence | Current |
| Virtual source/extension security posture | Consistent with accepted no-network profile |
| Dynamic execution/arbitrary network/inline secrets rejected | Consistent for current accepted policy |
| Production remote rendering exists | Not claimed explicitly, but paper status distinction is insufficient; it does not exist as a current GSP profile |
| View3D/camera/navigation work exists | True; paper materially underdescribes current scope and experimental boundary |
| Current implementation makes the boundary practical | Plausible interpretation, not established by the evidence presented in the paper |
| Bibliography keys resolve | All 12 cited keys exist; all 12 entries are cited |

## Inputs inspected

### White paper

- `whitepaper/gsp-whitepaper.tex`, all 711 lines
- `whitepaper/gsp-whitepaper.pdf`, all 17 rendered pages
- `whitepaper/references.bib`
- `whitepaper/README.md`
- `whitepaper/NOTES_FOR_NICOLAS.md`
- `whitepaper/capability_matrix_s030.md`
- all referenced figures:
  - `figures/gsp-architecture.pdf`
  - `figures/plot-decomposition.pdf`
  - six `review-*.png` comparison figures
- unreferenced `figures/visualization-pipeline.pdf`

### GSP_API authority and history

- `PROJECT_CHARTER.md`
- `ARCHITECTURE.md`
- `SPEC_INDEX.md`
- local `spec/current/scene.md`, `visuals.md`, and relevant detailed security/data/visual specs
- accepted mission/evidence records relevant to current 3D, gallery, lifecycle, and flat-Lambert
  status
- Git history and PDF metadata for the paper snapshot

### Fresh GSP

- `AGENTS.md`, `README.md`, package metadata
- `specs/current/` index, protocol, scene, visuals, views/layout, capabilities, queries,
  transports/extensions, backend profiles, and registries
- `docs/protocol-and-backends.md`
- public `gsp.__init__`, backend discovery/session protocol, immutable `Scene`, protocol records
- Matplotlib provider and typed capability declarations
- Datoviz provider, runtime probe, typed capability declarations, renderer/query boundaries

### Fresh VisPy2

- `AGENTS.md`, `README.md`, `pyproject.toml`
- public `vispy2.__init__`
- `protocol.py` public Figure/Axes/Axes3D and module-level API surface
- user guide
- producer/backend boundary
- gallery guide and examples index
- M292 capability matrix, human-review material, exact-wheel qualification, lifecycle evidence
- current Gallery 5 flat-Lambert implementation and `Axes3D.set_lighting`

### Datoviz boundary

- committed repository identity/branch/HEAD
- top-level README and public v0.4 scene/app positioning
- public header presence for capability snapshots, offscreen capture, View3D state, input,
  pixel/sphere/vector/primitive/mesh/text surfaces
- GSP adapter’s generated-binding qualification checks

Because the Datoviz checkout contained extensive unrelated tracked and untracked work, those
working-tree modifications were not used to strengthen any claim.

## Final audit verdict

No white-paper revision should begin from the current text by merely “updating the status section.”
The draft needs a controlled second edition:

1. resolve specification authority;
2. freeze current reviewed evidence;
3. correct the nine P0 items;
4. restructure around explicit contributions and target-versus-current boundaries;
5. add bounded, reproducible evaluation.

After those changes, the paper can become a compelling white paper. The conceptual core is already
good; the principal risk is not the thesis, but presenting a rapidly evolving prototype with more
currency, completeness, and empirical support than the current document actually contains.
