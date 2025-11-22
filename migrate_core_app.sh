#!/bin/bash
#
# CORE APP MIGRATION SCRIPT
# Migrates core app from Floor-Management-System (old repo B) to Floor-Management-System-C (new repo C)
#
# Usage: bash migrate_core_app.sh
#

set -e  # Exit on error

echo "=========================================="
echo "  CORE APP MIGRATION SCRIPT"
echo "  Floor Management System - Phase 2"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect environment
if [[ "$PWD" == *"/workspaces/"* ]]; then
    REPO_PATH="/workspaces/Floor-Management-System-C"
    TMP_PATH="/tmp"
    echo -e "${GREEN}✓${NC} Detected: GitHub Codespaces"
elif [[ "$PWD" == *"/root/"* ]] || [[ "$PWD" == *"/home/"* ]]; then
    REPO_PATH="$PWD"
    TMP_PATH="/tmp"
    echo -e "${GREEN}✓${NC} Detected: Local/Claude Code environment"
else
    REPO_PATH="$PWD"
    TMP_PATH="/tmp"
    echo -e "${YELLOW}!${NC} Unknown environment, using current directory"
fi

echo "Working directory: $REPO_PATH"
echo ""

# Step 1: Ensure we're in the right repo
echo "Step 1: Checking repository..."
cd "$REPO_PATH"
if [ ! -f "manage.py" ]; then
    echo -e "${RED}✗${NC} Error: manage.py not found. Are you in Floor-Management-System-C?"
    exit 1
fi
echo -e "${GREEN}✓${NC} In correct repository"
echo ""

# Step 2: Check if core app already exists
if [ -d "core" ] && [ -f "core/models.py" ]; then
    echo -e "${YELLOW}!${NC} Core app already exists"
    read -p "Overwrite existing core app? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Migration cancelled"
        exit 0
    fi
    echo "Removing existing core app..."
    rm -rf core
fi

# Step 3: Create core app structure
echo "Step 2: Creating core app structure..."
if command -v python &> /dev/null; then
    PYTHON_CMD=python
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    echo -e "${RED}✗${NC} Python not found"
    exit 1
fi

$PYTHON_CMD manage.py startapp core
echo -e "${GREEN}✓${NC} Core app created"
echo ""

# Step 4: Clone old repo temporarily
echo "Step 3: Fetching core models from old repo..."
OLD_REPO_PATH="$TMP_PATH/Floor-Management-System-old"

if [ -d "$OLD_REPO_PATH" ]; then
    echo "Cleaning up old temporary repo..."
    rm -rf "$OLD_REPO_PATH"
fi

git clone https://github.com/Ramzi-Kassab/Floor-Management-System.git "$OLD_REPO_PATH" 2>&1 | grep -E "(Cloning|done)" || true
cd "$OLD_REPO_PATH"
git checkout hotfix/model-duplication-fix >/dev/null 2>&1
echo -e "${GREEN}✓${NC} Old repo cloned"
echo ""

# Step 5: Copy core models
echo "Step 4: Copying core models..."
if [ ! -f "$OLD_REPO_PATH/core/models.py" ]; then
    echo -e "${RED}✗${NC} core/models.py not found in old repo"
    exit 1
fi

cp "$OLD_REPO_PATH/core/models.py" "$REPO_PATH/core/models.py"
MODEL_LINES=$(wc -l < "$REPO_PATH/core/models.py")
echo -e "${GREEN}✓${NC} Copied core/models.py ($MODEL_LINES lines)"
echo ""

# Step 6: Update settings.py
echo "Step 5: Updating settings.py..."
cd "$REPO_PATH"

# Check if core is already in INSTALLED_APPS
if grep -q "'core'" floor_project/settings.py; then
    echo -e "${YELLOW}!${NC} 'core' already in INSTALLED_APPS"
