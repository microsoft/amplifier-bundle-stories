# Stories Bundle Backport Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Backport improvements from ramparte/amplifier-stories (v2.0.0) into microsoft/amplifier-bundle-stories (v1.0.0)
**Architecture:** Surgical copy-and-adapt operation with namespace fixes and validation checkpoints
**Tech Stack:** Markdown files, Python tools, sed for namespace replacement, Amplifier validation recipes

---

## Prerequisites

Before starting, ensure you're in the correct working directory:

```bash
cd /home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories
pwd  # Should show: /home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories
```

Verify both source and target directories exist:
```bash
ls -la /home/bkrabach/dev/update-stories-bundle/amplifier-stories/agents | wc -l  # Should show 11 agent files
ls -la /home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories/agents | wc -l  # Should show 11 agent files
```

---

### Task 1: Update context/storyteller-instructions.md

**Files:**
- Source: `/home/bkrabach/dev/update-stories-bundle/amplifier-stories/context/storyteller-instructions.md`
- Target: `/home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories/context/storyteller-instructions.md`

**Step 1: Copy file from source to target**
```bash
cp /home/bkrabach/dev/update-stories-bundle/amplifier-stories/context/storyteller-instructions.md \
   /home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories/context/storyteller-instructions.md
```

**Step 2: Fix namespace references**
```bash
sed -i 's/@amplifier-module-stories:/@stories:/g' context/storyteller-instructions.md
```

**Step 3: Verify namespace fix worked**
```bash
grep -n "@amplifier-module-stories:" context/storyteller-instructions.md
```
Expected: No output (all references should be fixed)

**Step 4: Verify new @stories: references exist**
```bash
grep -n "@stories:" context/storyteller-instructions.md
```
Expected: Shows lines with `@stories:` namespace references

**Step 5: Check file was updated**
```bash
git status
```
Expected: Shows `context/storyteller-instructions.md` as modified

---

### Task 2: Update context/presentation-styles.md

**Files:**
- Source: `/home/bkrabach/dev/update-stories-bundle/amplifier-stories/context/presentation-styles.md`
- Target: `/home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories/context/presentation-styles.md`

**Step 1: Copy file from source to target**
```bash
cp /home/bkrabach/dev/update-stories-bundle/amplifier-stories/context/presentation-styles.md \
   /home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories/context/presentation-styles.md
```

**Step 2: Fix namespace references**
```bash
sed -i 's/@amplifier-module-stories:/@stories:/g' context/presentation-styles.md
```

**Step 3: Verify namespace fix worked**
```bash
grep -n "@amplifier-module-stories:" context/presentation-styles.md
```
Expected: No output (all references should be fixed)

**Step 4: Check file was updated**
```bash
git status
```
Expected: Shows both context files as modified

---

### Task 3: Update All 11 Agent Files

**Files:**
- Source: `/home/bkrabach/dev/update-stories-bundle/amplifier-stories/agents/*.md`
- Target: `/home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories/agents/*.md`

All 11 agent files: `case-study-writer.md`, `community-manager.md`, `content-adapter.md`, `content-strategist.md`, `data-analyst.md`, `executive-briefer.md`, `marketing-writer.md`, `release-manager.md`, `story-researcher.md`, `storyteller.md`, `technical-writer.md`

**Step 1: Copy all agent files from source to target**
```bash
cp /home/bkrabach/dev/update-stories-bundle/amplifier-stories/agents/*.md \
   /home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories/agents/
```

**Step 2: Fix namespace references in all agent files**
```bash
sed -i 's/@amplifier-module-stories:/@stories:/g' agents/*.md
```

**Step 3: Verify namespace fixes worked across all files**
```bash
grep -n "@amplifier-module-stories:" agents/*.md
```
Expected: No output (all references should be fixed in all files)

**Step 4: Verify new @stories: references exist**
```bash
grep -c "@stories:" agents/*.md
```
Expected: Shows count of `@stories:` references in each agent file

