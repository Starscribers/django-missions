#!/bin/bash
#
# Test GitHub Actions Workflow Logic Locally
#
# This script simulates the GitHub Actions workflow for testing missions.
# Use it to verify your changes before pushing to GitHub.
#
# Usage:
#   ./scripts/test-workflow-locally.sh mission/m01-landing-page
#   ./scripts/test-workflow-locally.sh mission/m02-admin-setup
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

# Get branch name from argument or current branch
if [ -n "$1" ]; then
    BRANCH_NAME="$1"
else
    BRANCH_NAME=$(git branch --show-current)
fi

print_header "Testing Workflow for Branch: $BRANCH_NAME"

# Step 1: Extract mission from branch name
print_info "Step 1: Extracting mission from branch name..."

if [[ $BRANCH_NAME =~ ^mission/m([0-9]+)-.+$ ]]; then
    MISSION_NUMBER="${BASH_REMATCH[1]}"
    MISSION_NAME="m${MISSION_NUMBER}"
    MISSION_MARKER="mission${MISSION_NUMBER}"
    VALID_MISSION=true
    
    print_success "Detected mission: $MISSION_NAME"
    print_success "Mission marker: $MISSION_MARKER"
    print_success "Branch format is valid"
else
    VALID_MISSION=false
    print_error "Branch name does not match pattern: mission/m##-*"
    print_error "Example valid names: mission/m01-landing-page, mission/m02-admin"
    exit 1
fi

# Step 2: Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Not in project root directory!"
    print_info "Please run this script from the django-missions directory"
    exit 1
fi

print_success "In project root directory"

# Step 3: Check if src directory exists
if [ ! -d "src" ]; then
    print_error "src directory not found!"
    exit 1
fi

print_success "Source directory found"

# Step 4: Check environment
print_header "Step 2: Checking Environment"

if [ ! -f "src/.env" ]; then
    print_warning ".env file not found in src/"
    print_info "Creating test .env file..."
    
    cat > src/.env << EOF
DEBUG=True
SECRET_KEY=test-secret-key-for-local-ci
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
SKELLAR_API_ENDPOINT=http://localhost:8000
SKELLAR_API_KEY=test-key
EOF
    
    print_success "Created .env file with SQLite configuration"
else
    print_success ".env file exists"
fi

# Step 5: Install dependencies
print_header "Step 3: Installing Dependencies"

print_info "Running: uv sync --dev"
if uv sync --dev > /dev/null 2>&1; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Step 6: Run migrations
print_header "Step 4: Running Migrations"

cd src
print_info "Running: uv run python manage.py migrate"
if uv run python manage.py migrate --noinput; then
    print_success "Migrations completed"
else
    print_error "Migrations failed"
    cd ..
    exit 1
fi
cd ..

# Step 7: Run tests
print_header "Step 5: Running Tests for $MISSION_MARKER"

cd src
print_info "Running: pytest -m $MISSION_MARKER --tb=short -v"
echo ""

# Run pytest and capture exit code
if uv run pytest -m "$MISSION_MARKER" --tb=short -v; then
    TEST_EXIT_CODE=0
    TEST_PASSED=true
else
    TEST_EXIT_CODE=$?
    TEST_PASSED=false
fi

cd ..

# Step 8: Summary
print_header "Test Summary"

echo "Branch Name:      $BRANCH_NAME"
echo "Mission Name:     $MISSION_NAME"
echo "Mission Marker:   $MISSION_MARKER"
echo "Valid Mission:    $VALID_MISSION"
echo "Tests Passed:     $TEST_PASSED"
echo "Exit Code:        $TEST_EXIT_CODE"
echo ""

if [ "$TEST_PASSED" = true ] && [ "$VALID_MISSION" = true ]; then
    print_success "All checks passed! ✨"
    print_success "Your changes are ready to push to GitHub"
    echo ""
    print_info "Next steps:"
    echo "  1. Review your changes: git status"
    echo "  2. Commit your changes: git add . && git commit -m 'Complete $MISSION_NAME'"
    echo "  3. Push to GitHub: git push origin $BRANCH_NAME"
    echo "  4. Create a Pull Request on GitHub"
    echo ""
    exit 0
else
    print_error "Some checks failed"
    
    if [ "$VALID_MISSION" = false ]; then
        print_error "Branch name is invalid"
        print_info "Rename your branch: git branch -m mission/m##-description"
    fi
    
    if [ "$TEST_PASSED" = false ]; then
        print_error "Tests failed (exit code: $TEST_EXIT_CODE)"
        print_info "Review the test output above and fix any issues"
        print_info "Run tests again: cd src && pytest -m $MISSION_MARKER -v"
    fi
    
    echo ""
    exit 1
fi
