# Listing Orchestrator — CLI + live Etsy / eBay setup

**How linking works:** Studio saves seed packs. The **orchestrator CLI** reads those packs and calls Etsy/eBay using credentials in `.env`. No Shopify required.

```
Cozy /studio  →  data/seed-inventory/<sku>/
                      ↓
              python publish.py --channels etsy,ebay
                      ↓
              Live APIs (if .env linked)  or  mock (if not)
```

---

## Part A — Orchestrator CLI (once linked)

### One-time setup on your PC

```powershell
cd c:\Users\desmo\Projects\Project-Showcase\projects\listing-orchestrator
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` after you create keys (Parts B and C below).

### Day-to-day flow

**1. Add inventory in Studio**  
Open http://localhost:3000/studio → upload photos → Save seed pack  
→ files land in `cozy-connoisseur-co\data\seed-inventory\<SKU>\`

**2. Confirm accounts are LIVE (not mock)**

```powershell
cd c:\Users\desmo\Projects\Project-Showcase\projects\listing-orchestrator
.\.venv\Scripts\activate
python verify_accounts.py --channels etsy,ebay
```

Expect something like:

```text
etsy: LIVE · shop_id=... · name=...
ebay: LIVE · environment=sandbox
```

If it says `MOCK`, credentials are missing/expired — fix `.env` / re-run OAuth.

**3. Publish listings**

```powershell
python publish.py --seed "c:\Users\desmo\Projects\cozy-connoisseur-co\data\seed-inventory" --channels etsy,ebay
```

- With keys → `mode: "live"` in `outputs/publish_log.json`  
- Without keys → `mode: "mock"` (safe demo)

**4. Sync sales → notify + contact log**

```powershell
python sync_orders.py --channels etsy,ebay
```

Writes `outputs/seller_notifications.json` and appends `outputs/contacts.jsonl`.

### Useful CLI commands

| Command | Purpose |
| --- | --- |
| `python run_demo.py` | Built-in demo seed (no Cozy needed) |
| `python etsy_oauth.py` | Link Etsy shop → writes tokens into `.env` |
| `python verify_accounts.py --channels etsy` | Check Etsy link |
| `python verify_accounts.py --channels ebay` | Check eBay link |
| `python publish.py --seed <path> --channels etsy` | Etsy only |
| `python publish.py --seed <path> --channels ebay,etsy` | Both |
| `python sync_orders.py --channels etsy,ebay` | Pull sales |

---

## Part B — Create Etsy seller account + API keys

### B1. Seller shop (if you don’t have one)

1. https://www.etsy.com/sell → open a shop for **Cozy Connoisseur**  
2. Complete shop setup (payment, shipping, policies) so API listing creates are allowed  

### B2. Developer app (API keys)

1. Sign in as the **same** seller account  
2. Open https://www.etsy.com/developers/your-apps  
3. **Create a new app** (Personal / Seller app is fine to start)  
4. On the app page, copy:
   - **Keystring** → this is `ETSY_API_KEY`  
   - Shared secret → keep private (usually not needed for our PKCE flow)  
5. Set **Callback / redirect URL** to exactly:

   `http://localhost:8765/callback`

### B3. Link shop to the orchestrator backend

```powershell
cd c:\Users\desmo\Projects\Project-Showcase\projects\listing-orchestrator
.\.venv\Scripts\activate
# Put keystring in .env:
# ETSY_API_KEY=paste_keystring_here
python etsy_oauth.py
```

What happens:

1. Browser opens Etsy OAuth  
2. You approve access for your Cozy shop  
3. Script writes to `.env`:
   - `ETSY_ACCESS_TOKEN`
   - `ETSY_REFRESH_TOKEN`
   - `ETSY_SHOP_ID`

4. Verify:

```powershell
python verify_accounts.py --channels etsy
```

### B4. Taxonomy ID (category)

1. In Etsy seller tools / API docs, find a **seller taxonomy** node for clothing (hats, tops, etc.)  
2. Put it in `.env`:

```env
ETSY_TAXONOMY_ID=123456789
```

Without a real ID, live create may fail or land in the wrong category.

**Official auth docs:** https://developer.etsy.com/documentation/essentials/authentication

---

## Part C — Create eBay seller account + API keys

### C1. Seller account

1. https://www.ebay.com/ → register / sign in  
2. Open a **seller** account (same identity you’ll use for Cozy inventory)  
3. Complete selling requirements (payee, policies) as eBay prompts  

### C2. Developer account + application

1. Go to https://developer.ebay.com/  
2. Register / sign in (link to your eBay account)  
3. **Create an application key set** (Sandbox first, then Production)  
4. Note your App ID (Client ID), Cert ID (Client Secret), Dev ID  

### C3. User OAuth token (links *your* seller account)

eBay needs a **user access token** for *your* Cozy seller identity (not just the app ID).

1. In the eBay Developer portal, open **Get a User Token** / OAuth tools  
   (or follow: https://developer.ebay.com/api-docs/static/oauth-authorization-code-grant.html)  
2. Select **Sandbox** first  
3. Request scopes at least for:
   - Sell Inventory (`https://api.ebay.com/oauth/api_scope/sell.inventory`)  
   - Sell Fulfillment (`.../sell.fulfillment`)  
4. Complete the consent screen while logged in as your **Cozy seller**  
5. Copy the **access token**

### C4. Put token in orchestrator `.env`

```env
EBAY_ACCESS_TOKEN=v^1.1#...paste...
EBAY_ENVIRONMENT=sandbox
```

Later, when ready for real buyers:

```env
EBAY_ENVIRONMENT=production
# + a Production user token
```

### C5. Verify

```powershell
python verify_accounts.py --channels ebay
```

Expect: `ebay: LIVE · environment=sandbox`

### C6. Important limitation (current code)

Live eBay publish currently **upserts an inventory item**. A full “for sale” listing also needs:

- Merchant location  
- Business policies (payment / shipping / return)  
- Create **offer** + **publish offer**

Those are the next engineering step after Etsy is solid. Sandbox token linking still works for verify + inventory upsert testing.

**Developer hub:** https://developer.ebay.com/

---

## Part D — What `.env` looks like when both are linked

```env
# Etsy
ETSY_API_KEY=your_keystring
ETSY_ACCESS_TOKEN=...
ETSY_REFRESH_TOKEN=...
ETSY_SHOP_ID=12345678
ETSY_TAXONOMY_ID=...

# eBay
EBAY_ACCESS_TOKEN=...
EBAY_ENVIRONMENT=sandbox

# Shopify — leave blank for now
# SHOPIFY_STORE_DOMAIN=
# SHOPIFY_ADMIN_TOKEN=
```

Never commit `.env`. Only `.env.example` is in git.

---

## Suggested order checklist

1. [ ] Etsy shop open  
2. [ ] Etsy developer app + keystring  
3. [ ] `python etsy_oauth.py` → `verify_accounts.py` shows LIVE  
4. [ ] `publish.py --channels etsy` on one Studio SKU  
5. [ ] eBay seller + developer app  
6. [ ] Sandbox user token in `.env` → verify LIVE  
7. [ ] `publish.py --channels ebay,etsy`  
8. [ ] Later: eBay production + offer/publish completion  

Etsy-only detail also lives in [SETUP_ETSY.md](SETUP_ETSY.md).
