
const express = require("express");
const bodyParser = require("body-parser");
const libxmljs = require("libxmljs");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const crypto = require("crypto");

const app = express();

app.use(bodyParser.json());
app.use(bodyParser.text({ type: "application/xml" }));

// Restrict upload size and store files in memory.
const storage = multer.memoryStorage();

const upload = multer({
  storage,
  limits: {
    fileSize: 5 * 1024 * 1024,
    files: 1,
  },
});

// Secure file upload endpoint.
app.post("/ufo/upload", upload.single("file"), (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }

  // Allow only simple text files for this challenge.
  if (path.extname(req.file.originalname).toLowerCase() !== ".txt") {
    return res.status(400).send("Invalid file type.");
  }

  // Never use the original filename as a filesystem path.
  const safeFilename = `${crypto.randomUUID()}.txt`;
  const uploadDirectory = path.join(__dirname, "uploads");

  try {
    fs.mkdirSync(uploadDirectory, { recursive: true });

    const uploadedFilePath = path.join(uploadDirectory, safeFilename);
    fs.writeFileSync(uploadedFilePath, req.file.buffer, { flag: "wx" });

    return res.status(200).send("File uploaded successfully.");
  } catch (error) {
    console.error("File upload failed");
    return res.status(500).send("File upload failed.");
  }
});

// JSON and XML endpoint.
app.post("/ufo", (req, res) => {
  const contentType = req.headers["content-type"];

  if (contentType && contentType.startsWith("application/json")) {
    console.log("Received JSON request");
    return res.status(200).json({
      ufo: "Received JSON data from an unknown planet.",
    });
  }

  if (contentType && contentType.startsWith("application/xml")) {
    try {
      if (typeof req.body !== "string") {
        throw new Error("Invalid XML body");
      }

      // Reject DTD declarations and entity definitions.
      if (/<!DOCTYPE|<!ENTITY/i.test(req.body)) {
        throw new Error("DTD and entity declarations are not allowed");
      }

      const xmlDoc = libxmljs.parseXml(req.body, {
        replaceEntities: false,
        recover: false,
        nonet: true,
      });

      if (!xmlDoc.root()) {
        throw new Error("Missing XML root element");
      }

      const extractedContent = [];

      xmlDoc.root().childNodes().forEach((node) => {
        if (node.type() === "element") {
          extractedContent.push(node.text());
        }
      });

      // XML content is treated strictly as data.
      // No shell commands or external entities are executed.
      return res
        .status(200)
        .type("text/plain")
        .send(extractedContent.join(" "));
    } catch (error) {
      console.error("XML parsing or validation failed");
      return res.status(400).send("Invalid XML: request rejected");
    }
  }

  return res.status(405).send("Unsupported content type");
});

const PORT = process.env.PORT || 3000;

const server = app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

module.exports = server;
