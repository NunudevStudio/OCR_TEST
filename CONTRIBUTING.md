# 🤝 Contributing Guide - Jalanamal OCR Payment Validator

Terima kasih atas minat Anda untuk berkontribusi pada proyek ini! Panduan ini akan membantu Anda memulai.

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How to Contribute](#-how-to-contribute)
- [Development Setup](#-development-setup)
- [Coding Standards](#-coding-standards)
- [Testing Guidelines](#-testing-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Issue Reporting](#-issue-reporting)

---

## 📜 Code of Conduct

### Our Pledge

Kami berkomitmen untuk membuat proyek ini terbuka dan ramah untuk semua kontributor.

### Expected Behavior

- ✅ Gunakan bahasa yang sopan dan inklusif
- ✅ Hormati sudut pandang dan pengalaman yang berbeda
- ✅ Terima kritik konstruktif dengan baik
- ✅ Fokus pada yang terbaik untuk komunitas

### Unacceptable Behavior

- ❌ Bahasa atau gambar yang bersifat seksual
- ❌ Trolling, komentar menghina/merendahkan
- ❌ Harassment publik atau privat
- ❌ Publikasi informasi pribadi orang lain tanpa izin

---

## 🚀 How to Contribute

### 1. Ways to Contribute

**Code Contributions:**
- 🐛 Bug fixes
- ✨ New features
- ⚡ Performance improvements
- 🔒 Security enhancements

**Non-Code Contributions:**
- 📝 Documentation improvements
- 🌍 Translations
- 🧪 Testing and bug reports
- 💡 Feature suggestions

### 2. First-Time Contributors

**Good First Issues:**
- Look for issues labeled `good first issue`
- Start with documentation improvements
- Add tests for existing features
- Fix typos or improve comments

**Example Tasks:**
```
- Add new bank to BANK_BEHAVIORS
- Improve error messages
- Add unit tests
- Update README with examples
```

---

## 💻 Development Setup

### 1. Fork & Clone

```bash
# Fork repository di GitHub, kemudian clone
git clone https://github.com/YOUR_USERNAME/OCR_TEST.git
cd OCR_TEST

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/OCR_TEST.git
```

### 2. Create Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# atau
git checkout -b fix/bug-description
```

**Branch Naming Convention:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `perf/` - Performance improvements

### 3. Setup Development Environment

```bash
# Backend setup
cd backend-ocr
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install pytest pytest-cov black flake8  # Dev dependencies

# Frontend setup
cd ../frontend
npm install
npm install --save-dev @types/node @types/react
```

---

## 📏 Coding Standards

### Python (Backend)

#### Style Guide
- Follow **PEP 8**
- Use **Black** for formatting
- Use **type hints** where possible

#### Code Formatting

```bash
# Format with Black
black backend-ocr/*.py

# Check with flake8
flake8 backend-ocr/*.py --max-line-length=100
```

#### Example:

```python
# Good ✅
def extract_data_from_image(path: str) -> Optional[Dict[str, Any]]:
    """Extract payment data from screenshot using OCR.
    
    Args:
        path: Path to payment screenshot
    
    Returns:
        Dictionary containing extracted data or None if processing fails
    """
    if not os.path.exists(path):
        logger.error(f"Image file not found: {path}")
        return None
    # ... rest of code

# Bad ❌
def extract_data_from_image(path):
    if not os.path.exists(path):
        return None
    # ... rest of code (no docstring, no types)
```

#### Naming Conventions:

```python
# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024
API_SECRET = "..."

# Functions and variables
def validate_donation(ocr_data, mutation):
    expected_amount = mutation["amount"]
    
# Classes
class ValidationEngine:
    def __init__(self):
        self.reader = None
```

### TypeScript/JavaScript (Frontend)

#### Style Guide
- Follow **Airbnb Style Guide**
- Use **Prettier** for formatting
- Use **TypeScript** for type safety

#### Code Formatting

```bash
# Format with Prettier
npx prettier --write "**/*.{ts,tsx,js,jsx}"

# Lint with ESLint
npx eslint "**/*.{ts,tsx,js,jsx}"
```

#### Example:

```typescript
// Good ✅
interface ValidationResult {
  status: 'VERIFIED' | 'REVIEW' | 'REJECTED';
  score: number;
  ocr_data: OCRData;
  notes: string[];
  timestamp: string;
}

const validatePayment = async (
  file: File,
  expectedAmount: number
): Promise<ValidationResult> => {
  // ... implementation
};

// Bad ❌
const validatePayment = async (file, expectedAmount) => {
  // ... no types
};
```

---

## 🧪 Testing Guidelines

### Backend Tests

#### Writing Tests

```python
# backend-ocr/test_validator.py
import pytest
from validator import clean_currency, detect_bank

class TestCurrencyParsing:
    """Test suite for currency parsing"""
    
    def test_indonesian_format(self):
        """Test Indonesian number format (10.546,00)"""
        assert clean_currency("Rp 10.546,00") == 10546
        assert clean_currency("Rp10.546") == 10546
    
    def test_international_format(self):
        """Test international number format (10,546.00)"""
        assert clean_currency("Rp 10,546.00") == 10546
    
    def test_edge_cases(self):
        """Test edge cases"""
        assert clean_currency("") == 0
        assert clean_currency("abc") == 0
        assert clean_currency("Rp 0") == 0

class TestBankDetection:
    """Test suite for bank detection"""
    
    def test_bca_detection(self):
        """Test BCA bank detection"""
        text = "BCA MOBILE TRANSFER BERHASIL Rp 50.000"
        assert detect_bank(text) == "BCA"
    
    def test_unknown_bank(self):
        """Test unknown bank fallback"""
        text = "Some random text without bank info"
        assert detect_bank(text) == "UNKNOWN"
```

#### Running Tests

```bash
cd backend-ocr

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest test_validator.py::TestCurrencyParsing::test_indonesian_format

# Run with verbose output
pytest -v
```

#### Test Coverage Requirements
- Minimum **80% coverage** for new code
- All critical paths must be tested
- Include edge cases and error scenarios

### Frontend Tests

```typescript
// frontend/__tests__/ValidationCard.test.tsx
import { render, screen } from '@testing-library/react';
import ValidationCard from '@/components/ValidationCard';

describe('ValidationCard', () => {
  it('renders verified status correctly', () => {
    const result = {
      status: 'VERIFIED',
      score: 90,
      ocr_data: { /* ... */ },
      notes: ['✅ Amount match'],
      timestamp: '2026-01-19T20:00:00'
    };
    
    render(<ValidationCard result={result} />);
    expect(screen.getByText('Terverifikasi')).toBeInTheDocument();
    expect(screen.getByText('90/100')).toBeInTheDocument();
  });
});
```

---

## 🔄 Pull Request Process

### 1. Before Submitting

**Checklist:**
- [ ] Code follows style guidelines
- [ ] Added/updated tests
- [ ] All tests pass
- [ ] Documentation updated (if needed)
- [ ] Commit messages are clear
- [ ] No merge conflicts

### 2. Commit Messages

Follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples:**

```bash
# Good ✅
git commit -m "feat(validator): add support for Seabank detection"
git commit -m "fix(api): handle file upload timeout error"
git commit -m "docs(readme): add installation instructions"

# Bad ❌
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

**Multi-line example:**
```
feat(validator): add support for Seabank detection

- Added Seabank to BANK_BEHAVIORS dictionary
- Included brand keywords and success indicators
- Added test cases for Seabank detection

Closes #123
```

### 3. Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name
```

Go to GitHub and create Pull Request with:

**Title:** Clear and descriptive
```
feat: Add Seabank support to validator
```

**Description Template:**
```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran to verify your changes

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
Add screenshots to help explain your changes
```

### 4. Review Process

- Maintainer akan review code Anda
- Address feedback dengan commit baru atau amend
- Setelah approved, maintainer akan merge

---

## 🐛 Issue Reporting

### Bug Reports

**Template:**

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Upload screenshot '....'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows 11]
 - Python version: [e.g. 3.10]
 - Browser: [e.g. chrome, safari]
 - Version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### Feature Requests

**Template:**

```markdown
**Is your feature request related to a problem?**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

---

## 🎯 Development Priorities

### High Priority
- 🔒 Security improvements
- 🐛 Critical bug fixes
- ⚡ Performance optimization
- 📱 Mobile banking app support expansion

### Medium Priority
- ✨ New features
- 🧪 Test coverage improvement
- 📝 Documentation enhancement
- 🌍 Internationalization

### Low Priority
- 🎨 UI/UX improvements
- ♻️ Code refactoring
- 🔧 Dev tooling

---

## 📚 Resources

### Documentation
- [README.md](README.md) - Project overview
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Technical documentation
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [EasyOCR GitHub](https://github.com/JaidedAI/EasyOCR)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Next.js Documentation](https://nextjs.org/docs)

---

## 💬 Communication

### Where to Ask Questions

- 💬 **GitHub Discussions** - General questions
- 🐛 **GitHub Issues** - Bug reports and feature requests
- 📧 **Email** - Private concerns (support@jalanamal.com)

### Response Time

- Issues: 24-48 hours
- Pull Requests: 2-5 days
- Security issues: ASAP (within 24 hours)

---

## 🏆 Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

Top contributors may be invited as maintainers!

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## 🙏 Thank You!

Every contribution, no matter how small, makes a difference.

**Happy Contributing! 🚀**

---

**Jalanamal Team**
