Module 1: Source discovery

ingestion options

1. Manual job URL input
   ingest-job https://boards.greenhouse.io/openai/jobs/12345
2. Greenhouse public jobs
   ------ requires company list OR discovery step
   Best structured ATS ingestion target !
   https://boards.greenhouse.io/{company}
3. lever --same as GH

4. Workday JSON endpoint
   /wday/cxs/{tenant}/{company}/jobs

5. Google search scraping
   Pros-
   broad discovery
   flexible
   powerful
   Cons
   requires search API OR scraping engine
   Google blocks raw scraping
   Serper / SerpAPI cost money (after free tier)
   Verdict: Add later after pipeline stable

Search dimension

Daily:

3 palettes
× 5 locations
× ATS domains.

---

Use:

Serper = primary discovery engine

Later optionally add:

direct ATS board scraping

so search API usage drops further.

Example:

Instead of searching:

site:boards.greenhouse.io backend python

you directly scrape:

https://boards.greenhouse.io/openai
https://boards.greenhouse.io/scale
https://boards.greenhouse.io/databricks
That costs 0 API queries.

---

Module 4: ATS scoring module

Given:

normalized job
candidate profile
master resume facts

Return:

total fit score
component scores
reasons
must-have gaps
recommendation: reject / review / shortlist

Input files

From your own design:

structured candidate profile YAML/JSON
master resume text/markdown
normalized job JSON

4.1 Candidate profile loader

scoring/profile_loader.py

Loads a structured profile like:

target_roles
seniority_level
work_auth
locations
skill_clusters
tools
domain_experience
strongest_projects
hard_constraints

This is crucial. Without this, your scorer becomes keyword soup.

---

one experience
many bullets
each bullet has tags

Then selection becomes automatic.

Example tag vocabulary you should use

Start with:
backend
distributed_systems
microservices
java
python
api
kafka
spark
etl
ml_pipeline
llm
rag
aws
analytics
fintech
compliance
data_modeling
experimentation
vector_search
async_processing

The LLM should not invent bullets.

It should only do 3 things:

select from approved bullet bank
compress / merge related bullets
rewrite in the lane tone

So for a 1-page resume, the LLM can combine two evidence units into one stronger bullet, but only if both are already in your KB.

Example:

From two approved bullets:

built Node/Express APIs
productionized LLM-integrated backend pipelines

It can generate:

Built Node.js/Express backend services and productionized LLM-integrated pipelines for structured downstream analytics workflows.

-0-0-0-0-0-
v1

keyword overlap baseline
You already have this.

v2

structured rule-based ATS scoring
Add weighted components like:

title match
seniority match
must-have skill match
preferred skill match
domain match
location / work auth fit
v3

light NLP improvements
Then add:

normalization of terms
synonym mapping
phrase matching
maybe stemming/lemmatization
maybe embeddings later
0-0-0-0-0-0-0

4.2 Resume fact extractor

scoring/resume_index.py

Creates a compact indexed view of your resume:

companies
titles
technologies
project keywords
years of experience hints
leadership signals
education keywords

This should be precomputed once and cached.

4.3 Job analyzer

scoring/job_analyzer.py

Extracts from the normalized job:

required skills
preferred skills
title family
likely seniority
remote/on-site/visa constraints
domain tags
implied responsibilities

This is deterministic first.

4.4 Rule-based scoring engine

scoring/rules.py

This is the core ATS-ish scorer.

Subscores:

title similarity: 0–20
required skill match: 0–25
preferred skill overlap: 0–10
seniority match: 0–10
domain/industry match: 0–10
location/remote/work auth fit: 0–10
keyword density / terminology overlap: 0–10
bonus for strong relevant project evidence: 0–5

Total = 100

Output shape
{
"job_id": "job_123",
"score_total": 78,
"decision": "shortlist",
"component_scores": {
"title_similarity": 15,
"required_skill_match": 22,
"preferred_skill_overlap": 6,
"seniority_match": 8,
"domain_match": 7,
"location_fit": 10,
"keyword_overlap": 7,
"project_evidence_bonus": 3
},
"matched_skills": ["python", "fastapi", "rag", "llm"],
"missing_must_haves": ["kubernetes", "aws"],
"risk_flags": ["onsite requirement unclear"],
"reasons": [
"Strong overlap with backend + AI tooling",
"Resume shows relevant LLM and production workflow experience",
"Missing explicit cloud infrastructure depth"
]
}

End-to-end flow on your server
run discovery for query preset
get raw links from Serper for Greenhouse + Lever
fetch each real job page
normalize fields
compute dedupe key
upsert into SQLite
run ATS scorer against candidate profile
mark job as reject / review / shortlist
for shortlisted jobs, run LLM insights
generate application packet files
update tracking row
optionally sync to Google Sheets / Drive
optionally notify you
