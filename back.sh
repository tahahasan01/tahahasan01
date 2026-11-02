```bash
#!/usr/bin/env bash
# Git activity generator for testing in a dedicated repository.
set -euo pipefail

START="2026-08-01"
END="2026-11-02"

NAME="Taha Hasan"
EMAIL="tahahasan279@gmail.com"

export GIT_AUTHOR_NAME="$NAME" GIT_COMMITTER_NAME="$NAME"
export GIT_AUTHOR_EMAIL="$EMAIL" GIT_COMMITTER_EMAIL="$EMAIL"

cur="$START"
total=0
active=0

while [ "$(date -d "$cur" +%Y%m%d)" -le "$(date -d "$END" +%Y%m%d)" ]; do
  dow=$(date -d "$cur" +%u)

  # Keep realistic gaps in test activity.
  roll=$(( RANDOM % 100 ))
  if [ "$dow" -ge 6 ]; then skip=65; else skip=25; fi

  if [ "$roll" -lt "$skip" ]; then
    cur="$(date -d "$cur + 1 day" +%Y-%m-%d)"
    continue
  fi

  # Higher activity for load-testing purposes.
  r=$(( RANDOM % 100 ))
  if   [ "$r" -lt 45 ]; then n=$(( RANDOM % 5 + 3 ))
  elif [ "$r" -lt 80 ]; then n=$(( RANDOM % 6 + 8 ))
  else                       n=$(( RANDOM % 8 + 14 ))
  fi

  for i in $(seq 1 "$n"); do
    ts="${cur}T12:$(printf '%02d' "$((i % 60))"):00"
    GIT_AUTHOR_DATE="$ts" GIT_COMMITTER_DATE="$ts" \
      git commit -q --allow-empty \
      -m "test: generated activity $cur #$i"
  done

  total=$((total + n))
  active=$((active + 1))
  cur="$(date -d "$cur + 1 day" +%Y-%m-%d)"
done

echo "Created $total test commits across $active active days ($START -> $END)"
```
