#!/usr/bin/env bash
# Publish game/dist (build it first: npm --prefix game run deploy:build) on a slow uplink: wrangler uploads in
# parallel batches that time out there, so the files go up a few at a time as non-live versions first.
set -u
cd "$(dirname "$0")/.."
DIST=game/dist; ST=build/deploy/stage
big=$(find $DIST -type f -size +1M -printf "%s %P\n" | sort -n | awk '{print $2}')
rm -rf $ST; mkdir -p $ST
(cd $DIST && find . -type f -size -1025k -print0 | cpio -0pdm --quiet ../../$ST)        # all small files first
cfg() { sed "s|\"directory\": \"../game/dist\"|\"directory\": \"../build/deploy/stage\"|" deploy/wrangler.jsonc > deploy/stage.jsonc; }
cfg
up() { for i in 1 2 3 4; do (mkdir -p build/deploy; cd deploy && npx --yes wrangler@4 versions upload -c stage.jsonc > ../build/deploy/vup.log 2>&1) && return 0; sleep 15; done; return 1; }
up && echo "small files: ok" || echo "small files: FAILED"
n=0
for f in $big; do
  mkdir -p "$ST/$(dirname "$f")"; ln -f "$DIST/$f" "$ST/$f"; n=$((n+1))
  if [ $((n % 2)) -eq 0 ]; then up && echo "big $n: ok ($f)" || echo "big $n: FAILED ($f)"; fi
done
up && echo "all staged: ok" || echo "all staged: FAILED"
rm -f deploy/stage.jsonc
(cd deploy && npx --yes wrangler@4 deploy)       # goes live; nothing left to upload
