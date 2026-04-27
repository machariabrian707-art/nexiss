import fs from "fs";
import OpenAI from "openai";
import dotenv from "dotenv";

dotenv.config();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const filePath = process.argv[2];

if (!filePath) {
  console.log("Please provide a file: node ai-review.js <file>");
  process.exit(1);
}

const code = fs.readFileSync(filePath, "utf8");

if (code.length > 12000) {
  console.log("File too large for review");
  process.exit(0);
}

try {
  const response = await openai.chat.completions.create({
    model: "gpt-4.1",
    messages: [
      {
        role: "system",
        content:
          "You are a senior software engineer. Review code strictly. Output: bugs, risks, improvements, and improved version.",
      },
      {
        role: "user",
        content: `FILE: ${filePath}\n\nCODE:\n${code}`,
      },
    ],
  });

  const output = response.choices[0].message.content;

  fs.writeFileSync(filePath + ".review.txt", output);

  console.log("✅ AI review generated:", filePath);
} catch (error) {
  console.error("❌ AI review failed:", error.message);
}