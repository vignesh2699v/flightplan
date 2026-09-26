#!/usr/bin/env bash
# Build the "Acme Shop" fixture project that fixtures-v3.md runs against.
#
#   bash eval/build-fixture.sh /path/to/new/dir
#
# It is small on purpose: every file exists to give a fixture something true
# to find by reading (a payments rule, a funnel with two drop-offs, 40 legacy
# class names, a store with no tenant concept, a placeholder test).
set -euo pipefail

FX=${1:?usage: build-fixture.sh DIR}
rm -rf "$FX" && mkdir -p "$FX" && cd "$FX"
git init -q -b main
git config user.email fixture@example.com
git config user.name "Fixture Dev"
mkdir -p src/app/checkout src/app/onboarding/steps src/state src/styles src/api/routes tests/fixtures docs

cat > README.md <<'EOF'
# Acme Shop

Storefront for Acme Handmade — small-batch ceramics sold direct to customers.
Next.js 14 (app router), TypeScript, Stripe for payments, a REST API under
`src/api/routes`, and a single client-side store in `src/state/store.ts`.

## Develop

    pnpm install
    pnpm dev          # http://localhost:3000
    pnpm test         # jest unit tests
    pnpm e2e          # playwright, needs STAGING_URL

Staging deploys go through `pnpm deploy:staging` (Vercel preview, needs
VERCEL_TOKEN). Production deploys are manual and owned by Priya.
EOF

cat > CLAUDE.md <<'EOF'
# Working in acme-shop

- Package manager is pnpm. Run `pnpm test` before calling anything done.
- Payments code (`src/app/checkout`, `src/api/routes/payments.ts`) needs a
  second reviewer — never merge changes there without one.
- Use the seeded test accounts in `tests/fixtures/accounts.json` for anything
  that signs up or logs in. Never create accounts against real customer data.
- CSS: we are migrating class names to BEM (`block__element--modifier`).
EOF

cat > package.json <<'EOF'
{
  "name": "acme-shop",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "test": "jest",
    "e2e": "playwright test",
    "deploy:staging": "vercel deploy --token $VERCEL_TOKEN"
  },
  "dependencies": { "next": "14.2.3", "react": "18.3.1", "react-dom": "18.3.1", "stripe": "15.4.0" },
  "devDependencies": { "typescript": "5.4.5", "jest": "29.7.0", "@playwright/test": "1.44.0" }
}
EOF

cat > src/app/checkout/checkout.tsx <<'EOF'
"use client";
import { useState } from "react";
import { createPaymentIntent } from "../../api/client";

export default function Checkout({ cartTotal }: { cartTotal: number }) {
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createPaymentIntent(cartTotal);
      window.location.href = "/order/confirmed";
    } catch (err) {
      setError("Payment failed. Please try again.");
    }
  }

  return (
    <form onSubmit={onSubmit} className="checkoutForm">
      <p className="checkoutTotal">Total: ${cartTotal.toFixed(2)}</p>
      {error && <p className="errorText">{error}</p>}
      <button type="submit" className="primaryBtn">Pay now</button>
    </form>
  );
}
EOF

for s in Welcome Email Password Profile VerifyEmail Done; do
cat > "src/app/onboarding/steps/$s.tsx" <<EOF
export default function ${s}Step({ onNext }: { onNext: () => void }) {
  return (
    <section className="onboardStep">
      <h2 className="stepTitle">${s}</h2>
      {/* TODO: copy from design */}
      <button className="primaryBtn" onClick={onNext}>Continue</button>
    </section>
  );
}
EOF
done

cat > src/app/onboarding/flow.tsx <<'EOF'
// Six steps, no back button, no saved progress. Abandoning VerifyEmail
// restarts the whole flow (see docs/analytics-2026-08.md).
import Welcome from "./steps/Welcome";
import Email from "./steps/Email";
import Password from "./steps/Password";
import Profile from "./steps/Profile";
import VerifyEmail from "./steps/VerifyEmail";
import Done from "./steps/Done";
export const STEPS = [Welcome, Email, Password, Profile, VerifyEmail, Done];
EOF

cat > src/state/store.ts <<'EOF'
// One global store for the whole app. Every slice lives here and every
// component subscribes to the root. There is no notion of a tenant.
type State = { user: unknown; cart: unknown[]; catalog: unknown[]; flags: Record<string, boolean> };
let state: State = { user: null, cart: [], catalog: [], flags: {} };
const listeners = new Set<() => void>();
export const getState = () => state;
export function setState(patch: Partial<State>) { state = { ...state, ...patch }; listeners.forEach((l) => l()); }
export const subscribe = (l: () => void) => (listeners.add(l), () => listeners.delete(l));
EOF

for c in checkoutForm checkoutTotal errorText primaryBtn secondaryBtn onboardStep stepTitle navBar navLink navLinkActive \
         productCard productImage productTitle productPrice cartDrawer cartItem cartItemQty cartTotalRow footerWrap footerLink \
         heroBanner heroTitle heroSubtitle searchInput searchResults badgeNew badgeSale modalBackdrop modalPanel modalClose \
         toastWrap toastSuccess toastError formRow formLabel formInput formHint spinnerSmall spinnerLarge pageContainer; do
  echo ".$c { /* legacy name */ }" >> src/styles/app.css
done

for r in products orders users payments; do
cat > "src/api/routes/$r.ts" <<EOF
// REST handler for /api/$r — GET list, GET by id, POST create.
export async function GET(req: Request) { return Response.json([]); }
export async function POST(req: Request) { return Response.json({ ok: true }); }
EOF
done

cat > src/api/client.ts <<'EOF'
export async function createPaymentIntent(amount: number) {
  const res = await fetch("/api/payments", { method: "POST", body: JSON.stringify({ amount }) });
  if (!res.ok) throw new Error("payment failed");
  return res.json();
}
EOF

echo 'test("session expires after AUTH_TIMEOUT_MS", () => { expect(true).toBe(true); });' > tests/auth.test.ts
echo '[{"email":"test+1@acme.test","password":"seeded"}]' > tests/fixtures/accounts.json

cat > docs/analytics-2026-08.md <<'EOF'
# Onboarding funnel, August 2026

Welcome 100% -> Email 81% -> Password 74% -> Profile 52% -> VerifyEmail 31% -> Done 29%.
Biggest drops: Profile (asks for address and phone before any value is shown)
and VerifyEmail (abandoning it restarts the flow from Welcome).
EOF

git add -A && git commit -q -m "Initial storefront: checkout, catalog, REST API"
echo "// retry once on network error" >> src/api/client.ts && git commit -qam "Retry payment intent once on network error"
echo "" >> src/app/onboarding/flow.tsx && git commit -qam "Add VerifyEmail step to onboarding"
echo "/* dark mode pending */" >> src/styles/app.css && git commit -qam "Stub dark-mode styles"
echo "// TODO tenants" >> src/state/store.ts && git commit -qam "Note: store has no tenant concept yet"
git remote add origin https://github.com/acme/shop.git
echo "Built $(git rev-list --count HEAD) commits in $FX"
