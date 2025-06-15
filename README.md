# 🧠 Eddix — Real-Time Collaborative Code Editor

Eddix is a basic yet functional real-time collaborative code editor that enables users to create or join shared coding sessions. Built with the aim of simplifying team-based coding, Eddix allows developers to work together on the same set of files — no more sharing ZIPs on WhatsApp!

🔗 **Live Demo**: [https://eddix.onrender.com](https://eddix.onrender.com)

---

## ✨ Features

- ✅ Real-time collaboration with multiple users in the same room
  
- 📁 Upload and share entire folders or files across the room
  
- 💬 Changes reflect instantly using a basic Operational Transformation (OT) algorithm
  
- 💾 Download any file after collaborative editing
  
- 🔐 Room-based isolation — each room is independent
  
- 🧱 Clean and minimal interface using CodeMirror for code editing

---

## 🚀 Motivation

The idea stemmed from a very real and relatable problem: during group projects, my team and I often found ourselves sharing zipped code files on messaging platforms. There was no go-to collaborative coding space we were aware of. That’s when I decided to build one from scratch.

Although I later discovered tools like Replit and CodePen, this project gave me hands-on experience in building one myself — and it was worth every line of code!

---

## 🛠 Tech Stack

- **Backend**: Django, Django Channels
  
- **Realtime Communication**: Redis (cloud-based)
  
- **Frontend**: HTML, CSS, JavaScript
  
- **Editor**: CodeMirror (customized with OT sync logic)

---

## 💡 How It Works

1. A user creates or joins a room via a simple interface.
   
2. Users can upload files or folders.
   
3. All users in the room can view and edit the files simultaneously.
   
4. Changes are synced using a basic custom OT (Operational Transformation) implementation.
   
5. Files can be downloaded individually after collaboration.

---

## 🧑‍💻 Author

Made with 💻 by **Tirth Gajera** as a solo project.

---

## 🚧 Limitations & Roadmap

Eddix is still in its early stages and comes with a few limitations:

- No user authentication or persistent sessions
  
- Limited to basic OT; may lag under heavy simultaneous edits
  
- No code execution or syntax checking
  
- No UI for file tree or rich UX

### Future Plans

- Add user authentication & persistent room history
  
- Improve performance and scalability
  
- Add syntax-aware OT for better precision
  
- Support for live chat or commenting
  
- Real-time file tree viewer

---

## 📜 License

MIT License

---

## 🙌 Acknowledgements

Thanks to the open-source community and tools like CodeMirror, Django, and Redis for enabling this project.
