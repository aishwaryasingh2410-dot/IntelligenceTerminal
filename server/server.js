const express = require("express")
const cors = require("cors")

const { connectDB } = require("./config/mongo")
const optionsRoutes = require("./routes/options")

const app = express()

app.use(cors())
app.use(express.json())

app.get("/", (req, res) => {
  res.json({
    status: "ok",
    service: "options-api",
    message: "Options API is running",
    endpoints: [
      "/api/options/summary",
      "/api/options/live-market",
      "/api/options/top-oi",
      "/api/options/pcr",
    ],
  })
})

app.use("/api/options", optionsRoutes)

async function startServer() {
  try {

    await connectDB()

    app.listen(5000, () => {
      console.log("Server running on port 5000")
    })

  } catch (error) {

    console.error("Failed to start server:", error)

  }
}

startServer()
