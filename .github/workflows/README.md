# GitHub Actions Workflows

## Mission Validator Workflow

### Overview

The `verify.yml` workflow automatically validates student submissions for Django missions using pytest markers.

### How It Works

#### 1. Trigger Conditions
- Runs on Pull Requests to `main` branch
- Triggers on: `opened`, `synchronize`, `reopened`

#### 2. Branch Naming Convention

Students must create branches following this pattern:
```
mission/m01-description
mission/m02-description
mission/m03-description
...
mission/m99-description
```

**Examples:**
- ✅ `mission/m01-landing-page` → Tests with marker `landing_page`
- ✅ `mission/m02-admin-setup` → Tests with marker `admin_interface`
- ✅ `mission/m10-advanced-queries` → Tests with marker `mission10`
- ❌ `mission/my-work` → Invalid (no mission number)
- ❌ `feature/m01-test` → Invalid (wrong prefix)

#### 3. Test Execution

The workflow:
1. Extracts mission number from branch name (e.g., `01` from `m01-landing-page`)
2. Constructs pytest marker (e.g., `landing_page`)
3. Runs: `pytest -m landing_page` in the `src/` directory
4. All tests with `@pytest.mark.landing_page` are executed

#### 4. Environment Setup

**Services:**
- PostgreSQL 16 database
- Host: `localhost:5432`
- Database: `django_missions_test`
- User/Password: `postgres`/`postgres`

**Environment Variables:**
```bash
DEBUG=True
SECRET_KEY=test-secret-key-for-ci
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/django_missions_test
ALLOWED_HOSTS=localhost,127.0.0.1
SKELLAR_API_ENDPOINT=http://localhost:8000
SKELLAR_API_KEY=test-key
```

**Steps:**
1. Checkout code
2. Setup Python 3.13
3. Install uv package manager
4. Install dependencies via `uv sync --dev`
5. Create `.env` file with test configuration
6. Run Django migrations
7. Extract mission number from branch name
8. Run pytest with mission marker
9. Submit results to Skellar API

#### 5. Success Criteria

A mission passes if:
- ✅ Branch name matches pattern `mission/m##-*`
- ✅ All tests with the mission marker pass
- ✅ No Python errors or exceptions
- ✅ Database migrations succeed

#### 6. API Integration

Results are submitted to Skellar API:
- **Endpoint:** `$SKELLAR_API_HOST/api/v1/coding/validate-pr/`
- **Authentication:** Bearer token from `SKELLAR_API_TOKEN` secret
- **Payload includes:**
  - Repository information
  - PR number and commit SHA
  - GitHub username
  - Validation status
  - Test results
  - Error messages (if any)

### Pytest Markers

Tests are organized by mission using pytest markers:

```python
@pytest.mark.landing_page
@pytest.mark.django_db
def test_landing_page_accessible():
    """Test for Mission 01"""
    # test code...

@pytest.mark.admin_interface
@pytest.mark.django_db
def test_admin_registration():
    """Test for Mission 02"""
    # test code...
```

### Running Tests Locally

Students can test locally before pushing:

```bash
# Run all Mission 01 tests
cd src/
pytest -m landing_page -v

# Run with short traceback
pytest -m landing_page --tb=short

# Run specific mission with coverage
pytest -m admin_interface --cov=polls

# List all available markers
pytest --markers
```

### Available Missions

| Mission | Marker | Description |
|---------|--------|-------------|
| 01 | `landing_page` | Landing Page & Polls Setup |
| 02 | `admin_interface` | Admin Interface |
| 03 | `mission03` | Models & ORM |
| 04 | `mission04` | Django Signals |
| 05 | `mission05` | URLs & Views |
| 06 | `mission06` | Template Views |
| 07 | `mission07` | API Views |

### Workflow Configuration

#### Required Secrets
- `SKELLAR_API_TOKEN` - Authentication token for Skellar API

#### Required Variables
- `SKELLAR_API_HOST` - Base URL for Skellar API (e.g., `https://api.skellar.com`)

#### Dependencies
- Python 3.13
- uv package manager
- PostgreSQL 16
- pytest & pytest-django
- All packages from `pyproject.toml`

### Debugging Failed Tests

If tests fail, check:

1. **Branch Name**
   - Ensure format is `mission/m##-description`
   - Mission number must be 2 digits (01, 02, etc.)

2. **Test Markers**
   - Verify tests have correct marker: `@pytest.mark.missionXX`
   - Check marker is registered in `pyproject.toml`

3. **Dependencies**
   - Ensure all required packages are in `pyproject.toml`
   - Run `uv sync` locally to verify

4. **Database**
   - Check migrations are up to date
   - Verify database connection settings

5. **Test Code**
   - Run tests locally: `pytest -m missionXX -v`
   - Check for environment-specific issues

### Example Workflow Run

```yaml
Branch: mission/m01-landing-page

Steps:
1. ✅ Checkout code
2. ✅ Setup Python 3.13
3. ✅ Install uv
4. ✅ Install dependencies (uv sync --dev)
5. ✅ Setup environment (.env file created)
6. ✅ Run migrations (15 migrations applied)
7. ✅ Extract mission (Detected: m01, marker: landing_page)
8. ✅ Run tests (pytest -m landing_page)
   - test_landing_page_accessible PASSED
   - test_landing_page_has_setup_complete_message PASSED
   - test_ready_to_explore_button_links_to_polls_index PASSED
   - ... (all 9 tests passed)
9. ✅ Submit to Skellar (validation_passed: true)

Result: ✅ All checks passed
```

### Troubleshooting

**Problem: "Invalid branch pattern"**
- Solution: Rename branch to `mission/m##-description` format

**Problem: "No tests collected"**
- Solution: Add `@pytest.mark.missionXX` to your tests

**Problem: "Database connection failed"**
- Solution: Check if PostgreSQL service is running in CI

**Problem: "Module not found"**
- Solution: Add missing package to `pyproject.toml` dependencies

**Problem: "Migration failed"**
- Solution: Ensure migrations are committed and valid

### Best Practices

1. **Test Locally First**
   ```bash
   # Before pushing, run:
   pytest -m landing_page -v
   ```

2. **Use Descriptive Branch Names**
   ```bash
   git checkout -b mission/m01-landing-page-setup
   ```

3. **Keep Tests Focused**
   - One mission per PR
   - All tests should be related to mission objectives

4. **Check Test Output**
   - Review CI logs for detailed error messages
   - Fix issues incrementally

5. **Follow Django Best Practices**
   - Use Django test client
   - Mark database tests with `@pytest.mark.django_db`
   - Clean up test data properly

---

**Maintained by:** Django Missions Team
**Last Updated:** October 5, 2025
**CI/CD Platform:** GitHub Actions
