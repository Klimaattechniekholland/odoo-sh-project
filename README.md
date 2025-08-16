# sale_multi_proposal

Addon to manage multiple proposal quotations in Odoo 18.

- **New Proposal** button → create proposal from main quotation.
- **Proposal fields** on sale order: is_proposal, parent, state, count.
- **Smart button** → view all proposals of a main quotation.
- **Accept Proposal wizard**:
  - Marks proposal as Accepted.
  - Updates parent quotation with proposal lines.
  - If parent is draft/sent → replace lines.
  - If parent is confirmed → set old lines qty=0, then add proposal lines.
- **Service layer** (`sale.proposal.service`) handles duplication safely.