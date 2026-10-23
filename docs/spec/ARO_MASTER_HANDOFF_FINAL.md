# ARO_MASTER_HANDOFF_FINAL

Snapshot: 2026-10-17 UTC; RC1 continuation. This document replaces the need to read old chats. It is an operational handoff, **not a declaration of product acceptance**. Current state: editor/A24 fixes committed and RC1 validation recorded below; A18/G1/live integration/production release remain BLOCKED. Preserve the existing project.

## 1. Non-negotiable continuation rule

**DO NOT REDESIGN / DO NOT DELETE LEGACY CAPABILITIES.** Continue the existing architecture and code. Preserve Android editing, manual Gemini, API translation, approved Film Memory, glossary, voice assignment, VieNeu/Edge, source import/OCR/ASR, on-screen signs, background modes, rendering, preview/audition/waveform, resumability, cancellation, fencing, historical evidence and checkpoints. A temporary explicit unsupported-operation error is not completion of that feature. Do not replace the worker, contracts or app to evade integration defects. Never overwrite historical acceptance or mark a missing check PASS.

User authorization: audit → targeted fixes → A18 → integration → validation → release, autonomously. Stop only for genuine architecture conflict, unavoidable external credential/owner action, or unrecoverable repository/data integrity. No architectural conflict was established in this audit. Live OAuth/Colab and owner final quality review remain external actions. Do not invent credentials, owner approvals, translations, model output or Golden evidence.

## Latest continuation evidence

RC1 continuation implements real worker consumption of the committed editor dataset and TTS locks, replacing the temporary guard. Kotlin editor exports were consumed by production worker stages and real VieNeu: 3/3 tests passed, including wrong-source/corrupt-page rejection, subtitle text verification, locked spoken text and minimal synthesis invalidation. This is a cross-language fixture over LocalStore, not physical Android/live Drive/Golden acceptance. A24 pending outputs, persistence across Room close/reopen and streamed full-byte ACCEPT_RESULT verification are implemented. Final regression:941 passed/9 explicit skips (331.98s) worker;111 Android tests/0 failures/0 skips; lint0 errors. Lock/Ruff/format/mypy passed. Full suites ran after source fixes. Evidence commit40f9343 changes artifacts only; worker/android trees equal tested implementation e87c2cb. APK regenerated from final HEAD40f9343, signed v2 and readback hash verified. Full logs in artifacts/RC1 and RC1-evidence.zip.

A18 remains at the preserved cp12 POLISH manual gate. Original13 responses have been consumed; only11 NEW POLISH responses are outstanding. Drive responses folder checked2026-10-17 still contains original13 only. A03 live smoke actually attempted and returned DRIVE_AUTH_REQUIRED; PENDING_LIVE. No A25 work, no redesign, no source re-OCR in RC1.

## 2. Source identity, current HEAD and recovery package

- Verified Arena source baseline: `ea47de2b49bc14dce5e16aecd495ea29f356f5bd` (A25 evidence commit).
- **Current audited repository HEAD: `40f93439b902bceddeaa61a6f2e0e13541d24be0`**, branch `main`.
- Working checkout in this session: `/workspace/aro`. Git worktree clean after commits below.
- Original A25 bundle Drive ID: `1JNuvImiSW2vtDoOaLA1fJmqZ6pDYIMGE`; SHA-256 `e585dc455fd8261e318595ed6e8e2b4142b0f610bc6dead6f9ea8271793859ff`. Downloaded, hashed, cloned successfully.
- Historical recovery bundle (superseded locally by ARO_CP12.bundle): **`ARO_AUDIT_FINAL.bundle`**, Drive ID `13Qfk6vUQx3_cSAsLA06amNoF0-S0oTx5`, saved alongside this handoff in ARO_MASTER. Full history, main and HEAD at the audited HEAD. SHA-256: `ecedfddb60a781e83ea153321043f64c9f1254108b967b6371db9a88925ad7c7`.
- Latest complete code/history bundle: ARO_RC1.bundle, Drive1vs6RZSoSFmZgKIMOju4Huho_cCJvA3qN; SHA256330ea41b391a222149d6eb22d8b29a945ebf25730826c13ebe9a7132b420d31c. Includes both RC1 commits and all historical refs; verified with git bundle verify. Use this bundle for new recovery.
- This handoff is a sidecar to that code snapshot, not a commit claiming its own self-referential hash. Copy it into the recovered repo after cloning; commit it on the next development change if desired.
- GitHub discovery found private `trandong4088-oss/ARO-Donghua-Studio-V2-`, but its README is a different V2 baseline. Its equivalence to the A25 bundle was **not established**. No changes were pushed there. Do not overwrite it or assume it is the canonical remote.
- `origin` in the recovered checkout points to the original local bundle. A local commit is not a GitHub push.

Commits applied:

