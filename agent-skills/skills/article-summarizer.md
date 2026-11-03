---
name: article-summarizer
description: >
  Use this skill whenever the user asks to summarize articles, compare articles, 
  or extract key points from article links. Trigger for requests like 
  "summarize this article", "compare these articles", "find similar articles", 
  "extract key points", "create notes from this article". 
  This skill accepts single or multiple article links (Medium, news sites, blogs, etc.), 
  summarizes content, finds similar articles if needed, compares them, and creates 
  comprehensive bullet-point notes of important findings.
---

# Article Summarizer Skill

Summarize articles from any website, find similar articles, compare content, and create comprehensive notes of key findings with comparison analysis.

---

## Purpose

Summarize and analyze articles from any URL, extract key insights, compare against similar articles, and create comprehensive bullet-point notes for learning and reference.

## When to Use This Skill

Use this skill when:
- You need to quickly understand what an article is about
- You need to extract key points and create study notes
- You want detailed bullet-point analysis of article content
- You're doing research and need organized reference material
- You want to save time by getting structured summaries
- (Optional) You want to compare multiple articles you provide
- (Optional) You want to find similar articles (request explicitly)

Do NOT use this skill for:
- Very short snippets (less than 200 words)
- Non-text content (pure images, videos)
- Content that requires interactive navigation
- Real-time feeds or dynamic content

---

## Expected Input Format

**Input Type:** Article URL link(s)

**Supported Formats:**
- Single article URL: `https://medium.com/article-name`
- Multiple article URLs: 
  ```
  https://medium.com/article-1
  https://example.com/article-2
  https://news.site.com/article-3
  ```
- Any article from: Medium, news sites, blogs, technical articles, research posts

**Supported Sources:**
- Medium articles
- News websites (CNN, BBC, etc.)
- Blog posts
- Technical articles
- Magazine articles
- Newsletter content
- Industry publications

**URL Requirements:**
- Must be valid, accessible URL
- Must point to article/text content
- Should not be broken/404 links

---

## Workflow Steps

### Step 1: Input Validation
- Verify URL format validity
- Check if URL is accessible
- Count number of URLs (1 vs multiple)
- Identify article source/domain
- Check for paywall detection

### Step 2: Paywall & Access Check
- Detect if article is behind paywall
- If paywall detected:
  - **Stop here**
  - **Inform user:** "This article is behind a paywall"
  - **Provide options:**
    1. Paste article text directly into chat
    2. Copy article content and share as text
    3. Use browser's reader mode to access freely
    4. Check archive.org for older version
    5. Skip this article
  - Wait for user response

### Step 3: Content Extraction
- Fetch article content from URL
- Extract: Title, author, publication date
- Extract: Main body text/content
- Clean up: Remove ads, sidebars, non-essential content
- Preserve: Structure, headings, important formatting

### Step 4: Article Summarization
For the main article:
- Write 1-2 paragraph summary
- Identify main topic/theme
- Extract core message
- Note target audience
- Identify article type (opinion, tutorial, news, analysis, etc.)

### Step 5: Extract Key Points - Main Article
Create bullet-point notes:
- Main thesis/argument
- Key findings/conclusions
- Supporting evidence/data
- Methodology (if applicable)
- Limitations/caveats
- Actionable insights
- Statistics/data points
- Quotes (if significant)
- Tools/resources mentioned

### Step 6: Create Study/Reference Notes
Format final notes as:
- Organized sections
- Clear hierarchy
- Easy-to-scan bullet points
- Actionable takeaways
- Resource links

---

## Tools to Use

**Required Tools:**
- **Web Search** - For finding top 5 similar articles
- **Web Fetch/Content Extraction** - To read article content from URLs

**Optional Tools:**
- **Python** (optional) - For organizing/formatting notes
- **Text summarization** - For creating abstracts

---

## Rules and Constraints

### Must Follow

1. **Always validate URLs first** - Check if accessible before processing
2. **Detect paywalls early** - Don't waste time if can't access
3. **Be honest about access issues** - Tell user if can't fetch content
4. **Only search web if 1 article** - Skip search for 2+ articles
5. **Create comprehensive notes** - Bullet points should be detailed
6. **Compare fairly** - Show both similarities and differences
7. **Preserve article intent** - Don't misrepresent author's message

### Should Avoid

1. ❌ Don't try to bypass paywalls automatically
2. ❌ Don't access articles without proper authorization
3. ❌ Don't create fake similar articles if search fails
4. ❌ Don't summarize without reading full article
5. ❌ Don't compare articles from irrelevant topics
6. ❌ Don't claim to access content you couldn't fetch
7. ❌ Don't miss important nuances in comparison

### About Paywalls

**Important Limitation:**
- ❌ **Cannot access content after user login**
- ❌ **Cannot maintain browser sessions or cookies**
- ❌ **Cannot store login credentials**
- **Why:** Skills are stateless—each request starts fresh with no session memory
- **Solution:** User copies article text and pastes into chat
- **Workaround:** If user provides text content, still get full analysis (summaries, comparison, study notes)

---

## Output Format

### 1. Article Summary (Initial)