**Step 5: Check all files were updated**
```bash
git status
```
Expected: Shows all 11 agent files plus 2 context files as modified

**Step 6: Verify file count**
```bash
ls -la agents/ | grep ".md" | wc -l
```
Expected: Shows 11 (all agent files present)

---

### Task 4: Replace tools/html2pptx.py with v2

**Files:**
- Source: `/home/bkrabach/dev/update-stories-bundle/amplifier-stories/tools/html2pptx_v2.py`
- Target: `/home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories/tools/html2pptx.py` (replacing existing)

**Step 1: Copy and rename html2pptx_v2.py to html2pptx.py**
```bash
cp /home/bkrabach/dev/update-stories-bundle/amplifier-stories/tools/html2pptx_v2.py \
   tools/html2pptx.py
```

**Step 2: Check for any namespace references in the Python file**
```bash
grep -n "amplifier-module-stories" tools/html2pptx.py
```
Expected: No output (Python tools don't contain namespace references)

**Step 3: Verify file was replaced**
```bash
git status
```
Expected: Shows `tools/html2pptx.py` as modified

**Step 4: Quick check the file is the v2 version**
```bash
head -5 tools/html2pptx.py
```
Expected: Should show the updated v2 version header/comments

---

### Task 5: Add tools/pptx_verify.py

**Files:**
- Source: `/home/bkrabach/dev/update-stories-bundle/amplifier-stories/tools/pptx_verify.py`
- Target: `/home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories/tools/pptx_verify.py` (new file)

**Step 1: Copy pptx_verify.py as new file**
```bash
cp /home/bkrabach/dev/update-stories-bundle/amplifier-stories/tools/pptx_verify.py \
   tools/pptx_verify.py
```

**Step 2: Check for any namespace references in the Python file**
```bash
grep -n "amplifier-module-stories" tools/pptx_verify.py
```
Expected: No output (Python tools don't contain namespace references)

**Step 3: Verify new file was added**
```bash
git status
```
Expected: Shows `tools/pptx_verify.py` as a new file

**Step 4: Verify file is executable Python**
```bash
head -3 tools/pptx_verify.py
```
Expected: Should show Python shebang and imports

---

### Task 6: Add tools/deck-style-fix.py

**Files:**
- Source: `/home/bkrabach/dev/update-stories-bundle/amplifier-stories/tools/deck-style-fix.py`
- Target: `/home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories/tools/deck-style-fix.py` (new file)

**Step 1: Copy deck-style-fix.py as new file**
```bash
cp /home/bkrabach/dev/update-stories-bundle/amplifier-stories/tools/deck-style-fix.py \
   tools/deck-style-fix.py
```

**Step 2: Check for any namespace references in the Python file**
```bash
grep -n "amplifier-module-stories" tools/deck-style-fix.py
```
Expected: No output (Python tools don't contain namespace references)

**Step 3: Verify new file was added**
```bash
git status
```
Expected: Shows both new tool files plus all previous modifications

**Step 4: Verify all tools are present**
```bash
ls -la tools/
```
Expected: Should show `html2pptx.py`, `pptx_verify.py`, `deck-style-fix.py` plus existing tools

---

### Task 7: Run Bundle Validation Recipe

**Step 1: Validate the updated bundle loads correctly**
```bash
amplifier recipes execute @recipes:validation/bundle-validation.yaml --context bundle_path=$(pwd)
```
Expected: Bundle validation passes with no errors

**Step 2: If validation fails, check the error details**
If the above command fails, examine the output carefully for:
- Missing agent references
- Invalid context file paths  
- Broken cross-references between agents
- Malformed YAML frontmatter

**Step 3: Document any validation errors**
If errors are found, note them for fixing in Task 9:
```bash
echo "Bundle validation errors found - see Task 9" >> validation-issues.txt
```

---

### Task 8: Run Agent Validation Recipe

**Step 1: Validate all agent descriptions parse correctly**
```bash
amplifier recipes execute @recipes:validation/agent-validation.yaml --context bundle_path=$(pwd)
```
Expected: Agent validation passes with no errors

**Step 2: If validation fails, check specific agent issues**
If the above command fails, examine output for:
- Malformed example blocks
- Broken @stories: cross-references
- Invalid agent frontmatter
- Description parsing errors

**Step 3: Document any agent validation errors**
If errors are found, note them for fixing in Task 9:
```bash
echo "Agent validation errors found - see Task 9" >> validation-issues.txt
```

---

### Task 9: Fix Any Validation Issues and Commit

**Step 1: Check if any validation issues were found**
```bash
test -f validation-issues.txt && cat validation-issues.txt || echo "No validation issues recorded"
```

**Step 2: If issues exist, fix them systematically**
For common issues:
- **Namespace references**: Double-check all `@stories:` references are correct
- **Agent cross-references**: Verify agent names match exactly between files
- **File paths**: Ensure context file paths in agents are valid

Fix command examples:
```bash
# Re-run namespace fix if any were missed
grep -r "@amplifier-module-stories:" . --exclude-dir=.git
# Fix any found references manually with sed or direct editing
```

**Step 3: Re-run validation after fixes**
```bash
amplifier recipes execute @recipes:validation/bundle-validation.yaml --context bundle_path=$(pwd)
amplifier recipes execute @recipes:validation/agent-validation.yaml --context bundle_path=$(pwd)
```
Expected: Both validations pass

**Step 4: Clean up validation tracking file**
```bash
rm -f validation-issues.txt
```

**Step 5: Final verification of all changes**
```bash
git status
```
Expected: Shows 13 modified files (2 context + 11 agents) and 2 new files (tools)

**Step 6: Verify no leftover namespace references**
```bash
grep -r "@amplifier-module-stories:" . --exclude-dir=.git
```
Expected: No output (all references should be fixed)

**Step 7: Commit all changes**
```bash
git add .
git commit -m "feat: backport improvements from ramparte stories v2.0.0

- Enhanced agent descriptions with PASS IN parameter specs
- Added WCAG accessibility compliance to presentation styles  
- Included source verification safeguards in storyteller instructions
- Added quality gates and antagonistic review checklists
- Updated html2pptx.py to v2 with improved CSS handling
- Added pptx_verify.py and deck-style-fix.py production tools
- Fixed namespace references from @amplifier-module-stories: to @stories:
- Preserved emojis and agent meta blocks as specified

All bundle and agent validations pass."
```

**Step 8: Verify commit was successful**
```bash
git log --oneline -1
```
Expected: Shows the commit message for the backport

**Step 9: Final bundle status check**
```bash
git status
```
Expected: Working directory clean

---

## Verification Checklist

After completing all tasks, verify:

- [ ] All 11 agent files updated with ramparte versions
- [ ] Both context files updated (storyteller-instructions.md, presentation-styles.md)  
- [ ] html2pptx.py replaced with v2 version
- [ ] pptx_verify.py and deck-style-fix.py added as new tools
- [ ] All `@amplifier-module-stories:` references changed to `@stories:`
- [ ] No leftover namespace references in any file
- [ ] Bundle validation recipe passes
- [ ] Agent validation recipe passes
- [ ] All changes committed with descriptive message
- [ ] Working directory is clean

## Success Criteria

- **Bundle loads correctly** without any reference errors
- **All agents functional** with proper cross-references
- **Tools operational** with updated namespace handling  
- **Validation clean** with both bundle and agent recipes passing
- **Git history clean** with single descriptive commit
- **Emojis preserved** from ramparte's intentional usage
- **Production ready** with all quality gates and safeguards in place

## Rollback Plan

If issues arise that cannot be fixed quickly:

```bash
# Reset to pre-backport state
git reset --hard HEAD~1

# Verify rollback
git status  # Should show clean working directory
```

Then investigate issues in a separate branch before re-attempting.