| Commit | Exact change | Evidence / limit |
|---|---|---|
| `44c5c77ebd282a13047c9c10dab45b1c93944b42` | Worker stops with `BLOCKED_RETRYABLE / EDITED_REVISION_UNSUPPORTED` when frozen revision contains `cue_dataset_ref`, before source download and pipeline execution. Prevents silently discarding editor changes/TTS lock. AGENTS now reflects D18 and preservation rule. | One regression test passed; baseline mutation failed for intended source-download defect. This is containment, **not editor-aware execution implemented**. |
| `b586e448fa5926542065e87935da30a4f92edcf8` | Colab startup no longer depends on stale `worker.runner` doctor capability; requires successful core doctor, workspace + root ID; passes required `--root-id`, state directory and pinned runtime environment paths. README status corrected. | Two notebook-cell/real-CLI-parser tests passed. Interactive Colab not run. |
| `f5640409e6718590ec7305bd44eebe4a4dd5cb02` | Preserves 13 received Gemini response text files and reproducible partial structural preflight; corrects stale “responses missing” status. | 13/13 match request batch/hash and exact IDs, 194 nonempty translations; at that commit full validator/import were not run; cp12 now completed both. |
| `f04eafaacb9ddbb9b7216968ac3e88e2aca6c2af` | Rebind already-imported responses to current worker attempt instead of treating old import as current ACK. cp12 recovery evidence. | Original13 consumed; no owner retransmission. |
| `e87c2cb2977018c98a3fe516ae369fefb9ff71e8` | Real editor revision/page consumption, source/hash validation, TTS lock preservation and fit enforcement; pending Output Library and actual aux/default FINAL byte verification; cancellation zombie fix; typed response rebind; RC version and verified Gradle metadata. | Complete regression and Kotlin→worker→real VieNeu proof recorded in artifacts/RC1. |
| `40f93439b902bceddeaa61a6f2e0e13541d24be0` | Commits all RC1 regression evidence, test XML, real TTS proof, limitations and device instructions. Production source trees unchanged from e87c2cb. | Final APK rebuilt at this HEAD; bundle contains full history. |

## 3. Architecture and design authority

ARO turns private Chinese donghua into Vietnamese burned-in subtitles + Vietnamese speech mixed with background, producing an accepted `FINAL.mp4` on Drive. Android is controller/editor/player; Python does all OCR, ASR, translation validation, TTS, DSP and FFmpeg. Colab is an ephemeral worker host, not a second application backend. No tunnel or phone ML/FFmpeg requirement. Gemini manual mode is a supported provider, with no browser/app automation.

Authoritative design: `docs/architecture/00…13` and corresponding Drive ARO_MASTER files. Priority: 03 lifecycle/storage, 04 wire models, domain specs 05–09, 11 acceptance, 10 taskbook. Read order 01→03→04→02→10. Source RE influenced requirements; do not copy proprietary code, weights, fonts or cached artifacts from GenMedia/EZMaxSub.

Two owner amendments already exist and must be preserved:

- D17 / A-2026-10-15: G-SOURCE/G-MEANING can use `OWNER_ACCEPTED_WITH_QA_REVIEW`, without inventing a Chinese-reading human reviewer. Requires source QA without meaning-changing errors, G-STRUCT, terminology/name consistency, and an actual owner final Vietnamese review. Missing conditions remain BLOCKED. Historical OWNER_WAIVED records are history, not a current blanket PASS.
- D18 / A-2026-10-15b: A19–A24 may be implemented before G1, labelled IMPLEMENTED_PRE_G1; deferred live/G1/device acceptance must still run. Thus doing Android before G1 was an authorized deviation, not an Arena design violation.

Repository layout (implemented directories):

```text
AGENTS.md, README.md, Makefile
android/
  app/                         Compose shell
  core/{model,database,sync,media,...}/  wire DTOs, Room, Drive/outbox, playback
  feature/{editor,memory,voices,outputs,...}/
  gradle/, gradlew, tools/      pinned build + interop fixtures/bootstrap
worker/
  pyproject.toml, uv.lock
  src/aro_worker/
    cli.py
    core/                      models/config/canonical/doctor/stages/runner
    storage/                   Drive API, LocalStore, artifacts
    jobs/                      controller/commands/reducer/recovery/lease/auxiliary
    subtitle/, ocr/, asr/, translation/, memory/
    tts/, audio/, media/, render/, validation/, cache/
  tests/{unit,integration,media,...}/
contracts/v1/                  JSON schemas (aux minor 1.1 included)
contracts/fixtures/            cross-language valid/invalid/canonical data
configs/, profiles/genres/, assets/fonts/
models/                        model manifests, not weights
locks/                         runtime/FFmpeg/TTS locks
notebooks/ARO_Colab.ipynb
 docs/architecture/, docs/adr/, docs/master-amendments/, docs/runbooks/golden.md
 tests/golden/                 case, source prep, review/report/pack/restore tools
 artifacts/A01…A25/            historical evidence; A18 source/job/handoff context
 artifacts/FINAL_AUDIT/        this audit's tests, APK readback, responses/preflight
.cache/                        runtime models/media/store/cache; not in git bundle
```

## 4. Design conformance assessment

This was a targeted code/evidence audit, not exhaustive certification of every task.

Observed aligned with design: modular Python package and native Android layers; strict schema/canonical models; separate controller and worker attempts; runner authority checks, checkpointed execution and manifest-last artifact storage; controller-only acceptance; production manual handoff parser; persisted editor revisions with lineage; auxiliary request/result separation and feature gates; real worker audition rather than Android synthetic TTS. Code locations: `core/runner.py`, `jobs/auxiliary.py`, `core/models.py`, `translation/handoff.py`, `android/core/sync/EditorRepository.kt`, `RevisionMerge.kt`, `AuxJobs.kt`.

Confirmed incorrect/incomplete:

1. Worker ignored `ProjectRevision.cue_dataset_ref`; Android saved revisions but final jobs regenerated source cues. A23/A24 reports admitted this. RC1 now consumes verified committed pages; the original guard is superseded by actual execution and integrity tests.
2. Editor `extensions["aro.editor"].tts_locked` has no worker enforcement. RC1 preserves the lock in polish and prevents fit rewrites; real synthesis and display-only reuse are verified.
3. Colab startup required `worker.runner`, while `core/doctor.py` still lists it NOT_IMPLEMENTED; final command also omitted required `--root-id` and failed to propagate paths from doctor-only config. Notebook fixed, live validation pending. Doctor still contains stale NOT_IMPLEMENTED labels for implemented modules; do not treat those labels as the production registry.
4. README/AGENTS lagged amendments and task status; corrected.
5. Preview/audition do not implement arbitrary edited-revision preview or fresh newly assigned voice audition. Preview requires an accepted matching base result; audition reuses accepted fitted/raw voice clips and labels requested vs actual voice. Preserve this behavior; expand through the existing contracts with tests.
6. `make release` has no `scripts/package_release.py`; A28 is not implemented. No production release can be inferred from the debug APK.
7. Original cp10 manifest remains missing. Independent exact-archive-hash recovery completed, with distinct recovered-state-manifest.json and all 295 store blobs verified; cp12 snapshot now preserves resumed state.