```
Title: [Article title]
Source: [Website/Publication]
Author: [Author name, if available]
Date Published: [Date]
Article Type: [Opinion/Tutorial/News/Analysis/How-to/etc]
Read Time: [Estimated reading time]

Summary:
[1-2 paragraph summary of main content]

Main Topic: [Core subject]
Target Audience: [Who should read this]
```

### 2. Paywall Detection (If Applicable)

```
⚠️ PAYWALL DETECTED

This article is behind a paywall/login requirement.

Options:
1. Copy the full article text from your browser and paste it in chat
2. Use your browser's reader mode to access freely, then copy text
3. Check archive.org for an older, free version of this article
4. Skip this article and focus on others

Note: I cannot maintain browser sessions or login credentials across calls.
But if you provide the article text, I can fully analyze and create 
comprehensive notes, including finding 5 similar articles and detailed comparison.
```

### 3. Key Points - Main Article

**Main Article: [Title]**

```
📌 Core Concepts:
• [Key concept 1]
• [Key concept 2]
• [Key concept 3]

🎯 Main Arguments:
• [Argument 1] - [supporting detail]
• [Argument 2] - [supporting detail]
• [Argument 3] - [supporting detail]

📊 Key Data/Statistics:
• [Statistic 1]: [value/finding]
• [Statistic 2]: [value/finding]
• [Statistic 3]: [value/finding]

💡 Key Insights:
• [Insight 1]
• [Insight 2]
• [Insight 3]

✅ Actionable Takeaways:
• [Action 1]
• [Action 2]
• [Action 3]

⚠️ Limitations/Caveats:
• [Limitation 1]
• [Limitation 2]

🔗 Resources Mentioned:
• [Resource 1]
• [Resource 2]

🎓 Target Audience:
[Who should read this]

💬 Notable Quotes:
• "[Quote 1]" - [context]
• "[Quote 2]" - [context]
```

### 4. Study Notes Format

**[Article Name] - Complete Notes**

```
═══════════════════════════════════════════════════════════

OVERVIEW
────────────────────────────────────────────────────────────
Topic: [Main topic]
Source: [Publication]
Key Message: [One sentence summary]

MAIN CONCEPTS
────────────────────────────────────────────────────────────
1. [Concept with explanation]
   └─ Supporting details:
      • Detail 1
      • Detail 2

2. [Concept with explanation]
   └─ Supporting details:
      • Detail 1
      • Detail 2

KEY FINDINGS
────────────────────────────────────────────────────────────
• Finding 1 - Evidence: [source/stat]
• Finding 2 - Evidence: [source/stat]
• Finding 3 - Evidence: [source/stat]

PRACTICAL APPLICATIONS
────────────────────────────────────────────────────────────
How to apply this:
1. [Application 1]
2. [Application 2]
3. [Application 3]

RELATED ARTICLES
────────────────────────────────────────────────────────────
For more on this topic, see:
• [Article 1]
• [Article 2]
• [Article 3]

═══════════════════════════════════════════════════════════
```

---

## Error Handling

### Error: Invalid URL

**Response:**
```
❌ INVALID URL

The URL you provided is not valid or not accessible.

Please verify:
1. URL is complete (starts with http:// or https://)
2. URL points to an article/text content
3. No typos in the URL
4. Domain is accessible

Please share a valid article URL and I'll summarize it.
```

### Error: Paywall/Login Required

**Response:**
```
⚠️ PAYWALL DETECTED

This article requires login/subscription (e.g., Medium membership, 
news site subscription) to read.

Here's what you can do:

Option 1: Copy Article Text (Recommended)
- Log in to your account in your browser
- Copy the full article text
- Paste it in the chat
- I'll provide complete analysis

Option 2: Use Reader Mode
- Open the article in your browser
- Enable reader mode (⌘+Shift+R on Mac, Ctrl+Shift+R on Windows)
- Copy text from the simplified view
- Paste in chat for full analysis

Option 3: Check Archive
- Visit archive.org
- Search for the article URL
- An older version might be freely available

Note: I cannot automatically access your login session or maintain
browser authentication between requests. However, if you provide the
article text, I can fully analyze it and find similar articles.
```

### Error: Non-Article Content

**Response:**
```
⚠️ NOT AN ARTICLE

The URL points to non-article content (possibly:
- Video page
- Social media profile
- Login page
- Image/media file
- Empty page

This skill is designed for text articles. Please share:
- Blog posts
- News articles
- Medium/Substack posts
- Technical articles
- Magazine articles
- Any readable text content
```

### Error: Can't Access Article

**Response:**
```
❌ UNABLE TO FETCH CONTENT

The article URL is valid but I cannot fetch the content.
This could be due to:
- Site blocking automated access
- Network issue
- Content removed
- Special formatting

Workaround:
Copy the article text and paste it in the chat.
I can then summarize and analyze it completely.
```

---

## Limitations & Important Notes

### What This Skill CAN Do

✅ Summarize articles from URLs  
✅ Extract key points and insights  
✅ Find similar articles via web search  
✅ Compare multiple articles  
✅ Create comprehensive notes  
✅ Handle multiple article URLs  
✅ Work with any text-based article  

