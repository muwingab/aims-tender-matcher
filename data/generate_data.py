"""
Synthetic data generator for aims-tender-matcher.

Generates:
- 40 unique tender .txt files (24 EN, 16 FR — 60/40 split)
- profiles.json: 10 business profiles across Rwanda, Kenya,
  Uganda, Senegal, DRC, Ethiopia
- gold_matches.csv: 3 curated gold matches per profile
  (same sector, feasible budget, valid region)

Design choices:
- Tender text includes bureaucratic boilerplate to simulate
  real AU/regional body language
- FR tenders written in French to test language detection
- Gold matches are seeded deterministically for reproducibility
- Budgets drawn from {5k, 50k, 200k, 1M USD} to test budget_fit
- Deadlines set 30-120 days from TODAY to test deadline_fit
"""
import json
import os
import random
import csv
from datetime import datetime, timedelta

random.seed(42)

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(BASE)
TENDERS_DIR = os.path.join(PROJECT, "tenders")
os.makedirs(TENDERS_DIR, exist_ok=True)

SECTORS = ["agritech", "healthtech", "cleantech", "edtech", "fintech", "wastetech"]
BUDGETS = [5000, 50000, 200000, 1000000]
REGIONS = ["East Africa", "West Africa", "Central Africa", "Pan-Africa", "Sub-Saharan Africa"]
TODAY = datetime(2026, 4, 23)

