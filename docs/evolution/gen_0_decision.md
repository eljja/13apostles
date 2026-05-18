# Generation 0 Decision

**Issue:** What should this program do? (Initial Purpose Definition)

## Candidates
### Candidate 0: AI Task Automation Engine (Automated Local Agent)
- **Description:** A background agent that can monitor folders, run python scripts automatically, and automate tedious daily tasks based on natural language instructions.
- **Cost:** Medium (Requires local LLM or API integration, safe file-system access)
- **Risk:** Medium (Could accidentally modify wrong files if not sandboxed)

### Candidate 1: Personal Knowledge Graph Assistant
- **Description:** An AI tool that ingests daily logs, automatically tags them, and builds a searchable semantic graph of personal knowledge.
- **Cost:** High (Requires embedding models, vector DB, continuous indexing)
- **Risk:** Low (Mostly read-only operations on text data)

### Candidate 2: MAGI-13 Self-Evolving Codebase Framework
- **Description:** A meta-program where the core functionality is to continuously rewrite and optimize its own codebase based on external metrics or goals provided by the user.
- **Cost:** Low (Text manipulation)
- **Risk:** High (Self-destruction or infinite loops, requires strict veto checks)

## Voting Results
- Candidate 0: 63 points 
- Candidate 1: 54 points 
- Candidate 2: 13 points (VETOED)

## Final Selection
**Winner:** Candidate 0 (AI Task Automation Engine (Automated Local Agent))
**Score:** 63

## Next Steps
Creating git branch corresponding to this candidate (e.g. `0`).
