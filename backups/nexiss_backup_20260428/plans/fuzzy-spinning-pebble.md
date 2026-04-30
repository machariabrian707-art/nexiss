# Traxist Marketplace — Full Implementation Plan

## Context
Build a public, self-serve marketplace with buyer/seller/delivery/admin roles, mock wallet + manual payment proof, and order tracking. MVP focuses on **solid auth + role enforcement on the server**, not premature optimization.

---

## Tech Stack
- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **Backend:** Supabase (PostgreSQL + Auth + RLS)
- **Database:** PostgreSQL with Row-Level Security (RLS) for role-based access
- **Auth:** Supabase Auth (email/password), roles stored on `user_metadata`
- **Hosting:** Vercel (frontend) + Supabase Cloud (backend)

---

## Data Model & Auth

### Core Tables
```
users
├── id (UUID, PK)
├── email
├── role (enum: buyer, seller, delivery, admin)
├── status (active, pending_review, suspended)
├── wallet_balance (mock, for display)
└── created_at

sellers
├── id (UUID, FK: users.id)
├── shop_name
├── description
├── verification_status (unverified, verified, suspended)
└── created_at

delivery_partners
├── id (UUID, FK: users.id)
├── service_name
├── rates_per_km (JSON or separate table)
├── status (available, unavailable)
└── created_at

products
├── id (UUID, PK)
├── seller_id (FK: sellers.id)
├── name
├── description
├── price
├── quantity_available
├── created_at

orders
├── id (UUID, PK)
├── buyer_id (FK: users.id)
├── seller_id (FK: sellers.id)
├── delivery_partner_id (FK: delivery_partners.id, nullable)
├── status (pending_payment, awaiting_fulfillment, in_transit, delivered, disputed)
├── total_price
├── created_at

order_items
├── id (UUID, PK)
├── order_id (FK: orders.id)
├── product_id (FK: products.id)
├── quantity
├── price_at_time

payments
├── id (UUID, PK)
├── order_id (FK: orders.id)
├── payment_method (mock_wallet, manual_proof)
├── status (pending, verified, failed)
├── proof_url (if manual_proof)
├── created_at

messages
├── id (UUID, PK)
├── sender_id (FK: users.id)
├── receiver_id (FK: users.id)
├── order_id (FK: orders.id, nullable)
├── content
├── created_at

admin_logs
├── id (UUID, PK)
├── admin_id (FK: users.id)
├── action (suspend_user, verify_seller, etc.)
├── target_id (user affected)
├── created_at
```

### Row-Level Security (RLS) Rules
- **Sellers:** Only see/edit their own products and orders.
- **Delivery partners:** Only see orders assigned to them; only update their own rates.
- **Buyers:** Only see products; only see their own orders and messages.
- **Admin:** See all (with audit logs).

---

## Pages & Routes

### Public (No Login Required)
- `/` — Landing page (hero, featured products, signup CTA)
- `/products` — Browse all products by seller
- `/auth/signup` — Sign up (role selection: buyer / seller)
- `/auth/login` — Login

### Authenticated Routes
#### Buyer Dashboard (`/dashboard/buyer`)
- Overview: recent orders, wallet balance, saved sellers
- Orders: view orders, track delivery, dispute
- Messages: conversations with sellers/delivery partners
- Account: profile, wallet top-up (mock), payment method mgmt

#### Seller Dashboard (`/dashboard/seller`)
- Products: create, edit, delete, manage inventory
- Orders: incoming orders, fulfill, mark shipped
- Delivery: select delivery partner or mark self-ship
- Messages: conversations with buyers
- Analytics: revenue, order count (simple)
- Account: shop profile, verification status

#### Delivery Partner Dashboard (`/dashboard/delivery`)
- Jobs: available orders to pick up, filter by location/price
- Active pickups: current jobs in transit
- Completed: delivery history, earnings
- Rates: set base rate per km, surge pricing (mock)
- Account: profile, bank details for payout

#### Admin Dashboard (`/dashboard/admin`)
- Users: list, search, suspend/unsuspend, verify sellers
- Orders: view all, dispute resolution
- Payments: verify manual proofs, mark as complete
- Sellers: manage verification queue
- Logs: audit trail of admin actions

---

## Authentication & Authorization

### Sign-Up Flow
1. User picks role (buyer / seller / delivery).
2. Email + password signup via Supabase Auth.
3. `user_metadata.role` set at signup; `status: 'active'` for buyers, `'pending_review'` for sellers/delivery.
4. Sellers/delivery redirected to verification page (mock: auto-verify after 1 min for MVP).
5. Admin manually verifies in admin dashboard (toggle in MVP for speed).

### Login Flow
1. Email + password via Supabase Auth.
2. Role + status fetched from JWT (decoded client-side; validated server-side on every API call).
3. Redirect to role-specific dashboard.

### Server-Side Authorization
- Every API route checks: `req.user.role` + `req.user.status` against the action.
- Example: `POST /api/orders` → verify `role === 'buyer'` + `status === 'active'`.
- Supabase RLS enforces row-level checks (e.g., sellers can only update their own products).

---

## Payment & Escrow (MVP)