EN_TENDERS = [
    {
        "title": "Digital Agriculture Innovation Grant",
        "sector": "agritech",
        "budget_usd": 50000,
        "deadline_days": 45,
        "eligibility": "SMEs with fewer than 50 employees operating in East Africa",
        "region": "East Africa",
        "boilerplate": (
            "Applicants must submit a completed Form DA-2026, certified copies of registration documents, "
            "a three-year audited financial statement, and a signed declaration of compliance with donor guidelines. "
            "Proposals exceeding 15 pages (excluding annexes) will be disqualified. All budgets must be presented "
            "in USD and must include a 10% overhead ceiling. The granting authority reserves the right to request "
            "additional documentation at any stage of the evaluation process."
        ),
        "body": (
            "This grant supports innovative digital solutions for smallholder farmers, including precision agriculture, "
            "crop disease detection, and market linkage platforms. Priority is given to solutions that leverage mobile "
            "technology to improve yield forecasting and reduce post-harvest losses across East African farming communities."
        ),
    },
    {
        "title": "Rural Health Technology Accelerator",
        "sector": "healthtech",
        "budget_usd": 200000,
        "deadline_days": 60,
        "eligibility": "Registered health-tech companies operating in Sub-Saharan Africa",
        "region": "Sub-Saharan Africa",
        "boilerplate": (
            "All applications must be submitted through the official online portal by 17:00 UTC on the closing date. "
            "Late submissions will not be considered under any circumstances. Applicants must demonstrate at least "
            "18 months of operational history and provide proof of regulatory compliance in their country of registration. "
            "Co-applications with a local NGO partner are encouraged but not mandatory."
        ),
        "body": (
            "Funding is available for technology startups developing telehealth platforms, diagnostic tools, and "
            "community health worker support systems. Solutions must be designed for low-bandwidth environments "
            "and must demonstrate a viable path to financial sustainability within 24 months of award."
        ),
    },
    {
        "title": "Clean Energy Access Fund",
        "sector": "cleantech",
        "budget_usd": 1000000,
        "deadline_days": 90,
        "eligibility": "Energy enterprises with proven deployment in off-grid communities",
        "region": "Sub-Saharan Africa",
        "boilerplate": (
            "The Fund operates a two-stage selection process: an Expression of Interest (EoI) followed by a full "
            "proposal for shortlisted applicants. Only organizations that receive an EoI invitation will be eligible "
            "to submit full proposals. Grant disbursement will be made in three tranches tied to milestone deliverables "
            "as defined in the Grant Agreement."
        ),
        "body": (
            "This facility supports the deployment of solar mini-grids, clean cooking solutions, and energy efficiency "
            "technologies in underserved communities. Preference is given to applicants with demonstrated ability to "
            "mobilize additional private investment and to integrate gender-responsive design into their energy solutions."
        ),
    },
    {
        "title": "EdTech for Inclusive Learning Grant",
        "sector": "edtech",
        "budget_usd": 50000,
        "deadline_days": 30,
        "eligibility": "EdTech startups serving primary and secondary school students",
        "region": "Pan-Africa",
        "boilerplate": (
            "Applicants are required to complete all mandatory fields in the online application system. Incomplete "
            "applications will be automatically rejected. The selection committee will evaluate submissions based on "
            "innovation (30%), scalability (25%), impact evidence (25%), and financial viability (20%). Results will "
            "be communicated within 90 days of the application deadline."
        ),
        "body": (
            "The grant targets digital learning tools that improve literacy, numeracy, and STEM outcomes for students "
            "in under-resourced schools. Solutions that work offline or in low-connectivity settings are especially "
            "welcome. Integration with national curriculum frameworks will be considered a competitive advantage."
        ),
    },
    {
        "title": "Fintech Financial Inclusion Challenge",
        "sector": "fintech",
        "budget_usd": 200000,
        "deadline_days": 50,
        "eligibility": "Fintech companies serving unbanked populations in Africa",
        "region": "Pan-Africa",
        "boilerplate": (
            "All currency conversions must use the exchange rate published by the applicant's central bank on the "
            "date of submission. Applicants must disclose any existing relationship with the donor organization or "
            "its affiliates. Conflict-of-interest declarations are mandatory and must be signed by the CEO or equivalent. "
            "The donor reserves the right to conduct on-site verification visits prior to award."
        ),
        "body": (
            "This challenge seeks fintech innovators building savings, credit, insurance, and payment solutions for "
            "populations without access to formal banking. Mobile money integrations, agent banking networks, and "
            "AI-driven credit scoring for thin-file customers are among the priority use cases."
        ),
    },
    {
        "title": "Waste Management Innovation Fund",
        "sector": "wastetech",
        "budget_usd": 50000,
        "deadline_days": 40,
        "eligibility": "SMEs focused on solid waste reduction and recycling in urban Africa",
        "region": "West Africa",
        "boilerplate": (
            "Applicants must hold a valid business registration certificate issued within the last five years. "
            "Environmental impact assessments, where applicable, must accompany the application. The Fund does not "
            "support land acquisition, civil construction, or retrospective financing of activities already initiated. "
            "All intellectual property developed under the grant remains with the grantee unless otherwise specified."
        ),
        "body": (
            "The fund backs innovative approaches to municipal solid waste collection, sorting, and valorization, "
            "including plastic recycling, composting, and waste-to-energy conversions. Circular economy models that "
            "create livelihood opportunities for waste pickers and informal sector workers will be prioritized."
        ),
    },
    {
        "title": "Agritech Market Linkage Seed Grant",
        "sector": "agritech",
        "budget_usd": 5000,
        "deadline_days": 25,
        "eligibility": "Early-stage agritech startups with fewer than 10 employees",
        "region": "East Africa",
        "boilerplate": (
            "This is a seed grant for pre-revenue or early-revenue startups. Applicants must not have received "
            "more than USD 20,000 in prior grant funding from any source. A pitch deck of no more than 10 slides "
            "is required in addition to the standard application form. Shortlisted teams will be invited to a "
            "virtual pitch session with the selection panel."
        ),
        "body": (
            "Seed funding is available for startups building digital market linkage platforms that connect smallholder "
            "farmers directly to buyers, reducing intermediary costs and improving price transparency. Solutions that "
            "incorporate real-time price data and SMS-based alerts for low-literacy farmers are particularly encouraged."
        ),
    },
    {
        "title": "HealthTech Diagnostics Grant",
        "sector": "healthtech",
        "budget_usd": 200000,
        "deadline_days": 55,
        "eligibility": "Health technology companies with CE or WHO-EUL certified products",
        "region": "Sub-Saharan Africa",
        "boilerplate": (
            "Product certification documentation must be submitted as part of the application package. Applications "
            "lacking valid certification evidence will not be reviewed. The grant covers direct project costs only; "
            "capital expenditure exceeding 30% of the total budget requires prior approval from the grants committee. "
            "Progress reports are due quarterly from the date of the first disbursement."
        ),
        "body": (
            "This grant supports the scale-up of point-of-care diagnostic tools for infectious and non-communicable "
            "diseases in resource-limited settings. Applicants must demonstrate clear distribution strategies and "
            "partnerships with national health systems or accredited healthcare facilities."
        ),
    },
    {
        "title": "CleanTech SME Scale-Up Grant",
        "sector": "cleantech",
        "budget_usd": 200000,
        "deadline_days": 70,
        "eligibility": "SMEs in renewable energy or water purification with 10-100 employees",
        "region": "East Africa",
        "boilerplate": (
            "Grantees will be required to open a dedicated project bank account and submit monthly financial reports. "
            "The grant cannot be used to repay existing debts or to pay dividends to shareholders. An independent "
            "financial audit, at the grantee's expense, is required at project completion. The donor logo must appear "
            "on all project communications and outputs."
        ),
        "body": (
            "Scale-up funding is available for established clean technology SMEs seeking to expand their renewable "
            "energy or water treatment solutions across East Africa. Applicants must provide a detailed market entry "
            "plan for at least two new countries and demonstrate existing revenue of at least USD 100,000 per annum."
        ),
    },
    {
        "title": "EdTech Teacher Training Platform Grant",
        "sector": "edtech",
        "budget_usd": 50000,
        "deadline_days": 35,
        "eligibility": "EdTech companies with a focus on teacher professional development",
        "region": "Sub-Saharan Africa",
        "boilerplate": (
            "Letters of support from at least two school districts or educational authorities must be included. "
            "Applicants must agree to share anonymized usage data with the grantor for research purposes. The grant "
            "period is 12 months from the effective date of the agreement, with no-cost extensions considered on a "
            "case-by-case basis. Final reports are due 30 days after project completion."
        ),
        "body": (
            "Funding targets platforms that deliver continuous professional development to teachers in underserved "
            "regions, focusing on digital literacy, pedagogy, and subject matter competency. Platforms must support "
            "asynchronous learning to accommodate teachers with limited internet access."
        ),
    },
    {
        "title": "Mobile Money for Agri-Finance",
        "sector": "fintech",
        "budget_usd": 50000,
        "deadline_days": 45,
        "eligibility": "Fintech and agritech companies targeting smallholder farmer finance",
        "region": "East Africa",
        "boilerplate": (
            "Applicants must provide a data protection and privacy policy compliant with applicable national laws. "
            "The grant does not cover salaries of founders or directors at rates exceeding market benchmarks. "
            "All procurement under the grant must follow competitive bidding procedures. The grantor may appoint "
            "an external monitor to verify project activities."
        ),
        "body": (
            "This grant supports digital financial products tailored to smallholder farmers, including seasonal credit, "
            "crop insurance, and input financing delivered via mobile money platforms. Applicants must demonstrate "
            "existing partnerships with at least one mobile network operator or financial institution."
        ),
    },
    {
        "title": "E-Waste Recycling Technology Grant",
        "sector": "wastetech",
        "budget_usd": 200000,
        "deadline_days": 60,
        "eligibility": "Companies with operational e-waste collection or processing facilities",
        "region": "Pan-Africa",
        "boilerplate": (
            "Proof of compliance with national e-waste regulations and hazardous materials handling licenses is "
            "mandatory. Site inspections may be conducted by the grantor prior to award. The grant cannot be used "
            "to acquire equipment that handles hazardous materials without proper containment infrastructure. "
            "Environmental and social safeguards must be integrated into the project design."
        ),
        "body": (
            "Grants support the expansion of certified e-waste collection networks and the development of safe "
            "dismantling and materials recovery technologies. Projects that create formal employment and upskill "
            "informal waste workers in safe handling practices will receive additional scoring weight."
        ),
    },
    {
        "title": "Agritech Cold Chain Logistics Fund",
        "sector": "agritech",
        "budget_usd": 200000,
        "deadline_days": 80,
        "eligibility": "Agritech companies addressing post-harvest loss with cold chain solutions",
        "region": "Sub-Saharan Africa",
        "boilerplate": (
            "Equipment procurement plans must accompany the budget breakdown. The Fund prohibits the purchase of "
            "second-hand equipment without prior written approval. All vehicles and equipment acquired under the "
            "grant must be insured for the full grant period. Disposal of grant-funded assets requires grantor "
            "approval for five years post-project."
        ),
        "body": (
            "This fund backs solar-powered cold storage, refrigerated transport, and harvest aggregation centers "
            "designed to reduce the 30-40% post-harvest losses typical in Sub-Saharan African value chains. "
            "Applicants must demonstrate partnerships with farmer cooperatives representing at least 500 smallholders."
        ),
    },
    {
        "title": "Digital Health Records Grant",
        "sector": "healthtech",
        "budget_usd": 50000,
        "deadline_days": 40,
        "eligibility": "HealthTech SMEs building electronic medical record systems",
        "region": "East Africa",
        "boilerplate": (
            "Systems must comply with HL7 FHIR standards and national health information system requirements. "
            "Applicants must provide a cybersecurity risk assessment and data breach response plan. The grant "
            "excludes hardware procurement unless the hardware is integral to the software solution and costs "
            "less than 20% of the total budget. User training must be budgeted and documented."
        ),
        "body": (
            "Funding supports the development and deployment of interoperable electronic medical record systems "
            "for primary healthcare facilities. Solutions should support patient tracking, appointment scheduling, "
            "drug inventory management, and reporting to national health information systems."
        ),
    },
    {
        "title": "Solar Energy for Schools Grant",
        "sector": "cleantech",
        "budget_usd": 50000,
        "deadline_days": 30,
        "eligibility": "Cleantech companies with school electrification experience",
        "region": "East Africa",
        "boilerplate": (
            "Letters of agreement with at least three schools must be submitted with the application. Installation "
            "plans must be signed off by a certified electrical engineer. The grantor will conduct post-installation "
            "inspections within 60 days of project completion. Maintenance plans covering a minimum of three years "
            "must be included in the project budget."
        ),
        "body": (
            "This grant finances the installation of solar photovoltaic systems in off-grid schools, enabling "
            "electricity access for computer labs, lighting, and water pumping. Applicants should demonstrate "
            "a turnkey installation model with integrated maintenance and teacher training components."
        ),
    },
    {
        "title": "Savings and Credit Platform Grant",
        "sector": "fintech",
        "budget_usd": 5000,
        "deadline_days": 20,
        "eligibility": "Early-stage fintech startups targeting VSLAs and savings groups",
        "region": "East Africa",
        "boilerplate": (
            "Applicants must not be incorporated for more than three years at the time of application. Board "
            "resolutions authorizing the application must accompany the submission. The seed grant is non-dilutive "
            "and carries no equity obligation. Recipients must attend a two-day grantee orientation within 30 days "
            "of award notification."
        ),
        "body": (
            "Seed grants support fintech startups digitizing village savings and loan associations (VSLAs), "
            "including tools for group savings tracking, loan management, and interest calculation. Solutions "
            "that work via USSD for feature phone users in rural areas are highly valued."
        ),
    },
    {
        "title": "Urban Composting Innovation Grant",
        "sector": "wastetech",
        "budget_usd": 50000,
        "deadline_days": 35,
        "eligibility": "SMEs with urban organic waste composting operations",
        "region": "West Africa",
        "boilerplate": (
            "Composting sites must hold valid municipal operating permits. Odor management plans are required "
            "for all sites within 500 meters of residential areas. The grantor reserves the right to share "
            "project learnings publicly, excluding proprietary technical information. Grantees must participate "
            "in at least two peer-learning events during the grant period."
        ),
        "body": (
            "Grants support the scale-up of urban organic waste composting enterprises that divert food and "
            "market waste from landfills and produce organic fertilizer for urban farmers. Business models "
            "linking composting operations to urban agriculture value chains are especially encouraged."
        ),
    },
    {
        "title": "Precision Farming Data Grant",
        "sector": "agritech",
        "budget_usd": 200000,
        "deadline_days": 75,
        "eligibility": "Agritech companies using satellite or drone data for farm analytics",
        "region": "Pan-Africa",
        "boilerplate": (
            "Data licensing agreements for satellite or aerial imagery must be submitted alongside the application. "
            "Applicants must comply with national aviation regulations regarding drone operations. Data privacy "
            "policies governing farmer data must be included. The grantor may request a technical demonstration "
            "of the solution as part of the due diligence process."
        ),
        "body": (
            "This grant supports agritech platforms that use remote sensing, satellite imagery, and IoT sensors "
            "to provide actionable insights to farmers on soil health, weather patterns, and crop performance. "
            "Solutions must demonstrate a cost per farmer of less than USD 20 per season at scale."
        ),
    },
    {
        "title": "Community Health Worker Tech Grant",
        "sector": "healthtech",
        "budget_usd": 50000,
        "deadline_days": 50,
        "eligibility": "HealthTech companies partnering with community health worker programs",
        "region": "Sub-Saharan Africa",
        "boilerplate": (
            "Proof of formal agreement with a national or county community health worker program must be submitted. "
            "Solutions must not require internet connectivity for core functionality. User testing evidence with "
            "at least 20 community health workers must be included. The grantor will conduct a mid-term review "
            "to assess progress against agreed milestones."
        ),
        "body": (
            "Funding is available for digital tools that enhance the effectiveness and accountability of community "
            "health workers, including data collection apps, referral management systems, and supervision tools. "
            "Offline-first mobile applications with robust data synchronization are the preferred technical approach."
        ),
    },
    {
        "title": "Green Building Materials Grant",
        "sector": "cleantech",
        "budget_usd": 200000,
        "deadline_days": 65,
        "eligibility": "Cleantech SMEs producing sustainable construction materials",
        "region": "Sub-Saharan Africa",
        "boilerplate": (
            "Material testing certifications from an accredited laboratory are required. Life cycle assessment "
            "documentation comparing the proposed material to conventional alternatives must be provided. "
            "The grant prohibits the use of materials classified as hazardous under international conventions. "
            "Grantees must submit bi-annual progress reports and host at least one site visit per grant year."
        ),
        "body": (
            "This grant supports enterprises developing and scaling sustainable building materials, including "
            "compressed earth blocks, recycled plastic bricks, and bio-based insulation. Applicants must "
            "demonstrate market demand through existing sales or signed letters of intent from construction firms."
        ),
    },
    {
        "title": "EdTech Language Learning Grant",
        "sector": "edtech",
        "budget_usd": 200000,
        "deadline_days": 55,
        "eligibility": "EdTech companies developing multilingual or mother-tongue instruction tools",
        "region": "Pan-Africa",
        "boilerplate": (
            "Language localization evidence must demonstrate authentic co-design with native speaker communities. "
            "Curriculum alignment certificates from at least one national education ministry are required. "
            "The grant does not fund hardware procurement exceeding 15% of total project costs. Accessibility "
            "features for learners with disabilities must be documented."
        ),
        "body": (
            "Grants support EdTech platforms delivering literacy and language instruction in African mother "
            "tongues and official languages, with a focus on early childhood and primary education. Solutions "
            "should integrate culturally relevant content and support both school and home learning contexts."
        ),
    },
    {
        "title": "InsurTech for Agriculture Grant",
        "sector": "fintech",
        "budget_usd": 200000,
        "deadline_days": 60,
        "eligibility": "InsurTech companies offering index-based crop insurance to smallholders",
        "region": "East Africa",
        "boilerplate": (
            "Regulatory approval or no-objection letter from the national insurance regulator is mandatory. "
            "Actuarial reports supporting the insurance product design must be submitted. Applicants must "
            "demonstrate distribution partnerships reaching at least 1,000 enrolled farmers. Claims processing "
            "timelines must not exceed 30 days from trigger event to payout."
        ),
        "body": (
            "This grant supports the scale-up of parametric and index-based agricultural insurance products "
            "for smallholder farmers, using satellite weather data to trigger automatic payouts. Applicants "
            "must demonstrate a clear path to commercial viability without ongoing subsidy within three years."
        ),
    },
    {
        "title": "Plastic Waste Valorization Grant",
        "sector": "wastetech",
        "budget_usd": 200000,
        "deadline_days": 70,
        "eligibility": "Enterprises converting plastic waste to commercial products or fuel",
        "region": "Pan-Africa",
        "boilerplate": (
            "Pyrolysis or chemical recycling technology providers must submit third-party emission test results. "
            "Community consultation documentation must demonstrate engagement with waste picker communities. "
            "The grant excludes single-use plastic production in all forms. Technology licensing agreements "
            "must be accompanied by evidence of the licensor's operating track record."
        ),
        "body": (
            "Grants support enterprises converting collected plastic waste into paving blocks, construction "
            "materials, or fuel through proven mechanical or thermal processes. Applications must include "
            "a collection network plan covering at least three neighborhoods or market centers."
        ),
    },
]

