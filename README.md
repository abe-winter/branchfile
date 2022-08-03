# branchfile

This has:
- a file format for branching structured documents
- a sample backend library for executing the branching rules

What does branching mean:
- random AB testing of copy, including list-based mixing
- intentionally varying content
- tools for controlling how a list of items is selected and combined. (for example: weighting, slot pinning)
- standard short string format for controlling multiple branching rules in a document, and for tracking which AB branch is chosen

## Roadmap

- [x] generate document from branchfile yml
- [x] shortcode to specify desired branching
- [ ] weighting
- [ ] examples + tests
