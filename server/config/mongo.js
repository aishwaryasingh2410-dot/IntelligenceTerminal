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
if (!uri) {
    throw new Error("Missing MONGO_URI environment variable. Set it in .env or the environment.")
}

const client = new MongoClient(uri)

let collection
let mongoAvailable = false

async function connectDB() {
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
    return client.db("cursor_database")
}

function isMongoAvailable() {
    return mongoAvailable
}

module.exports = { connectDB, getCollection, getDB, isMongoAvailable }
