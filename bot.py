const TelegramBot = require("node-telegram-bot-api");
const fs = require("fs");
const axios = require("axios");

const token = "8693061713:AAFTcWKRtPlJJudYVrfU38aM7byIednW-eM";
const bot = new TelegramBot(token, { polling: true });

let userStates = {};

bot.on("message", async (msg) => {
  const chatId = msg.chat.id;

  // If user already sent file and waiting for new name
  if (userStates[chatId] && msg.text) {
    const fileId = userStates[chatId].fileId;
    const newName = msg.text;

    try {
      const fileLink = await bot.getFileLink(fileId);
      const response = await axios({
        url: fileLink,
        method: "GET",
        responseType: "stream"
      });

      const filePath = `./${newName}`;
      const writer = fs.createWriteStream(filePath);

      response.data.pipe(writer);

      writer.on("finish", async () => {
        await bot.sendDocument(chatId, filePath, {
          caption: "✅ File Renamed Successfully!"
        });

        fs.unlinkSync(filePath);
      });

      writer.on("error", (err) => {
        console.log(err);
      });

      delete userStates[chatId];

    } catch (err) {
      console.log(err);
      bot.sendMessage(chatId, "❌ Error while renaming file.");
    }
  }

  // If user sends document or video
  if (msg.document || msg.video) {
    const fileId = msg.document ? msg.document.file_id : msg.video.file_id;

    userStates[chatId] = { fileId };

    bot.sendMessage(chatId, "✏️ Send me the new file name (with extension).\nExample:\nmovie.mp4");
  }
});

console.log("🤖 Rename Bot Running...");