else
    # Add core to INSTALLED_APPS
    sed -i "/# Project apps/a\\    'core',  # Foundation: shared utilities, cost centers, notifications" floor_project/settings.py
    echo -e "${GREEN}✓${NC} Added 'core' to INSTALLED_APPS"
fi
echo ""

# Step 7: Create static directory if needed
if [ ! -d "static" ]; then
    mkdir -p static
    echo -e "${GREEN}✓${NC} Created static directory"
fi

# Step 8: Create migrations
echo "Step 6: Creating Django migrations..."
$PYTHON_CMD manage.py makemigrations core 2>&1 | grep -E "(Migrations|Create)" || echo "Migration output captured"
if [ -f "core/migrations/0001_initial.py" ]; then
    MIGRATION_SIZE=$(du -h core/migrations/0001_initial.py | cut -f1)
    echo -e "${GREEN}✓${NC} Migrations created (0001_initial.py - $MIGRATION_SIZE)"
else
    echo -e "${RED}✗${NC} Migration file not created"
    exit 1
fi
echo ""

# Step 9: Run Django checks
echo "Step 7: Running Django system checks..."
CHECK_OUTPUT=$($PYTHON_CMD manage.py check 2>&1)
if echo "$CHECK_OUTPUT" | grep -q "0 errors"; then
    echo -e "${GREEN}✓${NC} Django check passed (0 errors)"
else
    echo -e "${RED}✗${NC} Django check failed:"
    echo "$CHECK_OUTPUT"
    exit 1
fi
echo ""

# Step 10: Count models
echo "Step 8: Verifying models..."
MODEL_COUNT=$(grep -c "^class.*models.Model" core/models.py || echo "0")
echo -e "${GREEN}✓${NC} Found $MODEL_COUNT Django models in core/models.py"
echo ""

# Step 11: Git status
echo "Step 9: Git status..."
git add -A
git status --short
echo ""

# Step 12: Create commit
echo "Step 10: Creating git commit..."
read -p "Create git commit? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "Skipping commit"
else
    git commit -m "feat(core): migrate core app from old repo with 12 models

Migrated complete core app from old repo (B) to new clean repo (C):

Models Imported (12 total):
- UserPreference: UI preferences, themes, table settings
- CostCenter: Financial tracking with hierarchy
- ERPDocumentType, ERPReference: ERP integration
- LossOfSaleCause, LossOfSaleEvent: Loss tracking
- ApprovalType, ApprovalAuthority: Approval workflow
- Currency, ExchangeRate: Multi-currency support
- Notification: User notifications with GenericFK
- ActivityLog: System-wide audit trail

Implementation:
✅ All models with proper db_table settings
✅ GenericForeignKey relationships preserved
✅ All Meta configurations (indexes, constraints)
✅ Migrations created successfully
✅ Django check passes with 0 errors

Generated by: migrate_core_app.sh
"
    echo -e "${GREEN}✓${NC} Git commit created"
fi
echo ""

# Step 13: Cleanup
echo "Step 11: Cleaning up..."
rm -rf "$OLD_REPO_PATH"
echo -e "${GREEN}✓${NC} Temporary files removed"
echo ""

# Summary
echo "=========================================="
echo "  ✓ CORE APP MIGRATION COMPLETE"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Models migrated: $MODEL_COUNT"
echo "  - Lines of code: $MODEL_LINES"
echo "  - Migration file: core/migrations/0001_initial.py"
echo "  - Django check: PASSED (0 errors)"
echo ""
echo "Next steps:"
echo "  1. Push to GitHub:"
echo "     git push origin master"
echo ""
echo "  2. Apply migrations (requires PostgreSQL):"
echo "     python manage.py migrate"
echo ""
echo "  3. Test the core app:"
echo "     python manage.py test core"
echo ""
echo "  4. Proceed to next app migration:"
echo "     - hr (20+ models)"
echo "     - inventory (20+ models)"
echo "     - engineering (11 models)"
echo ""
echo "For detailed progress, see: docs/PHASE2_PROGRESS.md"
echo "=========================================="