## 5. Drive inventory and IDs

Account used: Loan / `l7628862@gmail.com`. Folder links: `https://drive.google.com/drive/folders/<ID>`; file links: `https://drive.google.com/file/d/<ID>/view`. Keep private source and outputs private.

| Location | Drive ID |
|---|---|
| Dự án Aro (name has trailing space) | `1jqZLgA0c20g4XAt_uASmZ9bAeSxqGH7l` |
| ARO_MASTER: current architecture + this handoff + audit bundle | `1D5PD7yR9WKjs4VuuKqLOG2CqQhG2I5YG` |
| RC1 release folder | `1FGXbbXggg5Yrrnd56CcPKdID5nPySfyb` |
| ARO_BUILD: per-task evidence | `1qKtJ9k9uvfWmwF8Ilx4dOWExBvtX8A2n` |
| ARO_BUILD/ARO_MASTER_HISTORY | `1UdLNDg2wsfGIHIKlqtCX0_4YIUV-OYFB` |
| ARO_BUILD/A18 | `1OA055BOHu00naktfl6MvTik4W12okiUk` |
| A18/checkpoints | `1qY2dAIpeLyyaln5luXgmLUQyMp1-nPtv` |
| A18/checkpoints/cp10-post-import: actual runtime state | `19PNKL1WIUQvt5_7yQBaXGG3MJGcLx79x` |
| A18/checkpoints/cp11-amendment: amendment only, state unchanged | `1NNrJPwMncmCsoYlQMOW1tL8Qnv0e9E35` |
| A18/source-parts | `1vdwUbVfUmdNDhVAwJ0xL1zzIsQWCJnE6` |
| A18/review-r4 | `186s3QlaYb5roBqRS3hYrItLxLWpbmA_a` |
| A18/gemini-handoff-run4 | `1OlbfNgmRafl5cL05NmE4HkYJMZmMO2MV` |
| handoff/responses: **13 files now present** | `1ZvoFLuMZmphEm9niDB8njcahI04PfXqO` |
| ARO_BUILD/A24 | `18YDAxzL9jUGo6jR4auVRQ-WQ_t4CQamN` |
| ARO_BUILD/A25 | `1PTjNBOtuXUY2aKAoilSSpGj58mfhVj_d` |
| A03 isolated live smoke folder | `1goyNlLLXREoQV3kFFX15V2tRE9_fJpz6` |
| Older 01_ARENA_WORKSPACE (not current code authority) | `1rmt3eS5YT77lOmWGpSuo7aSmqO4q6Uwg` |
| Older 00_ARCHITECT_MASTER (not current design authority) | `1AO1cDiAo0NbfX2vcwlOXsFjVS6K4FlQg` |

Latest amended master documents: 10 `1GYpqEO5-WqpCn_9iPiAD1cao1JSGGrqd`; 11 `1yDlIDSTsPGyQ_-1FbbUD8YGN1bunV2q1`; 13 `1Q8NbS7OlZB5NOjVXfPgpRb6vYy1cfgGU`.

A previous runtime folder `1agc7s-0230hXMG5W0xZVL3XLnTGxpKFh` exists in older context. It was **not verified as this run's live workspace**. Do not write to it by assumption. `/AroStudio` is the logical protocol layout, not permission to select a folder by name.

## 6. Lifecycle and contracts

One active controller per workspace; immutable sequenced commands and frozen revisions/requests. Each worker boot has a new session UUID. START_ATTEMPT assigns job, attempt and monotonic generation to that exact session. Local OS lock protects the scheduler; heartbeat/lease are advisory, not a Drive mutex. No active-active takeover by timeout. CLI→Android controller transfer must drain old writer and record TRANSFER_CONTROLLER, preserving last command sequence/hash.

Manifest-last publication and reserved Drive IDs make retries adopt only matching bytes. Exact IDs + byte size + SHA-256 are authoritative; filename, timestamp and `project.json` head convenience are not. At-least-once computation/provider billing; no exactly-once promise.

Normal flow: project create/upload → immutable ProjectRevision → CREATE_JOB → QUEUED → START_ATTEMPT/ACK → RUNNING → optional WAITING_USER (source review, translation, polish, timing) / BLOCKED_RETRYABLE → VALIDATING → worker RESULT_PROPOSED/PUBLISH_PENDING → controller verifies artifacts/current generation → ACCEPT_RESULT → SUCCEEDED. CANCEL revokes publication; physical stop requires worker ACK. Terminal retry creates new job and reuses verified artifacts. Old worker may finish computation but may not publish the current result.

Logical Drive paths:

```text
workspace.json
controller/commands/<seq>-<id>.json
workers/<session>/{hello.json,heartbeat.json,...}
projects/<project>/revisions/<revision>.json
projects/<project>/input/<source>/video
projects/<project>/jobs/<job>/request.json
projects/<project>/jobs/<job>/attempts/<attempt>/
  assignment.json, state.json, events/, checkpoints/, handoff/, result.json
projects/<project>/{subtitle,translation,memory,tts,audio,cache}/...
projects/<project>/output/<job>/<attempt>/{FINAL.mp4,validation.json}
projects/<project>/output/published/<publish>.json
```

