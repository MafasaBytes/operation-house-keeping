# Bounded decision-workflow persistent environment report

## 1. Outcome and authorization boundary

The environmental prerequisites for the already designed bounded decision workflow are complete on this WSL installation. A private persistent workspace now exists on a verified local ext4 filesystem, the exact approved dependency set is retained as hashed wheels, and an isolated CPython 3.13 environment contains only that set plus its `pip` bootstrap tool. Fresh-process verification succeeds.

This work provisions an execution environment only. It adds no production application code, changes no semantic or resource policy, and does not authorize implementation. The development checkout remains where it was. No mount, system Python, global package, authoritative fixture, ledger, or repository history was changed.

## 2. Verified checkpoint and frozen commitments

The checkout was inspected before provisioning:

- branch: `brc-exp001`;
- HEAD: `ec027add0cb2dae5434c42f67454752eb93f7228`;
- [implementation readiness report](./2026-09-15-bounded-decision-workflow-implementation-readiness-report.md): SHA-256 `3792d9ade000b83c9226d50217b4b35154e8abfc780c39d6d9c3ce797f568d93`;
- [candidate package](./2026-09-15-bounded-decision-workflow-candidate-package.json): SHA-256 `0d3b3a6f53c465dc45a3fc44b79523bc7d51131c42b342e9f4afa62795d29365`;
- [candidate manifest](./2026-09-15-bounded-decision-workflow-candidate-manifest.json): SHA-256 `6ac24d274ac5f898876a0ab28f7c250ae1413b909260e1a48eb6d3f00aa55959`;
- approved dependency lock-text commitment: `aca75138681ef473898adf84559e155c6e1a2a7968f67071103e51dce161201e`.

The lock-text commitment is the SHA-256 of the canonical JSON string encoding of the concatenated runtime and test lock text, as specified by the candidate package. It is not the digest of the raw concatenated bytes; that separate digest is `7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817`.

The lock pinned ten versions but did not pin artifact hashes. Provisioning therefore did not treat it as a hash-complete installation lock. The acquired wheel hashes were frozen separately into a derived `--require-hashes` input whose raw SHA-256 is `6bcc7bd80022ce38d984ada0b4e4d4986272befea760ae895c76a8c6f3937fcf`.

## 3. Host, interpreter, and filesystem

The resolved WSL account is `mafasa` (UID 1000) with Linux home `/home/mafasa`; no username was assumed. The distribution reports `Ubuntu`, the installed release is Ubuntu 24.04.2 LTS, and the kernel is `5.15.167.4-microsoft-standard-WSL2` on x86-64.

The selected workspace resolves to `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow`. `findmnt` identifies its backing mount as `/dev/sdc`, filesystem `ext4`, with observed options `rw,relatime,discard,errors=remount-ro,data=ordered`. Every existing component below `/home/mafasa` was checked with `lstat`/`namei`; none is a symlink. The workspace root and its private parent are owned by `mafasa:mafasa` and mode `0700`. Each role directory below is also owned by `mafasa:mafasa` and mode `0700`.

The checkout at `/mnt/d/operation-house-keeping` is on WSL `9p`/DrvFS. It remains the development checkout and was not selected for runtime inputs or retained results because it does not satisfy the accepted ext4/XFS contract. Filesystem type was determined from the actual backing mount, not inferred from path syntax or from WSL presence.

The exact interpreter is `/home/mafasa/miniconda3/bin/python3.13`, CPython 3.13.11. Its executable SHA-256 is `47f615b1be25c94e9304ccd9339f9a8ef21d2194fca32643c441fb2dad290264`, platform is `linux-x86_64`, and SOABI is `cpython-313-x86_64-linux-gnu`. The interpreter was used to create a `venv`; neither the base environment nor system Python was modified.

## 4. Persistent directory roles

| Role | Resolved path |
|---|---|
| Development checkout | `/mnt/d/operation-house-keeping` |
| Persistent workspace | `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow` |
| Runtime inputs | `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/inputs` |
| Completed result bundles | `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/results` |
| Dependency artifacts | `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/dependency-artifacts` |
| Isolated environments | `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments` |
| CPython 3.13 environment | `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001` |
| Administrative evidence | `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/provisioning` |

The selected root did not exist before this task. It was created without repurposing or overwriting data. Runtime input and result directories are currently empty. Temporary acquisition and probe material was kept in `/tmp` and removed only after its evidence was retained; no retained result was placed there.

## 5. Dependency acquisition and artifact commitments

The exact ten names and versions from the approved package were requested individually from `https://pypi.org/simple` with dependency resolution disabled, source builds forbidden, and binary wheels required. A second acquisition with pip's cache disabled produced the same filenames and SHA-256 values as the retained copies. No fallback version or sdist was accepted.

| Distribution | Retained wheel tag | SHA-256 |
|---|---|---|
| `annotated-types==0.8.0` | `py3-none-any` | `f072f4d804ea359e4eaf198b1af7a8b0943881a87f31bb764f8bf219bb9419e0` |
| `iniconfig==2.3.0` | `py3-none-any` | `f631c04d2c48c52b84d0d0549c99ff3859c98df65b3101406327ecc7d53fbf12` |
| `packaging==26.3` | `py3-none-any` | `d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c` |
| `pluggy==1.6.0` | `py3-none-any` | `e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746` |
| `pydantic==2.13.4` | `py3-none-any` | `45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba` |
| `pydantic-core==2.46.4` | `cp313-cp313-manylinux_2_17_x86_64`, `cp313-cp313-manylinux2014_x86_64` | `9551187363ffc0de2a00b2e47c25aeaeb1020b69b668762966df15fc5659dd5a` |
| `Pygments==2.20.0` | `py3-none-any` | `81a9e26dd42fd28a23a2d169d86d7ac03b46e2f8b59ed4698fb4785f946d0176` |
| `pytest==9.1.1` | `py3-none-any` | `37a86b45efb9a47a61a36449063e8e18d0cab3161329fc099eb21783169c4f0c` |
| `typing-extensions==4.16.0` | `py3-none-any` | `481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8` |
| `typing-inspection==0.4.2` | `py3-none-any` | `4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7` |

