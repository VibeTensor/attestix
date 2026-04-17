# Attestix Demo Recording

Two options are checked in here so whoever ships the demo can pick the path that works on their machine.

## Option A: VHS (recommended, produces a GIF)

VHS is a scripted terminal recorder from Charmbracelet. The tape file at `public/demo.tape` scripts the entire pip install and CLI walkthrough. Render with:

```bash
vhs public/demo.tape
```

This writes `public/demo.gif`. Commit the GIF so it is served from the static export.

Install VHS:

- macOS: `brew install vhs`
- Linux: `go install github.com/charmbracelet/vhs@latest`
- Windows: `scoop install vhs` (or run inside WSL)

## Option B: asciinema (produces a .cast file)

If VHS is unavailable, record a terminal session directly:

```bash
asciinema rec public/demo.cast \
  --title "Attestix Quick Start" \
  --idle-time-limit 2
```

Run these commands inside the recording so viewers see the real output:

```bash
pip install attestix
attestix init
attestix status
attestix verify ./credentials/agent-card.vc.json
```

Stop the recording with `Ctrl+D`. To embed the `.cast` file on the site, drop the asciinema web player script in the page that hosts the hero.

## Where the media is used

The hero section at `src/components/sections/hero.tsx` expects a media asset. After generating either `public/demo.gif` or converting the asciinema cast to a GIF, update the hero to reference `/demo.gif`.
