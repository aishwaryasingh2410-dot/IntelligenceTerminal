const fs = require("fs")
const path = require("path")

const DATA_DIR = path.resolve(__dirname, "..", "..", "data")

let cachedRecords = null

function toNumber(value) {
  const num = Number(value)
  return Number.isFinite(num) ? num : 0
}

function parseCsv(content) {
  const lines = content.split(/\r?\n/).filter(Boolean)
  if (lines.length < 2) return []

  const headers = lines[0].split(",").map(h => h.trim())

  return lines.slice(1).map(line => {
    const values = line.split(",")
    const record = {}

    headers.forEach((header, index) => {
      record[header] = values[index]?.trim() ?? ""
    })

    record.strike = toNumber(record.strike)
    record.oi_CE = toNumber(record.oi_CE)
    record.oi_PE = toNumber(record.oi_PE)

    return record
  }).filter(record => record.strike)
}

function loadLocalOptionsData() {
  if (cachedRecords) return cachedRecords
  if (!fs.existsSync(DATA_DIR)) return []

  const files = fs.readdirSync(DATA_DIR).filter(file => file.endsWith(".csv"))
  cachedRecords = files.flatMap(file => {
    const fullPath = path.join(DATA_DIR, file)
    const content = fs.readFileSync(fullPath, "utf8")
    return parseCsv(content)
  })

  return cachedRecords
}

module.exports = { loadLocalOptionsData }
