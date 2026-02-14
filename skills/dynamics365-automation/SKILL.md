---
name: Dynamics 365 Automation
description: "Dynamics 365 Automation: manage CRM contacts, accounts, leads, opportunities, sales orders, invoices, and cases via the Dynamics CRM Web API"
requires:
  mcp: [rube]
---

# Dynamics 365 Automation

Automate Microsoft Dynamics 365 CRM operations including creating and updating contacts, accounts, leads, opportunities, sales orders, invoices, and support cases.

**Toolkit docs:** [composio.dev/toolkits/dynamics365](https://composio.dev/toolkits/dynamics365)

---

## Setup

This skill requires the **Rube MCP server** connected at `https://rube.app/mcp`.

Before executing any tools, ensure an active connection exists for the `dynamics365` toolkit. If no connection is active, initiate one via `RUBE_MANAGE_CONNECTIONS`.

---

## Core Workflows

### 1. Manage Leads

Create, update, retrieve, and list lead records.

**Tools:**
- `DYNAMICS365_DYNAMICSCRM_CREATE_LEAD` -- Create a new lead
- `DYNAMICS365_DYNAMICSCRM_UPDATE_LEAD` -- Update an existing lead
- `DYNAMICS365_DYNAMICSCRM_GET_A_LEAD` -- Retrieve a lead by GUID
- `DYNAMICS365_DYNAMICSCRM_GET_ALL_LEADS` -- List/filter all leads

**Key Parameters for `DYNAMICS365_DYNAMICSCRM_CREATE_LEAD`:**
- `firstname` -- First name of the lead
- `lastname` -- Last name of the lead
- `emailaddress1` -- Primary email address
- `telephone1` -- Primary phone number
- `companyname` -- Associated company name
- `subject` -- Brief title/description

**Key Parameters for `DYNAMICS365_DYNAMICSCRM_GET_ALL_LEADS`:**
- `filter` -- OData filter, e.g., `"contains(fullname,'John')"`
- `select` -- Fields to return, e.g., `"fullname,emailaddress1"`
- `orderby` -- Sort expression, e.g., `"createdon desc"`
- `top` -- Max number of results

**Example:**
```
Tool: DYNAMICS365_DYNAMICSCRM_CREATE_LEAD
Arguments:
  firstname: "Jane"
  lastname: "Smith"
  emailaddress1: "jane.smith@example.com"
  companyname: "Acme Corp"
  subject: "Interested in Enterprise plan"
```

---

### 2. Manage Accounts

Create and organize account (company) records in the CRM.

**Tool:** `DYNAMICS365_DYNAMICSCRM_CREATE_ACCOUNT`

**Key Parameters:**
- `name` -- Account/company name
- `description` -- Description of the account
- `revenue` -- Revenue amount (number)
- `accountcategorycode` -- Category code (integer, default: 1)
- `creditonhold` -- Whether account is on credit hold (boolean)

**Example:**
```
Tool: DYNAMICS365_DYNAMICSCRM_CREATE_ACCOUNT
Arguments:
  name: "Contoso Ltd"
  description: "Strategic partner for cloud services"
  revenue: 5000000
  creditonhold: false
```

---

### 3. Manage Contacts

Create detailed contact records with address and phone information.

**Tool:** `DYNAMICS365_DYNAMICSCRM_CREATE_CONTACT`

**Key Parameters:**
- `firstname`, `lastname` -- Contact name
- `emailaddress1` -- Primary email
- `telephone1` -- Primary phone
- `mobilephone` -- Mobile phone
- `jobtitle` -- Job title
- `address1_city`, `address1_stateorprovince`, `address1_postalcode`, `address1_country` -- Address fields

**Example:**
```
Tool: DYNAMICS365_DYNAMICSCRM_CREATE_CONTACT
Arguments:
  firstname: "Bob"
  lastname: "Johnson"
  emailaddress1: "bob.johnson@example.com"
  jobtitle: "VP of Engineering"
  address1_city: "Seattle"
  address1_stateorprovince: "WA"
```

---

### 4. Manage Opportunities

Create and update sales opportunities with estimated values and close dates.

**Tools:**
- `DYNAMICS365_DYNAMICSCRM_CREATE_OPPORTUNITY` -- Create a new opportunity
- `DYNAMICS365_DYNAMICSCRM_UPDATE_OPPORTUNITY` -- Update an existing opportunity

**Key Parameters for `DYNAMICS365_DYNAMICSCRM_CREATE_OPPORTUNITY`:**
- `name` (required) -- Opportunity title
- `description` -- Brief description
- `estimatedvalue` -- Anticipated revenue (number)
- `estimatedclosedate` -- Expected close date in `YYYY-MM-DD` format
- `customer_account_id` -- GUID of the related account (no curly braces)
- `customer_contact_id` -- GUID of the related contact (no curly braces)

**Key Parameters for `DYNAMICS365_DYNAMICSCRM_UPDATE_OPPORTUNITY`:**
- `opportunity_id` (required) -- GUID of the opportunity
- `opportunityratingcode` -- 1 (Cold), 2 (Warm), 3 (Hot)
- `salesstagecode` -- 1 (Qualify), 2 (Develop), 3 (Propose)

**Example:**
```
Tool: DYNAMICS365_DYNAMICSCRM_CREATE_OPPORTUNITY
Arguments:
  name: "Enterprise Cloud Migration"
  estimatedvalue: 250000
  estimatedclosedate: "2026-06-30"
  description: "Full cloud migration project for Contoso"
```

---

### 5. Manage Sales Orders and Invoices

Create and update sales orders; generate invoices for billing.

**Tools:**
- `DYNAMICS365_DYNAMICSCRM_CREATE_SALES_ORDER` -- Create a new sales order
- `DYNAMICS365_DYNAMICSCRM_UPDATE_SALES_ORDER` -- Update an existing sales order
- `DYNAMICS365_DYNAMICSCRM_CREATE_INVOICE` -- Create a new invoice

**Key Parameters for `DYNAMICS365_DYNAMICSCRM_CREATE_SALES_ORDER`:**
- `name` -- Sales order name
- `description` -- Description
- `account_id` -- Reference to account, format: `"/accounts(GUID)"`
- `currency_id` -- Currency reference, format: `"/transactioncurrencies(GUID)"`
- `price_level_id` -- Price list reference, format: `"/pricelevels(GUID)"`

**Key Parameters for `DYNAMICS365_DYNAMICSCRM_UPDATE_SALES_ORDER`:**
- `salesorder_id` (required) -- GUID of the sales order
- `name` -- Updated name
- `discountamount` -- Updated discount
- `freightamount` -- Updated shipping cost

**Key Parameters for `DYNAMICS365_DYNAMICSCRM_CREATE_INVOICE`:**
- `name` -- Invoice name/number, e.g., `"Invoice #12345"`
- `description` -- Invoice description
- `account_id` -- Related account reference
- `currency_id` -- Currency reference
- `price_level_id` -- Price list reference

---

### 6. Create Support Cases

Create incident/case records for customer support tracking.

**Tool:** `DYNAMICS365_DYNAMICSCRM_CREATE_CASE`

**Key Parameters:**
- `title` -- Subject/title of the case
- `description` -- Detailed description
- `prioritycode` -- 1 (Low), 2 (Normal), 3 (High)
- `caseorigincode` -- 1 (Phone), 2 (Email), 3 (Web)
- `account_id` -- Related account, format: `"/accounts(GUID)"`
- `contact_id` -- Related contact, format: `"/contacts(GUID)"`

**Example:**
```
Tool: DYNAMICS365_DYNAMICSCRM_CREATE_CASE
Arguments:
  title: "Login issue reported by customer"
  description: "Customer unable to access portal since Feb 10"
  prioritycode: 3
  caseorigincode: 2
```

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| **GUID format** | All entity IDs are GUIDs (e.g., `"00000000-0000-0000-0000-000000000000"`). Do not include curly braces for opportunity/contact references. |
| **Reference format** | Related entity references use the format `"/entityset(GUID)"` (e.g., `"/accounts(abc-123)"`). Missing the leading slash or parentheses causes errors. |
| **OData filter syntax** | Use Dynamics 365 OData syntax for `filter` (e.g., `contains(fullname,'John')`). Incorrect syntax returns empty or error responses. |
| **user_id default** | Most tools default `user_id` to `"me"` for the authenticated user. Override only when acting on behalf of another user. |
| **Required fields** | `CREATE_OPPORTUNITY` requires `name`. Other create tools have no strict required fields but will create empty records without data. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `DYNAMICS365_DYNAMICSCRM_CREATE_LEAD` | Create a new lead record |
| `DYNAMICS365_DYNAMICSCRM_UPDATE_LEAD` | Update an existing lead |
| `DYNAMICS365_DYNAMICSCRM_GET_A_LEAD` | Retrieve a lead by GUID |
| `DYNAMICS365_DYNAMICSCRM_GET_ALL_LEADS` | List/filter all leads |
| `DYNAMICS365_DYNAMICSCRM_CREATE_ACCOUNT` | Create a new account |
| `DYNAMICS365_DYNAMICSCRM_CREATE_CONTACT` | Create a new contact |
| `DYNAMICS365_DYNAMICSCRM_CREATE_OPPORTUNITY` | Create a new opportunity |
| `DYNAMICS365_DYNAMICSCRM_UPDATE_OPPORTUNITY` | Update an existing opportunity |
| `DYNAMICS365_DYNAMICSCRM_CREATE_SALES_ORDER` | Create a new sales order |
| `DYNAMICS365_DYNAMICSCRM_UPDATE_SALES_ORDER` | Update an existing sales order |
| `DYNAMICS365_DYNAMICSCRM_CREATE_INVOICE` | Create a new invoice |
| `DYNAMICS365_DYNAMICSCRM_CREATE_CASE` | Create a support case/incident |

---

*Powered by [Composio](https://composio.dev)*
