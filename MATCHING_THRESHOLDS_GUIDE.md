# Matching Threshold Guidelines & Configuration

## Default Thresholds

### Search API

- **Default Confidence Threshold**: 80%
- **Recommended Range**: 60-90%
  - 60%: Sensitive search, catches loose matches (higher false positives)
  - 80%: Balanced (recommended for most use cases)
  - 90%: Strict search, high confidence only

### Batch Screening API

- **Default Confidence Threshold**: 80%
- **Configurable**: Users can adjust via "Match Threshold (%)" parameter
- **Recommended Thresholds by Use Case**:
  - 50-60%: High-risk screening, maximum sensitivity
  - 70-80%: Standard compliance screening
  - 85-95%: High-confidence alerts only

## Score Interpretation

### Individual Matches

| Score Range | Interpretation             | Action                | Example                                    |
| ----------- | -------------------------- | --------------------- | ------------------------------------------ |
| 95-100%     | **Exact/Near-Exact Match** | Immediate Action      | "Vladimir Putin" vs "Vladimir Putin"       |
| 85-94%      | **Likely Match**           | Review & Verify       | "Vladmir Putin" (typo) vs "Vladimir Putin" |
| 75-84%      | **Probable Match**         | Investigation         | "Putin" vs "Vladimir Putin"                |
| 65-74%      | **Possible Match**         | Consider context      | "Jon Smith" vs "John Smith"                |
| 50-64%      | **Weak Match**             | May be false positive | Partial name overlap                       |
| <50%        | **No Match**               | Ignore                | Unrelated names                            |

### Use Case Recommendations

#### 1. **High-Risk Entities** (Financial, Defense, etc.)

```
Threshold: 65%
Action: Review all matches above 65%
Why: Cannot afford false negatives
```

#### 2. **Standard Compliance** (Most Common)

```
Threshold: 75-80%
Action: Flag matches above 75%, manual review of 75-85%
Why: Balances false positives and negatives
```

#### 3. **Low-Risk Screening** (Internal checks)

```
Threshold: 80-85%
Action: Escalate only high-confidence matches
Why: High efficiency, some risk acceptable
```

#### 4. **Customer Onboarding** (KYC)

```
Threshold: 70%
Action: Block matches above 70%, review above 60%
Why: Regulatory requirement for false positive prevention
```

## Factors Affecting Match Score

### Increases Score

✓ Exact name match
✓ Matching aliases
✓ Name with correct prefixes/suffixes removed
✓ Phonetically similar names (Soundex/Metaphone)
✓ High token overlap in multi-word names
✓ Proper diacritic handling

### Decreases Score

✗ Typos (minor: -5-10%, major: -20-30%)
✗ Different word order (minor: -10-20%)
✗ Missing middle names (context-dependent)
✗ Completely different names (0%)
✗ Common name variations not in aliases

## Advanced Configuration

### Query Parameters

#### Search API

```bash
GET /search_sanctions?q=putin&limit=50
# Returns all matches sorted by confidence descending

# With filters
GET /search_sanctions?q=putin&country=russia&program=SDN
# Only considers matches matching all filters
```

#### Batch Screening API

```bash
POST /batch_screening
{
  "file": <Excel or CSV>,
  "entity_type": "individual",  # or "company"
  "threshold": 80  # Configurable 0-100
}
```

## Tuning Strategy

### For High False Positives

1. **Increase threshold**: 80% → 85%
2. **Review aliases**: Ensure accurate aliases in Firestore
3. **Check data quality**: Remove duplicates/variations
4. **Analyze failures**: Why are unrelated names matching?

### For High False Negatives

1. **Decrease threshold**: 80% → 75%
2. **Improve name preprocessing**: Check if names are being normalized
3. **Add aliases**: Names like "Vladimir" for "V."
4. **Check phonetic match**: Verify Soundex/Metaphone codes

## Batch Processing Examples

### Example 1: High-Risk Financial Screening

```
File: customers.csv
Entity Type: Company
Threshold: 65%
Expected: ~95% of matches are true positives
Action: Manual review of all matches
```

### Example 2: Employee Onboarding

```
File: new_hires.csv
Entity Type: Individual
Threshold: 75%
Expected: ~98% of matches are true positives
Action: Immediate block of high-confidence matches
```

### Example 3: Quarterly Compliance Check

```
File: customer_database.csv
Entity Type: Individual
Threshold: 80%
Expected: ~99% accuracy
Action: Flag suspicious matches, escalate to compliance team
```

## Monitoring & Metrics

### Track These KPIs

1. **Match Rate**: % of entities with any match above threshold
2. **False Positive Rate**: % of matches determined invalid in review
3. **False Negative Rate**: % of known sanctions not matched
4. **Average Confidence**: Mean score of all matches
5. **Processing Time**: Time per entity

### Recommended Monitoring Dashboard

```
Daily Report:
├─ Total Entities Screened: [n]
├─ Matches Found (>threshold): [n] ([x]%)
├─ High-Confidence (>90%): [n]
├─ Medium-Confidence (75-90%): [n]
├─ Low-Confidence (<75%): [n]
├─ Average Response Time: [ms]
└─ False Positive Rate: [x]%
```

## Performance Notes

### Matching Speed

- **Per Name**: ~50-100ms average
- **Batch of 1000**: ~50-100 seconds
- **Batch of 10000**: ~500-1000 seconds

### Factors Affecting Speed

- Database size (currently: ~30,382 sanctions)
- Number of aliases per record
- Query complexity (filtering)
- Network latency

## Future Enhancement Opportunities

1. **Machine Learning**: Train model on historical matches
2. **Weight Customization**: Allow different weightings for phonetic vs Levenshtein
3. **Caching**: Cache common matches for speed
4. **Batch Optimization**: Parallel processing for large batches
5. **Analytics**: Track which matching techniques are most effective
