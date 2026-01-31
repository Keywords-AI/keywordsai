# Keywords AI → Respan Rebranding Implementation Plan

**Date:** 2025-01-29
**Status:** Planning
**Scope:** Backend customer-facing strings + Public SDKs

---

## Overview

Rebrand from "Keywords AI" to "Respan". This plan covers:
1. **Backend (this repo):** Customer-facing API responses, error messages, emails
2. **Public SDKs:** Publish new packages under `respan-*` / `@respan/*` names

**Strategy for SDKs:** Publish as completely separate packages (not updates to existing). Old packages remain but stop receiving updates. Customers migrate to new packages at their convenience.

---

## Part 1: Backend - Customer-Facing String Changes

### 1.1 Error Messages in API Responses

| File | Line(s) | Current String | New String |
|------|---------|----------------|------------|
| [llm_models/views.py](llm_models/views.py) | 359 | `"Cannot delete managed model. This model is managed by Keywords AI."` | `"Cannot delete managed model. This model is managed by Respan."` |
| [llm_models/views.py](llm_models/views.py) | 382 | `"Cannot modify managed model. This model is managed by Keywords AI."` | `"Cannot modify managed model. This model is managed by Respan."` |
| [llm_models/views.py](llm_models/views.py) | 851 | `"Cannot delete managed provider. This provider is managed by Keywords AI..."` | `"Cannot delete managed provider. This provider is managed by Respan..."` |
| [llm_models/serializers.py](llm_models/serializers.py) | 519, 587 | `"Cannot modify '{field}' for Keywords AI managed providers."` | `"Cannot modify '{field}' for Respan managed providers."` |

### 1.2 Rate Limit & Access Error Messages

| File | Line(s) | Current Reference | New Reference |
|------|---------|-------------------|---------------|
| [api/views/core.py](api/views/core.py) | 602, 630, 713, 766, 1064 | `"...Keywords AI API key..."` + `platform.keywordsai.co` | `"...Respan API key..."` + `platform.respan.ai` |
| [api/views/core.py](api/views/core.py) | 1671 | `docs.keywordsai.co` | `docs.respan.ai` |
| [user/views.py](user/views.py) | 259 | `team@keywordsai.co` | `team@respan.ai` |
| [utils/permissions/access_management.py](utils/permissions/access_management.py) | 165, 184 | `"...using Keywords AI..."` + `platform.keywordsai.co` | `"...using Respan..."` + `platform.respan.ai` |
| [utils/permissions/keywordsai_permissions.py](utils/permissions/keywordsai_permissions.py) | 57 | `platform.keywordsai.co` | `platform.respan.ai` |
| [utils/permissions/admin_permissions.py](utils/permissions/admin_permissions.py) | 34 | `"Keywords AI admin access required"` | `"Respan admin access required"` |
| [utils/exceptions.py](utils/exceptions.py) | 265 | `"...Keywords AI's managed..."` | `"...Respan's managed..."` |
| [utils/exceptions.py](utils/exceptions.py) | 271, 288, 330 | `platform.keywordsai.co` | `platform.respan.ai` |
| [utils/exceptions.py](utils/exceptions.py) | 326 | `docs.keywordsai.co` | `docs.respan.ai` |
| [utils/exceptions.py](utils/exceptions.py) | 334 | `team@keywordsai.co` | `team@respan.ai` |
| [utils/exceptions.py](utils/exceptions.py) | 611 | `"...Keywords AI dashboard"` | `"...Respan dashboard"` |
| [utils/preprocessing/llm_generation/chat_generation.py](utils/preprocessing/llm_generation/chat_generation.py) | 224 | `docs.keywordsai.co` | `docs.respan.ai` |
| [utils/preprocessing/llm_generation/credentials.py](utils/preprocessing/llm_generation/credentials.py) | 525 | `platform.keywordsai.co` | `platform.respan.ai` |
| [utils/llm_completion_methods.py](utils/llm_completion_methods.py) | 154 | `platform.keywordsai.co` | `platform.respan.ai` |
| [utils/warnings.py](utils/warnings.py) | 43 | `"...Keywords AI's credentials..."` | `"...Respan's credentials..."` |
| [utils/warnings.py](utils/warnings.py) | 58 | `docs.keywordsai.co` | `docs.respan.ai` |
| [api/serializers.py](api/serializers.py) | 1061 | `"...Keywords AI's pricing list..."` | `"...Respan's pricing list..."` |

