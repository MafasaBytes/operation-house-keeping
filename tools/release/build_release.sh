#!/bin/bash
# Build one offline L2 release on a reference Ubuntu Server 24.04 amd64 build host (build host only).
#
# Design: docs/superpowers/reports/2026-10-22-t1-linux-ext4-l2-packaging-fresh-install-PROPOSAL.md
# (74a39d87...) sections 3 and 4.4, as amended by the scope addendum (6bca403b...) sections 2 and 5.4.
#
# Every external input is an explicit argument with an explicit expected SHA-256 supplied by the
# operator; nothing is downloaded, guessed or substituted, and a version label is never taken as
# identity. Argument and input-digest checks run before anything is created; the source-set,
# tooling and lock checks then run on the committed export. Git runs here only, for the source
# export and the L1 release-identity record. Bit-for-bit reproducibility is NOT claimed. The
# printed manifest digest is package integrity relative to whichever channel later delivers it;
# it is not a signature (ID-2 open) and not provenance (D-P open).
#
# usage: build_release.sh --repository REPO --commit C --release-root R_REL
#          --cpython-tarball Python-3.13.11.tar.xz --cpython-sha256 H
#          --pip-zipapp pip.pyz --pip-zipapp-sha256 H
#          --wheelhouse DIR --requirements-hashed FILE --requirements-hashed-sha256 H
#          --expected-source-set D_dev --out NEW_DIR
set -euo pipefail
umask 022
export LC_ALL=C TZ=UTC

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
KNOWN="repository commit release-root cpython-tarball cpython-sha256 pip-zipapp pip-zipapp-sha256 wheelhouse
requirements-hashed requirements-hashed-sha256 expected-source-set out"
PYTHON_VERSION=3.13.11
TOOLS="git tar xz sha256sum make gcc ldd readelf find grep awk sed cut cmp sort stat python3 nproc dpkg-query"

refuse() { printf 'build_release: REFUSED %s\n' "$*" >&2; exit 1; }
usage() { printf 'build_release: usage: see the header of %s\n' "$0" >&2; exit 2; }
note() { printf 'build_release: %s\n' "$*" >&2; }
sha() { sha256sum -- "$1" | cut -c1-64; }

declare -A A=()
while [ $# -gt 0 ]; do
  case "$1" in --?*) name=${1#--} ;; *) usage ;; esac
  [ $# -ge 2 ] && [ -n "$2" ] || usage
  case " $(echo $KNOWN) " in *" $name "*) ;; *) usage ;; esac
  [ -z "${A[$name]+set}" ] || usage
  A[$name]=$2
  shift 2
done
for name in $KNOWN; do [ -n "${A[$name]+set}" ] || usage; done

REPO=${A[repository]} C=${A[commit]} R_REL=${A[release-root]} OUT=${A[out]}
P=${A[cpython-tarball]} Z=${A[pip-zipapp]} W=${A[wheelhouse]} F=${A[requirements-hashed]}
D_DEV=${A[expected-source-set]}

