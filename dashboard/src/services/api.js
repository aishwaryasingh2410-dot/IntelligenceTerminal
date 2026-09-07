import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000/api",
});

export const getSummary = () => API.get("/options/summary");
export const getTopOI = () => API.get("/options/top-oi");
export const getCallPutOI = () => API.get("/options/call-put-oi");
export const getPCR = () => API.get("/options/pcr");
export const getMaxPain = () => API.get("/options/max-pain");
export const getUnusualOI = () => API.get("/options/unusual-oi");
export const getNiftyTicks = () => API.get("/options/nifty-ticks");
export const getLiveMarket = () => API.get("/options/live-market");
