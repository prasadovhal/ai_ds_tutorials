# Article Summarizer Skill - Complete Documentation

**Date:** 2026-08-03
**Version:** v1.0
**Status:** Ready to Use
**Skill Type:** Content Analysis & Comparison

---

## 🎯 What This Skill Does

The article-summarizer skill helps you:

1. **Quickly understand articles** from any website (Medium, news sites, blogs)
2. **Find related content** by searching for top 5 similar articles automatically
3. **Compare multiple articles** and see what's included in each one
4. **Extract key insights** with comprehensive bullet-point notes
5. **Create study materials** formatted for easy reference and learning

---

## 📋 Key Features

### ✅ Smart URL Validation
- Checks if URLs are accessible before processing
- Identifies article source/domain
- Validates URL format
- Gives clear error messages if URL is invalid

### ✅ Paywall Detection
- Detects articles behind paywalls early
- Provides clear user options (copy-paste alternative)
- Offers workarounds (archive.org, browser reader mode, etc.)
- **Important:** Cannot bypass paywalls automatically, but can fully analyze text if user provides it

### ✅ Content Extraction & Summarization
- Fetches article content from URLs
- Extracts: title, author, publication date, main body text
- Cleans up ads, sidebars, non-essential content
- Creates 1-2 paragraph summary of main content

### ✅ Intelligent Web Search (Conditional)
**If 1 article:** 
- Searches web for top 5 similar articles
- Filters for quality sources
- Prioritizes free/accessible articles
- Uses keywords from main article

**If 2+ articles:**
- Skips web search entirely
- Focuses on comparing provided articles
- Saves time and API calls

### ✅ Comprehensive Key Point Extraction
For each article, extracts:
- Core concepts and thesis
- Main arguments with supporting details
- Key data and statistics
- Key insights and takeaways
- Limitations and caveats
- Resources and tools mentioned
- Quotes (if significant)
- Target audience

### ✅ Comparison Analysis
Creates comparison matrix showing:
- What topics each article covers
- What's unique to the main article
- What other articles provide that main doesn't
- Unique perspectives and angles
- Overlapping areas

### ✅ Master Notes & Study Materials
Generates:
- **Comprehensive master notes** - Synthesized insights across all articles
- **Study notes format** - Organized sections with hierarchy
- **Reading order recommendations** - Sequential learning path
- **Gaps identification** - What's not covered by any article
- **Actionable takeaways** - What you can do with this knowledge

---

## 📊 Workflow: How It Works

### Single Article Workflow

```
User provides 1 article URL
       ↓
Step 1: Validate URL
       ↓
Step 2: Check for paywall
       ↓
Step 3: Extract content
       ↓
Step 4: Summarize article
       ↓
Step 5: SEARCH WEB → Find top 5 similar articles ← Only for 1 article
       ↓
Step 6: Extract key points from main article
       ↓
Step 7: Extract key points from 5 similar articles
       ↓
Step 8: Create comparison matrix
       ↓
Step 9: Generate master notes
       ↓
Step 10: Format study notes
       ↓
OUTPUT: Comprehensive analysis with comparison
```

### Multiple Articles Workflow

```
User provides 2+ article URLs
       ↓
Step 1: Validate all URLs
       ↓
Step 2: Check for paywalls
       ↓
Step 3: Extract content from all
       ↓
Step 4: Summarize each article
       ↓
Step 5: SKIP WEB SEARCH ← No search for 2+ articles
       ↓
Step 6: Extract key points from each
       ↓
Step 7: (Skipped)
       ↓
Step 8: Create comparison matrix
       ↓
Step 9: Generate master notes
       ↓
Step 10: Format study notes
       ↓
OUTPUT: Comparison-focused analysis
```

**Key difference:** Single article triggers web search; multiple articles skip it.

---

## 🔄 Conditional Logic Explained

### Why Conditional Search?

**Single Article (Search enabled):**
- You want to understand the article AND see what else is out there
- Search helps find context and alternative perspectives
- Great for research and learning
- You have time for deeper exploration

**Multiple Articles (Search disabled):**
- You already have multiple sources
- You want to compare them, not find more
- Saves time and API calls
- Focuses on what you already provided

---

## 🎯 Use Cases

### Use Case 1: Learning a New Topic
```
User: "Summarize this article on machine learning and find similar ones"
https://medium.com/intro-to-ml

Skill does:
✅ Summarizes the article
✅ Finds 5 similar ML articles
✅ Shows what's unique about the original
✅ Creates study notes for learning
```

### Use Case 2: Comparing Perspectives
```
User: "Compare these 3 articles on remote work productivity"
https://example.com/article-1
https://example.com/article-2
https://example.com/article-3

Skill does:
✅ Summarizes each article
✅ Skips web search (you gave 3 articles)
✅ Shows what each covers
✅ Highlights unique perspectives
✅ Creates comprehensive comparison
```