### 1.2.1 Error Message Constants

| File | Line(s) | Change |
|------|---------|--------|
| [utils/constants/error_message_constants.py](utils/constants/error_message_constants.py) | 135, 155 | `platform.keywordsai.co` URLs |
| [utils/constants/error_message_constants.py](utils/constants/error_message_constants.py) | 754 | `"...not available on Keywords AI..."` → `"...not available on Respan..."` |
| [utils/constants/error_message_constants.py](utils/constants/error_message_constants.py) | 889 | `"...Keywords AI's model database..."` → `"...Respan's model database..."` |

### 1.2.2 Filter Labels (UI-Facing)

| File | Line(s) | Change |
|------|---------|--------|
| [utils/constants/filters_constant.py](utils/constants/filters_constant.py) | 1890 | `"Managed by Keywords AI"` → `"Managed by Respan"` |

### 1.3 Email Content & Configuration

| File | Line(s) | Change |
|------|---------|--------|
| [tasks/email_tasks.py](tasks/email_tasks.py) | 26 | Welcome email: `"Welcome to Keywords AI!"` → `"Welcome to Respan!"` |
| [user/tasks.py](user/tasks.py) | 92, 95 | Budget warning email: `"Keywords AI Credentials"` → `"Respan Credentials"` |
| [utils/email.py](utils/email.py) | 168 | Error email subject: `"...Keywords AI..."` → `"...Respan..."` |
| [utils/email.py](utils/email.py) | 180 | Error email subject: `"...Keywords AI API Call"` → `"...Respan API Call"` |
| [utils/postprocessing/generic_postprocessing.py](utils/postprocessing/generic_postprocessing.py) | 860, 862 | Error email subjects |
| [utils/notifications.py](utils/notifications.py) | 32 | Alert prefix: `"[Keywords AI Alert]"` → `"[Respan Alert]"` |
| [keywordsai/settings.py](keywordsai/settings.py) | 479, 482 | `EMAIL_FRONTEND_DOMAIN`, `EMAIL_FRONTEND_SITE_NAME` defaults |
| [.env.template](.env.template) | 66 | `EMAIL_FRONTEND_SITE_NAME="Keywords AI"` → `"Respan"` |

### 1.4 Email Addresses & Contact Info

| File | Location | Current | New |
|------|----------|---------|-----|
| [utils/constants/__init__.py](utils/constants/__init__.py) | 182-183 | `team@keywordsai.xyz`, `admin@keywordsai.co` | `team@respan.ai`, `admin@respan.ai` |
| [utils/notifications.py](utils/notifications.py) | 44 | `noreply@keywordsai.co` | `noreply@respan.ai` |
| Various views | Multiple | `team@keywordsai.co` | `team@respan.ai` |

### 1.5 Platform URLs in User-Facing Messages

| File | Line(s) | URLs to Update |
|------|---------|----------------|
| [user/views.py](user/views.py) | 90, 112, 146, 187 | `platform.keywordsai.co` (invitation links) |
| [automation/utils/core.py](automation/utils/core.py) | 1152 | `platform.keywordsai.co/logs/{log_id}` (Slack webhooks) |
| [keywordsai/settings.py](keywordsai/settings.py) | 479 | `EMAIL_FRONTEND_DOMAIN` default |

### 1.6 Feature Documentation (API Docs)

These files contain example responses/documentation strings that may be returned to customers:

