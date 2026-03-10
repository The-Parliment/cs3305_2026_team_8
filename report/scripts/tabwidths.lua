-- tabwidths.lua — column widths + smaller font + zebra striping (safe with longtable)
-- Env:
--   TABLE_FONT        -> \small | \footnotesize | \scriptsize   (default: \footnotesize)
--   TABLE_ROWSTRETCH  -> line height multiplier                  (default: 1.08)
--   TABLE_STRIPE      -> LaTeX color for odd rows (default: gray!12)
--   TABLE_STRIPE_EVEN -> LaTeX color for even rows (default: white)

local widths_2 = {0.18, 0.82}        -- Tool | Purpose
local widths_3 = {0.25, 0.35, 0.40}  -- Behaviour | Col A | Col B

local size_cmd    = os.getenv("TABLE_FONT")        or "\\footnotesize"
local stretch     = tonumber(os.getenv("TABLE_ROWSTRETCH") or "1.08")
local stripe_odd  = os.getenv("TABLE_STRIPE")      or "gray!12"
local stripe_even = os.getenv("TABLE_STRIPE_EVEN") or "white"

function Table(tbl)
  local widths = nil
  if     #tbl.colspecs == 2 then widths = widths_2
  elseif #tbl.colspecs == 3 then widths = widths_3
  end

  if not widths then return tbl end

  for i, w in ipairs(widths) do
    tbl.colspecs[i][1] = "AlignLeft"
    tbl.colspecs[i][2] = w
  end

  local pre = table.concat({
    "\\begingroup",
    string.format("\\renewcommand{\\arraystretch}{%.2f}", stretch),
    size_cmd,
    "\\rowcolors{2}{" .. stripe_odd .. "}{" .. stripe_even .. "}"
  }, "\n")
  local post = "\\par\\endgroup"

  return { pandoc.RawBlock("latex", pre), tbl, pandoc.RawBlock("latex", post) }
end