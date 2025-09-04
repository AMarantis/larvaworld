# Larvaworld Architecture Diagrams

This folder contains comprehensive architecture diagrams for the larvaworld project.

## Viewing the Diagrams

### Option 1: GitHub (Recommended)
- Open `architecture_diagrams.md` in GitHub
- The Mermaid diagrams should render automatically
- If you see "Unable to render rich display", try refreshing the page

### Option 2: Mermaid Live Editor
1. Go to https://mermaid.live/
2. Copy the Mermaid code from any diagram section
3. Paste it into the editor to see the rendered diagram

### Option 3: VS Code / Cursor
1. Install the Mermaid extension
2. Open `architecture_diagrams.md`
3. Use Cmd+Shift+V for markdown preview

### Option 4: Command Line Export
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Export to PNG
mmdc -i architecture_diagrams.md -o diagrams.png

# Export to SVG
mmdc -i architecture_diagrams.md -o diagrams.svg
```

## Diagram Contents

The `architecture_diagrams.md` file contains 10 comprehensive diagrams:

1. **Project Structure Diagram** - Hierarchical folder and file structure
2. **System Architecture Diagram** - High-level system components and relationships
3. **Larva Model Architecture** - Internal structure of the Larva Agent
4. **Data Flow Diagram** - Data flow from input to output
5. **Module Interaction Diagram** - Module interactions during simulation
6. **Technology Stack Diagram** - Technologies and libraries used
7. **Behavioral Modules Detailed Architecture** - Detailed behavioral module structure
8. **Environment and Arena Architecture** - Environment system architecture
9. **Simulation Modes and Workflows** - Different simulation approaches
10. **Class Hierarchy and Inheritance Diagram** - Class relationships and inheritance

## Documentation

See `ARCHITECTURE_README.md` for detailed usage instructions and best practices.

## Troubleshooting

If diagrams don't render in GitHub:
1. Make sure you're viewing the file in GitHub (not a local copy)
2. Try refreshing the page
3. Check if your browser supports Mermaid rendering
4. Use the Mermaid Live Editor as an alternative

## Contributing

When updating diagrams:
1. Test them in Mermaid Live Editor first
2. Ensure they follow Mermaid syntax guidelines
3. Update this README if needed
4. Test rendering in GitHub after pushing changes