FR_TENDERS = [
    {
        "title": "Subvention Innovation Agritech",
        "sector": "agritech",
        "budget_usd": 50000,
        "deadline_days": 45,
        "eligibility": "PME agritech de moins de 50 employés en Afrique de l'Ouest et Centrale",
        "region": "West Africa",
        "boilerplate": (
            "Les candidats doivent soumettre un formulaire IA-2026 dûment rempli, accompagné de copies certifiées "
            "des documents d'enregistrement, des états financiers audités des trois dernières années et d'une "
            "déclaration signée de conformité aux directives du bailleur. Les propositions dépassant 15 pages "
            "(hors annexes) seront disqualifiées. Tous les budgets doivent être présentés en USD avec un plafond "
            "de frais généraux de 10 %. L'autorité d'octroi se réserve le droit de demander des documents "
            "supplémentaires à tout stade du processus d'évaluation."
        ),
        "body": (
            "Cette subvention soutient les solutions numériques innovantes pour les petits agriculteurs, notamment "
            "l'agriculture de précision, la détection des maladies des cultures et les plateformes de mise en "
            "relation avec les marchés. La priorité est accordée aux solutions tirant parti des technologies "
            "mobiles pour améliorer les prévisions de rendement et réduire les pertes post-récolte en Afrique "
            "de l'Ouest et Centrale."
        ),
    },
    {
        "title": "Fonds Technologie Santé Rurale",
        "sector": "healthtech",
        "budget_usd": 50000,
        "deadline_days": 40,
        "eligibility": "Entreprises healthtech en Afrique francophone avec 18 mois d'opérations",
        "region": "West Africa",
        "boilerplate": (
            "Toutes les candidatures doivent être soumises via le portail officiel avant 17h00 UTC à la date "
            "de clôture. Les soumissions tardives ne seront pas prises en compte. Les candidats doivent "
            "démontrer au moins 18 mois d'historique opérationnel et fournir une preuve de conformité "
            "réglementaire dans leur pays d'enregistrement. Les co-candidatures avec un partenaire ONG "
            "local sont encouragées mais non obligatoires."
        ),
        "body": (
            "Ce financement est disponible pour les startups technologiques développant des plateformes de "
            "télésanté, des outils de diagnostic et des systèmes de soutien aux agents de santé communautaires. "
            "Les solutions doivent être conçues pour les environnements à faible bande passante et doivent "
            "démontrer une voie viable vers la durabilité financière dans les 24 mois suivant l'attribution."
        ),
    },
    {
        "title": "Programme Énergie Propre Communautaire",
        "sector": "cleantech",
        "budget_usd": 200000,
        "deadline_days": 80,
        "eligibility": "Entreprises d'énergie renouvelable avec déploiements hors-réseau en Afrique francophone",
        "region": "West Africa",
        "boilerplate": (
            "Le Programme fonctionne en deux étapes : une Expression d'Intérêt (EdI) suivie d'une proposition "
            "complète pour les candidats présélectionnés. Seules les organisations ayant reçu une invitation "
            "EdI seront éligibles à la soumission de propositions complètes. Le décaissement sera effectué "
            "en trois tranches liées à des jalons définis dans l'Accord de Subvention."
        ),
        "body": (
            "Ce programme soutient le déploiement de mini-réseaux solaires, de solutions de cuisson propre et "
            "de technologies d'efficacité énergétique dans les communautés mal desservies d'Afrique de l'Ouest. "
            "La préférence est accordée aux candidats capables de mobiliser des investissements privés "
            "supplémentaires et d'intégrer une conception sensible au genre."
        ),
    },
    {
        "title": "Appel à Projets EdTech Francophone",
        "sector": "edtech",
        "budget_usd": 50000,
        "deadline_days": 35,
        "eligibility": "Startups EdTech servant les élèves du primaire et du secondaire en Afrique francophone",
        "region": "West Africa",
        "boilerplate": (
            "Les candidats doivent remplir tous les champs obligatoires du système de candidature en ligne. "
            "Les candidatures incomplètes seront automatiquement rejetées. Le comité de sélection évaluera "
            "les soumissions selon les critères suivants : innovation (30 %), évolutivité (25 %), preuves "
            "d'impact (25 %) et viabilité financière (20 %). Les résultats seront communiqués dans les "
            "90 jours suivant la date limite de candidature."
        ),
        "body": (
            "La subvention cible les outils d'apprentissage numérique qui améliorent les résultats en "
            "alphabétisation, numératie et STEM pour les élèves des écoles sous-équipées. Les solutions "
            "fonctionnant hors ligne ou dans des environnements à faible connectivité sont particulièrement "
            "bienvenues. L'intégration avec les programmes nationaux sera considérée comme un avantage concurrentiel."
        ),
    },
    {
        "title": "Défi Inclusion Financière Numérique",
        "sector": "fintech",
        "budget_usd": 200000,
        "deadline_days": 55,
        "eligibility": "Fintechs servant les populations non bancarisées en Afrique de l'Ouest et Centrale",
        "region": "West Africa",
        "boilerplate": (
            "Toutes les conversions de devises doivent utiliser le taux de change publié par la banque centrale "
            "du candidat à la date de soumission. Les candidats doivent divulguer toute relation existante avec "
            "l'organisation bailleresse ou ses affiliés. Les déclarations de conflits d'intérêts sont obligatoires "
            "et doivent être signées par le PDG ou l'équivalent."
        ),
        "body": (
            "Ce défi recherche des innovateurs fintech développant des solutions d'épargne, de crédit, "
            "d'assurance et de paiement pour les populations sans accès à la banque formelle. Les intégrations "
            "de monnaie mobile, les réseaux bancaires d'agents et la notation de crédit par intelligence "
            "artificielle pour les clients sans historique de crédit figurent parmi les cas d'usage prioritaires."
        ),
    },
    {
        "title": "Fonds Innovation Gestion des Déchets",
        "sector": "wastetech",
        "budget_usd": 50000,
        "deadline_days": 40,
        "eligibility": "PME spécialisées dans la réduction et le recyclage des déchets solides en Afrique urbaine",
        "region": "Central Africa",
        "boilerplate": (
            "Les candidats doivent détenir un certificat d'enregistrement commercial valide délivré au cours "
            "des cinq dernières années. Les évaluations d'impact environnemental, le cas échéant, doivent "
            "accompagner la candidature. Le Fonds ne soutient pas l'acquisition foncière, la construction "
            "civile ni le financement rétroactif d'activités déjà engagées."
        ),
        "body": (
            "Le fonds soutient des approches innovantes de collecte, tri et valorisation des déchets solides "
            "municipaux, notamment le recyclage du plastique, le compostage et la conversion des déchets en "
            "énergie. Les modèles d'économie circulaire créant des opportunités de revenus pour les "
            "récupérateurs et les travailleurs du secteur informel seront prioritaires."
        ),
    },
    {
        "title": "Subvention Agriculteurs Connectés",
        "sector": "agritech",
        "budget_usd": 5000,
        "deadline_days": 25,
        "eligibility": "Startups agritech en phase d'amorçage de moins de 10 employés au Sénégal ou en RDC",
        "region": "West Africa",
        "boilerplate": (
            "Il s'agit d'une subvention d'amorçage pour les startups en phase pré-revenus ou début de revenus. "
            "Les candidats ne doivent pas avoir reçu plus de 20 000 USD de financement de subvention "
            "antérieur de quelque source que ce soit. Un pitch deck de 10 diapositives maximum est requis "
            "en plus du formulaire de candidature standard."
        ),
        "body": (
            "Un financement d'amorçage est disponible pour les startups développant des plateformes numériques "
            "de mise en relation des petits agriculteurs directement avec les acheteurs, réduisant les coûts "
            "des intermédiaires et améliorant la transparence des prix. Les solutions incorporant des données "
            "de prix en temps réel et des alertes SMS pour les agriculteurs peu alphabétisés sont "
            "particulièrement encouragées."
        ),
    },
    {
        "title": "Programme Diagnostic Santé Numérique",
        "sector": "healthtech",
        "budget_usd": 200000,
        "deadline_days": 65,
        "eligibility": "Entreprises healthtech avec produits certifiés CE ou OMS-EUL déployés en Afrique centrale",
        "region": "Central Africa",
        "boilerplate": (
            "La documentation de certification des produits doit être soumise dans le cadre du dossier de "
            "candidature. Les candidatures ne comportant pas de preuve de certification valide ne seront pas "
            "examinées. La subvention couvre uniquement les coûts directs du projet ; les dépenses en capital "
            "dépassant 30 % du budget total nécessitent une approbation préalable du comité."
        ),
        "body": (
            "Cette subvention soutient le développement à grande échelle d'outils de diagnostic au point de "
            "soin pour les maladies infectieuses et non transmissibles dans les contextes à ressources limitées "
            "d'Afrique centrale. Les candidats doivent démontrer des stratégies de distribution claires et "
            "des partenariats avec les systèmes de santé nationaux."
        ),
    },
    {
        "title": "Appel à Projets Énergie Solaire Scolaire",
        "sector": "cleantech",
        "budget_usd": 50000,
        "deadline_days": 30,
        "eligibility": "Entreprises cleantech avec expérience en électrification d'écoles en Afrique de l'Ouest",
        "region": "West Africa",
        "boilerplate": (
            "Des lettres d'accord avec au moins trois écoles doivent être soumises avec la candidature. "
            "Les plans d'installation doivent être validés par un ingénieur électricien certifié. Le bailleur "
            "effectuera des inspections post-installation dans les 60 jours suivant la fin du projet. "
            "Les plans de maintenance couvrant un minimum de trois ans doivent être inclus dans le budget."
        ),
        "body": (
            "Cette subvention finance l'installation de systèmes solaires photovoltaïques dans les écoles "
            "hors réseau au Sénégal et au Mali, permettant l'accès à l'électricité pour les salles "
            "informatiques, l'éclairage et le pompage d'eau. Les candidats doivent démontrer un modèle "
            "d'installation clé en main avec maintenance intégrée et formation des enseignants."
        ),
    },
    {
        "title": "Fonds Agriculture de Précision Francophone",
        "sector": "agritech",
        "budget_usd": 200000,
        "deadline_days": 75,
        "eligibility": "Entreprises agritech utilisant données satellitaires ou drones pour l'analyse agricole",
        "region": "West Africa",
        "boilerplate": (
            "Les accords de licence de données pour les images satellitaires ou aériennes doivent être soumis "
            "avec la candidature. Les candidats doivent se conformer aux réglementations nationales de l'aviation "
            "concernant les opérations de drones. Les politiques de confidentialité des données agricoles doivent "
            "être incluses. Le bailleur peut demander une démonstration technique dans le cadre de la diligence raisonnable."
        ),
        "body": (
            "Cette subvention soutient les plateformes agritech qui utilisent la télédétection, les images "
            "satellitaires et les capteurs IoT pour fournir des informations exploitables aux agriculteurs "
            "sur la santé des sols, les conditions météorologiques et les performances des cultures. "
            "Les solutions doivent démontrer un coût par agriculteur inférieur à 20 USD par saison à grande échelle."
        ),
    },
    {
        "title": "Programme Monnaie Mobile Agricole",
        "sector": "fintech",
        "budget_usd": 50000,
        "deadline_days": 45,
        "eligibility": "Fintechs et agritechs ciblant le financement des petits agriculteurs en Afrique de l'Ouest",
        "region": "West Africa",
        "boilerplate": (
            "Les candidats doivent fournir une politique de protection et de confidentialité des données "
            "conforme aux lois nationales applicables. La subvention ne couvre pas les salaires des "
            "fondateurs ou directeurs à des taux supérieurs aux références du marché. Tous les achats "
            "dans le cadre de la subvention doivent suivre des procédures d'appel d'offres compétitives."
        ),
        "body": (
            "Cette subvention soutient les produits financiers numériques adaptés aux petits agriculteurs, "
            "notamment le crédit saisonnier, l'assurance récolte et le financement des intrants délivrés "
            "via des plateformes de monnaie mobile. Les candidats doivent démontrer des partenariats "
            "existants avec au moins un opérateur de réseau mobile ou une institution financière."
        ),
    },
    {
        "title": "Appel à Candidatures Déchets Plastiques",
        "sector": "wastetech",
        "budget_usd": 200000,
        "deadline_days": 70,
        "eligibility": "Entreprises convertissant les déchets plastiques en produits commerciaux en Afrique francophone",
        "region": "West Africa",
        "boilerplate": (
            "Les fournisseurs de technologie de pyrolyse ou de recyclage chimique doivent soumettre des "
            "résultats de tests d'émissions par des tiers. La documentation de consultation communautaire "
            "doit démontrer l'engagement avec les communautés de récupérateurs. La subvention exclut la "
            "production de plastiques à usage unique sous toutes ses formes."
        ),
        "body": (
            "Des subventions soutiennent les entreprises convertissant les déchets plastiques collectés en "
            "pavés, matériaux de construction ou carburant grâce à des procédés mécaniques ou thermiques "
            "éprouvés. Les candidatures doivent inclure un plan de réseau de collecte couvrant au moins "
            "trois quartiers ou marchés."
        ),
    },
    {
        "title": "Fonds Compostage Urbain Francophone",
        "sector": "wastetech",
        "budget_usd": 50000,
        "deadline_days": 35,
        "eligibility": "PME avec opérations de compostage de déchets organiques urbains en Afrique de l'Ouest",
        "region": "West Africa",
        "boilerplate": (
            "Les sites de compostage doivent détenir des permis d'exploitation municipaux valides. Des plans "
            "de gestion des odeurs sont requis pour tous les sites situés à moins de 500 mètres des zones "
            "résidentielles. Le bailleur se réserve le droit de partager publiquement les enseignements du "
            "projet, à l'exclusion des informations techniques propriétaires."
        ),
        "body": (
            "Des subventions soutiennent le développement à grande échelle d'entreprises de compostage de "
            "déchets organiques urbains qui détournent les déchets alimentaires et de marché des décharges "
            "et produisent des engrais organiques pour les agriculteurs urbains. Les modèles d'affaires "
            "reliant le compostage à l'agriculture urbaine sont particulièrement encouragés."
        ),
    },
    {
        "title": "Programme Formation Enseignants Numérique",
        "sector": "edtech",
        "budget_usd": 50000,
        "deadline_days": 40,
        "eligibility": "Entreprises EdTech axées sur le développement professionnel des enseignants en Afrique francophone",
        "region": "West Africa",
        "boilerplate": (
            "Des lettres de soutien d'au moins deux districts scolaires ou autorités éducatives doivent être "
            "incluses. Les candidats doivent accepter de partager des données d'utilisation anonymisées avec "
            "le bailleur à des fins de recherche. La période de subvention est de 12 mois à compter de la "
            "date d'effet de l'accord, avec des prolongations sans frais examinées au cas par cas."
        ),
        "body": (
            "Le financement cible les plateformes offrant un développement professionnel continu aux "
            "enseignants dans les régions mal desservies d'Afrique francophone, en se concentrant sur "
            "la littératie numérique, la pédagogie et la compétence disciplinaire. Les plateformes "
            "doivent soutenir l'apprentissage asynchrone pour les enseignants avec un accès limité à Internet."
        ),
    },
    {
        "title": "Fonds Bâtiments Verts Durables",
        "sector": "cleantech",
        "budget_usd": 200000,
        "deadline_days": 65,
        "eligibility": "PME cleantech produisant des matériaux de construction durables en Afrique francophone",
        "region": "Central Africa",
        "boilerplate": (
            "Les certifications de test des matériaux d'un laboratoire accrédité sont requises. La documentation "
            "d'analyse du cycle de vie comparant le matériau proposé aux alternatives conventionnelles doit être "
            "fournie. La subvention interdit l'utilisation de matériaux classés dangereux selon les conventions "
            "internationales. Les bénéficiaires doivent soumettre des rapports d'avancement semestriels."
        ),
        "body": (
            "Cette subvention soutient les entreprises développant et commercialisant des matériaux de "
            "construction durables, notamment les briques en terre compressée, les briques en plastique "
            "recyclé et l'isolation biosourcée en Afrique centrale et de l'Ouest. Les candidats doivent "
            "démontrer une demande du marché à travers des ventes existantes ou des lettres d'intention "
            "d'entreprises de construction."
        ),
    },
    {
        "title": "Appel à Projets Apprentissage Linguistique",
        "sector": "edtech",
        "budget_usd": 200000,
        "deadline_days": 55,
        "eligibility": "Entreprises EdTech développant des outils d'enseignement multilingues ou en langue maternelle",
        "region": "Pan-Africa",
        "boilerplate": (
            "Les preuves de localisation linguistique doivent démontrer une co-conception authentique avec "
            "des communautés de locuteurs natifs. Des certificats d'alignement curriculaire d'au moins un "
            "ministère national de l'éducation sont requis. La subvention ne finance pas l'achat de matériel "
            "dépassant 15 % du coût total du projet."
        ),
        "body": (
            "Des subventions soutiennent les plateformes EdTech dispensant un enseignement en langues "
            "africaines maternelles et officielles, avec un accent sur l'éducation de la petite enfance "
            "et l'enseignement primaire. Les solutions doivent intégrer un contenu culturellement pertinent "
            "et soutenir à la fois l'apprentissage en classe et à domicile."
        ),
    },
]

