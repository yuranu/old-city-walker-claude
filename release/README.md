# Old City Walker: running a release

A release archive is the built game: a walkable, geo-registered model of Jerusalem's walled Old
City, ready to run in a browser without Blender or the build pipeline. The source, the method and
the research behind it are at <https://github.com/yuranu/old-city-walker-claude>.

## Run it

The game is a set of static files. Browsers refuse to load them from `file://`, so serve the
folder with any local web server. With Python 3 (installed on most systems):

```bash
cd old-city-walker-<version>
python3 serve.py            # then open http://127.0.0.1:8000
```

On Windows, double-click `serve.py` if Python is installed, or run `py serve.py`. Any other static
server works as well, for example `npx serve game` with Node.

A recent desktop browser with WebGL 2 runs it best. Integrated GPUs manage about 6-10 ms a frame
at 1024x768. The city streams in by sector as you walk.

## Controls

| | |
|---|---|
| click | start walking (captures the mouse; **Esc** releases it) |
| **WASD** + mouse | walk and look |
| **Shift** / **Space** | run / jump |
| **P**, **N** | nearest real photograph of the spot (Wikimedia Commons, with credit), next one |
| **G** | open the same spot and heading in Google Street View |
| **O** | ambient occlusion on or off |
| **F3** | performance and streaming overlay |

On a phone or tablet: drag to look and use the on-screen stick to walk.

URL parameters: `?x=60&y=8&h=90` starts at x metres east and y metres north of the Jaffa Gate,
facing compass heading `h`.

The **P** photographs and **G** links load from the internet; everything else runs offline.

## Contents

```
serve.py        a minimal static server (Python standard library only)
game/           the built game
LICENSE         MIT licence for the code
ATTRIBUTION.md  data sources and their licences
VERSION         the release tag and the source commit it was built from
```

## Licence and attribution

The code is MIT-licensed (`LICENSE`). The model is derived from OpenStreetMap data
© OpenStreetMap contributors (ODbL), and uses other open data listed in `ATTRIBUTION.md`.
