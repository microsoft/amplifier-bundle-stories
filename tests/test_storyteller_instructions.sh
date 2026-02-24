#!/bin/bash
# Test: context/storyteller-instructions.md update verification
# Tests all acceptance criteria for task-1

set -e
REPO_DIR="/home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories"
SOURCE_DIR="/home/bkrabach/dev/update-stories-bundle/amplifier-stories"
TARGET_FILE="$REPO_DIR/context/storyteller-instructions.md"
SOURCE_FILE="$SOURCE_DIR/context/storyteller-instructions.md"
PASS=0
FAIL=0

run_test() {
    local name="$1"
    local result="$2"
    if [ "$result" = "0" ]; then
        echo "  PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Testing context/storyteller-instructions.md ==="

# Test 1: File has v2.0.0 content (check for key sections that exist in source but not old target)
# The source has "Source Verification (Avoid Anthropic Repos)" section which the old target lacks
grep -q "Source Verification" "$TARGET_FILE" 2>/dev/null
run_test "AC1: File updated with ramparte v2.0.0 content (has Source Verification section)" "$?"

# Test 1b: Another v2.0.0-specific section: "Sources & Methodology Slide (REQUIRED)"
grep -q "Sources & Methodology Slide" "$TARGET_FILE" 2>/dev/null
run_test "AC1b: File has v2.0.0 Sources & Methodology Slide section" "$?"

# Test 1c: v2.0.0 has "More Amplifier Stories" link section
grep -q "More Amplifier Stories" "$TARGET_FILE" 2>/dev/null
run_test "AC1c: File has v2.0.0 More Amplifier Stories link" "$?"

# Test 1d: v2.0.0 has Accuracy checklist section
grep -q "Accuracy (verify FIRST" "$TARGET_FILE" 2>/dev/null
run_test "AC1d: File has v2.0.0 Accuracy checklist section" "$?"

# Test 2: No remaining @amplifier-module-stories: namespace references
if grep -q "@amplifier-module-stories:" "$TARGET_FILE" 2>/dev/null; then
    run_test "AC2: No @amplifier-module-stories: references remain" "1"
else
    run_test "AC2: No @amplifier-module-stories: references remain" "0"
fi

# Test 3: File is non-empty and valid (source file has no namespace refs to convert)
if [ -s "$TARGET_FILE" ]; then
    run_test "AC3: File is non-empty and valid" "0"
else
    run_test "AC3: File is non-empty and valid" "1"
fi

# Test 4: git status shows file as modified
cd "$REPO_DIR"
if git status --porcelain | grep -q "context/storyteller-instructions.md"; then
    run_test "AC4: git status shows file as modified" "0"
else
    run_test "AC4: git status shows file as modified" "1"
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
else
    exit 0
fi
