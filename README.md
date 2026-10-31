# Brightloop Subscription Management System

An Odoo 19-based subscription management solution.

## Project Overview

This project aims to manage the complete subscription lifecycle:

- Customer registration and access management
- Staff and administrator roles
- Product and product variant management
- Subscription plans
- Quotations and subscriptions
- Recurring invoices and billing
- Taxes and discounts
- Payment tracking
- Finance dashboard and reports
- Restricted evaluator access

## Technology Stack

| Component | Technology |
|---|---|
| ERP | Odoo 19 |
| Backend | Python |
| Frontend | Odoo XML Views and JavaScript |
| Database | PostgreSQL |
| Version Control | Git and GitHub |

## Repository Structure

- custom_addons: Custom Odoo modules
- docs: Project documentation
- config: Example configuration
- scripts: Development scripts

## Custom Addons

| Addon | Purpose |
|---|---|
| brightloop_base | Shared functionality |
| brightloop_subscription | Subscription lifecycle |
| brightloop_billing | Billing and invoices |
| brightloop_discount | Discount management |
| brightloop_portal | Customer and evaluator portal |
| brightloop_dashboard | Dashboards and reports |

## Development

1. Set up Odoo 19 and PostgreSQL.
2. Configure the custom addon path.
3. Restart the Odoo server.
4. Update the Apps List.
5. Install the required custom addons.

Refer to docs/installation.md.

## Git Workflow

- main: Stable branch
- integration: Integration branch
- feature branches: Individual development tasks

All changes must be tested before merging into main.

## Security

Never commit passwords, API keys, or private credentials.

## Project Status

Initial repository structure created. Implementation pending.
