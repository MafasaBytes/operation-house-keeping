#!/bin/sh
# Install one verified L2 release offline. Root only. Never run under the runtime account.
#
# Design: docs/superpowers/reports/2026-10-22-t1-linux-ext4-l2-packaging-fresh-install-PROPOSAL.md
# (74a39d87...) section 4.5, as amended by the scope addendum (6bca403b...).
#
# usage: install_release.sh --tarball T --manifest-sha256 D --release-root R_REL
#          --config-template C --data-root DR --account NAME
#          [--config /etc/ohk-bdw/deployment.json] [--manifest-tool PATH/release_manifest.py]
#
# D is the manifest digest delivered out of band by the owner-designated channel (OD-L2-B is
# open: this installer names no channel). A match is integrity relative to that channel only:
# no builder authentication, no signature (--signature refuses SIGNATURE_POLICY_UNDEFINED until
# ID-2 is decided) and no provenance (D-P open).
#
# Every refusal prints "install_release: REFUSED <CODE> ..." and exits 1; usage exits 2. Nothing
# is deleted on failure: R_REL.partial, created directories and an exclusively written
# configuration stay for inspection. There is no 'current' link, upgrade or uninstall.
set -eu
umask 022
LC_ALL=C
TZ=UTC
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL TZ PATH

refuse() { printf 'install_release: REFUSED %s\n' "$*" >&2; exit 1; }
usage() { printf 'install_release: usage: see the header of %s\n' "$0" >&2; exit 2; }
note() { printf 'install_release: %s\n' "$*" >&2; }

TARBALL= DIGEST= R_REL= TEMPLATE= DATA_ROOT= ACCOUNT= SIGNATURE=
CONFIG=/etc/ohk-bdw/deployment.json
TOOL=$(dirname "$0")/release_manifest.py
SEEN=' '
while [ $# -gt 0 ]; do
  [ $# -ge 2 ] && [ -n "$2" ] || usage
  case " $SEEN " in *" $1 "*) usage ;; esac
  SEEN="$SEEN $1"
  case "$1" in
    --tarball) TARBALL=$2 ;;
    --manifest-sha256) DIGEST=$2 ;;
    --release-root) R_REL=$2 ;;
    --config-template) TEMPLATE=$2 ;;
    --data-root) DATA_ROOT=$2 ;;
    --account) ACCOUNT=$2 ;;
    --config) CONFIG=$2 ;;
    --manifest-tool) TOOL=$2 ;;
    --signature) SIGNATURE=$2 ;;
    *) usage ;;
  esac
  shift 2
done
[ -n "$TARBALL" ] && [ -n "$DIGEST" ] && [ -n "$R_REL" ] && [ -n "$TEMPLATE" ] && [ -n "$DATA_ROOT" ] \
  && [ -n "$ACCOUNT" ] || usage
[ -z "$SIGNATURE" ] || refuse SIGNATURE_POLICY_UNDEFINED

# ------------------------------------------------------------------ 1. host and arguments
[ "$(id -u)" = 0 ] || refuse NOT_ROOT
[ "$(uname -s)" = Linux ] && [ "$(uname -m)" = x86_64 ] || refuse PLATFORM_UNSUPPORTED
for tool in python3 findmnt ldconfig adduser getent install chown chmod stat sync date; do
  command -v "$tool" >/dev/null 2>&1 || refuse "TOOL_MISSING $tool"
