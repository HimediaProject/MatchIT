"""
Step 9: Final Validation and Quality Checks
"""
import json
from pathlib import Path
from collections import Counter

print("=" * 70)
print("Step 9: Final Validation and Quality Checks")
print("=" * 70)

# Load the final integrated data
print("\n[1] Loading integrated data...")
with open('./results/final_integrated_jobs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

metadata = data['metadata']
statistics = data['statistics']
jobs = data['jobs']

print(f"    Loaded {len(jobs)} jobs")

# Basic validation
print("\n[2] Running basic validations...")

# Check for required fields
required_fields = ['id', 'source', 'title', 'skills']
invalid_jobs = []

for i, job in enumerate(jobs):
    for field in required_fields:
        if field not in job or not job[field]:
            if field != 'skills' or not job.get('skills'):
                invalid_jobs.append((i, field))

if invalid_jobs:
    print(f"    WARNING: {len(invalid_jobs)} jobs missing required fields")
    for i, field in invalid_jobs[:5]:
        print(f"      - Job {i}: missing '{field}'")
else:
    print(f"    All jobs have required fields: OK")

# Check skills distribution
print("\n[3] Validating skills distribution...")

skills_per_job = [len(job.get('skills', [])) for job in jobs]
avg_skills = sum(skills_per_job) / len(skills_per_job) if skills_per_job else 0
max_skills = max(skills_per_job) if skills_per_job else 0
min_skills = min(skills_per_job) if skills_per_job else 0

print(f"    Avg skills per job: {avg_skills:.2f}")
print(f"    Max skills in a job: {max_skills}")
print(f"    Min skills in a job: {min_skills}")

jobs_no_skills = sum(1 for count in skills_per_job if count == 0)
print(f"    Jobs with no skills: {jobs_no_skills} ({jobs_no_skills/len(jobs)*100:.1f}%)")

# Check source distribution
print("\n[4] Validating source distribution...")
source_counts = Counter(job['source'] for job in jobs)
for source, count in source_counts.items():
    print(f"    {source}: {count} ({count/len(jobs)*100:.1f}%)")

# Sample validation
print("\n[5] Sample validation (first 5 jobs)...")
for i in range(min(5, len(jobs))):
    job = jobs[i]
    print(f"\n    Job {i+1}:")
    print(f"      Source: {job.get('source', 'N/A')}")
    print(f"      Title: {job.get('title', 'N/A')[:50]}...")
    print(f"      Company: {job.get('company', 'N/A')[:30]}")
    print(f"      Skills: {len(job.get('skills', []))} skills")
    print(f"      Top 5 skills: {job.get('skills', [])[:5]}")

# Quality scores
print("\n" + "=" * 70)
print("QUALITY ASSESSMENT")
print("=" * 70)

score = 100

# Deduct points for issues
if jobs_no_skills > len(jobs) * 0.1:  # More than 10% have no skills
    penalty = 20
    score -= penalty
    print(f"\n  - High % of jobs without skills: -{penalty} points")

if invalid_jobs:
    penalty = 10
    score -= penalty
    print(f"\n  - Jobs with missing fields: -{penalty} points")

if avg_skills < 2:
    penalty = 10
    score -= penalty
    print(f"\n  - Low average skills per job: -{penalty} points")

print(f"\nFINAL QUALITY SCORE: {score}/100")

if score >= 90:
    print("Status: EXCELLENT - Ready for production")
elif score >= 75:
    print("Status: GOOD - Minor issues to address")
elif score >= 60:
    print("Status: ACCEPTABLE - Some improvements needed")
else:
    print("Status: POOR - Significant issues need fixing")

# Final summary
print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)
print(f"\nTotal jobs validated: {len(jobs):,}")
print(f"Data sources: {len(source_counts)}")
print(f"Unique skills: {metadata['total_skills']}")
print(f"Quality score: {score}/100")
print("\n" + "=" * 70)
print("VALIDATION COMPLETE!")
print("=" * 70)
