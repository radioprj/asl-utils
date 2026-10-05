#!/bin/bash
#
# install.sh - audio z noda ASL3 w przegladarce przez WebRTC (MediaMTX)
#
#   sudo ./install.sh NODE [options]
#   sudo ./install.sh --uninstall NODE
#
# Options:
#   --replace-broadcastify  disable asl-broadcastify@NODE (it reads the same FIFO)
#   --update-config         edit the dashboard config.ini without asking
#   --no-config             never touch config.ini
#   --config PATH           dashboard config.ini (default /var/www/html/config.ini)
#
# Wszystkie pliki trzymamy w /opt/mediamtx (jedno miejsce = latwy backup).
#
set -euo pipefail

MEDIAMTX_VERSION="${MEDIAMTX_VERSION:-v1.21.1}"
DEST="/opt/mediamtx"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SVC_USER="mediamtx"
UDP_PORT=8189
FILES="mediamtx.yml asl-mediamtx mediamtx.service asl-mediamtx@.service mediamtx-whep.conf"

say()  { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!! \033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

NODE=""; REPLACE=0; UNINSTALL=0; CONFIG="/var/www/html/config.ini"; CFGMODE="ask"
while [ $# -gt 0 ]; do
    case "$1" in
        --replace-broadcastify) REPLACE=1 ;;
        --uninstall)            UNINSTALL=1 ;;
        --update-config)        CFGMODE="yes" ;;
        --no-config)            CFGMODE="no" ;;
        --config)               shift; CONFIG="${1:?--config needs a path}" ;;
        -h|--help)              sed -n '2,14p' "$0"; exit 0 ;;
        -*)                     die "Unknown option: $1" ;;
        *)                      NODE="$1" ;;
    esac
    shift
done
[ -n "$NODE" ] || die "Usage: sudo $0 NODE [options]  (see --help)"
[[ "$NODE" =~ ^[0-9A-Za-z_-]+$ ]] || die "Invalid node number: $NODE"
[ "$(id -u)" -eq 0 ] || die "Run as root (sudo)."

# ---------------------------------------------------------------- uninstall
if [ "$UNINSTALL" -eq 1 ]; then
    say "Uninstalling (node ${NODE})"
    systemctl disable --now "asl-mediamtx@${NODE}" 2>/dev/null || true
    systemctl disable --now mediamtx 2>/dev/null || true
    rm -f /etc/systemd/system/mediamtx.service "/etc/systemd/system/asl-mediamtx@.service"
    systemctl daemon-reload
    if command -v a2disconf >/dev/null 2>&1; then
        a2disconf -q mediamtx-whep 2>/dev/null || true
        rm -f /etc/apache2/conf-available/mediamtx-whep.conf
        systemctl reload apache2 2>/dev/null || true
    fi
    if command -v firewall-cmd >/dev/null 2>&1 && firewall-cmd --state >/dev/null 2>&1; then
        firewall-cmd --permanent --remove-port="${UDP_PORT}/udp" >/dev/null 2>&1 || true
        firewall-cmd --reload >/dev/null 2>&1 || true
    fi
    say "Done. Files in ${DEST} were left untouched. Remove webrtc_* from config.ini."
    exit 0
fi

# ------------------------------------------------------------------ prechecks
command -v systemctl >/dev/null || die "systemd is required."
for c in curl tar sha256sum ffmpeg; do
    command -v "$c" >/dev/null || die "Missing command: $c"
done
encoders="$(ffmpeg -hide_banner -encoders 2>/dev/null || true)"
grep -q libopus <<<"$encoders" || die "ffmpeg has no libopus encoder."
id asterisk >/dev/null 2>&1 || die "User 'asterisk' not found (is this ASL3?)."

# asl-broadcastify czyta ten sam FIFO - dwoch czytelnikow = dziurawe oba strumienie
if systemctl is-active --quiet "asl-broadcastify@${NODE}"; then
    if [ "$REPLACE" -eq 1 ]; then
        warn "Disabling asl-broadcastify@${NODE} (it reads the same FIFO)."
        systemctl disable --now "asl-broadcastify@${NODE}"
    else
        die "asl-broadcastify@${NODE} is running and reads the same FIFO. Both streams would break.
       Re-run with --replace-broadcastify to disable it (this also stops a Broadcastify feed)."
    fi
fi

# ---------------------------------------------------------------------- files
say "Files -> ${DEST}"
mkdir -p "$DEST"
if [ "$SRC" != "$DEST" ]; then
    for f in $FILES; do
        [ -f "$SRC/$f" ] || die "Missing file: $SRC/$f"
        # istniejacego, ewentualnie zmienionego mediamtx.yml nie nadpisujemy
        if [ "$f" = "mediamtx.yml" ] && [ -f "$DEST/$f" ]; then continue; fi
        install -m 644 "$SRC/$f" "$DEST/$f"
    done
