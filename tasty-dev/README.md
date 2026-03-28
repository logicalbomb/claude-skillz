# tasty-dev

A feedback-driven development system for Claude Code that helps you become a better developer through continuous learning and systematic reflection.

**Status:** Under active development (v0.1.0)

## What It Does

Tasty-dev implements a meta-learning system that captures insights during development and enables continuous improvement across projects:

- **Reflexion Loops**: Capture insights and learnings as they emerge during development
- **Correction Cycles**: Identify and fix recurring mistakes or anti-patterns
- **Weekly Reviews**: Systematic project and knowledge reviews
- **Structured Knowledge**: Store decisions in ADRs and patterns in mulch
- **Cross-Project Learning**: Apply insights from one project to future work

## Prerequisites

- [Claude Code](https://claude.ai/claude-code) CLI
- Python 3.8+ (for hooks and tests)
- Git (for version control of knowledge base)

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/logicalbomb/claude-skillz.git
cd claude-skillz/tasty-dev

# Install to Claude Code skills directory
mkdir -p ~/.claude/skills/tasty-dev
cp -r skills hooks bin SKILL.md ~/.claude/skills/tasty-dev/

# Add skill permission to Claude Code settings
# Edit ~/.claude/settings.json and add:
# {
#   "skills": {
#     "tasty-dev": {
#       "enabled": true
#     }
#   }
# }
```

### Manual Setup

1. Copy the skill directory:
   ```bash
   cp -r tasty-dev ~/.claude/skills/
   ```

2. Enable the skill in your Claude Code configuration

3. Create your knowledge base:
   ```bash
   mkdir -p ~/knowledge-base/{adrs,mulch,reviews}
   cd ~/knowledge-base
   git init
   ```

## Usage

Once installed, use natural language commands with Claude Code:

```
# Capture an insight during development
"I just learned something important - let me reflect on this"

# Correct a previous decision
"That pattern I used yesterday was wrong, I need to correct it"

# Run weekly reviews
"Let's do the weekly project review"
"Time for the knowledge review"
```

### Available Commands

- `reflect` - Capture a development insight or decision
- `correct` - Correct a previous decision or pattern
- `review-project` - Run weekly project review
- `review-knowledge` - Run weekly knowledge repo review

## Knowledge Storage

Tasty-dev organizes your learnings in a structured knowledge base:

```
~/knowledge-base/
├── adrs/           # Architectural Decision Records
├── mulch/          # Tactical patterns and quick wins
└── reviews/        # Weekly review outputs
```

## Development

### Running Tests

```bash
# Install test dependencies
python3 -m venv venv
source venv/bin/activate
pip install pytest pyyaml

# Run tests
pytest tests/ -v
```

### Project Structure

```
tasty-dev/
├── SKILL.md                 # Skill manifest with commands and hooks
├── README.md                # This file
├── bin/                     # CLI utilities
│   ├── init-project-storage # Initialize .tasty-dev in a project
│   ├── capture-reflexion    # Capture insight to queue
│   ├── create-adr           # Create new ADR from template
│   ├── query-adr            # Search ADRs by topic
│   ├── query-mulch          # Search mulch patterns
│   └── run-project-review   # Run weekly project review
├── hooks/                   # Event hooks for auto-triggers
│   ├── detect_reflexion_triggers.py  # Detect reflexion moments
│   └── nudge_weekly_review.py        # Remind about overdue reviews
├── skills/                  # Skill implementations
│   ├── reflexion/capture.md          # Reflexion capture workflow
│   ├── reviews/project-weekly.md     # Weekly review process
│   └── superpowers-enhanced/         # Enhanced superpowers
│       ├── brainstorming-enhanced.md # ADR-aware brainstorming
│       └── writing-plans-enhanced.md # Knowledge-integrated planning
├── templates/               # Templates
│   └── adr-template.md      # Standard ADR format
├── tests/                   # Test suite (21 tests)
└── docs/plans/              # Design documents
```

## Roadmap

- [x] Task 1: Initialize plugin structure
- [x] Task 2: Setup project storage structure
- [x] Task 3: Reflexion trigger detection hook
- [x] Task 4: Reflexion capture skill
- [x] Task 5: ADR creation tool
- [x] Task 6: Project weekly review skill
- [x] Task 7: Enhanced brainstorming skill
- [x] Task 8: Enhanced writing plans skill
- [x] Task 9: Weekly review nudge hook
- [x] Task 10: Integration tests
- [x] Task 11: Comprehensive documentation

## Contributing

This is a personal development tool under active construction. Contributions, suggestions, and feedback are welcome!

## License

MIT License - See LICENSE file for details
