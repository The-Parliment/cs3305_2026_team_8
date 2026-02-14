-- tabwidths.lua — widths + smaller font + zebra striping (safe with longtable)
-- Env:
--   TABLE_FONT        -> \small | \footnotesize | \scriptsize   (default: \footnotesize)
--   TABLE_ROWSTRETCH  -> line height multiplier                  (default: 1.08)
--   TABLE_STRIPE      -> LaTeX color for odd rows (default: gray!12)
--   TABLE_STRIPE_EVEN -> LaTeX color for even rows (default: white)

local widths_5 = {0.16, 0.22, 0.30, 0.08, 0.24}  -- Area, Reco, Repo, Status, Notes
local size_cmd = os.getenv("TABLE_FONT") or "\\footnotesize"
local stretch  = tonumber(os.getenv("TABLE_ROWSTRETCH") or "1.08")
local stripe_odd  = os.getenv("TABLE_STRIPE") or "gray!12"
local stripe_even = os.getenv("TABLE_STRIPE_EVEN") or "white"

function Table(tbl)
  -- only touch 5-col tables like yours
  if #tbl.colspecs == 5 then
    for i, w in ipairs(widths_5) do
      tbl.colspecs[i].align = "Left"
      tbl.colspecs[i].width = w
    end

    -- scope font + row spacing + rowcolors to this table only
    local pre = table.concat({
      "\\begingroup",
      string.format("\\renewcommand{\\arraystretch}{%.2f}", stretch),
      size_cmd,
      "\\rowcolors{2}{" .. stripe_odd .. "}{" .. stripe_even .. "}"  -- start striping from row 2
    }, "\n")
    local post = "\\par\\endgroup"

    return { pandoc.RawBlock("latex", pre), tbl, pandoc.RawBlock("latex", post) }
  end
  return tbl
end
