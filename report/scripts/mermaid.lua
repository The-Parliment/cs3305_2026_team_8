-- mermaid.lua — render ```mermaid blocks with mmdc to PNG for PDF.
-- Requires: @mermaid-js/mermaid-cli (mmdc) on PATH.

local counter = 0
local puppeteer_cfg = "scripts/puppeteer.json"  -- <-- we’ll pass this file

local function has_class(el, class)
  if not el.classes then return false end
  for _, c in ipairs(el.classes) do
    if c == class then return true end
  end
  return false
end

function CodeBlock(el)
  if not has_class(el, "mermaid") then return nil end

  counter = counter + 1
  local base = string.format("mermaid-%03d", counter)
  local in_mmd  = base .. ".mmd"
  local out_png = base .. ".png"

  -- write diagram source
  local f = assert(io.open(in_mmd, "w"))
  f:write(el.text)
  f:close()

  -- render via mmdc; pass puppeteer config, set white bg + a bit of scale
  local cmd = string.format('mmdc -i %q -o %q -b white -s 1.25 -p %q',
                            in_mmd, out_png, puppeteer_cfg)
  local ok = os.execute(cmd)
  if ok ~= true and ok ~= 0 then
    io.stderr:write("mermaid.lua: mmdc failed for " .. in_mmd .. "\n")
    return nil
  end

  -- embed image; width=100% fits page width
  return pandoc.Para{ pandoc.Image({ width = "100%" }, out_png) }
end