### Use Case 3: Paywalled Content (Medium Membership)
```
User: "Summarize this article"
https://medium.com/premium-article

Skill detects paywall:
⚠️ "This is behind Medium paywall"
✅ Offers solutions:
   1. Log in → Copy text → Paste in chat
   2. Use reader mode → Copy → Paste
   3. Check archive.org for free version

User follows option 1:
→ Pastes full article text in chat

Skill provides:
✅ Summary of the Medium article
✅ 5 similar free Medium articles
✅ Comparison of all 6
✅ Study notes
```

### Use Case 4: Research Synthesis
```
User: "I'm researching AI ethics. Find articles and compare"
https://example.com/ai-ethics-1

Skill does:
✅ Summarizes the one you provided
✅ Finds 5 more on AI ethics
✅ Creates comparison of all 6
✅ Highlights key themes across sources
✅ Identifies gaps in coverage
```

---

## 📝 Output Sections Explained

### 1. Article Summary
```
Title, Source, Author, Date, Type, Read Time
+ 1-2 paragraph summary
+ Main topic
+ Target audience
```
**Use for:** Quick overview of what article is about

### 2. Key Points - Main Article
```
📌 Core Concepts
🎯 Main Arguments
📊 Key Data/Statistics
💡 Key Insights
✅ Actionable Takeaways
⚠️ Limitations/Caveats
🔗 Resources Mentioned
🎓 Target Audience
💬 Notable Quotes
```
**Use for:** Deep understanding of the article's content

### 3. Similar Articles Analysis (if single article)
```
Summary of each article
Key points for each
Relation to main article
Source URL
```
**Use for:** Understanding how article fits in context of similar work

### 4. Comparison Matrix
```
Topics covered in each
What's unique to main
What's in others but not main
```
**Use for:** Visual comparison of coverage and gaps

### 5. Comprehensive Master Notes
```
Key concepts across all
Most important points
Data & statistics summary
Synthesized insights
Actionable takeaways
Gaps & questions
Reading order recommendation
```
**Use for:** Comprehensive learning resource

### 6. Study Notes Format
```
Overview
Main Concepts (with details)
Key Findings
Practical Applications
Related Articles
```
**Use for:** Long-term reference and studying

---

## ⚠️ Paywall Handling

### What Happens When Paywall Detected

```
Skill: "This article is behind a paywall"
Offers options:
1. Copy article text and paste it → Still analyze completely
2. Use browser reader mode → Copy text from simplified view
3. Try archive.org → Wayback machine might have old version
4. Skip article → Move to another
```

### Important Limitation

**❌ CANNOT:**
- Automatically access content after you login
- Maintain browser sessions or cookies
- Store or use your login credentials
- Replay your login across multiple skill calls
- Keep you logged in for future requests

**WHY:**
- Skills are stateless (each call starts with no session memory)
- Cannot authenticate on your behalf
- Cannot maintain cookies/tokens between calls
- This is an architectural constraint, not a technical oversight

**✅ WORKAROUND:**
- You log in to your account in your browser
- Copy the full article text
- Paste it into chat
- Skill analyzes it fully (provides same output as URL)
- Get summaries, comparisons, and study notes instantly

**This is actually better for privacy** — your credentials never leave your browser

**This is a designed limitation, not a bug.**

---

## 🎯 Success Examples

### Example 1: Single Article with Web Search

**Input:**
```
Summarize this article about AI trends
https://medium.com/ai-trends-2026
```

**Output includes:**
- ✅ Summary of the Medium article
- ✅ 5 similar articles found via web search
- ✅ Comparison of what makes the Medium article unique
- ✅ Master notes synthesizing all 6 articles
- ✅ Recommended reading order
- ✅ Study notes for future reference

### Example 2: Multiple Articles (No Web Search)

**Input:**
```
Compare these 3 articles on remote work
https://blog1.com/remote-work
https://blog2.com/remote-benefits
https://blog3.com/remote-productivity
```

**Output includes:**
- ✅ Summary of all 3 articles
- ✅ No web search (you gave 3 articles already)
- ✅ Detailed comparison matrix
- ✅ What each article emphasizes
- ✅ Unique perspectives per article
- ✅ Master notes of all 3

### Example 3: Paywalled Article + User Provides Text

**Input:**
```
This article is behind paywall:
https://paywalled-journal.com/article

Here's the text: [user pastes full article]
```

**Output includes:**
- ✅ Full analysis despite paywall
- ✅ 5 similar free articles found
- ✅ Comparison with similar articles
- ✅ Comprehensive notes
- ✅ Study materials

---

## 🛠️ Tools This Skill Uses

**Required:**
- **Web Search** - Find similar articles
- **Web Fetch** - Extract article content from URLs
- **Content Parsing** - Clean and structure article text

**Optional:**
- **Python** - Format and organize notes
- **Text Analysis** - Create summaries

---

## 📏 When NOT to Use This Skill

❌ Very short content (< 200 words)  
❌ Videos or podcasts (text only)  
❌ Real-time feeds or dynamic content  
❌ Images or image galleries  
❌ Interactive content that needs navigation  
❌ Single-page applications requiring login  

**For these, use alternative approaches or provide text manually**

---

## 🎓 Model Recommendation

