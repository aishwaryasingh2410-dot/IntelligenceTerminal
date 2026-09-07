const path = require("path")
require("dotenv").config({ path: path.resolve(__dirname, "..", "..", ".env") })

const dns = require("dns")
const { MongoClient } = require("mongodb")

const dnsServers = (process.env.MONGO_DNS_SERVERS || "8.8.8.8,1.1.1.1")
    .split(",")
    .map(server => server.trim())
    .filter(Boolean)

if (dnsServers.length > 0) {
    dns.setServers(dnsServers)
}

const uri = process.env.MONGO_URI

let client = null
let collection = null
let mongoAvailable = false

if (uri) {
    client = new MongoClient(uri)
}

async function connectDB() {
    if (!client) {
        console.log("MongoDB not configured, using local CSV fallback")
        return
    }

    try {
        await client.connect()

        const db = client.db("cursor_database")
        collection = db.collection("options_chain")
        mongoAvailable = true

        console.log("MongoDB connected")
    } catch (error) {
        collection = null
        mongoAvailable = false

        console.warn("MongoDB unavailable, using local CSV fallback")
        console.warn(error.message)
    }
}

function getCollection() {
    return collection
}

function getDB() {
    if (!client) return null
    return client.db("cursor_database")
}

function isMongoAvailable() {
    return mongoAvailable
}

module.exports = {
    connectDB,
    getCollection,
    getDB,
    isMongoAvailable
}
