const express = require("express")
const cors = require("cors")

const { connectDB } = require("./config/mongo")
const optionsRoutes = require("./routes/options")

const app = express()

app.use(cors())
app.use(express.json())

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
