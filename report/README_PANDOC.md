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