- [boilerplates/keywordsai/feature_docs/webhooks/webhooks_api_docs.md](boilerplates/keywordsai/feature_docs/webhooks/webhooks_api_docs.md)
- [boilerplates/keywordsai/feature_docs/batch_api/batch_api_docs.md](boilerplates/keywordsai/feature_docs/batch_api/batch_api_docs.md)
- [boilerplates/keywordsai/feature_docs/traces/traces_api_docs.md](boilerplates/keywordsai/feature_docs/traces/traces_api_docs.md)
- [boilerplates/keywordsai/feature_docs/files_api/files_api_docs.md](boilerplates/keywordsai/feature_docs/files_api/files_api_docs.md)
- [boilerplates/keywordsai/feature_docs/billing/credit_transactions_api_docs.md](boilerplates/keywordsai/feature_docs/billing/credit_transactions_api_docs.md)
- [boilerplates/keywordsai/feature_docs/scores/scores_api_docs.md](boilerplates/keywordsai/feature_docs/scores/scores_api_docs.md)
- [boilerplates/keywordsai/feature_docs/llm_models/models_api_docs.md](boilerplates/keywordsai/feature_docs/llm_models/models_api_docs.md) - Update `affiliation_category: "keywordsai"` → `is_managed: true`

### 1.7 Sample Data & Onboarding

| File | Line(s) | Change |
|------|---------|--------|
| [utils/onboarding/sample_data.py](utils/onboarding/sample_data.py) | 100, 102 | `"welcome to Keywords AI!"` → `"welcome to Respan!"` |
| [utils/onboarding/sample_data.py](utils/onboarding/sample_data.py) | 121 | `demo@keywordsai.co` → `demo@respan.ai` |
| [utils/onboarding/sample_data.py](utils/onboarding/sample_data.py) | 122 | `"Keywords AI Demo"` → `"Respan Demo"` |

### 1.7.1 Stripe/Payment Constants

| File | Line(s) | Change |
|------|---------|--------|
| [utils/constants/payment_constants.py](utils/constants/payment_constants.py) | 48 | `CREDIT_PRODUCT_NAME = "Keywords AI Platform Credits"` → `"Respan Platform Credits"` |
| [utils/constants/payment_constants.py](utils/constants/payment_constants.py) | 49 | `CREDIT_PRODUCT_DESCRIPTION = "...Keywords AI..."` → `"...Respan..."` |
| [utils/keywordsai_types/payment_types.py](utils/keywordsai_types/payment_types.py) | 54, 55, 126, 127 | Stripe checkout URLs `platform.keywordsai.co` → `platform.respan.ai` |

### 1.7.2 Hardcoded URLs in Postprocessing

| File | Line(s) | Change |
|------|---------|--------|
| [utils/postprocessing/generic_postprocessing.py](utils/postprocessing/generic_postprocessing.py) | 903 | `platform.keywordsai.co` |
| [utils/postprocessing/generic_postprocessing.py](utils/postprocessing/generic_postprocessing.py) | 906 | `enterprise.keywordsai.co` |

### 1.8 Model `affiliation_category` → `is_managed` Migration

**Problem:** `LLMModel.affiliation_category` returns `"keywordsai"` or `"custom"` to customers in API responses.

**Current State:**
```python
# utils/constants/llm_model_constants.py
class AffiliationCategory(models.TextChoices):
    CUSTOM = "custom"
    KEYWORDSAI = "keywordsai"  # ← Customer sees this string

# llm_models/models.py
affiliation_category = models.CharField(..., default=AffiliationCategory.KEYWORDSAI)
```

**Solution:** Add `is_managed` boolean (like `LLMProvider` already has), stop exposing `affiliation_category`.

| File | Change |
|------|--------|
| [llm_models/models.py](llm_models/models.py) | Add `is_managed = models.BooleanField(default=False)` to `LLMModel` |
| [llm_models/serializers.py](llm_models/serializers.py) | Add `'affiliation_category'` to `CUSTOM_MODEL_PUBLIC_EXCLUDE_FIELDS` |
| [llm_models/serializers.py](llm_models/serializers.py) | Add `is_managed` as a read-only field in model serializers |
| [llm_models/views.py](llm_models/views.py) | Update checks from `affiliation_category == KEYWORDSAI` → `is_managed == True` |
| [llm_models/signals.py](llm_models/signals.py) | Update signal checks to use `is_managed` |
| [llm_models/utils.py](llm_models/utils.py) | Set `is_managed=True` for global models, `is_managed=False` for custom |
| Migration | See migration strategy below |

