#!/usr/bin/env bash
# Realistic GitHub contribution backfill: gaps, lighter weekends, varied intensity.
set -euo pipefail

START="2025-01-01"     # first day
END="2026-11-02"       # last day (today)
NAME="Taha Hasan"
EMAIL="tahahasan279@gmail.com"

export GIT_AUTHOR_NAME="$NAME" GIT_COMMITTER_NAME="$NAME"
export GIT_AUTHOR_EMAIL="$EMAIL" GIT_COMMITTER_EMAIL="$EMAIL"

cur="$START"
total=0
active=0
while [ "$(date -d "$cur" +%Y%m%d)" -le "$(date -d "$END" +%Y%m%d)" ]; do
  dow=$(date -d "$cur" +%u)          # 1=Mon .. 7=Sun
  roll=$(( RANDOM % 100 ))

  # skip probability: weekdays ~30% off, weekends ~65% off
  if [ "$dow" -ge 6 ]; then skip=72; else skip=42; fi

  if [ "$roll" -lt "$skip" ]; then
    cur="$(date -d "$cur + 1 day" +%Y-%m-%d)"
    continue                          # empty day (a gap)
  fi

  # intensity: mostly light, some medium, rare heavy
  r=$(( RANDOM % 100 ))
  if   [ "$r" -lt 60 ]; then n=$(( RANDOM % 4 + 1 ));   # 1-4  light
  elif [ "$r" -lt 88 ]; then n=$(( RANDOM % 5 + 5 ));   # 5-9  medium
  else                       n=$(( RANDOM % 6 + 10 )); fi # 10-15 heavy

  for i in $(seq 1 "$n"); do
    ts="${cur}T12:$(printf '%02d' $((i % 60))):00"
    GIT_AUTHOR_DATE="$ts" GIT_COMMITTER_DATE="$ts" \
      git commit -q --allow-empty -m "chore: activity $cur #$i"
  done
  total=$((total + n))
  active=$((active + 1))
  cur="$(date -d "$cur + 1 day" +%Y-%m-%d)"
done
echo "Created $total commits across $active active days ($START -> $END)"    i want you to update the dates recent to latest  and ncrase the commts 
