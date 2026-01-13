import { SentimentData } from "../types";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

// Extract 11-char YouTube video ID from URL or fallback assuming direct ID supplied
const extractVideoId = (input: string): string => {
  const match = input.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/(?:v|e(?:mbed)?))|(?:v|e(?:mbed)?|watch)(?:\?v=|\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : input.trim();
};

export const analyzeVideoSentiment = async (urlOrId: string): Promise<SentimentData> => {
  const videoId = extractVideoId(urlOrId);
  const res = await fetch(`${BACKEND_URL}/analyse/${videoId}`);
  if (!res.ok) {
    throw new Error(`Backend error ${res.status}`);
  }
  const data: SentimentData = await res.json();
  return data;
};