**Migration Strategy (Backward Compatible):**
```python
# 1. Add is_managed field with data migration
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='llmmodel',
            name='is_managed',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.RunSQL(
            sql="UPDATE llm_models_llmmodel SET is_managed = TRUE WHERE affiliation_category = 'keywordsai'",
            reverse_sql="UPDATE llm_models_llmmodel SET is_managed = FALSE",
        ),
    ]

# 2. Later: State migration to remove affiliation_category (--fake for cleanup)
# This allows rollback compatibility - column stays in DB but Django ignores it
class Migration(migrations.Migration):
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='llmmodel',
                    name='affiliation_category',
                ),
            ],
            database_operations=[],  # Don't actually drop column yet
        ),
    ]
```

**API Response Change:**
```python
# Before (customer sees "keywordsai")
{"model_name": "gpt-4", "affiliation_category": "keywordsai", ...}

# After (clean boolean)
{"model_name": "gpt-4", "is_managed": true, ...}
```

**Internal Note:** Keep `affiliation_category` column for now (internal use), just stop exposing it.

---

## Part 2: Public SDK Rebranding

### Strategy: Publish as New Packages

**Rationale:**
- Publishing as `respan-*` creates entirely new PyPI/npm packages
- Old `keywordsai-*` packages remain but stop receiving updates
- Customers see "last updated" stale on old packages, prompting migration
- No breaking changes for existing customers on old packages

### 2.1 Python SDKs (PyPI)

| Current Package | New Package | PyPI Status |
|-----------------|-------------|-------------|
| `keywordsai` (v1.0.4) | `respan` | New package |
| `keywordsai-sdk` (v0.5.2) | `respan-sdk` | New package |
| `keywordsai-tracing` (v0.0.59) | `respan-tracing` | New package |
| `keywordsai-exporter-agno` (v0.1.0) | `respan-exporter-agno` | New package |
| `keywordsai-exporter-haystack` (v0.1.1) | `respan-exporter-haystack` | New package |
| `keywordsai-exporter-litellm` (v0.1.0) | `respan-exporter-litellm` | New package |
| `keywordsai-exporter-openai-agents` (v0.1.6) | `respan-exporter-openai-agents` | New package |
| `keywordsai-instrumentation-langfuse` (v0.1.1) | `respan-instrumentation-langfuse` | New package |

**Changes per Python SDK:**
1. `pyproject.toml`:
   - `name = "respan-*"`
   - `description` - update company name
   - `authors` - update email domain
   - `homepage`, `repository`, `documentation` URLs
2. Module/package names in `packages = [...]`
3. Source directory rename: `src/keywordsai_*` → `src/respan_*`
4. Internal imports
5. README.md updates
6. Environment variable names (e.g., `KEYWORDS_API_KEY` → `RESPAN_API_KEY`)

### 2.2 JavaScript/TypeScript SDKs (npm)

| Current Package | New Package | npm Status |
|-----------------|-------------|------------|
| `@keywordsai/keywordsai-sdk` (v0.0.18) | `@respan/sdk` | New package |
| `@keywordsai/n8n-nodes-keywordsai` (v0.1.6) | `@respan/n8n-nodes` | New package |
| `@keywordsai/exporter-openai-agents` (v0.0.7) | `@respan/exporter-openai-agents` | New package |
| `@keywordsai/exporter-vercel` (v1.0.27) | `@respan/exporter-vercel` | New package |

**Changes per JS SDK:**
1. `package.json`:
   - `name` field
   - `description`
   - `author` email
   - `homepage`, `repository` URLs
2. README.md updates
3. Environment variable names

### 2.3 MCP Server (`keywordsai-mcp` repo)

| Current | New |
|---------|-----|
| `keywords-mcp` (v1.0.0) | `respan-mcp` |
| `https://mcp.keywordsai.co/api/mcp` | `https://mcp.respan.ai/api/mcp` |
| `KEYWORDS_API_KEY` env var | `RESPAN_API_KEY` |

**Changes:**
1. `package.json` - name, description, usage docs
2. `vercel.json` - if contains domain references
3. README.md
4. All hardcoded URLs referencing `keywordsai.co`

---

## Part 3: Implementation Order

### Phase 1: Backend (This Repo)
1. **affiliation_category → is_managed migration** (do first - requires DB migration)
   - Add `is_managed` field to `LLMModel`
   - Create data migration to set `is_managed=True` where `affiliation_category='keywordsai'`
   - Update serializers to exclude `affiliation_category`, expose `is_managed`
   - Update views/signals/utils to use `is_managed`
