# Observability Parameters Guide

Complete guide to using Keywords AI's observability parameters in the n8n node for tracking, monitoring, and analyzing your LLM calls.

## 📊 Overview

The Keywords AI node includes **5 observability parameters** that help you:
- Track user sessions and requests
- Monitor costs and performance
- Filter and search logs efficiently
- Group related calls together
- Get detailed metrics in responses

All observability parameters are **optional** and found in **Additional Fields**.

---

## 🔍 Available Parameters

### 1. Metadata (JSON)

**Purpose**: Store custom key-value pairs for reference

**How to use**:
1. Expand "Additional Fields"
2. Add "Metadata (JSON)"
3. Enter a JSON object:

```json
{
  "session_id": "sess_abc123",
  "user_type": "premium",
  "feature": "chat_assistant",
  "version": "v2.1",
  "environment": "production"
}
```

**Use cases**:
- Session tracking
- A/B testing variants
- Feature flags
- Environment tagging
- Custom business logic

**View in Keywords AI**: Visible in log details, searchable via filters

---

### 2. Custom Identifier

**Purpose**: Fast, indexed tag for filtering logs

**How to use**:
1. Expand "Additional Fields"
2. Add "Custom Identifier"
3. Enter a string value:

```
transaction_12345
```

**Difference from Metadata**:
- ✅ **Indexed** - faster search and filtering
- ✅ Shows as "Custom ID" field in logs
- ✅ Single string value
- ❌ Can't store multiple key-value pairs

**Use cases**:
- Transaction IDs
- Request IDs
- Order numbers
- Ticket numbers
- Unique identifiers you search frequently

**Best practice**: Use this for IDs you'll search often, use metadata for everything else.

---

### 3. Customer Identifier

**Purpose**: Tag to identify the end user making the request

**How to use**:
1. Expand "Additional Fields"
2. Add "Customer Identifier"
3. Enter user ID:

```
user_john_doe_123
```

**What it enables**:
- User-level analytics
- Per-user cost tracking
- Usage patterns by user
- User-specific logs filtering

**View in Keywords AI**: 
- Users page shows aggregated data per customer
- Can filter logs by customer_identifier

**Example workflow**:
```
HTTP Request (get user from database)
  ↓
Set Variable (userId = "user_123")
  ↓
Keywords AI (customer_identifier: "user_123")
```

---

### 4. Customer Params (JSON)

**Purpose**: Pass detailed customer information for monitoring

**How to use**:
1. Expand "Additional Fields"
2. Add "Customer Params (JSON)"
3. Enter JSON with customer details:

```json
{
  "customer_identifier": "user_123",
  "name": "John Doe",
  "email": "john@example.com",
  "period_start": "2025-01-01",
  "period_end": "2025-01-31",
  "period_budget": 100.0,
  "total_budget": 500.0,
  "budget_duration": "monthly",
  "markup_percentage": 20.0,
  "group_identifier": "enterprise_tier_1"
}
```

**Available fields**:

| Field | Type | Description |
|-------|------|-------------|
| `customer_identifier` | string | **Required** - Unique user ID |
| `name` | string | Customer name |
| `email` | string | Customer email |
| `group_identifier` | string | Group/tier ID |
| `period_start` | string | Budget period start (YYYY-MM-DD) |
| `period_end` | string | Budget period end (YYYY-MM-DD) |
| `period_budget` | float | Budget for the period |
| `total_budget` | float | Total lifetime budget |
| `budget_duration` | string | `yearly`, `monthly`, `weekly`, or `daily` |
| `markup_percentage` | float | Markup % for cost reporting |

**Use cases**:
- Per-user budget tracking
- Cost allocation
- Usage alerts per customer
- Tiered pricing
- Enterprise account management

**View in Keywords AI**: Users page with full analytics and budget tracking

---

### 5. Request Breakdown

**Purpose**: Get detailed metrics in the API response

**How to use**:
1. Expand "Additional Fields"
2. Toggle "Request Breakdown" to `true`

**What you get in response**:
```json
{
  "id": "chatcmpl-...",
  "choices": [...],
  "request_breakdown": {
    "prompt_tokens": 50,
    "completion_tokens": 100,
    "cost": 0.00015,
    "model": "gpt-4o-mini",
    "cached": false,
    "timestamp": "2025-12-31T02:30:00Z",
    "status_code": 200,
    "stream": false,
    "latency": 1.25,
    "routing_time": 0.15,
    "sentiment_score": 0,
    "scores": {},
    "category": "Questions",
    "metadata": {...},
    "prompt_messages": [...],
    "completion_message": {...},
    "full_request": {...}
  }
}
```

**Metrics included**:
- **Tokens**: Prompt, completion, total
- **Cost**: In USD
- **Performance**: Latency, routing time
- **Status**: HTTP status code
- **Caching**: Whether cached
- **Sentiment**: Sentiment score
- **Full request**: Complete request body

**Use cases**:
- Real-time cost monitoring
- Performance tracking
- Building usage dashboards
- Immediate validation
- Cost estimation in workflows

**Note**: In streaming mode, breakdown is sent as the last chunk.

---

## 🎯 Real-World Examples

### Example 1: E-commerce Customer Support

