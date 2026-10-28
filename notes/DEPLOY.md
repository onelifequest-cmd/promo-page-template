# Deploy notes (preview)

- GitHub: https://github.com/onelifequest-cmd/promo-page-template (public)
- Render static site: srv-dbgop7tg1s2s73bur7e0
- URL: https://promo-page-template-preview.onrender.com
- First deploy: dep-dbgop85g1s2s73bur800 live ~2026-10-28 1:48 AM ET
- Workspace: tea-db06k70u01pc7392vtsg
- Build: `python3 build.py` → publish `dist/`
- Mode: demoMode true (client-side localStorage holds). Real API in server/app.py not deployed yet.
- noindex on. Does not touch questwon.com DNS, ai.questwon.com, other previews, CC env, GHL, or Stripe.
