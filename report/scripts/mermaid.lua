-- mermaid.lua — render ```mermaid blocks with mmdc to PNG for PDF.
-- Requires: @mermaid-js/mermaid-cli (mmdc) on PATH.

local counter = 0
local puppeteer_cfg = "scripts/puppeteer.json"

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

  local f = assert(io.open(in_mmd, "w"))
  f:write(el.text)
  f:close()

  local cmd = string.format('mmdc -i %q -o %q -b white -s 1.25 -p %q',
                            in_mmd, out_png, puppeteer_cfg)
  local ok = os.execute(cmd)
  if ok ~= true and ok ~= 0 then
    io.stderr:write("mermaid.lua: mmdc failed for " .. in_mmd .. "\n")
    return nil
  end

  local caption = el.attributes and el.attributes["fig-cap"]
  local scale   = el.attributes and el.attributes["scale"]

  local attrs = {}
  if scale then attrs["scale"] = scale end

  if caption then
    local img = pandoc.Image(
      pandoc.read(caption, "markdown").blocks[1].content,
      out_png, "", attrs
    )
    return pandoc.Figure(
      pandoc.Blocks{ pandoc.Plain{ img } },
      { long = pandoc.read(caption, "markdown").blocks }
    )
  else
    local img = pandoc.Image({}, out_png, "", attrs)
    return pandoc.Para{ img }
  end
end