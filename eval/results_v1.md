# Evaluation Results (router v1, retriever tfidf)

- Routing accuracy vs expected: **14/14 (100.0%)**
- Avg tool-call latency (when tool used): **50.2 ms**
- Avg total end-to-end latency: **29.8 ms**

| # | Question | Expected route | Actual route | Match | Tool latency (ms) | Total latency (ms) |
|---|----------|-----------------|--------------|-------|--------------------|--------------------|
| 1 | How much does the Team plan cost per month? | tool | tool | ✅ | 50.2 | 51.4 |
| 2 | What is the difference between the Team and Business plans? | kb | kb | ✅ | - | 1.4 |
| 3 | How many API calls does the Business plan include per month? | tool | tool | ✅ | 50.2 | 51.3 |
| 4 | Is my data encrypted at rest? | kb | kb | ✅ | - | 1.3 |
| 5 | What is the annual price per month for the Starter plan? | tool | tool | ✅ | 50.2 | 51.1 |
| 6 | How long is version history retained on the Team plan? | kb | kb | ✅ | - | 1.2 |
| 7 | What is the overage rate per GB for the Business plan? | tool | tool | ✅ | 50.1 | 50.9 |
| 8 | Can I restrict external sharing for my whole organization? | kb | kb | ✅ | - | 1.1 |
| 9 | How many users are allowed on the Starter plan? | tool | tool | ✅ | 50.2 | 51.0 |
| 10 | What support channels are available on the Business tier? | kb | kb | ✅ | - | 1.5 |
| 11 | What happens to files after I delete them? | kb | kb | ✅ | - | 1.1 |
| 12 | How much storage do I get on the Team plan? | tool | tool | ✅ | 50.1 | 51.2 |
| 13 | What happens if I go over my storage limit, and what's the exact per-GB overage charge? | tool | tool | ✅ | 50.2 | 51.4 |
| 14 | If I exceed my included API calls on the Business plan, what happens and what does it cost? | tool | tool | ✅ | 50.1 | 51.4 |

## Answers (for manual quality review)

**Q1: How much does the Team plan cost per month?**

> [mock-llm] According to the live pricing lookup, plan_name=Team, monthly_price_usd=24, annual_price_usd_per_month=19, storage_gb=1000, max_users=10, api_calls_included_per_month=10000, overage_rate_per_gb_usd=0.04.

**Q2: What is the difference between the Team and Business plans?**

> [mock-llm] Based on the knowledge base: [02_plans.md] # CloudNest Plans (Feature Comparison)
CloudNest offers three tiers: Starter, Team, and Business.
- Starter: individual use, basic sharing, 2 device sync limit.
- Team: shared workspaces, admin console, unlimited device sync.
- Business: SSO, advanced audit logs, dedicated support, custom data residency.
Note: Exact current pricing, storage quotas, and included API calls change perio

**Q3: How many API calls does the Business plan include per month?**

> [mock-llm] According to the live pricing lookup, plan_name=Business, monthly_price_usd=59, annual_price_usd_per_month=49, storage_gb=5000, max_users=50, api_calls_included_per_month=50000, overage_rate_per_gb_usd=0.03.

**Q4: Is my data encrypted at rest?**

> [mock-llm] Based on the knowledge base: [04_security.md] # Security & Compliance
All data in CloudNest is encrypted at rest (AES-256) and in transit (TLS 1.2+).
CloudNest is SOC 2 Type II certified. Business tier customers can request a copy of the audit report.
Two-factor authentication (2FA) is available on all tiers via TOTP apps (Google Authenticator, Authy).
GDPR data processing agreements are available for EU customers on request.

**Q5: What is the annual price per month for the Starter plan?**

> [mock-llm] According to the live pricing lookup, plan_name=Starter, monthly_price_usd=9, annual_price_usd_per_month=7, storage_gb=100, max_users=1, api_calls_included_per_month=1000, overage_rate_per_gb_usd=0.05.

**Q6: How long is version history retained on the Team plan?**

> [mock-llm] Based on the knowledge base: [12_data_retention.md] # Data Retention and Deletion
Deleted files are moved to Trash and retained for 30 days before permanent deletion.
Version history is retained for 90 days on Team and Business tiers, 7 days on Starter.
Business tier customers can configure custom retention periods for compliance purposes.

[08_api_rate_limits.md] # API Rate Limits
The CloudNest REST API enforces per-plan rat

**Q7: What is the overage rate per GB for the Business plan?**

> [mock-llm] According to the live pricing lookup, plan_name=Business, monthly_price_usd=59, annual_price_usd_per_month=49, storage_gb=5000, max_users=50, api_calls_included_per_month=50000, overage_rate_per_gb_usd=0.03.

**Q8: Can I restrict external sharing for my whole organization?**

> [mock-llm] Based on the knowledge base: [06_sharing_permissions.md] # Sharing and Permissions
Files and folders can be shared via link (view/comment/edit) or invited by email with role-based access.
Roles available: Viewer, Commenter, Editor, and Owner.
Admins on Team and Business plans can restrict external sharing organization-wide via the admin console.
Shared links can be set to expire after a custom number of days.

[11_onboarding.

**Q9: How many users are allowed on the Starter plan?**

> [mock-llm] According to the live pricing lookup, plan_name=Starter, monthly_price_usd=9, annual_price_usd_per_month=7, storage_gb=100, max_users=1, api_calls_included_per_month=1000, overage_rate_per_gb_usd=0.05.

**Q10: What support channels are available on the Business tier?**

> [mock-llm] Based on the knowledge base: [10_support_channels.md] # Support Channels
Starter: community forum and email support (48-hour response target).
Team: email and live chat support (business hours, 4-hour response target).
Business: dedicated support engineer and 24/7 priority phone support.

[04_security.md] # Security & Compliance
All data in CloudNest is encrypted at rest (AES-256) and in transit (TLS 1.2+).
CloudNest is SOC 2

**Q11: What happens to files after I delete them?**

> [mock-llm] Based on the knowledge base: [13_backup_versioning.md] # Backup and Versioning
CloudNest automatically keeps prior versions of edited files, allowing rollback to any saved version.
Full account-level backup exports can be requested by admins and are delivered as a downloadable archive.
Version history storage does not count against a workspace's storage quota.

[14_mobile_app.md] # Mobile App
The CloudNest mobile app supports

**Q12: How much storage do I get on the Team plan?**

> [mock-llm] According to the live pricing lookup, plan_name=Team, monthly_price_usd=24, annual_price_usd_per_month=19, storage_gb=1000, max_users=10, api_calls_included_per_month=10000, overage_rate_per_gb_usd=0.04.

**Q13: What happens if I go over my storage limit, and what's the exact per-GB overage charge?**

> [mock-llm] According to the live pricing lookup, plan_name=Team, monthly_price_usd=24, annual_price_usd_per_month=19, storage_gb=1000, max_users=10, api_calls_included_per_month=10000, overage_rate_per_gb_usd=0.04.

**Q14: If I exceed my included API calls on the Business plan, what happens and what does it cost?**

> [mock-llm] According to the live pricing lookup, plan_name=Business, monthly_price_usd=59, annual_price_usd_per_month=49, storage_gb=5000, max_users=50, api_calls_included_per_month=50000, overage_rate_per_gb_usd=0.03.

