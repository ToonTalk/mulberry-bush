# Mulberry Bush

Two web versions of *Mulberry Bush*, a hand-drawn animated film made by Ken Kahn in 1976
([watch the film on YouTube](https://youtu.be/BfE71oTYjdI)), and a report on how they were made.
Both were built with Claude in one working session on 12 November 2026.

| Piece | What it is | Open |
|---|---|---|
| **Mulberry Bush** | Every drawing in the film, traced from the video into flat colour shapes and redrawn by the browser at twelve drawings a second. A new soundtrack is synthesized live on the beat of the original recording, with one instrument for each drawing medium. | `index.html` |
| **Round the Mulberry Bush** | A reinterpretation with nothing traced. Four shadow dancers circle a backlit paper screen, the screen turns out to be a phenakistoscope wheel of code-drawn dancers, and the four return. Includes a hands-on mode where you turn the wheel yourself. | `round/index.html` |
| **Making Mulberry Bush** | The making-of report: what was done, why, and with which tools. | `report/index.html` |

The two films are single HTML files with no dependencies; the report also loads its pictures from `report/img/`.
Download the repository and open a file in a browser (tested in Chromium-based browsers only). Sound starts when you press play.

The same three pages are published as Claude artifacts, which open only for people they have been shared with:
[Mulberry Bush](https://claude.ai/artifact/6iCocVZBschxP7SWCbTfRc),
[Round the Mulberry Bush](https://claude.ai/artifact/FMnBUCYBdFL6nU7vsi9QVs),
[Making Mulberry Bush](https://claude.ai/artifact/KG6a9jU9DqHBP1Jps11BXy).

In `round/index.html`, add `#t40` to the address to jump to the moment forty seconds in, or `#wheel` to start in hands-on mode.

## Layout

```
index.html              the traced film, complete in one file (3.2 MB)
round/
  index.html            Round the Mulberry Bush
  round.src.html        its single source: dancers, wheel, band and page
report/
  index.html            the making-of report
  report.src.html       its source
  img/                  its images
source/
  app.src.html          the traced page without its data
  scripts/              Python (NumPy + OpenCV) used to trace the film
  data/                 intermediate tracing results, enough to re-pack without re-tracing
  build.py              rebuilds index.html
  build_round.py        rebuilds round/index.html
  build_report.py       rebuilds report/index.html
  NOTES.txt             build notes
artifact/               copies of the three pages in the form published as Claude artifacts
```

The film itself is not in the repository.

## Credits

Film: Ken Kahn, 1976. Music on the original soundtrack: Nancy Koch (accordion) and Tommy Magee (fiddle).
Thanks, from the film's title cards: Fannie Newman, Cathy Shaw, Dave Taenzer.
The film was first shown as part of the live piece *Loops* at the Carpenter Center, Harvard.

## License

MIT. See [LICENSE](LICENSE).