fi
chmod 755 "$DEST/asl-mediamtx"

# --------------------------------------------------------------------- binary
case "$(uname -m)" in
    x86_64)        ARCH="linux_amd64" ;;
    aarch64|arm64) ARCH="linux_arm64" ;;
    armv7l)        ARCH="linux_armv7" ;;
    armv6l)        ARCH="linux_armv6" ;;
    *)             die "Unsupported architecture: $(uname -m)" ;;
esac

current=""
if [ -x "$DEST/mediamtx" ]; then current="$("$DEST/mediamtx" --version 2>/dev/null || true)"; fi
if [ "$current" = "$MEDIAMTX_VERSION" ]; then
    say "MediaMTX ${MEDIAMTX_VERSION} already installed"
else
    say "Downloading MediaMTX ${MEDIAMTX_VERSION} (${ARCH})"
    tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
    asset="mediamtx_${MEDIAMTX_VERSION}_${ARCH}.tar.gz"
    base="https://github.com/bluenviron/mediamtx/releases/download/${MEDIAMTX_VERSION}"
    curl -fsSL -o "$tmp/$asset" "$base/$asset"        || die "Download failed: $base/$asset"
    curl -fsSL -o "$tmp/checksums" "$base/checksums.sha256" || die "Checksum download failed."
    expected="$(grep -F "$asset" "$tmp/checksums" | cut -d' ' -f1)"
    actual="$(sha256sum "$tmp/$asset" | cut -d' ' -f1)"
    [ -n "$expected" ] && [ "$expected" = "$actual" ] || die "Checksum mismatch for $asset."
    tar -xzf "$tmp/$asset" -C "$tmp" mediamtx
    install -m 755 "$tmp/mediamtx" "$DEST/mediamtx.new"
    mv -f "$DEST/mediamtx.new" "$DEST/mediamtx"       # podmiana atomowa, dziala tez przy uruchomionej usludze
fi

# ----------------------------------------------------------------- user, units
id "$SVC_USER" >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin "$SVC_USER"
install -m 644 "$DEST/mediamtx.service"          /etc/systemd/system/mediamtx.service
install -m 644 "$DEST/asl-mediamtx@.service"     /etc/systemd/system/asl-mediamtx@.service
systemctl daemon-reload

# --------------------------------------------------------------------- Apache
APACHE_OK=0
if command -v apache2ctl >/dev/null 2>&1 && [ -d /etc/apache2/conf-available ]; then
    say "Apache: proxy /whep/ -> MediaMTX"
    a2enmod -q proxy proxy_http
    install -m 644 "$DEST/mediamtx-whep.conf" /etc/apache2/conf-available/mediamtx-whep.conf
    a2enconf -q mediamtx-whep
    if apache2ctl configtest >/dev/null 2>&1; then
        systemctl reload apache2
        APACHE_OK=1
    else
        a2disconf -q mediamtx-whep
        warn "Apache configtest failed - proxy NOT enabled. Check: apache2ctl configtest"
    fi
else
    warn "Apache not found. Add an equivalent rule to your web server, e.g. nginx:"
    warn "    location /whep/ { proxy_pass http://127.0.0.1:8889/; }"
fi

# ------------------------------------------------------------------- firewall
if command -v firewall-cmd >/dev/null 2>&1 && firewall-cmd --state >/dev/null 2>&1; then
    say "firewalld: opening ${UDP_PORT}/udp"
    firewall-cmd --permanent --add-port="${UDP_PORT}/udp" >/dev/null
    firewall-cmd --reload >/dev/null
elif command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q "Status: active"; then
    say "ufw: opening ${UDP_PORT}/udp"
    ufw allow "${UDP_PORT}/udp" >/dev/null
else
    say "No active firewall detected - make sure ${UDP_PORT}/udp is reachable"
fi

# ------------------------------------------------------------------- rpt.conf
if grep -Eq "^[[:space:]]*outstreamcmd[[:space:]]*=.*rpt_audio_writer,/var/lib/asterisk/${NODE}\.fifo" /etc/asterisk/rpt.conf 2>/dev/null; then
    say "rpt.conf: outstreamcmd for node ${NODE} found"
else
    warn "rpt.conf has no outstreamcmd for node ${NODE}. Add to the [${NODE}](node-main) section:"
    warn "    outstreamcmd = /usr/libexec/asl3/rpt_audio_writer,/var/lib/asterisk/${NODE}.fifo"
    warn "then restart Asterisk. (The installer does not edit rpt.conf.)"