2. Update error messages and API responses (string replacements)
3. Update email templates
4. Update settings defaults
5. Update feature documentation
6. Test all customer-facing flows

### Phase 2: SDKs (Separate Repos)
1. Fork/copy each SDK to new directory structure
2. Rename packages in manifests
3. Rename source directories and internal imports
4. Update all documentation
5. Update environment variable names
6. Publish to PyPI/npm under new names
7. Update main repo README to point to new packages

### Phase 3: Deprecation Notice
1. Add deprecation notice to old SDK READMEs
2. Consider final patch release with deprecation warning in code
3. Update old package descriptions on PyPI/npm

---

## Part 4: Domain Mapping

**Confirmed domain:** `respan.ai`

| Current | New |
|---------|-----|
| `keywordsai.co` | `respan.ai` |
| `platform.keywordsai.co` | `platform.respan.ai` |
| `api.keywordsai.co` | `api.respan.ai` |
| `docs.keywordsai.co` | `docs.respan.ai` |
| `mcp.keywordsai.co` | `mcp.respan.ai` |
| `endpoint.keywordsai.co` | `endpoint.respan.ai` |
| `team@keywordsai.co` | `team@respan.ai` |
| `support@keywordsai.co` | `support@respan.ai` |
| `noreply@keywordsai.co` | `noreply@respan.ai` |

---

## Part 5: Files Summary

### Backend Files to Modify (30+ files)

**LLM Models (affiliation_category → is_managed):**
- `llm_models/models.py` - Add `is_managed` field
- `llm_models/views.py` - Update checks + error messages
- `llm_models/serializers.py` - Exclude `affiliation_category`, add `is_managed`
- `llm_models/signals.py` - Update signal logic
- `llm_models/utils.py` - Set `is_managed` for new models

**Core API:**
- `api/views/core.py` - Rate limit error messages
- `api/serializers.py` - Pricing list error message
- `user/views.py` - Invitation error messages

**Utils - Permissions & Exceptions:**
- `utils/permissions/access_management.py` - Billing error messages
- `utils/permissions/keywordsai_permissions.py` - API key error message
- `utils/permissions/admin_permissions.py` - Admin access error
- `utils/exceptions.py` - Multiple error messages (265, 271, 288, 326, 330, 334, 611)

**Utils - Processing:**
- `utils/preprocessing/llm_generation/chat_generation.py` - Model error messages
- `utils/preprocessing/llm_generation/credentials.py` - Model list URL
- `utils/llm_completion_methods.py` - Model list URL
- `utils/postprocessing/generic_postprocessing.py` - Email subjects + URLs
- `utils/warnings.py` - Credential warnings

**Utils - Constants:**
- `utils/constants/__init__.py` - Email addresses
- `utils/constants/error_message_constants.py` - Multiple error messages
- `utils/constants/payment_constants.py` - Stripe product name/description
- `utils/constants/filters_constant.py` - UI filter labels

**Utils - Types:**
- `utils/keywordsai_types/payment_types.py` - Stripe checkout URLs

**Utils - Other:**
- `utils/notifications.py` - Alert prefix + from email
- `utils/email.py` - Error email subjects
- `utils/onboarding/sample_data.py` - Welcome messages

**Tasks:**
- `tasks/email_tasks.py` - Welcome email
- `user/tasks.py` - Budget warning emails

**Automation:**
- `automation/utils/core.py` - Slack webhook URLs

**Config:**
- `keywordsai/settings.py` - Email defaults
- `.env.template` - Site name

**Migration:**
- New migration for `is_managed` field + data migration + state migration

### SDK Repos to Rebrand (3 repos)

1. **`Keywords-AI/keywordsai`** - Main SDK monorepo
   - 8 Python packages
   - 4 JavaScript packages

2. **`Keywords-AI/keywordsai-mcp`** - MCP server

3. **`Keywords-AI/Keywords-AI-Docs`** - Documentation (if customer-facing references exist)

---

## Notes

- Internal variable names, import paths, and file names are NOT being changed (per user request)
- Old SDK packages will continue to work but stop receiving updates
- Customers will naturally migrate when they see "respan-*" packages with active development
