# village_agent.md: Offline Grant & Tender Distribution Workflow
## T2.2 · Multilingual Grant & Tender Matcher with Summarizer

---

## The User: Jean-Pierre, Cooperative Leader in Rural Rwanda

Jean-Pierre leads a 12-member agritech cooperative in Musanze district.
He owns a basic MTN feature phone, speaks Kinyarwanda, has no smartphone,
no internet access, and no formal education beyond primary school. He has
never successfully applied for a grant not because his cooperative is
ineligible, but because he has never heard about the right ones in time.

The matcher runs server-side. Jean-Pierre never touches it. The system
finds his matches, generates summaries, and a human agent delivers the
information to him in Kinyarwanda by phone call.

---

## Why Voice Call Center → IVR → Human Agent

Two options were considered:

**WhatsApp audio broadcast**: eliminated. Because it requires internet connectivity
and a smartphone. Rural cooperative leaders in Rwanda, Senegal, DRC,
Kenya, and Ethiopia overwhelmingly use basic feature phones with zero
data plans. WhatsApp fails at the last mile.

**Voice call center → IVR → human agent**: selected. Because it works on any
feature phone including the most basic MTN handset. Zero data required.
Zero literacy required. Zero smartphone required. The only requirement
is that Jean-Pierre picks up a call.

---

## Weekly Distribution Loop

### Step 1: System runs every Monday 06:00 UTC
The matcher processes all 10 profiles against the current tender database.
Top 3 matches per profile are selected. Summaries are generated in the
profile's system language (EN or FR).

### Step 2: Human agent review (Monday 08:00–10:00)
A human agent recruited locally, fluent in the cooperative leader's
language, reviews the generated summaries for their assigned profiles.
They prepare a 2-minute verbal brief in the local language.

### Step 3: Outbound voice call (Monday 10:00–14:00)
The agent calls the cooperative leader via Africa's Talking outbound
voice API. The call delivers:
- Name of the grant/tender
- Sector and budget in simple terms
- Deadline in days remaining (not calendar date)
- One action: "Call this number to apply" or "Visit your sector office"

### Step 4: Follow-up (Wednesday)
If the cooperative leader did not pick up Monday, one retry on Wednesday.
Maximum 2 attempts per week per profile.

---

## The Call Script (Rwanda example)

**Agent calls Jean-Pierre in Kinyarwanda:**

> "Muraho Jean-Pierre. Nitwa [Agent name] nkorera ikigo gifasha amashyirahamwe kubona inkunga Grant matcher.
> Iki cyumweru, twabonye inkunga ikwiriye coperative yawe.
> Izina ryayo ni 'Africa Agritech Innovation Fund.'
> Itanga amadolari 50,000 ku bikorwa byubuhinzi mwiterambere.
> Igihe cyo gusaba kizarangira mu minsi 45.
> Kugira ngo usabe, hamagara 0788XXXXXX cyangwa ujye
> ku biro byumurenge wawe bagufashe."

**Translation:**
> "Hello Jean-Pierre. I am [Agent name] from Grant Matcher.
> This week we found a grant suitable for your cooperative.
> It is called 'Africa Agritech Innovation Fund.'
> It offers $50,000 for agritech activities.
> The application deadline is in 45 days.
> To apply, call 0788XXXXXX or visit your Sector office."

**Key design decisions:**
- Deadline in days remaining, not calendar date, easier to act on
- One action only, reduces cognitive load
- Kinyarwanda throughout, zero language barrier
- Under 2 minutes, respects airtime cost on both ends

---

## Language Matrix

| Country | System output | Human agent language |
|---------|--------------|---------------------|
| Rwanda | English | Kinyarwanda |
| Kenya | English | Swahili |
| Senegal | French | Wolof |
| DRC | French | Lingala |
| Ethiopia | English | Amharic |

Note: Rwanda switched from French to English as primary official language
in 2008. System outputs for Rwandan profiles are generated in English,
not French. Human agents for Rwanda must be Kinyarwanda speakers.

---

## Weekly Cadence

| Day | Activity |
|-----|----------|
| Monday 06:00 | Matcher runs, summaries generated |
| Monday 08:00 | Human agents review summaries |
| Monday 10:00 | Outbound calls begin |
| Wednesday | Retry for missed calls |
| Friday | Conversion log submitted by agents |

---

## Cost Analysis at Scale

*Costs shown in RWF for Rwanda pilot. Africa's Talking operates across
all 5 target countries (Rwanda, Kenya, Uganda, Senegal, DRC) with
comparable per-minute voice rates. USD equivalents shown for
cross-country comparison.*

### Per call costs (Africa's Talking voice API — Rwanda baseline)
- Outbound voice call: ~75–100 RWF/min (~$0.05/min)
- Average call duration: 2 minutes
- Cost per call: ~150–200 RWF (~$0.10–0.13)
- Retry calls (est. 30% of cooperatives): same rate
- Effective cost per cooperative reached: ~210 RWF (~$0.14)

### At 500 cooperatives weekly

| Item | Cost (RWF) | Cost (USD) |
|------|------------|------------|
| Outbound calls (500 × 175 RWF) | 87,500 RWF/week | ~$58 |
| Retry calls (30% × 175 RWF) | 26,250 RWF/week | ~$17 |
| Human agents (5 agents × 2hrs × 3,000 RWF/hr) | 30,000 RWF/week | ~$20 |
| **Total weekly cost** | **~144,000 RWF/week** | **~$96** |
| **Cost per cooperative reached** | **~288 RWF** | **~$0.19** |

### Cost per activated cooperative (CAC)
Assume 15% activation rate (cooperative leader takes action after call):
- 500 calls → 75 activated cooperatives
- CAC = 144,000 RWF ÷ 75 = **~1,920 RWF per activated cooperative (~$1.28)**

---

## Privacy & Consent Plan (Rwanda as a case study)

**Consent at onboarding:**
- Cooperative leaders are onboarded via their district cooperative office
- Agent explains the service in Kinyarwanda/local language
- Verbal consent recorded (feature phone call recording or agent log)
- Leader can opt out at any time by saying "Simbishaka" (I don't want it)
  to any agent or calling the opt-out number

**Data stored:**
- Phone number, cooperative name, sector, country
- No financial data, no personal ID numbers stored
- Match logs retained for 90 days then deleted

**Who has access:**
- Human agents see only their assigned profiles
- No data sold or shared with tender issuers without explicit consent

---

## What Breaks First

- **Agent quality:** the system summary is only as good as the agent's
  translation into local language, agents need weekly calibration
- **Phone number churn:** cooperative leaders change phones frequently;
  database needs quarterly refresh via district cooperative offices
- **Tender database staleness:** if tenders are not updated weekly the
  matcher surfaces expired opportunities, automated deadline checks
  must flag and remove expired tenders every Monday before the run
- **Cold start:** at launch, profiles must be seeded via district
  cooperative offices or RDB/sector offices, zero organic acquisition

---

## Recommended Distribution Option

**Voice call center → IVR → human agent** is the only viable option
for this user profile. It requires no internet, no smartphone, no
literacy, and no app. At ~1,787 RWF CAC it is cost-effective for a
pilot of 500 cooperatives. The human agent layer solves the EN/FR →
local language gap that no automated system can currently bridge
reliably for Kinyarwanda, Wolof, Lingala, or Amharic at this scale.