### Payment Flow
1. **Buyer initiates checkout:**
   - Reviews cart (buyer's mock wallet has unlimited balance for MVP).
   - Selects payment method: mock wallet or manual proof.

2. **If mock wallet:**
   - Order status → `pending_fulfillment` immediately.
   - Display confirmation.

3. **If manual proof:**
   - Order status → `pending_payment`.
   - Buyer uploads M-Pesa/bank receipt.
   - Admin reviews in dashboard, clicks "Verify" or "Reject."
   - On verify → order status → `pending_fulfillment`.

4. **Seller fulfills:**
   - Seller marks order ready; selects delivery partner or self-ship.
   - Order status → `in_transit` or `shipped`.

5. **Delivery & completion:**
   - Delivery partner marks delivered (with photo proof, optional for MVP).
   - Order status → `delivered`.
   - Escrow released (mock: no actual fund movement; just mark complete).

---

## Implementation Phases

### Phase 1: Core Setup (Days 1–2)
- [ ] Next.js + Supabase setup
- [ ] Database schema + RLS policies
- [ ] Auth (signup, login, role selection)
- [ ] Home / landing page (static HTML + CTA)

### Phase 2: Buyer & Product Catalog (Day 3)
- [ ] Product listing page + product detail
- [ ] Shopping cart (client-side state)
- [ ] Checkout (mock wallet only)
- [ ] Order confirmation
- [ ] Buyer dashboard (order history)

### Phase 3: Seller & Product Management (Day 4)
- [ ] Seller signup + verification queue
- [ ] Seller dashboard: add/edit products
- [ ] Seller order dashboard: view, fulfill, ship
- [ ] Delivery partner selection (mock: auto-assign or buyer picks)

### Phase 4: Delivery Partners (Day 5)
- [ ] Delivery partner signup
- [ ] Delivery dashboard: available jobs, accept/complete
- [ ] Rate setting (simple form)
- [ ] Earnings tracker (mock)

### Phase 5: Admin & Manual Payments (Day 6)
- [ ] Admin auth + dashboard
- [ ] Seller verification queue
- [ ] Manual payment proof review
- [ ] User suspension/account management
- [ ] Audit logs (basic)

### Phase 6: Messaging & Polish (Day 7)
- [ ] Buyer–seller messaging (real-time via Supabase subscriptions)
- [ ] Delivery–seller messaging
- [ ] Message notifications (optional for MVP)
- [ ] UI polish, error handling

### Phase 7: Testing & Deployment (Day 8)
- [ ] End-to-end test (buyer flow, seller flow, admin flow)
- [ ] Deploy to Vercel + Supabase
- [ ] Performance review, security checklist

---

## Critical Implementation Rules

### Auth
- **Every API route must validate `req.user.role` server-side.** No role checking only in the UI.
- **Supabase RLS policies enforce data isolation.** E.g., a seller querying `/api/products/123` can only edit if `seller_id === req.user.id`.

### Data
- **No demo escrow stored in the UI.** All order state lives in the database (`status` column).
- **Manual proofs uploaded to Supabase Storage,** not just stored as URLs.

### Security
- **No hardcoded admin credentials in the prompt.** Admins are invited or manually added in Supabase.
- **Idempotent checkout:** If buyer double-clicks "Place Order," only one order is created (use a unique constraint on `(buyer_id, cart_hash)` or redirect after checkout).

---

## Verification (How to Test)

1. **Signup & login as each role:**
   - Buyer → lands in buyer dashboard
   - Seller → lands in seller dashboard (verification pending)
   - Delivery → lands in delivery dashboard (verification pending)
   - Admin → lands in admin dashboard

2. **Buyer flow:**
   - Browse products
   - Add to cart
   - Checkout (mock wallet)
   - Order appears in order history

3. **Seller flow:**
   - Create a product
   - Receive order from buyer
   - Mark fulfilled
   - Assign delivery partner

4. **Delivery flow:**
   - Accept job
   - Mark as in-transit
   - Mark as delivered

5. **Admin flow:**
   - Verify seller
   - Review manual payment proof (if used)
   - Suspend a user
   - Check audit logs

---

## Critical Files to Create

- `app/layout.tsx` — Root layout, auth context
- `app/auth/signup/page.tsx` — Signup form + role selection
- `app/auth/login/page.tsx` — Login form
- `app/page.tsx` — Landing page
- `app/products/page.tsx` — Product listing
- `app/products/[id]/page.tsx` — Product detail
- `app/dashboard/buyer/page.tsx` — Buyer dashboard
- `app/dashboard/seller/page.tsx` — Seller dashboard
- `app/dashboard/delivery/page.tsx` — Delivery dashboard
- `app/dashboard/admin/page.tsx` — Admin dashboard
- `lib/supabase.ts` — Supabase client
- `lib/auth.ts` — Auth helpers (check role, etc.)
- `api/auth/[auth].ts` — Auth callback
- `api/products.ts` — Product CRUD
- `api/orders.ts` — Order CRUD + status updates
- `api/payments.ts` — Payment proof upload + verification
- Database migrations (Supabase SQL)

---

## Next Steps
Once approved, I will:
1. Initialize Next.js + Supabase
2. Create database schema + RLS policies
3. Build Phase 1 (auth + landing page)
4. Continue through phases in order
5. Test end-to-end before deployment
