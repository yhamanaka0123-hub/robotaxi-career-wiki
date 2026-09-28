#!/usr/bin/env bash
# Offline demonstration. Run with Wi-Fi/Ethernet OFF, after restarting the terminal:
#   ./tools/offline_demo.sh
# Everything printed is also saved to evidence/offline/<timestamp>/transcript.txt
set -u
cd "$(dirname "$(readlink -f "$0")")/.."
OUT="evidence/offline/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
exec > >(tee "$OUT/transcript.txt") 2>&1

step() { printf '\n\n==================== %s ====================\n$ %s\n' "$1" "$2"; }

step "0. Proof of offline + device" "date; ping/curl to the internet; specs"
date
echo "--- internet check (expected to FAIL) ---"
ping -c 1 -W 3 8.8.8.8 && echo "!! ONLINE: ping succeeded" || echo "OK: ping 8.8.8.8 failed (offline)"
curl -sS --max-time 5 -o /dev/null https://www.google.com && echo "!! ONLINE: https succeeded" || echo "OK: https://www.google.com unreachable (offline)"
powershell.exe -NoProfile -Command "Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object Name,Status" 2>/dev/null
echo "--- device ---"
grep PRETTY_NAME /etc/os-release; uname -r
lscpu | grep -E "Model name|^CPU\(s\)"
free -h | head -2
powershell.exe -NoProfile -Command "'Host RAM (GB): ' + [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1); 'Host free RAM (GB): ' + [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)" 2>/dev/null
df -h . | tail -1

step "1. Help" "./wiki --help"
./wiki --help
step "1b. Status" "./wiki status"
./wiki status

step "2. Ingest a local source (regenerate its note with local Gemma)" "./wiki ingest \"./vault/raw/Zoox - Wikipedia.md\" --force"
/usr/bin/time -v ./wiki ingest "./vault/raw/Zoox - Wikipedia.md" --force 2> "$OUT/ingest-time.txt"
grep -E "Elapsed|Maximum resident" "$OUT/ingest-time.txt"
echo "--- notes after ingest (expect 6, no duplicates) ---"
find vault/wiki -name "*.md" | sort; find vault/wiki -name "*.md" | wc -l
echo "--- model memory while loaded ---"
curl -s http://localhost:11434/api/ps | python3 -c "import sys,json; [print(f\"{m['name']}: {m['size']/1e9:.2f} GB loaded ({m['details']['quantization_level']}), context {m.get('context_length')}\") for m in json.load(sys.stdin)['models']]"
powershell.exe -NoProfile -Command "Get-Process ollama* | Select-Object Name,@{n='WorkingSet_GB';e={[math]::Round(\$_.WorkingSet64/1GB,2)}}" 2>/dev/null

step "3. Search (retrieval only, no generation)" "./wiki search \"H-1B cap master's degree\""
./wiki search "H-1B cap master's degree"

step "4. Ask test 1" "./wiki ask \"Which company owns Zoox, and how much did it pay to acquire it?\" --mode local"
/usr/bin/time -f "wall %e s, max RSS of CLI %M KB" ./wiki ask "Which company owns Zoox, and how much did it pay to acquire it?" --mode local
step "5. Ask test 2" "./wiki ask \"If I finish a graduate degree at an American university, is there a separate H-1B quota I can apply under?\" --mode local"
/usr/bin/time -f "wall %e s" ./wiki ask "If I finish a graduate degree at an American university, is there a separate H-1B quota I can apply under?" --mode local
step "6. Ask test 3" "./wiki ask \"After I graduate from my MBA, how long can I work in the US on OPT before I need an H-1B?\" --mode local"
/usr/bin/time -f "wall %e s" ./wiki ask "After I graduate from my MBA, how long can I work in the US on OPT before I need an H-1B?" --mode local
step "7. Ask test 4 (unsupported)" "./wiki ask \"Does Moove sponsor H-1B visas for its employees?\" --mode local"
/usr/bin/time -f "wall %e s" ./wiki ask "Does Moove sponsor H-1B visas for its employees?" --mode local

# The "manager told me" line is a made-up test claim (not true) to check that chat claims never become ask evidence.
step "8. Chat mode checks" "./wiki chat  (scripted input)"
printf '%s\n' \
  "what can you help me with?" \
  "what can we do?" \
  "draft a short plan for my recruiting this fall, based on my notes" \
  "make that shorter" \
  "By the way, my manager told me Moove will definitely sponsor my H-1B." \
  "/ask Does Moove sponsor H-1B visas for its employees?" \
  "/exit" | ./wiki chat

step "9. Ask is independent of chat" "./wiki ask \"Does Moove sponsor H-1B visas for its employees?\" --mode local"
./wiki ask "Does Moove sponsor H-1B visas for its employees?" --mode local

step "10. Errors" "./wiki ingest ./does-not-exist ; WIKI_OLLAMA_URL=http://localhost:9 ./wiki ask test"
./wiki ingest ./does-not-exist
WIKI_OLLAMA_URL=http://localhost:9 ./wiki ask "test"

echo; echo "Transcript saved to $OUT/transcript.txt"