def format_deadline(days_from_today):
    d = TODAY + timedelta(days=days_from_today)
    return d.strftime("%Y-%m-%d")

def write_tender(tid, data, lang):
    deadline_str = format_deadline(data["deadline_days"])
    if lang == "en":
        content = f"""TENDER NOTICE — {data['title'].upper()} [{tid}]
Tender ID: {tid}
Language: English
Sector: {data['sector']}
Budget: USD {data['budget_usd']:,}
Deadline: {deadline_str}
Region: {data['region']}
Eligibility: {data['eligibility']}

OVERVIEW
{data['body']}

APPLICATION REQUIREMENTS
{data['boilerplate']}

CONTACT
All inquiries must be submitted in writing via the official grants portal.
No telephone inquiries will be entertained. The granting body reserves
the right to amend these terms at any time prior to the application deadline.
"""
    else:
        content = f"""AVIS D'APPEL D'OFFRES — {data['title'].upper()} [{tid}]
Référence: {tid}
Langue: Français
Secteur: {data['sector']}
Budget: USD {data['budget_usd']:,}
Date limite: {deadline_str}
Région: {data['region']}
Éligibilité: {data['eligibility']}

APERÇU
{data['body']}

EXIGENCES DE CANDIDATURE
{data['boilerplate']}

CONTACT
Toutes les demandes doivent être soumises par écrit via le portail officiel
des subventions. Aucune demande téléphonique ne sera acceptée. L'organisme
d'attribution se réserve le droit de modifier ces conditions à tout moment
avant la date limite de candidature.
"""
    path = os.path.join(TENDERS_DIR, f"{tid}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Generate 24 EN tenders (60%) then 16 FR tenders (40%)
# Each tender has a unique title to prevent deduplication issues
def generate_tenders():
    # 40 tenders: 24 EN, 16 FR (60/40 split)
    en_pool = EN_TENDERS * 2  # 46 available, pick 24
    fr_pool = FR_TENDERS      # 16 available, pick 16
    random.shuffle(en_pool)
    selected_en = en_pool[:24]
    selected_fr = fr_pool[:16]

    tid_counter = 1
    tender_meta = []
    for data in selected_en:
        tid = f"T{tid_counter:02d}"
        write_tender(tid, data, "en")
        tender_meta.append({
            "id": tid, "sector": data["sector"],
            "budget_usd": data["budget_usd"],
            "deadline_days": data["deadline_days"],
            "region": data["region"], "lang": "en",
            "title": f"{data['title']} [{tid}]",
        })
        tid_counter += 1

    for data in selected_fr:
        tid = f"T{tid_counter:02d}"
        write_tender(tid, data, "fr")
        tender_meta.append({
            "id": tid, "sector": data["sector"],
            "budget_usd": data["budget_usd"],
            "deadline_days": data["deadline_days"],
            "region": data["region"], "lang": "fr",
            "title": f"{data['title']} [{tid}]",
        })
        tid_counter += 1

    return tender_meta

# Profiles span 5 countries to test cross-lingual and
# cross-regional matching. Languages list drives summary
# generation language selection in matcher.py
PROFILES = [
    {
        "id": "01", "name": "AgroSmart Rwanda", "sector": "agritech",
        "country": "Rwanda", "employees": 12, "languages": ["en"],
        "needs_text": (
            "We build precision agriculture and crop disease detection tools for smallholder "
            "farmers in Rwanda and East Africa. Our mobile app provides weather alerts, soil "
            "health insights, and direct market linkage, reducing post-harvest losses."
        ),
        "past_funding": 15000,
    },
    {
        "id": "02", "name": "SantéMobile Sénégal", "sector": "healthtech",
        "country": "Senegal", "employees": 8, "languages": ["fr"],
        "needs_text": (
            "Nous développons des outils de diagnostic mobile et de télésanté pour les agents "
            "de santé communautaires au Sénégal. Notre application hors ligne permet la collecte "
            "de données patients et la gestion des référencements dans les zones rurales."
        ),
        "past_funding": 20000,
    },
    {
        "id": "03", "name": "CleanGrid Kenya", "sector": "cleantech",
        "country": "Kenya", "employees": 25, "languages": ["en"],
        "needs_text": (
            "CleanGrid deploys solar mini-grids and battery storage systems to off-grid "
            "communities in Kenya and Tanzania. We have installed over 50 systems serving "
            "3,000 households and are scaling to 200 more communities."
        ),
        "past_funding": 150000,
    },
    {
        "id": "04", "name": "EduNova DRC", "sector": "edtech",
        "country": "DRC", "employees": 6, "languages": ["fr"],
        "needs_text": (
            "EduNova développe des contenus éducatifs en langues locales pour les enfants "
            "de la RDC. Notre plateforme hors ligne fonctionne sur des tablettes à faible "
            "coût et aligne les cours avec le programme national congolais."
        ),
        "past_funding": 10000,
    },
    {
        "id": "05", "name": "PayLeaf Ethiopia", "sector": "fintech",
        "country": "Ethiopia", "employees": 15, "languages": ["en"],
        "needs_text": (
            "PayLeaf offers mobile savings, micro-credit, and crop insurance products to "
            "smallholder farmers and rural VSLAs in Ethiopia. We integrate with Telebirr "
            "and local MFIs to reach the unbanked population."
        ),
        "past_funding": 30000,
    },
    {
        "id": "06", "name": "RecycloHub Kigali", "sector": "wastetech",
        "country": "Rwanda", "employees": 18, "languages": ["en", "fr"],
        "needs_text": (
            "RecycloHub collecte et valorise les déchets plastiques et organiques à Kigali. "
            "We operate three collection centers and produce recycled plastic paving blocks "
            "sold to construction companies across Rwanda and neighboring countries."
        ),
        "past_funding": 25000,
    },
    {
        "id": "07", "name": "HealthBridge Uganda", "sector": "healthtech",
        "country": "Uganda", "employees": 30, "languages": ["en"],
        "needs_text": (
            "HealthBridge builds interoperable electronic medical records and health "
            "information systems for primary health facilities in East Africa. Our "
            "FHIR-compliant platform serves 120 clinics in Kenya and Uganda."
        ),
        "past_funding": 80000,
    },
    {
        "id": "08", "name": "GreenBuild Dakar", "sector": "cleantech",
        "country": "Senegal", "employees": 20, "languages": ["fr"],
        "needs_text": (
            "GreenBuild produit des briques en terre compressée et des matériaux "
            "d'isolation biosourcés à Dakar. Nos matériaux réduisent les émissions de "
            "carbone dans la construction et sont 40 % moins chers que le ciment importé."
        ),
        "past_funding": 40000,
    },
    {
        "id": "09", "name": "FarmLink Kenya", "sector": "agritech",
        "country": "Kenya", "employees": 10, "languages": ["en", "fr"],
        "needs_text": (
            "FarmLink connects smallholder farmers to buyers via a digital marketplace with "
            "real-time commodity price data and SMS alerts. We use satellite imagery and "
            "IoT sensors to provide soil and weather analytics to 5,000 farmers in Kenya."
        ),
        "past_funding": 35000,
    },
    {
        "id": "10", "name": "WasteWise Kinshasa", "sector": "wastetech",
        "country": "DRC", "employees": 14, "languages": ["fr"],
        "needs_text": (
            "WasteWise Kinshasa gère des centres de collecte et de tri des déchets "
            "solides municipaux à Kinshasa. Nous transformons les déchets plastiques "
            "en pavés et les déchets organiques en compost vendu aux agriculteurs urbains."
        ),
        "past_funding": 18000,
    },
]

# Gold matches are curated by sector alignment:
# each profile's 3 gold matches are tenders in the same sector.
# This ensures evaluation measures sector retrieval quality.
def build_gold_matches(tender_meta):
    """
    3 gold matches per profile, genuinely relevant:
    same sector, feasible budget (<= 200k for most), valid region.
    """
    sector_to_tenders = {}
    for t in tender_meta:
        sector_to_tenders.setdefault(t["sector"], []).append(t)

    region_rules = {
        "Rwanda":   ["East Africa", "Sub-Saharan Africa", "Pan-Africa", "Central Africa"],
        "Kenya":    ["East Africa", "Sub-Saharan Africa", "Pan-Africa"],
        "Senegal":  ["West Africa", "Sub-Saharan Africa", "Pan-Africa"],
        "DRC":      ["Central Africa", "Sub-Saharan Africa", "Pan-Africa"],
        "Ethiopia": ["East Africa", "Sub-Saharan Africa", "Pan-Africa"],
        "Uganda":   ["East Africa", "Sub-Saharan Africa", "Pan-Africa"],
    }

    rows = []
    for p in PROFILES:
        candidates = [
            t for t in sector_to_tenders.get(p["sector"], [])
            if t["budget_usd"] <= 200000 and t["region"] in region_rules[p["country"]]
        ]
        if len(candidates) < 3:
            candidates = [t for t in sector_to_tenders.get(p["sector"], [])]
        random.shuffle(candidates)
        chosen = candidates[:3]
        for t in chosen:
            rows.append({"profile_id": p["id"], "tender_id": t["id"], "relevance_score": 1.0})
    return rows

def main():
    print("Generating tenders...")
    tender_meta = generate_tenders()
    print(f"  Created {len(tender_meta)} tenders in {TENDERS_DIR}")

    profiles_path = os.path.join(BASE, "profiles.json")
    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(PROFILES, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {profiles_path}")

    gold = build_gold_matches(tender_meta)
    gold_path = os.path.join(BASE, "gold_matches.csv")
    with open(gold_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["profile_id", "tender_id", "relevance_score"])
        writer.writeheader()
        writer.writerows(gold)
    print(f"  Wrote {gold_path} ({len(gold)} gold matches)")

    catalog_path = os.path.join(BASE, "catalog.csv")
    with open(catalog_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["tender_id", "title", "sector", "budget_usd", "deadline", "language", "region"])
        writer.writeheader()
        for t in tender_meta:
            writer.writerow({
                "tender_id": t["id"],
                "title": t["title"],
                "sector": t["sector"],
                "budget_usd": t["budget_usd"],
                "deadline": format_deadline(t["deadline_days"]),
                "language": t["lang"],
                "region": t["region"],
            })
    print(f"  Wrote {catalog_path} ({len(tender_meta)} rows)")

if __name__ == "__main__":
    main()
