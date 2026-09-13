# Bengaluru Traffic Pulse — frontend

Next.js dashboard for the project: live corridor congestion, a rule-based risk calendar,
the Sep 11 2026 case study, and the solutions page.

## Getting started

```bash
cp .env.example .env.local   # point NEXT_PUBLIC_API_BASE_URL at your backend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The backend (see `../backend`) must be
running for pages to show real data — each page degrades gracefully with a "couldn't reach
the API" notice otherwise.

## Structure

- `app/page.tsx` — dashboard: live corridor status, today's risk, active incidents
- `app/risk-calendar/` — 60-day rule-based risk forecast
- `app/case-study/` — renders `data/case_study_sep11_2026.md` from the backend
- `app/solutions/` — personal + systemic recommendations
- `lib/api.ts` — typed fetch client for the backend's `/api/*` routes
- `lib/types.ts` — TypeScript mirrors of the backend's Pydantic schemas

All data pages are `force-dynamic` (fetched per-request, not at build time) so `npm run build`
succeeds without a backend available, matching CI.

## Learn more

- [Next.js Documentation](https://nextjs.org/docs)
- [Deploying to Vercel](https://nextjs.org/docs/app/building-your-application/deploying)
