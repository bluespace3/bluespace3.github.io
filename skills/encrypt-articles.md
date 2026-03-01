# Encrypt Articles Skill

Encrypt articles with password protection using the new simplified workflow.

## Description

Encrypt markdown articles by adding a `password` field to the front matter and running the auto-encrypt script. The script automatically wraps content in `{{% hugo-encryptor %}}` shortcode.

## New Workflow (Recommended)

### Step 1: Add Password Field

Add a `password` field to the article's front matter:

```markdown
---
title: 'My Secret Article'
categories: ["工作"]
password: "tian459996"  👈 Add this line
---

Article content here...
```

### Step 2: Run Auto-Encrypt Script

```bash
# Preview mode (recommended first)
python tools/auto_encrypt.py content/post/工作 --dry-run

# Actual encryption
python tools/auto_encrypt.py content/post/工作
```

### Step 3: Deploy

```bash
./deploy.sh
```

## Usage

```bash
# Encrypt all articles in a directory
python tools/auto_encrypt.py <directory>

# With preview
python tools/auto_encrypt.py <directory> --dry-run

# Examples
python tools/auto_encrypt.py content/post/工作
python tools/auto_encrypt.py content/post/私密笔记
```

## What It Does

1. ✅ Finds all `.md` files with `password` field in front matter
2. ✅ Adds `<!--more-->` tag if not present
3. ✅ Wraps content in `{{% hugo-encryptor "password" %}}` shortcode
4. ✅ Preserves front matter and metadata
5. ✅ Skips already encrypted files
6. ✅ Supports batch encryption

## Example

```bash
# Encrypt all articles in the 工作 directory
python tools/auto_encrypt.py content/post/工作

# Output:
# ============================================================
# 🔐 自动加密文章
# ============================================================
#   ✅ 已加密：0909工作.md
#   ✅ 已加密：1017.md
#   ✅ 已加密：25年终总结.md
#   ⏭️  已有加密标记，跳过：表结构.md
# ============================================================
# 📊 统计：总共 10 篇文章，加密 9 篇
# ============================================================
```

## Article Format After Encryption

**Before:**
```markdown
---
title: 'Article Title'
categories: ["工作"]
password: "tian459996"
---

Article content here...

## Section 1

Some content...
```

**After:**
```markdown
---
title: 'Article Title'
categories: ["工作"]
password: "tian459996"
---

<!--more-->

{{% hugo-encryptor "tian459996" %}}

Article content here...

## Section 1

Some content...

{{% /hugo-encryptor %}}
```

## Front Matter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `password` | ✅ Yes | Password for encryption (string) |
| `title` | ✅ Yes | Article title |
| `categories` | ✅ Yes | Article category |
| `date` | Optional | Publication date |
| `lastmod` | Optional | Last modified date |

## Requirements

- Python 3
- No additional packages required
- `password` field in front matter

## Important Notes

- ✅ **Always test with `--dry-run` first**
- ✅ **Use strong passwords**
- ⚠️ **Remember the password - it cannot be recovered**
- ✅ **Encryption works during deployment, not preview**
- ✅ **The `<!--more-->` tag is automatically added if missing**

## Common Use Cases

### Encrypt Single Article

```bash
# 1. Add password field to article
vim content/post/my-secret.md

# 2. Run encryption
python tools/auto_encrypt.py content/post

# 3. Deploy
./deploy.sh
```

### Batch Encrypt Multiple Articles

```bash
# 1. Add password field to all articles
for file in content/post/工作/*.md; do
  # Add: password: "tian459996" to front matter
done

# 2. Batch encrypt
python tools/auto_encrypt.py content/post/工作

# 3. Deploy
./deploy.sh
```

### Different Passwords for Different Articles

```bash
# Article 1: password: "work123"
# Article 2: password: "personal456"
# Article 3: password: "secret789"

python tools/auto_encrypt.py content/post/工作
# Script will use each article's own password
```

## Migration from Old Method

If you have articles encrypted with the old `batch-encrypt.sh` script:

1. **No action needed** - old encryption still works
2. **New articles** - use the new `password` field method
3. **Optional** - you can manually update old articles to use the new method

## Troubleshooting

### Script doesn't encrypt any articles

**Check:**
- Does the article have `password: "xxx"` in front matter?
- Is the file a `.md` file?
- Try with `--dry-run` to see what will be encrypted

### Encryption doesn't work on website

**Check:**
- Did you run `./deploy.sh` after encryption?
- Is `static/js/encrypted-content.js` present?
- Check browser console for errors

### Password not working

**Check:**
- Verify password matches front matter exactly (case-sensitive)
- Check for extra spaces or quotes in password field
- Try re-encrypting with `--dry-run` first

## Related Skills

- `deploy.md` - Deploy encrypted articles
- `preview.md` - Preview before encryption (content visible)
- `ENCRYPT_GUIDE.md` - Complete encryption guide (Chinese)

## See Also

- **[ENCRYPT_GUIDE.md](../ENCRYPT_GUIDE.md)** - Complete encryption documentation
- **[README.md](../README.md)** - Project documentation