# ------------------------------------------------------------ 1. argument shape
hex() { [[ $1 =~ ^[0-9a-f]{$2}$ ]]; }
path_ok() {   # absolute, normalized, the R_REL character set (the wrapper's quoted -c string relies on it)
  [[ $1 =~ ^/[A-Za-z0-9/._-]+$ ]] && [[ $1 != *//* && $1 != */./* && $1 != */../* && $1 != */. && $1 != */.. && $1 != */ ]]
}
hex "$C" 40 || refuse COMMIT_INVALID
for name in cpython-sha256 pip-zipapp-sha256 requirements-hashed-sha256 expected-source-set; do
  hex "${A[$name]}" 64 || refuse "DIGEST_ARGUMENT_INVALID --$name"
done
path_ok "$R_REL" || refuse RELEASE_ROOT_INVALID
path_ok "$OUT" || refuse OUT_INVALID
case "$OUT/" in /home/*|/mnt/*) refuse "OUT_UNDER_PERSONAL_PATH (build paths are embedded in the interpreter build)" ;; esac
case "$R_REL/" in /home/*|/mnt/*) refuse RELEASE_ROOT_UNDER_PERSONAL_PATH ;; esac
[ "$(uname -s)" = Linux ] && [ "$(uname -m)" = x86_64 ] || refuse PLATFORM_UNSUPPORTED

# --------------------------------------------- 2. explicit inputs, verified before any work
regular() { [ -f "$1" ] && [ ! -L "$1" ]; }
regular "$P" || refuse "INPUT_MISSING cpython-tarball"
regular "$Z" || refuse "INPUT_MISSING pip-zipapp"
regular "$F" || refuse "INPUT_MISSING requirements-hashed"
[ -d "$W" ] && [ ! -L "$W" ] || refuse "INPUT_MISSING wheelhouse"
[ "$(sha "$P")" = "${A[cpython-sha256]}" ] || refuse CPYTHON_DIGEST_MISMATCH
[ "$(sha "$Z")" = "${A[pip-zipapp-sha256]}" ] || refuse PIP_ZIPAPP_DIGEST_MISMATCH
[ "$(sha "$F")" = "${A[requirements-hashed-sha256]}" ] || refuse REQUIREMENTS_DIGEST_MISMATCH
wheels=0
for wheel in "$W"/* "$W"/.[!.]*; do
  [ -e "$wheel" ] || [ -L "$wheel" ] || continue
  case "$wheel" in *.whl) ;; *) refuse "WHEELHOUSE_UNEXPECTED_ENTRY $(basename "$wheel")" ;; esac
  regular "$wheel" || refuse "WHEELHOUSE_UNEXPECTED_ENTRY $(basename "$wheel")"
  wheels=$((wheels + 1))
done
[ "$wheels" -gt 0 ] || refuse WHEELHOUSE_EMPTY
for tool in $TOOLS; do command -v "$tool" >/dev/null 2>&1 || refuse "TOOL_MISSING $tool"; done
[ -d "$REPO" ] || refuse "INPUT_MISSING repository"
[ "$(git -C "$REPO" rev-parse --verify "$C^{commit}")" = "$C" ] || refuse COMMIT_ABSENT
[ ! -e "$R_REL" ] && [ ! -L "$R_REL" ] || refuse RELEASE_ROOT_EXISTS
[ ! -e "$OUT" ] && [ ! -L "$OUT" ] || refuse OUT_EXISTS
[ -d "$(dirname "$R_REL")" ] && [ -d "$(dirname "$OUT")" ] || refuse PARENT_MISSING
walked=
for part in ${R_REL//\// }; do
  walked=$walked/$part
  [ ! -L "$walked" ] || refuse "RELEASE_ROOT_SYMLINK_COMPONENT $walked"
done

# ------------------------------------------------------------ 3. committed source export
mkdir "$OUT"
WORK=$OUT/work
mkdir "$WORK" "$WORK/export" "$WORK/cpython" "$WORK/home"
note "exporting $C"
# tar.umask=022: Git's default 0002 would give group-writable entries, which the manifest refuses.
git -C "$REPO" -c tar.umask=022 archive --format=tar "$C" applications backend tools/release > "$WORK/source.tar"
tar -C "$WORK/export" -xf "$WORK/source.tar"
D=$(python3 -I -B "$SCRIPT_DIR/release_manifest.py" source-set --root "$WORK/export" | sed -n 's/.*"sha256": "\([0-9a-f]\{64\}\)".*/\1/p')
hex "$D" 64 || refuse SOURCE_SET_UNCOMPUTED
[ "$D" = "$D_DEV" ] || refuse "SOURCE_SET_MISMATCH export=$D expected=$D_DEV"   # check (i)
# The tooling that runs now must be the committed tooling.
( cd "$WORK/export/tools/release" && find . -type f | sort ) > "$WORK/tools-committed.txt"
( cd "$SCRIPT_DIR" && find . -type f -not -path '*/__pycache__/*' | sort ) > "$WORK/tools-running.txt"
cmp -s "$WORK/tools-committed.txt" "$WORK/tools-running.txt" || refuse TOOLS_DIFFER_FROM_COMMIT
while read -r name; do
  [ "$(sha "$WORK/export/tools/release/$name")" = "$(sha "$SCRIPT_DIR/$name")" ] || refuse "TOOLS_DIFFER_FROM_COMMIT $name"
done < "$WORK/tools-committed.txt"
LOCK=$WORK/export/applications/bounded_decision_workflow/requirements.lock
regular "$LOCK" || refuse LOCK_MISSING

# ------------------------------------------------------- 4. interpreter for prefix R_REL/python
SOURCE_DATE_EPOCH=$(stat -c %Y "$P")
export SOURCE_DATE_EPOCH
tar -C "$WORK/cpython" -xf "$P"
SRC=$WORK/cpython/Python-$PYTHON_VERSION
[ -x "$SRC/configure" ] || refuse CPYTHON_SOURCE_LAYOUT
dpkg-query -W > "$OUT/build-host-packages.txt"
mkdir "$R_REL"
note "building CPython $PYTHON_VERSION for $R_REL/python (no PGO/LTO)"
# --disable-test-modules: the optional CPython test package is neither built nor installed.
( cd "$SRC" && ./configure --prefix="$R_REL/python" --enable-shared --with-ensurepip=no \
    --without-static-libpython --disable-test-modules LDFLAGS="-Wl,-rpath,$R_REL/python/lib" ) \
    > "$OUT/configure.log" 2>&1
make -C "$SRC" -j"$(nproc)" > "$OUT/make.log" 2>&1
make -C "$SRC" install > "$OUT/make-install.log" 2>&1
PY=$R_REL/python/bin/python3.13
SITE=$R_REL/python/lib/python3.13/site-packages
[ -x "$PY" ] && [ ! -L "$PY" ] || refuse INTERPRETER_MISSING
[ "$("$PY" -I -B -c 'import sys; print(sys.version.split()[0])')" = "$PYTHON_VERSION" ] || refuse INTERPRETER_VERSION

# ----------------------------------------------- 5. locked wheels, by hash, offline, no bytecode
# pip runs as a build-only zipapp and is never installed into the prefix, so no residue removal
# is needed and no RECORD-listed file is ever deleted.
# PIP_CONFIG_FILE=/dev/null makes pip skip every configuration file (global, site and user);
# --isolated additionally ignores PIP_* environment options.
PIP_CONFIG_FILE=/dev/null HOME=$WORK/home "$PY" -I -B "$Z" install --isolated --no-index --find-links "$W" --require-hashes \
  --only-binary=:all: --no-compile --no-cache-dir --disable-pip-version-check -r "$F" > "$OUT/pip.log" 2>&1
"$PY" -I -B - "$LOCK" <<'EOF' || refuse DISTRIBUTION_SET_DIFFERS_FROM_LOCK
import importlib.metadata as metadata, re, sys
norm = lambda name: re.sub(r'[-_.]+', '-', name).lower()
lock = {norm(n): v for n, v in (line.split('==') for line in open(sys.argv[1]).read().split())}
found = {norm(d.metadata['Name']): d.version for d in metadata.distributions()}
if found != lock:
    print('differs:', sorted(set(found.items()) ^ set(lock.items())), file=sys.stderr)
    sys.exit(1)
EOF
[ -z "$(find "$SITE" -name direct_url.json)" ] || refuse DIRECT_URL_PRESENT
[ -z "$(find "$SITE" -name __pycache__)" ] || refuse SITE_PACKAGES_BYTECODE

# --------------------------------------------- 6. committed application tree and L1 identity
mkdir "$R_REL/app"
cp -a "$WORK/export/applications" "$WORK/export/backend" "$R_REL/app/"
"$PY" -I -B "$WORK/export/tools/release/release_identity_record.py" "$REPO" "$C" "$R_REL/app" \
  "$R_REL/app/RELEASE-IDENTITY.json"
APP_SET=$(python3 -I -B "$SCRIPT_DIR/release_manifest.py" source-set --root "$R_REL/app" | sed -n 's/.*"sha256": "\([0-9a-f]\{64\}\)".*/\1/p')
[ "$APP_SET" = "$D" ] || refuse APP_TREE_DIFFERS_FROM_EXPORT   # check (iii)

# ------------------------------------------------------------- 7. fixed-form wrappers
mkdir "$R_REL/bin"
set -C
cat > "$R_REL/bin/ohk-bdw-check" <<EOF
#!/bin/sh
exec $R_REL/python/bin/python3.13 -I -B -c 'import sys; sys.path.insert(0, "$R_REL/app"); from applications.bounded_decision_workflow.release_check import main; raise SystemExit(main())' "\$@"
EOF
cat > "$R_REL/bin/ohk-bdw-run" <<EOF
#!/bin/sh
exec $R_REL/python/bin/python3.13 -I -B -c 'import sys; sys.path.insert(0, "$R_REL/app"); from applications.bounded_decision_workflow.release_check import workflow_main; raise SystemExit(workflow_main())' "\$@"
EOF
set +C
chmod 0755 "$R_REL/bin/ohk-bdw-check" "$R_REL/bin/ohk-bdw-run"

# ------------------------------------------------------------- 8. native requirements
# Evidence for the dependency check: one '== FILE' block per dynamic ELF object of the release,
# selected by content (ELF magic and type), from ldd and readelf.
"$PY" -I -B "$WORK/export/tools/release/release_manifest.py" elf-objects --root "$R_REL" --release-root "$R_REL" \
  > "$OUT/elf-list.txt" || refuse "DEPENDENCY_EVIDENCE_FAILED elf-objects"
[ -s "$OUT/elf-list.txt" ] || refuse "DEPENDENCY_EVIDENCE_FAILED elf-objects"
while read -r object; do
  printf '== %s\n' "$object"; ldd "$object" || refuse "DEPENDENCY_EVIDENCE_FAILED ldd $object"
done < "$OUT/elf-list.txt" > "$OUT/ldd.txt"
while read -r object; do
  printf '== %s\n' "$object"; readelf -d "$object" || refuse "DEPENDENCY_EVIDENCE_FAILED readelf $object"
done < "$OUT/elf-list.txt" > "$OUT/readelf.txt"
! grep -q 'not found' "$OUT/ldd.txt" || refuse SONAME_UNRESOLVED
awk -v prefix="$R_REL/" '$2 == "=>" && index($3, prefix) != 1 && $1 !~ /^linux-vdso/ { print $1 }' "$OUT/ldd.txt" \
  | sort -u > "$OUT/required-sonames.txt"
[ -s "$OUT/required-sonames.txt" ] || refuse SONAMES_EMPTY

# ------------------------------------------------------------- 9. release self-checks
# Actual personal-path dependencies (interpreters, run-time sysconfig, pkg-config, resolved
# libraries, runpaths), the test-module exclusion and any *.pth file refuse; any other literal '/home/' or
# '/mnt/' string is listed in portability.json as a review finding. Missing or malformed
# evidence refuses.
"$PY" -I -B "$WORK/export/tools/release/release_manifest.py" portability --root "$R_REL" --release-root "$R_REL" \
  --ldd "$OUT/ldd.txt" --readelf "$OUT/readelf.txt" > "$OUT/portability.json" || refuse PORTABILITY_CHECK_FAILED
note "portability: $(grep -o '"literal_finding_files": [0-9]*' "$OUT/portability.json") (review findings, see $OUT/portability.json)"
set -- "$R_REL"/python/lib/python3.13/_sysconfigdata_*.py
[ $# -eq 1 ] && [ -f "$1" ] || refuse SYSCONFIGDATA_LAYOUT
grep -qF "'prefix': '$R_REL/python'" "$1" || refuse SYSCONFIG_PREFIX_MISMATCH
[ -z "$(find "$R_REL/app" -name __pycache__)" ] || refuse APP_BYTECODE
[ -z "$(find "$R_REL" -perm /022 ! -type l)" ] || refuse GROUP_OR_OTHER_WRITABLE
[ -z "$(find "$R_REL" ! -type f ! -type d ! -type l)" ] || refuse UNSUPPORTED_ENTRY_TYPE
[ -z "$(find "$R_REL" -type l ! -path "$R_REL/python/*")" ] || refuse SYMLINK_OUTSIDE_PYTHON

# ------------------------------------------------------------- 10. manifest and tarball
"$PY" -I -B "$WORK/export/tools/release/release_manifest.py" create --root "$R_REL" --release-root "$R_REL" \
  --commit "$C" --source-set "$D" --sonames "$OUT/required-sonames.txt" > "$OUT/manifest-create.json"
MANIFEST_SHA=$(sha "$R_REL/RELEASE-MANIFEST.json")
"$PY" -I -B "$WORK/export/tools/release/release_manifest.py" verify --root "$R_REL" --expect-sha256 "$MANIFEST_SHA" \
  --release-root "$R_REL" --symlink-owner-uid "$(id -u)" > "$OUT/manifest-verify.json"
tar --sort=name --owner=0 --group=0 --numeric-owner --hard-dereference --format=gnu \
  --mtime="@$SOURCE_DATE_EPOCH" -C "$R_REL" -cf "$OUT/release.tar" .
"$PY" -I -B "$WORK/export/tools/release/release_manifest.py" check-archive --tarball "$OUT/release.tar" \
  > "$OUT/archive-check.json"
TARBALL_SHA=$(sha "$OUT/release.tar")
L1_TESTED=null
[ "$D" != e6c9f2a342c70b2aace64315442707b3cb1783cc18a5e54f5f95ccf205ed47c0 ] || L1_TESTED="\"$D\""
set -C
printf '{"schema":"ohk-bdw.build-record.v1","commit":"%s","release_root":"%s","source_set":"%s","l1_tested_source_set":%s,"manifest_sha256":"%s","tarball_sha256":"%s","cpython_tarball_sha256":"%s","pip_zipapp_sha256":"%s","requirements_hashed_sha256":"%s","wheel_count":%d,"source_date_epoch":%s,"build_host":"%s","reproducible":"not claimed","provenance":"none; integrity relative to the digest delivery channel only"}\n' \
  "$C" "$R_REL" "$D" "$L1_TESTED" "$MANIFEST_SHA" "$TARBALL_SHA" "${A[cpython-sha256]}" "${A[pip-zipapp-sha256]}" \
  "${A[requirements-hashed-sha256]}" "$wheels" "$SOURCE_DATE_EPOCH" "$(uname -srm)" > "$OUT/BUILD-RECORD.json"
set +C
note "release staged at $R_REL (left in place for the staging tests and the staging release_check)"
printf 'manifest_sha256 %s\ntarball %s/release.tar sha256 %s\n' "$MANIFEST_SHA" "$OUT" "$TARBALL_SHA"
