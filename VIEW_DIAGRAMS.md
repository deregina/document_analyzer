# How to View Mermaid Diagrams in ARCHITECTURE.md

## Option 1: VS Code (Recommended)

### Install Extension

1. Open VS Code
2. Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux) to open Extensions
3. Search for: **"Markdown Preview Mermaid Support"**
4. Install the extension by **Matt Bierner**

### View Diagrams

1. Open `ARCHITECTURE.md` in VS Code
2. Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows/Linux) to open Markdown Preview
3. The Mermaid diagrams will render automatically!

**Alternative Extension**: You can also use **"Mermaid Preview"** by vstirbu for a dedicated Mermaid viewer.

---

## Option 2: Online Viewer (No Installation)

1. Go to: https://mermaid.live/
2. Copy the Mermaid code from `ARCHITECTURE.md` (the code between ` ```mermaid ` tags)
3. Paste it into the editor
4. View the rendered diagram instantly!

---

## Option 3: GitHub (If you push to GitHub)

GitHub automatically renders Mermaid diagrams in markdown files. Just:
1. Push your repository to GitHub
2. View the `ARCHITECTURE.md` file on GitHub
3. Diagrams will render automatically!

---

## Option 4: Other Editors

### Obsidian
- Built-in Mermaid support
- Just open the markdown file

### Typora
- Built-in Mermaid support
- Just open the markdown file

### JetBrains IDEs (PyCharm, IntelliJ, etc.)
- Install "Mermaid" plugin from JetBrains Marketplace

---

## Quick Test

To test if it's working, try viewing this simple diagram:

```mermaid
graph LR
    A[Start] --> B[Process]
    B --> C[End]
```

If you see a rendered diagram with boxes and arrows, it's working! ✅

