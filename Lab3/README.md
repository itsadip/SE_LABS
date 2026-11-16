# Lab 3 – Component Modelling & Architectural Pattern Selection

**Aditya Pradeep · PES2UG24AM900 · Section 5B**
**Scenario:** Self-Service Coffee Kiosk System · **Chosen architecture:** Layered

| Deliverable | File |
|-------------|------|
| Component diagram: 5 components plus the external gateway, 5 ball-and-socket interfaces and 1 «use» dependency | `ComponentDiagram.png`, `ComponentDiagram.pdf` (source: `ComponentDiagram.svg`) |
| Written justification (1 page) | `Architecture_Justification.docx`, `Architecture_Justification.pdf` |

## Components and interfaces

| Interface | Provided by (ball) | Required by (socket) | Protocol |
|-----------|--------------------|----------------------|----------|
| IOrderService | Order Manager | Kiosk Touch UI | In-process API call |
| IPaymentProcessing | Payment Service | Order Manager | API call `authorize(amount, card)` |
| IMenuCatalog | Menu & Pricing Repository | Order Manager | SQL query (SQLite) |
| IReceiptPrinting | Receipt Printer Service | Order Manager | Hardware interface: ESC/POS over USB |
| ICardGateway | Card Payment Gateway (external) | Payment Service | HTTPS / TLS 1.2 (PCI-DSS) |