The canonical ten-row artifact-set commitment is `26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1`. The retained artifact manifest SHA-256 is `17eb5aa4013994732909e1dae9b16263e2c4d9261d4f1b9d890cf3935aed17ad`. It records filenames, byte sizes, declared distribution names and versions, wheel tags, acquisition source, and individual hashes. The retained wheels occupy approximately 4.3 MiB.

These commitments show which bytes were acquired and installed. Neither the original lock-text commitment nor the wheel hashes prove the trustworthiness of PyPI, the publisher, the certificate-authority chain, or the package contents.

## 6. Isolated installation identity

The environment was populated from the retained directory only, using the equivalent of:

```text
pip install --no-index --find-links <dependency-artifacts> --require-hashes --no-deps --only-binary=:all: -r <requirements-hashed.txt>
```

It has `include-system-site-packages = false`. A distribution inventory found exactly the ten approved application/test dependencies and no additional distribution; `pip==25.3` is present solely as the `venv` bootstrap/install tool. `pip check` reported no broken requirements, and focused imports of all ten distributions succeeded. The verifier also hashes every installed file listed by each distribution and compares its installed-tree commitment.

The environment identity commitment is `693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`; its manifest SHA-256 is `da87127a571195b4129e6fefd393da39d57819667ecba4f1f8a37d5f1984bc34`. This identifies the interpreter, platform, retained artifact set, hashed install input, bootstrap tool, exact versions, and installed trees. It does not authenticate the executable merely by naming it. The environment occupies approximately 37 MiB.

## 7. Persistence, collision, and completeness checks

A clearly labelled 217-byte probe was created in `provisioning` with exclusive creation, flushed and `fsync`ed, and all handles were closed. A fresh process then read identical bytes with SHA-256 `f369e1b85d873829f7e789ebe8ca778691fadfc088c12f14ae1764bf89893364`. A second exclusive create returned `EEXIST` and did not change the probe.

Disposable bundle probes established the intended ordinary-process protocol:

- an existing bundle directory caused an `EEXIST` collision rather than replacement;
- a directory without its manifest was classified `incomplete_bundle`;
- a staged bundle remained incomplete before manifest rename;
- after manifest-last publication, a fresh process classified and verified it as complete;
- disposable bundle bytes were removed after the evidence record was retained.

Manifest-last publication defines application-level completeness. It does not make the directory appear atomically as a whole, promise that all earlier files survive a power failure, or establish crash durability. These checks demonstrate cross-process persistence and ordinary interruption behavior only. The WSL distribution was not restarted and no power-loss test was performed. This workspace is not a backup.

The retained persistence evidence SHA-256 is `85c747ad3b9bb5787e1ed979c095e8a2bfe783df6651509b03dedecb1ccc9e0f`. The canonical provisioning record SHA-256 is `d8935b94c2339ba2921e7b21ef48ebe147332d96295f7a9ae534257be739a16d`; the restart checksum inventory SHA-256 is `6968e78dfe7e7f7702f7ecca404e996be4cff19cd8d18dd569ce748167ba3515`.

## 8. Exact run-environment and later restart checks

After separately authorized implementation, invoke the maintained module from the unchanged checkout with the isolated interpreter, using request/snapshot files under `inputs` and new result directories under `results`:

```text
cd /mnt/d/operation-house-keeping
/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python -m applications.bounded_decision_workflow evaluate --request /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/inputs/REQUEST.json --snapshot /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/inputs/SNAPSHOT.json --output-dir /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/results/NEW-UNIQUE-BUNDLE
```

That command is an invocation contract, not a current executable finding: production implementation remains gated and the module was not created or run here.

After a later owner-performed WSL-session restart, the exact retained-environment check is:

```text
cd /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow
sha256sum --check provisioning/restart-checks.sha256
environments/cp313-bdw001/bin/python provisioning/verify-provisioning.py
```

The second command independently checks the ext4 filesystem, no-symlink root, interpreter identity, original lock commitment, hashed install input, complete wheel set and hashes, installed versions and trees, environment identity, and persistent probe. Its current fresh-process result is `status=verified` with all ten artifacts present.

## 9. Remaining decisions and limitations

No environmental blocker remains for implementing the approved application on this machine and in these paths. Production implementation, command-level acceptance, final runtime measurements against the approved build-owned limits, and release acceptance remain separate owner gates. The prepared environment does not authorize the application to alter its frozen observed-value admission, numerical, decision, path, retention, diagnostic, or resource policies.

Future execution must still use unique output directories, enforce the designed path and resource boundaries before expensive work, and keep user inputs/results on this verified ext4 workspace. If the interpreter, wheel set, filesystem, or retained manifests change, the environment identity and provisioning checks must be regenerated and reviewed rather than silently accepted. A later WSL restart check is documented above; it is not a prerequisite already claimed as performed.

END OF BOUNDED DECISION WORKFLOW PERSISTENT ENVIRONMENT REPORT
