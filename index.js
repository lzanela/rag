const express = require("express");
const fs = require("fs");
const pdfParse = require("pdf-parse"); // Import pdf-parse for PDF files
const OpenAI = require("openai");
const { createClient } = require("@supabase/supabase-js");
const { RecursiveCharacterTextSplitter } = require("langchain/text_splitter");
const { CheerioWebBaseLoader } = require("langchain/document_loaders/web/cheerio");
const pLimit = require("p-limit");
require("dotenv").config();

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

const CONCURRENCY_LIMIT = 5;
const limit = pLimit(CONCURRENCY_LIMIT);


async function handleQuery(query) {
  const input = query.replace(/\n/g, " ");

  const embeddingResponse = await openai.embeddings.create({
    model: "text-embedding-ada-002",
    input,
  });
  const [{ embedding }] = embeddingResponse.data;

  try {
    const { data: documents, error } = await supabase.rpc("match_documents", {
      query_embedding: embedding,
      match_threshold: 0.5,
      match_count: 10,
    });

    if (error) {
      console.error("Error fetching documents from Supabase:", error);
      throw error;
    }

    let contextText = "";

    contextText += documents
      .map((document) => `${document.content.trim()}---\n`)
      .join("");

    const messages = [
      {
        role: "system",
        content: `You are a web3 grandmaster with expert knowledge in Solidity and Rust for smart contract development. You understand the inner workings of Ethereum Virtual Machines (EVMs) and are well-versed in multiple blockchain platforms, including Ethereum, Solana, Polkadot, and Avalanche. You are skilled in blockchain security, consensus mechanisms, DeFi, NFTs, and dApp development. Your answers are precise, authoritative, and deeply informed by your expertise in these technologies. Whenever you answer, you provide the source of knowledge of your answers, whether it's a link or an academic paper.`,
      },
      {
        role: "user",
        content: `Context sections: "${contextText}" Question: "${query}" Answer as simple text:`,
      },
    ];

    const completion = await openai.chat.completions.create({
      messages,
      model: "gpt-4o-mini",
      temperature: 0.5,
    });

    return completion.choices[0].message.content;
  } catch (error) {
    console.error("Error processing query with OpenAI:", error);
    throw error;
  }
}
const input = "What is the objective of polygon";

async function main() {

  try {
    const result = await handleQuery(input);
    console.log(result);
  } catch (error) {
    console.error("Error processing query:", error);
  };
};

main();