fi

# ---------------------------------------------------------------------- start
say "Starting services"
systemctl enable mediamtx "asl-mediamtx@${NODE}" >/dev/null 2>&1
systemctl restart mediamtx
sleep 1
systemctl restart "asl-mediamtx@${NODE}"
sleep 4
for u in mediamtx "asl-mediamtx@${NODE}"; do
    if systemctl is-active --quiet "$u"; then say "$u: active"; else warn "$u: NOT active (journalctl -u $u -n 30)"; fi
done

probe_proxy() {
    local url hdr
    for url in "https://127.0.0.1" "http://127.0.0.1"; do
        hdr="$(curl -ksi --max-time 5 -X POST "${url}/whep/${NODE}/whep" \
               -H 'Content-Type: application/sdp' -d x 2>/dev/null || true)"
        if grep -qi '^server: mediamtx' <<<"$hdr"; then return 0; fi
    done
    return 1
}
if [ "$APACHE_OK" -eq 1 ]; then
    if probe_proxy; then say "Proxy check: Apache -> MediaMTX works"; else warn "Proxy check failed (no response from MediaMTX via Apache)."; fi
fi

# ------------------------------------------------------------------ config.ini
# Edytujemy WYLACZNIE sekcje [audio], po zrobieniu kopii; niczego nie kasujemy.
audio_has_key() {   # $1=plik $2=klucz (aktywny, nie zakomentowany) w sekcji [audio]
    awk -v key="$2" '
        /^[[:space:]]*\[/ { in_a = ($0 ~ /^[[:space:]]*\[audio\][[:space:]]*(;.*)?$/); next }
        in_a && $0 ~ ("^[[:space:]]*" key "[[:space:]]*=") { found = 1 }
        END { exit !found }' "$1"
}

update_config() {
    local bak tmp need_ext=0
    bak="${CONFIG}.bak-$(date +%Y%m%d-%H%M%S)"
    cp -a "$CONFIG" "$bak"
    tmp="$(mktemp)"
    if ! grep -Eq '^[[:space:]]*\[audio\]' "$CONFIG"; then
        { cat "$CONFIG"; printf '\n[audio]\nwebrtc_enabled  = yes\nwebrtc_external = no\ndescription = "ASL Node"\n'; } > "$tmp"
    else
        audio_has_key "$CONFIG" webrtc_external || need_ext=1
        awk -v add_ext="$need_ext" '
            /^[[:space:]]*\[/ {
                in_a = ($0 ~ /^[[:space:]]*\[audio\][[:space:]]*(;.*)?$/)
                print
                if (in_a) { print "webrtc_enabled  = yes"; if (add_ext == 1) print "webrtc_external = no" }
                next
            }
            in_a && /^[[:space:]]*stream_url[[:space:]]*=/ { print "; (old Icecast stream, no longer used) " $0; next }
            { print }' "$CONFIG" > "$tmp"
    fi
    cat "$tmp" > "$CONFIG"      # zachowuje wlasciciela i prawa pliku
    rm -f "$tmp"
    say "config.ini updated (section [audio] only). Backup: ${bak}"
}

CONFIG_DONE=0
if [ "$CFGMODE" != "no" ]; then
    if [ ! -f "$CONFIG" ]; then
        warn "Dashboard config not found: ${CONFIG} (use --config PATH)"
    elif audio_has_key "$CONFIG" webrtc_enabled; then
        say "config.ini: webrtc_enabled already set"
        CONFIG_DONE=1
    else
        do_it=0
        if [ "$CFGMODE" = "yes" ]; then
            do_it=1
        elif [ -t 0 ]; then
            read -r -p "Update ${CONFIG} for WebRTC (a backup is made, only [audio] is changed)? [Y/n] " ans
            case "${ans:-Y}" in [Yy]*) do_it=1 ;; esac
        fi
        if [ "$do_it" -eq 1 ]; then update_config; CONFIG_DONE=1; fi
    fi
fi

if [ "$CONFIG_DONE" -eq 0 ]; then cat <<EOF

Add to config.ini:

  [audio]
  webrtc_enabled  = yes
  webrtc_external = no
  ; remove or comment out the old stream_url (no longer used)
EOF
fi

cat <<EOF

Listeners outside your LAN: set webrtc_external = yes, forward ${UDP_PORT}/udp
(and your dashboard port) on the router, and in ${DEST}/mediamtx.yml
uncomment webrtcAdditionalHosts with your public address, then:
  sudo systemctl restart mediamtx
EOF