### What This Skill CANNOT Do

❌ **Access articles behind paywalls automatically**
- User must provide text or login manually
- Cannot maintain browser sessions after login
- Cannot access subscription-only content

❌ **Access videos, podcasts, or images as source content**
- Only works with text articles
- Cannot analyze non-text media

❌ **Access articles on pages requiring JavaScript/interaction**
- Only works with static/readable content
- Dynamic content may not fully extract

❌ **Guarantee perfect extraction from all sites**
- Some sites may have unusual formatting
- Complex layouts might lose some formatting
- Ads/sidebars sometimes included

### Workarounds for Limitations

**For Paywall Articles (Best → OK):**
1. **Best:** Log in → Copy full text → Paste in chat
2. **Good:** Use browser's reader mode → Copy → Paste
3. **Alternative:** Check archive.org for free old versions
4. **Last resort:** Share different article that's free

**For Complex Layouts:**
1. Use browser's reader mode (⌘+Shift+R or Ctrl+Shift+R)
2. Copy text from simplified view
3. Paste into chat for full analysis

**What NOT to do:**
1. ❌ Don't share your login credentials
2. ❌ Don't share password managers
3. ❌ Don't expect browser login to persist
4. ❌ Don't try workaround extensions (skill can't use them)

---

## Example Usage

### Single Article

**User Input:**
```
Summarize this article and create study notes:
https://medium.com/article-about-ai
```

**Skill Output:**
```
1. Article Summary
2. Key Points
3. Study Notes Format
```

### Multiple Articles

**User Input:**
```
Compare these 3 articles and create notes:
https://medium.com/article-1
https://example.com/article-2
https://blog.site.com/article-3
```

**Skill Output:**
```
1. Summary of Article 1
2. Summary of Article 2
3. Summary of Article 3
4. Combined Study Notes
```

### If User Wants Similar Articles

**User Input:**
```
Summarize this article and find similar ones on the same topic:
https://medium.com/article-about-ai
```

**Skill Output:**
```
1. Article Summary
2. Key Points
3. Study Notes
+ Web search for 5 similar articles on the topic (explicitly requested)
+ Comparison of all articles
```

### Paywall Article

**User Input:**
```
https://paywalled-site.com/premium-article
```

**Skill Output:**
```
⚠️ PAYWALL DETECTED - Asking user for options
[Wait for user to provide text or alternative]

Once user provides text:
1. Complete analysis
2. Comprehensive notes
3. Key points extraction
```

---

## Success Criteria

This skill is working well when:

✅ Articles are accurately summarized  
✅ Key points are comprehensive and specific  
✅ Similar articles are actually similar in topic  
✅ Comparison shows real differences  
✅ Notes are organized and easy to scan  
✅ Bullet points are concise but informative  
✅ Paywalls are detected early  
✅ User gets actionable insights  
✅ Multiple articles handled correctly (no search)  
✅ Comprehensive yet scannable format  

---

## Model Recommendation

- **Recommended:** Claude Opus (deep analysis, comparison)
- **Fallback:** Claude Sonnet (good balance)
- **Not recommended:** Claude Haiku (may miss nuances)

---

## Version History

- **v1.1** (2026-08-06) - Simplified output focus
  - Removed automatic web search for similar articles
  - Web search now opt-in (user requests explicitly)
  - Streamlined output: Summary + Key Points + Study Notes
  - Cleaner, less overwhelming analysis format
  - Fixed paywall handling (no credential sharing suggestions)
  - Support for multiple article comparison when provided

- **v1.0** (2026-08-03) - Initial release
  - Article summarization from URLs
  - Web search for similar articles (conditional on single article)
  - Comparison analysis
  - Comprehensive notes generation
  - Paywall detection with user guidance
  - Multi-article support with intelligent workflow
  - Markdown and study notes formatting

---

## Related Skills

- **research-paper-reviewer** - For academic paper analysis
- **humanwriter** - For writing summaries
- Consider creating: **content-analyzer**, **competitor-research**

---

## Important: Paywall Handling Strategy

This skill includes **paywall detection** but cannot bypass paywalls automatically.

**Why?** 
- Skills operate at the interface/input level
- Cannot maintain authenticated browser sessions
- Cannot store/use login credentials
- Cannot replay user login for content access

**Solution Provided:**
- Early detection (doesn't waste user's time)
- Clear user options (copy-paste alternative)
- Full analysis capability (if user provides text)

**This is a designed limitation, not a bug.**

---

## Notes for Users

1. **Free articles work best** - No login issues
2. **Copy-paste is your friend** - For paywalled content
3. **Quality improves with input** - Better articles = better notes
4. **Comparison reveals insights** - Similar articles show what's unique
5. **Use for learning** - Perfect for research and understanding topics
6. **Save the notes** - Useful for future reference

---

## Future Enhancements (Planned)

- [ ] Support for PDF articles (upload)
- [ ] Audio article transcription support
- [ ] Visual content extraction (images/charts)
- [ ] Multi-language article support
- [ ] Custom comparison criteria
- [ ] Export formats (PDF, Word, Markdown)
- [ ] Citation generation
- [ ] Topic trending analysis
