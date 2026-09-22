#!/bin/bash
# Usage: mix.sh <sfx_gain_db> <out.mp4> [subs_frames_dir]
set -e
FF=$HOME/bin/ffmpeg
SFXG=${1:-0}
OUT=${2:-final.mp4}
FRAMES=${3:-frames}
cd /home/user/project
# VO dominant: VO 0 dB (light limiter), music ~ -20 dB under, SFX ~ -15 dB under.
$FF -y -v error -stats \
  -framerate 30 -i "$FRAMES/f%06d.jpg" \
  -i vo.wav -i music.wav -i sfx.wav \
  -filter_complex "\
    [1:a]aformat=channel_layouts=stereo,alimiter=limit=0.95:level=false[vo];\
    [2:a]aformat=channel_layouts=stereo,volume=-20dB,lowpass=f=3200[mu];\
    [3:a]aformat=channel_layouts=stereo,volume=$((-15+SFXG))dB[fx];\
    [vo][mu][fx]amix=inputs=3:duration=first:normalize=0:dropout_transition=0,\
    alimiter=limit=0.97:level=false[a]" \
  -map 0:v -map "[a]" \
  -c:v libx264 -preset medium -crf 18 -threads 2 -x264-params rc-lookahead=20:ref=3 -pix_fmt yuv420p -r 30 -movflags +faststart \
  -c:a aac -b:a 256k -shortest "$OUT"
echo "wrote $OUT"
