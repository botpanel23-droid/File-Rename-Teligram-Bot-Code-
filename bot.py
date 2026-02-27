const TelegramBot = require("node-telegram-bot-api");
const fs = require("fs");
const axios = require("axios");
const path = require("path");

const token = "8693061713:AAFTcWKRtPlJJudYVrfU38aM7byIednW-eM";
const bot = new TelegramBot(token, { polling: true });

// Store temporary user states
let userStates = {};

// Start Command
bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id,
`👋 Welcome to Public Rename Bot!

📤 Send me any Video or File.
✏️ Then send the new name.
📥 I will resend it without buttons & old caption.

Enjoy 🔥`);
});

// When user sends file/video
bot.on("message", async (msg) => {
  const chatId = msg.chat.id;

  // If waiting for rename name
  if (userStates[chatId] && msg.text && !msg.text.startsWith("/")) {
    const { fileId, mimeType } = userStates[chatId];
    const newName = msg.text.trim();

    try {
      const fileLink = await bot.getFileLink(fileId);

      const response = await axios({
        url: fileLink,
        method: "GET",
        responseType: "stream"
      });

      const filePath = path.join(__dirname, newName);
      const writer = fs.createWriteStream(filePath);

      response.data.pipe(writer);

      writer.on("finish", async () => {
        await bot.sendDocument(chatId, filePath, {
          caption: "✅ Renamed Successfully!"
        });

        fs.unlinkSync(filePath);
      });

      writer.on("error", (err) => console.log(err));

      delete userStates[chatId];

    } catch (err) {
      console.log(err);
      bot.sendMessage(chatId, "❌ Error while renaming.");
    }
  }

  // If file/video received
  if (msg.document || msg.video) {
    const fileId = msg.document ? msg.document.file_id : msg.video.file_id;
    const mimeType = msg.document ? msg.document.mime_type : msg.video.mime_type;

    userStates[chatId] = { fileId, mimeType };

    bot.sendMessage(chatId,
`✏️ Send new file name with extension.

Example:
movie.mp4
file.zip`);
  }
});

console.log("🚀 Public Rename Bot Running...");