Wire: UTF-8 snake_case JSON; Draft 2020-12 schemas; strict Pydantic + Kotlin DTOs; UUID IDs; integer milliseconds; SHA-256; NFC and canonical JSON; no secret values in config hashes/Drive. Base major 1.0, explicit minor 1.1 auxiliary capability gates. Unknown required features reject. Cue identity stays stable across text/timing edits; split/merge gets new IDs with lineage. Required translation and TTS IDs must have complete coverage. Dialogue vs sign is distinct; sign translates/displays with no invented speech. Unknown speaker/listener stays unknown. No “next speaker is listener” heuristic.

Pipeline: probe → resolve imported/embedded/OCR/ASR → normalize/review → approved memory → translate → polish → subtitle export → TTS fit; background/audio extraction branches → mix → render → full validation → propose. Baseline defaults: OCR 4 fps; bounded translation context; manual batch ≤16 cues/12000-byte request; readability target 17 CPS, hard 22; ≤2 TTS rewrites, tempo ≤1.2; no cut words or silence placeholders; 48 kHz audio, mixed target -16±1 LU, encoded true peak ≤-1 dBTP; H.264/AAC/yuv420p, faststart/libass; full decode and duration tolerance max(100 ms, 2 frames). Preserve frozen actual model/config versions in cache keys. VieNeu primary, Edge explicit fallback, separation optional with explicit original-background mode.

## 7. Editor and auxiliary flows

Editor: load head's cue_dataset_ref or latest job dataset → Room draft autosave/undo → stable cue IDs and lineage edits → three-way merge if remote head moved → immutable CueDatasetManifest/pages + new ProjectRevision → new job against new revision. Running job never mutates. Font-only edits should invalidate ASS/render; voice/text changes affect relevant TTS/mix/render; timing changes may reuse raw speech but redo fit/neighbors. RC1 proves locked display-only changes reuse raw synthesis, spoken edits synthesize only the changed cue, unchanged cue fit remains cached, probe is reused, and source extraction is bypassed.

Implemented editor execution: hash-verify frozen revision and manifest/pages/lineage/quality refs, validate project/source/duration/coverage/page bounds, then normalize directly from committed cues. Preserve cue IDs, revisions, parents, exclusions, timing, voice and locks. Source-review provenance uses the Android committed lineage confirmation; missing confirmation remains a source-review gate. Quality validation downstream remains mandatory. Production translate/polish/fit stages consume this dataset. Integration test reads the output of Kotlin Lineage/EditPatch serialization and invokes real VieNeu; it does not claim final rendered A18 or a physical phone test.

Output Library distinguishes pending primary results (VALIDATING/PUBLISH_PENDING) from accepted publications, exposes explicit ACCEPT_RESULT with byte verification, and restores accepted state after Room close/reopen. Aux jobs do not block primary submit. Aux results and fallback FINAL acceptance stream bytes and verify size/SHA256, even when metadata falsely claims the original hash.

Auxiliary: schema 1.1 `AuxJobRequest`, `required_features` for PREVIEW/AUDITION/WAVEFORM; CREATE_JOB `extensions.aux_operation` → START_ATTEMPT → worker ACK → `aux-result.json` → RESULT_PROPOSED → ACCEPT_RESULT. Separate output contract, never a FINAL. PREVIEW checks accepted base source/master/ASS + exact revision; mismatch yields PREVIEW_NEEDS_RUN. AUDITION uses worker-produced fitted/raw clips and actual voice metadata. WAVEFORM generates 100/10/1 Hz tiles of 60 s. Android overlay is approximate; libass worker preview is authoritative. Outputs from old revisions remain visibly labelled. Large source fallback has 2 GiB cache/free-space limits.

## 8. Worker startup and Colab workflow

Production prerequisites: exact locks (uv 0.13.0, Python 3.11.17, worker/uv.lock), pinned FFmpeg, optional runtime/model manifests, working ADC OAuth. Credentials only in runtime secret storage; never paste tokens in chat or commit them.

```bash
python -m pip install uv==0.13.0
make bootstrap
make sync-separation tts-env fetch-tts-model
# sync-separation retains OCR/ASR/TTS extras; weights for optional ASR/separation
# must be fetched separately only if the configured job requires them.
make doctor
```

Before direct worker execution (Makefile exports do not persist into your shell):

```bash
export ARO_REPO_ROOT=/absolute/path/to/aro
export ARO_FFMPEG="$ARO_REPO_ROOT/.cache/aro/ffmpeg/bin/ffmpeg"
export ARO_FFPROBE="$ARO_REPO_ROOT/.cache/aro/ffmpeg/bin/ffprobe"
export ARO_MODEL_CACHE="$ARO_REPO_ROOT/.cache/aro/models"
export ARO_TTS_PYTHON="$ARO_REPO_ROOT/.cache/aro/tts-venv/bin/python"
export ARO_PROFILES_DIR="$ARO_REPO_ROOT/profiles/genres"
cd "$ARO_REPO_ROOT/worker"
uv run --frozen aro worker run --workspace-id "$WORKSPACE_ID" \
  --root-id "$ROOT_DRIVE_ID" --state-dir "$WORKER_STATE_DIR" --poll-s 10
```

Set the three uppercase identity/state variables to the **verified live** workspace and a new worker state directory. Do not substitute LocalStore IDs for real Drive IDs. Start worker, discover its published session, then assign from the sole controller: `aro job assign --job JOB --session SESSION` with the controller's existing home/backend options.

