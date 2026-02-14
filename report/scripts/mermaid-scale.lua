-- mermaid-scale.lua
function Image(el)
  if FORMAT:match("latex") and el.src:match("mermaid") then
    local latex = string.format(
      "{\\centering\\includegraphics[width=0.8\\linewidth,height=0.8\\textheight,keepaspectratio]{%s}\\par}",
      el.src
    )
    return pandoc.RawInline("latex", latex)
  end
  return el
end