```json
// In n8n Keywords AI node:

Additional Fields:
  ├─ Metadata (JSON):
  │    {
  │      "order_id": "ORD-12345",
  │      "issue_type": "refund",
  │      "priority": "high",
  │      "agent_id": "agent_42"
  │    }
  ├─ Custom Identifier: "ticket_67890"
  ├─ Customer Identifier: "customer_jane_smith"
  └─ Request Breakdown: true
```

**Benefits**:
- Track cost per support ticket
- Link conversations to orders
- Monitor response quality
- Alert on high-cost interactions

---

### Example 2: SaaS Multi-Tenant Platform

```json
Additional Fields:
  ├─ Customer Identifier: "tenant_acme_corp"
  ├─ Customer Params (JSON):
  │    {
  │      "customer_identifier": "tenant_acme_corp",
  │      "name": "Acme Corporation",
  │      "email": "admin@acme.com",
  │      "group_identifier": "enterprise",
  │      "period_budget": 1000.0,
  │      "period_start": "2025-01-01",
  │      "period_end": "2025-01-31",
  │      "markup_percentage": 25.0
  │    }
  └─ Metadata (JSON):
  │    {
  │      "plan": "enterprise",
  │      "feature": "ai_assistant",
  │      "api_version": "v2"
  │    }
```

**Benefits**:
- Per-tenant cost tracking
- Budget alerts
- Usage analytics by tenant
- Chargeback/billing data
- Cost + markup calculation

---

### Example 3: A/B Testing Different Prompts

```json
Workflow A:
  Metadata: {"variant": "A", "test_id": "prompt_test_001"}
  Custom Identifier: "test_001_variant_A"

Workflow B:
  Metadata: {"variant": "B", "test_id": "prompt_test_001"}
  Custom Identifier: "test_001_variant_B"
```

**Benefits**:
- Compare costs between variants
- Track performance differences
- Filter logs by test variant
- Analyze quality metrics

---

### Example 4: Session-Based Chat Application

```json
Additional Fields:
  ├─ Metadata (JSON):
  │    {
  │      "session_id": "sess_abc123",
  │      "conversation_id": "conv_456",
  │      "message_number": 5,
  │      "context": "customer_inquiry"
  │    }
  ├─ Customer Identifier: "user_789"
  └─ Request Breakdown: false
```

**Benefits**:
- Link all messages in a session
- Track conversation costs
- Monitor session lengths
- User engagement metrics

---

## 📈 Best Practices

### 1. **Consistent Naming**
Use consistent ID formats:
- ✅ `user_123`, `user_456`
- ❌ `123`, `user456`, `USER_789` (mixed formats)

### 2. **Strategic Field Selection**
- **High-frequency searches** → Custom Identifier
- **Related data** → Metadata
- **User analytics** → Customer Identifier + Customer Params
- **Cost monitoring** → Request Breakdown

### 3. **Budget Monitoring**
Set up customer params for users who need budget limits:
```json
{
  "customer_identifier": "user_123",
  "period_budget": 50.0,
  "budget_duration": "monthly",
  "period_start": "2025-01-01",
  "period_end": "2025-01-31"
}
```

### 4. **Workflow Integration**
```
Trigger → Get User Data → Set Variables → Keywords AI
                                            ↓
                            (Pass user data in customer params)
```

### 5. **Error Handling**
```json
// In metadata, track error states
{
  "retry_count": 0,
  "fallback_used": false,
  "original_model": "gpt-4o"
}
```

---

## 🔎 Filtering in Keywords AI Dashboard

### By Custom Identifier
```
Logs → Filter → Custom ID: "transaction_12345"
```

### By Customer
```
Logs → Filter → Customer Identifier: "user_123"
or
Users → Select user → View all logs
```

### By Metadata
```
Logs → Filter → Metadata → Key: "session_id", Value: "sess_abc"
```

---

## 🚨 Common Pitfalls

### ❌ Invalid JSON
```json
// BAD - missing quotes
{session_id: 123}

// GOOD
{"session_id": "123"}
```

### ❌ Nested JSON in Metadata Field
Don't pass already-stringified JSON:
```json
// BAD
"{\"key\": \"value\"}"

// GOOD
{"key": "value"}
```

### ❌ Missing Customer Identifier in Customer Params
```json
// BAD - will fail
{
  "name": "John"
}

// GOOD
{
  "customer_identifier": "user_123",
  "name": "John"
}
```

---

## 📚 Related Documentation

- [Keywords AI Metadata Docs](https://docs.keywordsai.co/features/generation/metadata)
- [Customer Identifier Guide](https://docs.keywordsai.co/features/generation/customer-identifier)
- [User Analytics](https://docs.keywordsai.co/features/user/user-creation)
- [API Reference](https://docs.keywordsai.co/api-endpoints/develop/gateway/chat-completions#observability-parameters)

---

## 🎓 Quick Reference

| Parameter | Format | Indexed | Use For |
|-----------|--------|---------|---------|
| Metadata | JSON | No | General data, flexible key-values |
| Custom Identifier | String | Yes | Fast searching, unique IDs |
| Customer Identifier | String | Yes | User tracking, per-user analytics |
| Customer Params | JSON | Yes | Budget tracking, user details |
| Request Breakdown | Boolean | N/A | Real-time metrics in response |

---

**Pro Tip**: Start with just `customer_identifier` and `metadata`, then add others as your monitoring needs grow!