Colab: open `notebooks/ARO_Colab.ipynb` from audited HEAD; authenticate interactively; use the audit bundle + full HEAD; bootstrap exact runtime; install required extras/models above before doctor/start; supply real ROOT_DRIVE_ID and WORKSPACE_ID; run doctor then startup. Current notebook fix passes both IDs and pinned paths. Core doctor success does not establish GPU/model/Drive readiness: run model probes and A03 live smoke. Notebook has no business pipeline logic. A lost Colab session gets a new worker session/attempt assignment, reuses verified remote checkpoints, and must not resume ownership via stale heartbeat.

Current execution host: uv0.13.0 installed in /workspace/aro-tools/bin; worker .venv Python3.11.17 synced frozen with OCR/ASR/TTS/separation extras. Pinned FFmpeg, isolated hash-locked VieNeu3.8.3 environment and both CPU ONNX model manifests verified. Regex/pytest available, integration tests run. No configured ADC/OAuth secrets or GPU; CPU ONNX lane does not require GPU. Network access works via approved scoped escalation; no WiFi action needed.

## 9. A18 exact state and manual Gemini workflow

A18 uses real owner-provided source, private processing only:

- Source Drive ID `1hAsKFbcoFmoPrWMAMny8lInwu7gE5niO`, 253616188 bytes, SHA `44ffec5a1e5e0ea43c69f80e230a29d7f84b931977950bd69b2c59bffd354067`.
- Segment 00:30–08:30 (8 minutes), MKV, SHA `f20c886b61904d720284ee306a0a3c9f2109355aa211891496638180e5944790`, 271247610 bytes, 14400 frames.
- Workspace `336c0e55-ca62-449d-854f-16b4d61148a4`; project `aade4e27-a128-4040-a4af-9568adc289ac`; frozen revision `78cffb05-c9ac-4512-b527-ff7c6c9f95a3`.
- Job **`0b7231fa-f54c-4e9b-9b5c-b1210c5e4911`**; attempt `6c3d72bf-0ddf-4406-b498-81f8298270c3`; generation4; assignment_seq23, imported responses seq24–36.
- Status: WAITING_USER / TRANSLATION_REVIEW. Worker stopped. Upstream stages reused verified cache; translate consumed all13 responses; polish waits for 11 new batches /23 cues.
- LocalStore root `goldendonghua001root00000`; workspace folder ID **`Lg4oCy7NKt1E_GDxOuyFj30YEkmEOsewq` is LOCAL, not Google Drive**.
- Current runtime directory `/workspace/aro/.cache/golden/donghua-001/run3`; historical run4 identity preserved.
- Source base SHA `f45e218bd699eb4aad21adacb00b0e53de618317d11d5c82b9e8c611a3b91c95`; 398 OCR rows before review, 194 retained = 174 dialogue +20 signs. Source accepted under owner/QA basis, not independent bilingual oracle.

**Updated 2026-10-16 cp12:** all 13 existing responses pass the full production validator and were imported and consumed. Translate succeeded for 194 cues; polish waits at TRANSLATION_REVIEW for 23 cues in 11 NEW POLISH requests. Never request the original13 again. Full Golden G-STRUCT/G-MEMORY still need final validation; response preflight is not final acceptance. Pinned dependencies, FFmpeg and VieNeu CPU ONNX models are installed. No real TTS/final render yet. See artifacts/RECOVERY/REPORT.md.

Manual workflow for further POLISH/DUB_REWRITE or rejected batches: export production request JSON/txt; owner copies PROMPT block to a new Gemini conversation; save JSON verbatim; do not edit IDs/hash; one optional JSON fence allowed; validate locally, immutable import/IMPORT_RESPONSE, worker validates/ACKs/checkpoints, then resume. Stale hash, duplicate/missing cues, extra fields/prose or empty translation reject. No agent-generated substitute labelled Gemini.

## 10. Exact resume procedure (cp12 supersedes old cp10 procedure)

Current local repo /workspace/aro; do not rerun recovery over it. Use the latest RC1 code bundle with the unchanged verified cp12 runtime archive; code and runtime are separate recovery artifacts. Worker7 stopped cleanly at manual gate. Historical fallback code bundle /workspace/recovery/ARO_CP12.bundle, SHA256 bb5e38b1b860cb7a171986d6e590eebba3df9a333279ecea2dce23991d0b5683; runtime /workspace/recovery/cp12/run-state.tar.gz and run-state-manifest.json, SHA256SUMS. Bundle includes full history. cp12 Drive folder 1NdfnTkGwVo4uOe2KQ8l_IVG3cYYZeN0u now contains verified bundle, runtime parts00–04, manifest, hashes and POLISH requests. Owner explicitly authorized all code/history/runtime backup on 2026-10-17; prior upload approval block is resolved. See verified ID/hash table below.

Runtime archive SHA256 5e45c53fea64ad0fda47ae10ba15e2ae0926050af3f4447bceec802385085fdd; manifest SHA256 1b6dff7790a67c072f5763cf269bdf0be6a5e322f7bde2a5c98402fc2be5d62e. All3335 archived file contents verified including deduplicated tar hardlinks. Includes full LocalStore blobs/source, controller outbox and worker7 journals; excludes scratch/model/dependency caches. Original cp10 remains unchanged.

