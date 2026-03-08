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

Note - be prepared for some serious pain here - it will require a lot of bouncing around with google/chatgpt to get the exact output you may want.....

A lot of time will be spend tailoring these lua scripts to control the final pdf rendering. What is good for this project may not be good for the next. Table layout is particularly painful, along with mermaid image generation - specifically their sizing....

BUT - if you are willing to put up with the pain, you get a really nice document.