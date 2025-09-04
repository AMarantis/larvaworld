# Larvaworld Architecture Documentation

## Overview

This document contains comprehensive architecture diagrams for the larvaworld project - a virtual lab for Drosophila larva behavioral modeling and analysis.

## Types of Diagrams

Developers use various types of diagrams to illustrate project architecture:

### 1. Project Structure Diagram
- **Purpose**: Shows the hierarchical structure of folders and files
- **Usage**: Understanding code organization
- **In larvaworld**: Shows the modular structure with separate modules for CLI, GUI, dashboards, and core library

### 2. System Architecture Diagram
- **Purpose**: Shows main components and their relationships
- **Usage**: Understanding high-level architecture
- **In larvaworld**: Illustrates the layers (UI, Application, Core Model, Data Processing)

### 3. Class Diagram
- **Purpose**: Shows classes and relationships between them
- **Usage**: Understanding object-oriented design
- **In larvaworld**: Shows the hierarchy of Larva classes and behavioral modules

### 4. Data Flow Diagram
- **Purpose**: Shows how data flows through the system
- **Usage**: Understanding data processing
- **In larvaworld**: Illustrates the pipeline from input data to analysis results

### 5. Interaction Diagram (Sequence Diagram)
- **Purpose**: Shows interaction between components
- **Usage**: Understanding execution flow
- **In larvaworld**: Shows how modules interact during simulation

### 6. Technology Stack Diagram
- **Purpose**: Shows technologies and libraries
- **Usage**: Understanding dependencies
- **In larvaworld**: Illustrates Python ecosystem, scientific libraries, visualization tools

## How to Use the Diagrams

### For New Developers
1. **Start with Project Structure Diagram** - Understand folder structure
2. **View System Architecture Diagram** - Understand main components
3. **Study Class Hierarchy Diagram** - Understand classes and relationships

### For Contributors
1. **Use Behavioral Modules Diagram** - Understand detailed architecture
2. **View Environment Architecture Diagram** - Understand environment system
3. **Study Simulation Modes Diagram** - Understand different simulation approaches

### For Researchers
1. **Use Data Flow Diagram** - Understand analysis pipeline
2. **View Technology Stack Diagram** - Understand technologies used
3. **Study Module Interaction Diagram** - Understand how behavioral modules work

## Tools for Viewing Diagrams

### Online Viewers
- **Mermaid Live Editor**: https://mermaid.live/
- **GitHub**: Diagrams display automatically in GitHub repositories
- **GitLab**: Supports Mermaid diagrams

### Local Tools
- **VS Code**: With Mermaid extension
- **Obsidian**: With Mermaid plugin
- **Typora**: Built-in Mermaid support

### Command Line
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Convert to PNG
mmdc -i architecture_diagrams.md -o diagrams.png

# Convert to SVG
mmdc -i architecture_diagrams.md -o diagrams.svg
```

## Updating Diagrams

When making changes to the project:

1. **Update relevant diagrams** in `architecture_diagrams.md`
2. **Check accuracy** of relationships and dependencies
3. **Test diagrams** in Mermaid viewer
4. **Update this README** if needed

## Best Practices

### For Diagrams
- **Keep them simple** - Avoid excessive complexity
- **Use consistent naming** - Same names across all diagrams
- **Group related elements** - Use subgraphs
- **Add descriptions** - Explain the significance of each component

### For Documentation
- **Keep updated** - Update diagrams with changes
- **Use version control** - Track changes in diagrams
- **Add context** - Explain why each component exists
- **Create multiple views** - Different diagrams for different purposes

## Sources and References

- **Mermaid Documentation**: https://mermaid-js.github.io/mermaid/
- **UML Diagrams**: https://www.uml.org/
- **Software Architecture Patterns**: https://martinfowler.com/architecture/
- **Larvaworld Documentation**: https://larvaworld.readthedocs.io

## Contributing

If you want to improve the diagrams:

1. **Fork the repository**
2. **Make your changes** in `architecture_diagrams.md`
3. **Test the diagrams** in Mermaid viewer
4. **Create Pull Request** with description of changes

---

*This document was created to help understand the larvaworld project architecture. For more information, see the [README.md](../README.md) and [official documentation](https://larvaworld.readthedocs.io).*