1. On this machine use existing repo and run3. On a new machine clone the latest RC1 bundle into /workspace/aro; verify its recorded HEAD. ARO_CP12.bundle is the historical f04eafa fallback, not the RC1 code. Verify cp12 SHA256SUMS, then extract archive using Python tarfile filter='data' into EMPTY /workspace/aro/.cache/golden/donghua-001/run3. Verify each file SHA/size against run-state-manifest.json before starting. Never overlay a different active run. Preserve original source/checkpoints. Install exact pins/extras and real runtime models as §8. LocalStore L-prefixed IDs are NOT live Drive IDs.
2. Owner runs only numbered polish-request-01.txt through11.txt in /workspace/recovery/ARO_POLISH_11_REQUESTS.zip, one complete request per Gemini prompt; saves JSON replies polish-response-NN.json. Original batch/hash/cue IDs must remain unchanged. Original13 translations are already in repo and accepted; do not ask for them again.
3. Set environment from repo root:

```bash
G=/workspace/aro/.cache/golden/donghua-001/run3
J=0b7231fa-f54c-4e9b-9b5c-b1210c5e4911
C=(--backend local --local-dir "$G/drive" --home "$G/ctl")
export ARO_FFMPEG=/workspace/aro/.cache/aro/ffmpeg/bin/ffmpeg
export ARO_FFPROBE=/workspace/aro/.cache/aro/ffmpeg/bin/ffprobe
export ARO_MODEL_CACHE=/workspace/aro/.cache/aro/models
export ARO_TTS_PYTHON=/workspace/aro/.cache/aro/tts-venv/bin/python
export ARO_PROFILES_DIR=/workspace/aro/profiles/genres
export ARO_TTS_CACHE="$G/tts-cache"
worker/.venv/bin/aro job status --job "$J" "${C[@]}"
worker/.venv/bin/aro worker run --workspace-id 336c0e55-ca62-449d-854f-16b4d61148a4 --root-id Lg4oCy7NKt1E_GDxOuyFj30YEkmEOsewq --backend local --local-dir "$G/drive" --state-dir "$G/w8" --poll-s 5
```

Use next unused state dir. In a second shell with same G/J/C, get new session from hello, run `worker/.venv/bin/aro job assign --job "$J" --session NEW_SESSION "${C[@]}"`. Never reuse dead session UUID. A new attempt may first return original TRANSLATION_HANDOFF because inputs require current-attempt ACK. In that case reimport EXISTING artifacts/FINAL_AUDIT/responses/response-*.json locally; controller fix emits REBOUND_TO_CURRENT_ATTEMPT without new uploads or owner work. Wait for worker to consume all13 and reproduce identical POLISH request hashes. Then validate/import each new polish JSON via `aro handoff validate` / `aro handoff import --job "$J" --file FILE "${C[@]}"`. Do not bypass failed validation. Observe actual status/ACKs.

4. Continue real VieNeu/fit/mix/render FINAL.mp4 and quality gates. Any new DUB_REWRITE gate must be fulfilled by real manual response. Do not rerun OCR/source QA absent material error. All original upstream cache keys hit on fresh worker7.
5. After ≥1 translation batch and ≥5 real TTS checkpoints, prove kill/new-session resume and stale publication refusal for G-RESUME/G-FENCE; recovery itself is not this proof.
6. Independent editor/A24 implementation and test RC are completed as recorded in RC1 evidence while waiting for POLISH. After the replies arrive: complete A18 → real live Drive/Android end-to-end → fix actual integration failures → rerun complete regressions → build final RC at final HEAD → G1/handoff. Keep A03 PENDING_LIVE until genuine runtime OAuth is available. 44c5c77 was containment only; RC1 replaces it with tested worker consumption. Do not work on optional A25.
7. A03 real smoke root 1goyNlLLXREoQV3kFFX15V2tRE9_fJpz6: `aro storage smoke --root-id ID --report FILE`, actual ADC credentials and Android exact-ID cross-client visibility. Connector upload and LocalStore runs are not A03 proof.
8. Obtain owner final Vietnamese/audio/video review; generate tests/golden/report.py using real final-validation and acceptance evidence. Never promote missing mandatory gates or debug APK to production PASS.

## 11. Validation evidence and exact commands

Current implementation commit: e87c2cb2977018c98a3fe516ae369fefb9ff71e8. RC1 evidence lives under artifacts/RC1; evidence.json records complete final suite results, exit codes and limitations. Original audit evidence under artifacts/FINAL_AUDIT and recovery evidence under artifacts/RECOVERY remain historical records, not overwritten acceptance.

- Real Kotlin editor fixture → production worker → real VieNeu:3/3 tests passed in27.94s. Actual subtitle text and synthesis request hashes checked. Wrong-source/corrupted-page paths rejected. Minimal synthesis/fit invalidation asserted. No physical Android/live Drive/Golden implication.
- Full Android test suite, lint and debug build: see android-final.log and regression summary. Old full run had109 tests; RC1 has111 tests including export/accept regressions. All unit-test tasks forced to execute via rerun-tests.gradle.
- Full worker suite: see worker-final.log, including all collected unit/integration/media tests and explicit skip reasons. Optional external lanes are NOT_RUN, not PASS.
- make lock-check lint: exact uv lock check, Ruff check/format and mypy110 source files succeeded. Strict Gradle dependency checks remain enabled, missing checksum entries independently verified against official metadata.
- Golden report selftest succeeded on synthetic test inputs; it does not mean A18 Golden passed.
- The /tmp-exhausted regression attempts failed due to the separate4.9GiB temporary partition. Logs preserved; generated test scratch removed and full suites retried with workspace TMPDIR. Golden cp12 runtime untouched.

Commands from repo root (after prerequisites in §8):