done
path_ok() {   # absolute, normalized, the builder's R_REL character set
  case $1 in /?*) ;; *) return 1 ;; esac
  case $1 in *[!A-Za-z0-9/._-]*|*//*|*/./*|*/../*|*/.|*/..|*/) return 1 ;; esac
  return 0
}
no_links() {   # no symlink in any existing prefix of $1
  rest=${1#/} walked=
  while [ -n "$rest" ]; do
    part=${rest%%/*}
    walked=$walked/$part
    if [ "$rest" = "$part" ]; then rest=; else rest=${rest#*/}; fi
    [ ! -L "$walked" ] || return 1
  done
  return 0
}
root_safe() {   # root-owned and neither group- nor other-writable
  set -- "$1" $(stat -c '%u %a' -- "$1")
  [ "$2" = 0 ] && [ $(( 0$3 & 18 )) -eq 0 ]
}
case $DIGEST in *[!0-9a-f]*) refuse DIGEST_INVALID ;; esac
[ ${#DIGEST} -eq 64 ] || refuse DIGEST_INVALID
case $ACCOUNT in [a-z_]*) ;; *) refuse ACCOUNT_INVALID ;; esac
case $ACCOUNT in *[!a-z0-9_-]*) refuse ACCOUNT_INVALID ;; esac
[ ${#ACCOUNT} -le 32 ] || refuse ACCOUNT_INVALID
for value in "$R_REL" "$DATA_ROOT" "$CONFIG"; do
  path_ok "$value" && no_links "$value" || refuse "PATH_INVALID $value"
done
PARTIAL=$R_REL.partial
PARENT=$(dirname "$R_REL")
[ ! -e "$R_REL" ] && [ ! -L "$R_REL" ] || refuse RELEASE_ROOT_EXISTS
[ ! -e "$PARTIAL" ] && [ ! -L "$PARTIAL" ] || refuse PARTIAL_EXISTS
[ -d "$PARENT" ] && root_safe "$PARENT" || refuse RELEASE_PARENT_UNSAFE
[ ! -e "$CONFIG" ] && [ ! -L "$CONFIG" ] || refuse CONFIG_EXISTS
# Root-owned inputs: nobody else can change them between validation and use.
for input in "$TARBALL" "$TOOL"; do
  [ -f "$input" ] && [ ! -L "$input" ] && root_safe "$input" || refuse "INPUT_UNSAFE $input"
done
[ -f "$TEMPLATE" ] && [ ! -L "$TEMPLATE" ] || refuse "INPUT_UNSAFE $TEMPLATE"
manifest() { python3 -I -B "$TOOL" "$@"; }

# ------------------------------- 2. validate every archive entry, then extract into R_REL.partial
note "extracting into $PARTIAL"
manifest extract --tarball "$TARBALL" --dest "$PARTIAL" >/dev/null || refuse ARCHIVE_REJECTED
chown -R -h root:root "$PARTIAL"

# --------------------------------------------------- 3. manifest against D, then native libraries
VERIFIED=$(manifest verify --root "$PARTIAL" --expect-sha256 "$DIGEST" --release-root "$R_REL") \
  || refuse MANIFEST_NOT_VERIFIED
SONAMES=$(manifest sonames --root "$PARTIAL" --expect-sha256 "$DIGEST") || refuse MANIFEST_NOT_VERIFIED
AVAILABLE=$(ldconfig -p | awk 'NR > 1 { print $1 }')
for name in $SONAMES; do
  printf '%s\n' "$AVAILABLE" | grep -qxF -- "$name" || refuse "SONAME_MISSING $name"
done

# ------------------------------------------------------ 4. runtime account and writable state
if ! getent passwd "$ACCOUNT" >/dev/null; then
  note "creating system account $ACCOUNT (uid allocated by the system)"
  adduser --system --group --home "$DATA_ROOT" --no-create-home --shell /usr/sbin/nologin "$ACCOUNT" >/dev/null
fi
ACCOUNT_UID=$(id -u "$ACCOUNT")
[ "$ACCOUNT_UID" != 0 ] || refuse ACCOUNT_IS_ROOT
ext4() { [ "$(findmnt -n -o FSTYPE --target "$1")" = ext4 ]; }
owner_only() { [ -d "$1" ] && [ ! -L "$1" ] && [ "$(stat -c '%u %a' -- "$1")" = "$ACCOUNT_UID 700" ]; }
DATA_PARENT=$(dirname "$DATA_ROOT")
[ -d "$DATA_PARENT" ] && root_safe "$DATA_PARENT" || refuse DATA_PARENT_UNSAFE
if [ -e "$DATA_ROOT" ] || [ -L "$DATA_ROOT" ]; then
  # An existing data root is checked, never changed.
  for dir in "$DATA_ROOT" "$DATA_ROOT/tmp" "$DATA_ROOT/evidence"; do
    owner_only "$dir" || refuse "DATA_ROOT_UNSAFE $dir"
  done
else
  ext4 "$DATA_PARENT" || refuse FILESYSTEM_UNSUPPORTED
  install -d -m 0700 -o "$ACCOUNT" -g "$ACCOUNT" "$DATA_ROOT" "$DATA_ROOT/tmp" "$DATA_ROOT/evidence"
fi
for dir in "$DATA_ROOT" "$DATA_ROOT/tmp" "$DATA_ROOT/evidence"; do
  ext4 "$dir" || refuse "FILESYSTEM_UNSUPPORTED $dir"   # findmnt: stat -f cannot tell ext4 from ext2/3
done

# ------------------------------------------------------------ 5. configuration, exclusively
CONFIG_PARENT=$(dirname "$CONFIG")
if [ ! -d "$CONFIG_PARENT" ]; then
  [ -d "$(dirname "$CONFIG_PARENT")" ] && root_safe "$(dirname "$CONFIG_PARENT")" || refuse CONFIG_PARENT_UNSAFE
  install -d -m 0755 -o root -g root "$CONFIG_PARENT"
fi
root_safe "$CONFIG_PARENT" || refuse CONFIG_PARENT_UNSAFE
CONFIG_SHA=$(manifest config --template "$TEMPLATE" --out "$CONFIG" --release-root "$R_REL" \
  --data-root "$DATA_ROOT" --account "$ACCOUNT" | sed -n 's/.*"sha256": "\([0-9a-f]\{64\}\)".*/\1/p') \
  || refuse CONFIG_REJECTED
[ -n "$CONFIG_SHA" ] || refuse CONFIG_REJECTED
chown root:root "$CONFIG"

# -------------------------------------------------- 6. publish only the complete verified release
chmod 0755 "$PARTIAL"
manifest publish --partial "$PARTIAL" --final "$R_REL" >/dev/null || refuse PUBLISH_FAILED
[ -d "$R_REL" ] && [ ! -L "$R_REL" ] && [ ! -e "$PARTIAL" ] || refuse PUBLISH_FAILED
manifest verify --root "$R_REL" --expect-sha256 "$DIGEST" --release-root "$R_REL" >/dev/null \
  || refuse PUBLISHED_RELEASE_NOT_VERIFIED
sync

# ------------------------------------------------------------------ 7. install record
STAMP=$(date -u +%Y%m%dt%H%M%Sz)
RECORD=install-$STAMP-$$.json
LIST=
for name in $SONAMES; do LIST="$LIST${LIST:+,}\"$name\""; done
# evidence/ belongs to the runtime account, so root never writes there through a path the
# account could redirect: the tool opens it by descriptor with O_NOFOLLOW and creates exclusively.
JSON=$(printf '{"schema":"ohk-bdw.install-record.v1","release_root":"%s","manifest_sha256":"%s","config":"%s","config_sha256":"%s","runtime_account":"%s","uid":%s,"required_sonames":[%s],"installed":"%s","integrity":"relative to the delivered manifest digest; not a signature or provenance"}' \
  "$R_REL" "$DIGEST" "$CONFIG" "$CONFIG_SHA" "$ACCOUNT" "$ACCOUNT_UID" "$LIST" "$STAMP")
manifest record --data-root "$DATA_ROOT" --name "$RECORD" --json "$JSON" >/dev/null || refuse RECORD_NOT_WRITTEN
note "installed $R_REL; record $DATA_ROOT/evidence/$RECORD"
printf '%s\n' "$VERIFIED"
