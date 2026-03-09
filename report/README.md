# Note

If you are reading this you most likely unzip this reports directory and are looking at the documentation. Here is a helpful(hopefully) guide.

- REPORT.pdf - a pdf version of our report
- REPORT.md - a markdown version of same.
- images/ - directory for screen shots used in report

NOTE - if focused on the markdown, be sure to have mermaid plugin installed in your IDE of choice. We have tested with InteliJ and VSCode. The reason is we are using mermaid - *diagrams as code* - for our technical diagrams. To render this properly so you can view images vs code blocks you need this plugin. Note this is enabled out of box if viewing in GitHub's site. Enabliing in your IDE is a trivial step.

- `generate_pdf.sh` - a simple script to generate a pdf from the markdown.

Turns out pandoc isn't as simple as one may think - so this script gives a repeatable pdf generation step. For more details on padocs complexities see the section below. If you are really interested in generating the doc from me, use this script and make sure your system is set up as documented below.

## Pandocs Info
`pandoc` is a "Pandoc is a universal document converter. It lets you take text written in one  format (like Markdown) and convert it into many other formats such as PDF, HTML, Word, LaTeX, or EPUB."

If you sqint you may see it as a document compiler. In this project we are using it to go from md to pdf. But interestingly `pandoc` creates an intermediatery format in LaTeX before final pdf generation.

For simple md you get a crude pdf doc - not very pretty. So if you want to improve the look/feel of the final document you need to intercept the intermediatery LaTeX with LaTeX configuration - this is where the `scripts` folder plays a part.
These scripts control everything from

- line spacing
- font selection
- font size
- table niceties
- mermaid diagram generation

The last one is important in this context. For those that advoce for Markdown, then logically leveraging Mermaid is hand-in-glove with this. Mermaid is *diagram-as-code* and offers the huge advantage of multiple collaborators being able to modify diagrams without the laborious steps of opening a diagramming tool, modifying, saving-as and committing essentially a binary object to github. Additionally changes to diagrams can now be tracked to a very fine level of granulaity. Every opensource project of consequence that is interested in quality documents are using this.

If you want to get pandoc generating nicely you need to add a few things to your system:

```bash
sudo apt install pandoc
sudo apt install texlive-xetex
sudo apt install nodejs npm
sudo npm install -g @mermaid-js/mermaid-cli
npx puppeteer browsers install chrome-headless-shell

# And possibly this if you run the npx as non-root
export PUPPETEER_EXECUTABLE_PATH="$HOME/.cache/puppeteer/chrome-headless-shell/linux-142.0.7444.61/chrome-headless-shell-linux64/chrome-headless-shell"
```

Once the above is installed, generating this document is as simple as running the script `generate_pdf.sh`.

If one looks closely, we do something funky in this script. We strip out the first 30 lines from the `report.md` and us that `temp-report.md` file to generate the document. This is because to generate a nice scientific report **heading** page you need the `meta.yaml` file. But that does not translate well to markdown. So here we simply control the markdown rendering by putting in a dedicated title/abstract section that presents nice in markdown viewers. But when we wnat to generate the pdf, we tear away all this and use the `meta.yaml` instead. The info is duplicated for sure, but the amount of duplication is minimal to justify the final outcome - pretty pdf AND markdown.

Why go to all this effort - well ironically these scripts and experience were build up over a year on various other projects, so you as a reader can benefit from all the pain I suffered :-). This author will not profess to expertise here - a lot of time went into using every tool available - google/AI/blogs to hack all the scripts together in the `scripts` folder.

Note - if you want to reuse this for your own project - there be dragons - be prepared for some serious pain here - it will require a lot of bouncing around with google/chatgpt to get the exact output you may want.....

A lot of time will be spend tailoring these lua scripts to control the final pdf rendering. What is good for this project may not be good for the next. Table layout is particularly painful, along with mermaid image generation - specifically their sizing....

BUT - if you are willing to put up with the pain, you get a really nice document!