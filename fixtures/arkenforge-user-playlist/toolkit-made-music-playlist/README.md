# Populated Toolkit user music control

Created 2026-11-04, Windows, Toolkit **0.5.1.18**, with Jeffrey's explicit
confirmation. Audio → Playlists → New playlist → **FB Native Music Control** →
Add new content → From File Import → selected the existing synthetic
`FBReference-tone.wav`. The importer completed and displayed a two-second song.
It embedded the original WAV; no transcoding occurred on that path.

For codec round trips, imported `sources/FBMusicControl-MP3.mp3` and then
`sources/FBMusicControl-OGG.ogg` separately using the same File Import command.
These are versions of the same original two-second, 440-Hz synthetic tone,
encoded with the separately installed PySceneDetect ffmpeg (libmp3lame and
libvorbis; one thread; no Toolkit encoder dependency). They contain no music
from the adventure or shipped packs. The original WAV source is retained at
`../../arkenforge-native-controls-2026-11-03/sources/FBReference-tone.wav`.
The MP3 is displayed as 00:01 by Toolkit, OGG and WAV as 00:02; byte/probe
durations must be distinguished from that UI rounding.

The native track dropdown displays **Master 80%**. Its populated
`MusicTrackInfo._trackVolumes` dictionary contains `Master: 0.8`, Version 2,
HashSize 3 and a String/Single KeyValuePairs array. The old ForgeBridge
playlist used empty dictionaries (Version 0, HashSize 0); its expanded mixer
showed no Master slider. Native ContentItem has only `_filePath` and `_content`,
with no `_officialFlag` member. Do not byte-patch these reference records.

Native file paths are preserved under `MyAssets/` in this folder; manifests and
comparison evidence distinguish raw bytes, field values and runtime claims.
All three source formats are stored in `AudioTrack._clipRAW`, with a matching
`_originalFile` extension. Metadata is not proof of audible playback.

Before repair, Jeffrey reported the original MP3 silent and, during this
session, confirmed **“OGG is silent”** after the second OGG track was started
explicitly and observed advancing to 00:56. No codec is declared working from
a timer, payload signature or successful import alone. Production MP3 remains
manual; corrected-playlist listening is a separate acceptance check.

Jeffrey subsequently confirmed **all three files here are audible**, identifying
this native control playlist in his supplied photo (2026-11-04): WAV,
FBMusicControl-MP3 and FBMusicControl-OGG. This supersedes the transient silence
observed while testing the native control; the intervening setting/session change
was not established. No root cause for that transient silence is claimed.
It does not pass the separate ForgeBridge-written FB MP3 Test playlist.

Toolkit was already closed when work resumed on 2026-11-05. Only then were the
eight native files copied, without modification. `manifest.json` records their
hashes and complete class/member/type declarations. Tests compare encoded bytes
through native import and schema serialization, including OGG production output.
The companion `validation/2026-11-05-music-comparison.json` records old/repaired
playlist, song and metadata fields, embedded-byte headers/hashes/lengths, codec
inspection and native controls. No song/metadata payload changed in the repaired
two-track experiment; only its `.rwpl` changed.