```bash
export ARO_FFMPEG="$PWD/.cache/aro/ffmpeg/bin/ffmpeg"
export ARO_FFPROBE="$PWD/.cache/aro/ffmpeg/bin/ffprobe"
export ARO_MODEL_CACHE="$PWD/.cache/aro/models"
export ARO_TTS_PYTHON="$PWD/.cache/aro/tts-venv/bin/python"
mkdir -p "$PWD/.cache/test-tmp"
export TMPDIR="$PWD/.cache/test-tmp"
worker/.venv/bin/pytest worker/tests -q -ra
make lock-check lint UV=/workspace/aro-tools/bin/uv
PYTHONPATH=worker/src worker/.venv/bin/python tests/golden/selftest/report_selftest.py
# JAVA_HOME/ANDROID_HOME/GRADLE_USER_HOME: provisioned JDK17, SDK36, Gradle cache
android/gradlew -p android -I "$PWD/artifacts/RC1/rerun-tests.gradle" \
  testDebugUnitTest lintDebug assembleDebug --no-daemon --console=plain
ARO_EDITOR_REAL_TTS=1 \
ARO_ANDROID_CUES_FILE="$PWD/android/core/sync/build/editor-worker/cues.jsonl" \
  worker/.venv/bin/pytest worker/tests/integration/test_editor_worker.py -q
```

On this managed host use JAVA_HOME=/workspace/android-toolchain/jdk, ANDROID_HOME=/workspace/android-toolchain/sdk, GRADLE_USER_HOME=/workspace/gradle-home and JAVA_TOOL_OPTIONS with the configured proxy: `-Dhttps.proxyHost=proxy -Dhttps.proxyPort=8080 -Dhttp.proxyHost=proxy -Dhttp.proxyPort=8080`. Managed CA was imported into this JDK truststore; TLS verification retained. See artifacts/RC1/COMMANDS.md. These proxy settings are host-specific, not an Android product requirement.

Golden/G1 **BLOCKED**. G-SOURCE/G-MEANING owner amendment conditions still require final review; G-STRUCT/G-MEMORY require final validation after POLISH; G-READ/TTS/FIT/AUDIO/VIDEO lack final A18 run evidence; G-DRIVE lacks live cross-client proof; G-RESUME/FENCE require the progressed Golden restart proof; G-PUBLISH requires accepted FINAL. No real A18 FINAL.mp4 yet. Unit tests and real short TTS fixture do not replace those gates.

## 12. Release and owner actions

New RC target: studio.aro versionCode25, versionName0.25.0-rc1-debug. See latest RC release table for audited HEAD, APK/hash/Drive ID, bundle and readback results. It is a TEST RC for Galaxy A51, not production PASS. Production status: NOT_RELEASED; A28 production packaging/signing and final acceptance are not implied.

Historical APK: aro-A25-0.24.0-pre-g1-debug.apk, Drive1VzqU1DTGzwOAnAHW34hSYzKTFm-CU3Mu,17565351bytes, SHA25646e27aa65eb27aa27e355bc1cbe87e4d0bc4241abc3c8916e4e2581763ec2cd5. Bytes and old signing certificate independently verified in RC1. Keep historical evidence.

Exact external owner actions:

1. Produce only11 NEW POLISH replies: download ARO_POLISH_11_REQUESTS.zip (Drive1mk8GmIO0tcJUJMR24pd-oQIaU_gc3AGK), send numbered request01–11 to Gemini, save verbatim JSON as polish-response-01.json…11.json, place them in responses folder1ZvoFLuMZmphEm9niDB8njcahI04PfXqO. Do not repeat original13. Developer then validates/imports/resumes per §10.
2. A03/live worker needs runtime OAuth: in the Colab notebook run the interactive authentication cell with the intended Drive account, or run gcloud auth application-default login on the worker host. Sharing the Drive folder and connector login do not provide worker ADC. Do not send tokens/credentials in chat. Then run the exact A03 smoke command in §10 and the cross-client case.
3. Install/test RC on a separate empty Android profile/device (signing constraint below), authenticate app, and later review actual final Vietnamese subtitles/audio/video. See artifacts/RC1/GALAXY_A51.md for the full device evidence checklist. Current production signing/owner approval not established.

No further backup permission needed: owner explicitly authorized complete source/Git/runtime/log/handoff backup. Preserve verified cp12 while adding RC1. Do not work on A25. Continue final A18/live/E2E → full regression → final RC when external inputs arrive; do not redesign or remove capabilities.

## Verified Drive backup — 2026-10-17

Folder: https://drive.google.com/drive/folders/1NdfnTkGwVo4uOe2KQ8l_IVG3cYYZeN0u . All ten payload files below downloaded again and SHA256 matched. Full concatenated runtime SHA256 also matched. Manifest includes3335 files; archive hash verification preserves prior per-file checks. Git bundle includes all1223 stored blobs and complete refs/history through f04eafa. Logs/evidence included in Git artifacts/RECOVERY and runtime journals. No known secret-format or populated credential-field matches in1223 Git blobs/1861 regular tar entries; model/dependency caches and runtime credentials are not included. Temporary signed download URLs are outside the backup. This backup verification is NOT A03 live worker/Android Drive or Golden/G1 acceptance.