| Task | Recommended Model |
|------|-------------------|
| **Deep comparison & analysis** | Claude Opus 4.7 |
| **Balanced performance** | Claude Sonnet 4.6 |
| **Quick summaries only** | Claude Haiku 4.5 |

**For best results:** Use Opus or Sonnet (Haiku may miss nuances in comparison)

---

## 📈 What's New vs Existing Skills

### Compared to Research Paper Reviewer
| Feature | Research Paper | Article Summarizer |
|---------|---------------|--------------------|
| **Input** | Markdown files only | Live URLs (web articles) |
| **Search for similar** | ❌ No | ✅ Yes (1 article only) |
| **Compare multiple** | ❌ No | ✅ Yes |
| **Paywall detection** | ❌ No | ✅ Yes |
| **Web access** | ❌ No | ✅ Yes |
| **Algorithm explanation** | ✅ Yes (v1.1) | ❌ No |

### Complementary Skills
- **research-paper-reviewer** - For academic papers
- **humanwriter** - For writing summaries yourself
- **article-summarizer** - For analyzing web articles (this skill)

---

## 🚀 Quick Start Examples

### Example 1: Basic Usage
```
/article-summarizer https://medium.com/article-name
```
Output: Summary + 5 similar articles + comparison + notes

### Example 2: Compare Multiple
```
/article-summarizer compare these:
https://blog1.com/article
https://blog2.com/article
https://blog3.com/article
```
Output: Comparison of all 3 (no web search)

### Example 3: With Paywall Workaround
```
This article is paywalled, here's the text:
[pasted article content]

Can you analyze it?
```
Output: Full analysis (still finds 5 similar free articles)

---

## 📊 Feature Matrix

| Feature | v1.0 | Planned |
|---------|------|---------|
| **URL Summarization** | ✅ | ✅ |
| **Web Search (conditional)** | ✅ | ✅ |
| **Multi-article comparison** | ✅ | ✅ |
| **Paywall detection** | ✅ | ✅ |
| **Key point extraction** | ✅ | ✅ |
| **Comparison matrix** | ✅ | ✅ |
| **Master notes** | ✅ | ✅ |
| **Study notes format** | ✅ | ✅ |
| **PDF article upload** | ❌ | 📋 v2.0 |
| **Audio transcription** | ❌ | 📋 v2.0 |
| **Multi-language** | ❌ | 📋 v2.0 |
| **Export to PDF/Word** | ❌ | 📋 v2.0 |

---

## 🎯 Common Questions

### Q: What if I give it 1 article but DON'T want web search?
A: Just mention it! Say "analyze but don't search for similar articles"

### Q: Can it handle very long articles?
A: Yes, but extremely long content may be summarized more concisely

### Q: What about articles with paywalls?
A: Detected early. Copy-paste the text and skill still provides full analysis

### Q: Can I compare 10 articles?
A: Yes! No limit, though more articles = longer analysis

### Q: Does it preserve formatting from original?
A: Headings and structure preserved, ads/sidebars removed

### Q: How accurate are the "similar articles"?
A: Based on web search relevance. Quality depends on indexing

### Q: Can I use this for academic research?
A: Yes, great for literature review and synthesis

### Q: What about private/internal articles?
A: Must be publicly accessible URLs (no private content)

---

## 🔄 Version History

### v1.0 (2026-08-03) - Initial Release
- Article summarization from URLs
- Web search for similar articles (conditional on single article input)
- Comparison analysis for multiple articles
- Comprehensive notes generation
- Paywall detection with user workarounds
- Multi-article support (2+ articles skip web search)
- Markdown and study notes formatting
- Error handling for invalid URLs and content
- Output in 7 standardized formats

---

## 📚 Related Documentation

- [docs/06-list-of-skills-and-explanations.md](06-list-of-skills-and-explanations.md) - Catalog of all skills
- [skills/article-summarizer.md](../skills/article-summarizer.md) - Full skill definition
- [CLAUDE.md](../CLAUDE.md) - Project skills registration
- [docs/02-basics-about-skills.md](02-basics-about-skills.md) - How skills work

---

## 🎊 Summary

**article-summarizer v1.0 is ready to use** for analyzing web articles, finding similar content, and creating comprehensive comparison notes.

You can now:
- ✅ Summarize articles from any website
- ✅ Automatically find 5 similar articles (single article mode)
- ✅ Compare multiple articles you provide
- ✅ Extract key insights with bullet points
- ✅ Create study materials and master notes
- ✅ Handle paywalled content (with copy-paste workaround)

**Start using it:**
```
Summarize this article and find similar ones:
https://medium.com/article-name
```

Happy learning! 📚

---

## 🔗 Next Skill Ideas

After article-summarizer, consider:
- **Dataset Quality Analyzer** - Evaluate data quality
- **RAG Evaluator** - Test retrieval-augmented generation systems
- **Experiment Reviewer** - Review ML/data science experiments
- **Code Reviewer** - Security and quality review of code
- **Competitor Research** - Analyze competitor content
- **Content Analyzer** - Extract entities, topics, sentiment
