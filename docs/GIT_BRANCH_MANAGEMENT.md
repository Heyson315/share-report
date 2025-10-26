# Git Branch Management Guide - M365 Security Toolkit

## 🌿 **Branch Structure Overview**

This repository follows a **Git Flow** inspired branching strategy for organized development and collaboration.

```
📁 Repository: share-report
├── 🏠 master                           # Production-ready code
├── 🔄 develop                         # Main integration branch  
├── 📋 evidence/2025-10-25             # Evidence/audit branch
├── 🚀 feature/mcp-server              # Custom MCP server development
├── 🔧 feature/automation-suite        # Additional automation tools
├── 📚 feature/enterprise-docs         # Documentation & guides
├── ⚡ feature/performance-toolkit-improvements
└── 🛠️ feature/powershell-compliance-final
```

## 🎯 **Branch Purposes & Usage**

### **🏠 Production Branches**
- **`master`** - Stable, production-ready code
  - Only merge from `develop` via Pull Requests
  - All releases are tagged from this branch
  - Never commit directly to master

### **🔄 Integration Branch**  
- **`develop`** - Main development integration branch
  - Merge feature branches here for testing
  - Pre-production testing and validation
  - Source for release branches

### **📋 Evidence/Audit Branches**
- **`evidence/YYYY-MM-DD`** - Time-stamped audit evidence
  - Contains compliance reports and audit trails
  - Immutable once created (for audit purposes)
  - Used for regulatory compliance documentation

### **🚀 Feature Branches**

#### **`feature/mcp-server`**
**Purpose**: Custom Model Context Protocol (MCP) server development
- Integration with existing M365 security toolkit
- AI assistant tool development
- Microsoft Graph API integrations
- Authentication and security implementations

**When to use**: 
- Developing MCP server components
- Creating AI automation tools
- Building Graph API integrations

#### **`feature/automation-suite`**
**Purpose**: Additional automation tools and workflows
- PowerShell automation scripts
- Python automation utilities  
- CI/CD enhancements
- Scheduled task implementations

**When to use**:
- Building new automation workflows
- Enhancing existing automation
- Adding scheduled operations

#### **`feature/enterprise-docs`**
**Purpose**: Enterprise documentation and user guides
- Comprehensive setup guides
- Best practices documentation
- Training materials
- API documentation

**When to use**:
- Creating user documentation
- Writing technical guides
- Updating README files
- Adding training materials

#### **`feature/performance-toolkit-improvements`**
**Purpose**: Performance optimization and monitoring
- Benchmark implementations
- Performance testing
- Resource optimization
- Monitoring capabilities

#### **`feature/powershell-compliance-final`**
**Purpose**: PowerShell ScriptAnalyzer compliance
- Code quality improvements
- PowerShell best practices
- Security compliance

## 🔄 **Workflow Guidelines**

### **Creating New Features**
```bash
# Start from develop branch
git checkout develop
git pull origin develop

# Create new feature branch
git checkout -b feature/your-feature-name

# Work on your feature...
git add .
git commit -m "feat: implement your feature"

# Push to remote
git push -u origin feature/your-feature-name
```

### **Merging Features**
```bash
# When feature is complete, merge to develop
git checkout develop
git pull origin develop
git merge feature/your-feature-name

# Push updated develop
git push origin develop

# Clean up feature branch (optional)
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

### **Creating Releases**
```bash
# From develop, create release branch
git checkout develop
git checkout -b release/v1.2.0

# Finalize release (version bumps, changelog, etc.)
git commit -m "chore: prepare release v1.2.0"

# Merge to master
git checkout master
git merge release/v1.2.0
git tag v1.2.0

# Merge back to develop
git checkout develop
git merge release/v1.2.0

# Push everything
git push origin master --tags
git push origin develop
```

## 🛡️ **Branch Protection Rules**

### **Master Branch**
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ Require up-to-date branches
- ❌ No direct pushes allowed

### **Develop Branch**
- ✅ Require pull request reviews for external contributors
- ✅ Allow direct pushes for maintainers
- ✅ Require status checks to pass

### **Feature Branches**
- ✅ No restrictions (development freedom)
- ✅ Automatic deletion after merge (optional)

## 📋 **Commit Message Conventions**

Follow **Conventional Commits** standard:

```
type(scope): description

Types:
- feat:     New feature
- fix:      Bug fix
- docs:     Documentation changes
- style:    Code formatting
- refactor: Code restructuring
- test:     Test additions/changes
- chore:    Build/tooling changes
- ci:       CI/CD changes
- perf:     Performance improvements
- security: Security improvements

Examples:
- feat(mcp): add Graph API authentication
- fix(sharepoint): resolve permission analysis bug
- docs(readme): update installation instructions
- chore(deps): update PowerShell modules
```

## 🚀 **Current Development Focus**

### **Active Branches**
1. **`feature/mcp-server`** - Priority: HIGH
   - Building custom MCP server for M365 integration
   - AI assistant tool development

2. **`feature/automation-suite`** - Priority: MEDIUM  
   - Expanding automation capabilities
   - Adding new workflow tools

3. **`feature/enterprise-docs`** - Priority: MEDIUM
   - Comprehensive documentation updates
   - User guide improvements

### **Ready for Release**
- **`evidence/2025-10-25`** - Audit documentation complete
- **`feature/powershell-compliance-final`** - Code quality improvements

## 🔧 **Useful Git Commands**

### **Branch Management**
```bash
# List all branches
git branch -a

# Switch branches
git checkout branch-name

# Create and switch to new branch
git checkout -b new-branch-name

# Delete local branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name
```

### **Syncing with Remote**
```bash
# Fetch all remote branches
git fetch --all

# Pull latest changes
git pull origin branch-name

# Push local branch to remote
git push -u origin branch-name
```

### **Branch Status**
```bash
# Show branch relationships
git show-branch

# Show commit history across branches
git log --oneline --graph --all

# Show which branches contain specific commit
git branch --contains commit-hash
```

## 📊 **Branch Health Monitoring**

Regular maintenance tasks:
- [ ] Weekly: Merge develop → feature branches (keep updated)
- [ ] Bi-weekly: Review stale branches for deletion
- [ ] Monthly: Clean up merged feature branches
- [ ] Quarterly: Review branch protection rules

## 🆘 **Troubleshooting**

### **Merge Conflicts**
```bash
# When merge conflicts occur
git status                    # See conflicted files
# Edit files to resolve conflicts
git add .                     # Stage resolved files
git commit                    # Complete the merge
```

### **Accidental Commits**
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)  
git reset --hard HEAD~1

# Undo pushed commit (create revert commit)
git revert commit-hash
```

### **Branch Synchronization Issues**
```bash
# Reset local branch to match remote
git fetch origin
git reset --hard origin/branch-name

# Force push (use carefully!)
git push --force-with-lease origin branch-name
```

---

**Remember**: This branching strategy enables organized development while maintaining audit trails and compliance requirements for the M365 Security Toolkit! 🚀