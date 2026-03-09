-- mermaid-scale.lua
function Image(el)
  if FORMAT:match("latex") and el.src:match("mermaid") then
    local scale = el.attributes["scale"] or "0.8"
    local latex = string.format(
      "{\\centering\\includegraphics[width=%s\\linewidth,height=%s\\textheight,keepaspectratio]{%s}\\par}",
      scale, scale, el.src
    )
    return pandoc.RawInline("latex", latex)
  end
  return el
end

function Figure(el)
  if not FORMAT:match("latex") then return nil end
  -- find the image inside the figure
  local img = nil
  for _, block in ipairs(el.content) do
    for _, inline in ipairs(block.content or {}) do
      if inline.t == "Image" and inline.src:match("mermaid") then
        img = inline
      end
    end
  end
  if not img then return nil end

  local scale = img.attributes["scale"] or "0.8"
  local caption = pandoc.utils.stringify(el.caption)
  local latex = string.format(
    "\\begin{figure}[H]\\centering\\includegraphics[width=%s\\linewidth,height=%s\\textheight,keepaspectratio]{%s}\\par\\small\\textit{%s}\\end{figure}",
    scale, scale, img.src, caption
  )
  return pandoc.RawBlock("latex", latex)
end