| File | Drive ID | SHA256 |
|---|---|---|
| ARO_CP12.bundle | 16_TcD805QJ_g9MoH-B8Vfca1JGFfEXia | bb5e38b1b860cb7a171986d6e590eebba3df9a333279ecea2dce23991d0b5683 |
| ARO_POLISH_11_REQUESTS.zip | 1mk8GmIO0tcJUJMR24pd-oQIaU_gc3AGK | 70c59d9dfb2f7e720f673dd5493e35e759165316465c88152edad5ed29c90f98 |
| run-state.tar.gz.part00 | 1hBBxS2DnxCJsGkKMtniNdHlB1KKytkjI | 9cb793e0fe7332160894ee190ab9261a7f3d1c4511c93b80448b870a2a877e0a |
| run-state.tar.gz.part01 | 10nExfNUtGs1rWf-B_ob9b_IrM73z4ipt | d3410482fb97bcbe6a149ed38604d464a2ec5ea9a2559e0aa153ee751f8d5c9a |
| run-state.tar.gz.part02 | 1SSU9m163Yscayark6cCGuhEjLkacI3X3 | bdbbeaa5a1357ac602abcb05f6afe07bdfcab9d8d8b10e6b49f804bfeedaa204 |
| run-state.tar.gz.part03 | 1mfoKQKtw3wS9rVaa29IEI7iMHrkX6Cj- | 756ee66265154b58675d17693dfd1d82735c77e4d2f40042bc3282a59a5d23a8 |
| run-state.tar.gz.part04 | 1zvcxHhExeP0czHbIfV2D2eDZobd_VpsM | 425d70e532a62c17c9bad3a372eeea46f9221e52270a4ee95a58ebf44ae88bf4 |
| run-state-manifest.json | 1zM2WPYALKXi5jz0CWsSOB0QDe3ZxNi7N | 1b6dff7790a67c072f5763cf269bdf0be6a5e322f7bde2a5c98402fc2be5d62e |
| parts.json | 14SE5bO3xHIGKWSxJIt00kFiy-mkiUC2T | 54704a70157427f1f1db07e7d2569de276dac54004f1044ebc3997b1decc5266 |
| SHA256SUMS | 1PLULaz-XpPoG8rupI70aDyCOFl1KcI6f | 9ec9249b8c165990ea711af6c5e040f41e9272552ebfc82f7c06cbbab201dbc8 |

Restore: download the five run-state.tar.gz.part00 through part04 and concatenate in numeric order: `cat run-state.tar.gz.part0[0-4] > run-state.tar.gz`. Verify parts.json and SHA256SUMS before extraction. Then follow section10 (empty target, safe extraction, per-file manifest verification, exact runtime pins, new worker assignment). Source media is contained in LocalStore blobs; do not re-OCR. Download ARO_CP12.bundle and verify its hash before clone. This handoff remains sidecar to exact code HEAD, not a self-referential commit.

## RC1 device signing constraint

The new debug APK uses SHA256 certificate 570cc106baf4827c8c8c2a376c170eda04ccd7cce866a4383c09e1c47e1c94ea; old A25 uses aa8c55ba258948834a791e9a19d115696ba9efef9c6b8fdf06c9396c00933dc4. Both signatures independently verified; they differ. In-place update will be rejected. Preserve the existing installation/data: test in a separate empty Android profile/device, or build/sign from the original signing environment. See artifacts/RC1/GALAXY_A51.md. Never back up the private signing key or OAuth secrets. Physical install/live OAuth/owner review are NOT_RUN.

## Latest RC1 release — verified 2026-10-17

HEAD: `40f93439b902bceddeaa61a6f2e0e13541d24be0`. Git worktree clean. Full worker941 passed/9 skips; Android111 passed/0 skips; lint0 errors; lock/Ruff/format/mypy success. APK built after evidence commit with unchanged tested worker/android trees. Full final-head build log and bundle/signature verification are in RC1-evidence.zip.

Folder: https://drive.google.com/drive/folders/1FGXbbXggg5Yrrnd56CcPKdID5nPySfyb
Master handoff file: https://drive.google.com/file/d/1GyEynypa6mYIPBd-M7GCGVbovkZEkaVZ/view

| File | Drive ID | SHA256 (full remote readback matched) |
|---|---|---|
| aro-0.25.0-rc1-debug.apk | 1oks5bGWYzsOoWbqhUirkDoWYqzMwFRQW | b0b6227828ace3a730729de1c11f6227141556a7c82902a257a6ae7e289978c6 |
| ARO_RC1.bundle | 1vs6RZSoSFmZgKIMOju4Huho_cCJvA3qN | 330ea41b391a222149d6eb22d8b29a945ebf25730826c13ebe9a7132b420d31c |
| RC1-evidence.zip | 1vz1p4qqGVf22PMMLDfB6kvJZd50dM7L8 | 3471c62ce6dcbc33e37a2f9741964c9b9a01e6e8bb24dadf15ac3da02e95d696 |
| HEAD.txt | 1id77_6-3E0iDanxVWX4Cn8rPjBqwExKm | 0ee89ef2cd8fc46f401c911ce3e6ffdd275164cb4df2d3aa8601659f301badd8 |

APK version0.25.0-rc1-debug/code25,17458804bytes, package studio.aro, minSdk26/targetSdk36. TEST_RC_ONLY; NOT production/G1 PASS. New and old APK signatures independently verified; in-place update is blocked by their different debug certificates (see signing constraint above).

Resume on a fresh host: download ARO_RC1.bundle and this handoff, verify their hashes using RC1 SHA256SUMS; `git clone ARO_RC1.bundle aro`; verify HEAD40f93439b902bceddeaa61a6f2e0e13541d24be0 and git bundle verify. Restore the separately verified cp12 runtime using its part hashes/manifest (§10 and backup table). Install pinned tools/models (§8), then proceed with existing original13/local response rebind and only NEW11 POLISH (§9–10). Never reinterpret LocalStore IDs as Drive IDs. Download RC1-evidence.zip for final-head build/signature evidence; reports are also committed under artifacts/RC1.

Remaining blockers: new11 manual POLISH; actual runtime OAuth/live Android→Drive→worker→FINAL→ACCEPT; final owner Vietnamese/audio/video review and mandatory Golden gates. No A18 FINAL exists yet. AUDITION reuses an accepted actual worker voice clip; fresh voice synthesis before a primary run is not implemented. PREVIEW requires a matching accepted base. These limitations remain visible, not silently declared complete.
