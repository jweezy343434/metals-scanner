# AI Customization Guide for Non-Technical Users

> **Use Claude or other AI assistants to customize this tool without coding knowledge!**

This guide is for people who want to modify the Metals Arbitrage Scanner but don't have programming experience. You can use AI tools like Claude Code, ChatGPT, or GitHub Copilot to make changes by describing what you want in plain English.

## Table of Contents

1. [What You Can Customize](#what-you-can-customize)
2. [Using Claude Code](#using-claude-code)
3. [Example Prompts for Common Changes](#example-prompts-for-common-changes)
4. [Step-by-Step Modification Guide](#step-by-step-modification-guide)
5. [Best Practices](#best-practices)
6. [Troubleshooting AI Interactions](#troubleshooting-ai-interactions)
7. [Safety Tips](#safety-tips)

## What You Can Customize

You can ask AI to help you:

✅ **Change appearance**
- Colors, fonts, layout
- Add/remove dashboard elements
- Reorganize information

✅ **Add features**
- New metal types (platinum, palladium)
- Email/SMS notifications
- Price alerts
- Historical charts

✅ **Modify behavior**
- Scan frequency
- Filter defaults
- Price calculation logic

✅ **Add data sources**
- Amazon, Craigslist, Facebook Marketplace
- Local coin dealers
- Other marketplaces

✅ **Improve filtering**
- Add weight filters
- Seller rating requirements
- Geographic filters

❌ **What requires more work**
- Completely changing databases (SQLite → PostgreSQL)
- Adding authentication systems
- Mobile app development
- Major architectural changes

## Using Claude Code

### What is Claude Code?

Claude Code is an AI assistant that can read, write, and modify code directly in your project. It's like having an expert developer helping you.

### How to Access Claude Code

**Option 1: Command Line (Recommended)**
```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Navigate to your project
cd /root/metals-scanner

# Start Claude Code
claude-code
```

**Option 2: VS Code Extension**
1. Install VS Code
2. Search for "Claude Code" in extensions
3. Install and authenticate
4. Open your metals-scanner folder

**Option 3: Web Interface**
- Visit [claude.ai](https://claude.ai)
- Share your code files
- Ask for modifications
- Copy changes back to your files

### How Claude Code Works

1. **You describe** what you want in plain English
2. **Claude reads** your existing code
3. **Claude makes changes** to the appropriate files
4. **You review** the changes
5. **You test** to make sure it works

## Example Prompts for Common Changes

### Changing Colors

**Prompt:**
```
Change the dashboard header color from blue to dark green.
Also change the "Scan Now" button to match the new green theme.
```

**What Claude will do:**
- Read `app/static/index.html`
- Find the color classes
- Replace blue with green
- Show you exactly what changed

### Adding Email Notifications

**Prompt:**
```
Add email notifications when a deal is found with more than 10% profit margin.
Use Gmail SMTP. Ask me for my email address and app password, and
add them to the .env file configuration.
```

**What Claude will do:**
- Create a notification system
- Add email configuration to `.env.example`
- Integrate with the scanning process
- Provide setup instructions

### Adding a New Metal Type

**Prompt:**
```
Add support for platinum bullion. I want to:
1. Scrape eBay for platinum listings
2. Show platinum spot prices in the dashboard header
3. Add platinum to the metal type filter dropdown
4. Use purple color for platinum badges in the table
```

**What Claude will do:**
- Update the database schema
- Add platinum to eBay searches
- Fetch platinum prices (XPT symbol)
- Update dashboard HTML and JavaScript
- List all files that were changed

### Changing Scan Frequency

**Prompt:**
```
I want to scan eBay every 4 hours instead of every 2 hours.
Also, I want to run a scan automatically when the application starts.
```

**What Claude will do:**
- Update configuration
- Modify scheduler settings
- Add startup scan logic
- Explain the changes

### Adding More Search Terms

**Prompt:**
```
Add these eBay search terms:
- "gold maple leaf"
- "silver eagle proof"
- "gold krugerrand"
- "silver britannia"

I want more variety in my search results.
```

**What Claude will do:**
- Find the search terms list
- Add new terms
- Show updated code

### Customizing the Table

**Prompt:**
```
In the listings table, I want to:
1. Add a column showing seller rating
2. Hide listings from sellers with less than 98% positive feedback
3. Add a "Shipping Cost" column (even if it says "Unknown" for now)
4. Make the table rows alternate between white and light gray
```

**What Claude will do:**
- Update table HTML
- Modify data fetching
- Add filtering logic
- Style the table

### Adding Price Alerts

**Prompt:**
```
Create a price alert system where I can set target margins for each metal.
For example:
- Alert me when gold deals exceed 8% margin
- Alert me when silver deals exceed 5% margin

Show the alerts as a notification banner at the top of the dashboard.
```

**What Claude will do:**
- Create alert configuration
- Add notification system
- Update dashboard UI
- Store alert settings

## Step-by-Step Modification Guide

### Example: Adding a "Favorites" Feature

Let's walk through adding a feature to save favorite listings.

#### Step 1: Describe Your Goal

**Your prompt:**
```
I want to add a "favorites" feature to the scanner. Here's what I need:

1. Add a ⭐ button next to each listing in the table
2. When clicked, save that listing as a favorite
3. Add a "Show Favorites Only" checkbox filter
4. Store favorites in the database so they persist between scans
5. Show favorite listings with a gold star next to the title

Can you implement this feature?
```

#### Step 2: Claude's Response

Claude will typically respond with:
- Overview of changes needed
- List of files to be modified
- Any questions for clarification

**Claude might ask:**
```
I can implement this feature. A few questions:

1. Should favorites persist forever, or expire after X days?
2. Do you want to be able to remove items from favorites?
3. Should we track how many times you've favorited an item?

I'll assume:
- Favorites persist forever (you can delete them manually)
- You can unfavorite by clicking the star again
- We'll add an "unfavorite" action

Should I proceed with these assumptions?
```

#### Step 3: Confirm or Clarify

**Your response:**
```
Yes, proceed with those assumptions. Also add a "Clear All Favorites"
button in the filters section.
```

#### Step 4: Claude Makes Changes

Claude will:
1. Update `app/database.py` - Add favorites table
2. Update `app/main.py` - Add API endpoints
3. Update `app/static/index.html` - Add UI elements

#### Step 5: Review Changes

Claude will show you:
```
I've made the following changes:

📝 app/database.py
   - Added Favorite table with listing_id and created_at
   - Added index for faster lookups

📝 app/main.py
   - Added POST /api/favorites endpoint
   - Added DELETE /api/favorites/<id> endpoint
   - Added GET /api/favorites endpoint

📝 app/static/index.html
   - Added star button to each row
   - Added "Show Favorites Only" checkbox
   - Added "Clear All Favorites" button
   - Added JavaScript functions for favorite management

To test:
1. Restart the application: docker-compose restart
2. Open dashboard
3. Click star icons to save favorites
4. Enable "Show Favorites Only" to filter
```

#### Step 6: Test

Test the new feature:
```bash
# Restart app
docker-compose restart

# Open browser
http://localhost:8000

# Try:
- Click star icons
- Toggle favorites filter
- Refresh page (favorites should persist)
- Clear all favorites
```

#### Step 7: Ask for Refinements

If something isn't quite right:
```
The favorites feature works great! Can you make these improvements:
1. Make the star turn gold when favorited (currently it's gray)
2. Add a count showing how many favorites I have
3. Sort favorites to the top when "Show Favorites Only" is unchecked
```

Claude will make incremental improvements.

## Best Practices

### 1. Be Specific

❌ **Vague:**
```
Make the dashboard look better
```

✅ **Specific:**
```
Change the dashboard header to use a gradient from navy blue to
dark purple. Increase the font size of spot prices to 40px.
Add rounded corners to all cards.
```

### 2. One Change at a Time

❌ **Too Much:**
```
Add platinum support, change colors, add notifications,
fix the sorting bug, add user authentication, and create
a mobile app.
```

✅ **Focused:**
```
Add platinum support with the following features:
- eBay scraping for "platinum bullion"
- Spot price fetching (XPT symbol)
- Dashboard display with purple color
```

### 3. Provide Context

❌ **No Context:**
```
Add a filter
```

✅ **With Context:**
```
Add a minimum weight filter to the dashboard. I want to filter out
listings below 0.5 oz because small fractional coins have high
premiums. Add this as a slider next to the margin filter.
```

### 4. Specify Testing Steps

✅ **Include Test Plan:**
```
Add email notifications for deals above 10% margin.

After implementing, tell me how to test it. I want to verify:
1. Emails are sent when deals are found
2. Emails aren't sent for deals below 10%
3. I don't get duplicate emails for the same listing
```

### 5. Ask for Explanations

✅ **Request Learning:**
```
Add a "last updated" timestamp to each listing.

Also, can you explain how the timestamp is generated and
where it's stored in the database? I want to understand
the code structure.
```

## Troubleshooting AI Interactions

### Issue: AI Doesn't Understand

**Symptom:** Claude asks too many questions or seems confused

**Solution:** Provide more context
```
Let me clarify my project structure:
- This is a Python FastAPI application
- The frontend is in app/static/index.html (no React/Vue)
- Database is SQLite
- I'm using Docker for deployment

Now, can you help me add [your feature]?
```

### Issue: Changes Break the App

**Symptom:** After AI modifications, app won't start

**Solution:** Ask AI to diagnose
```
After making the changes you suggested, I'm getting this error:
[paste error message here]

Can you help me fix this? If needed, you can revert your changes.
```

### Issue: AI Makes Too Many Changes

**Symptom:** AI modified files you didn't want changed

**Solution:** Be more specific next time
```
Only modify the dashboard HTML file (app/static/index.html).
Don't change any Python backend files or database schema.
```

### Issue: Testing Is Unclear

**Symptom:** You don't know how to verify the changes work

**Solution:** Ask for step-by-step testing
```
I don't know how to test this feature. Can you provide:
1. Exact commands to run
2. What to look for in the logs
3. What to see in the dashboard
4. How to verify it worked correctly
```

### Issue: Feature Partially Works

**Symptom:** Some parts work, others don't

**Solution:** Be specific about what's broken
```
The feature is partially working. Here's what I see:
✅ The star icons appear next to listings
✅ I can click them
❌ When I refresh the page, favorites disappear
❌ The favorites counter shows "0" even after adding favorites

Can you fix the persistence and counter issues?
```

## Advanced Prompting Techniques

### Incremental Development

Build features in stages:

**Stage 1:**
```
First, add basic email notification support. Just send a test
email when I click a "Test Email" button in the dashboard.
Don't integrate with deals yet.
```

**Stage 2:**
```
Now integrate the email system with the deal scanning. Send
an email when any deal is found (no threshold yet).
```

**Stage 3:**
```
Add configurable threshold. Let me set the minimum margin %
in the .env file.
```

### Request Alternatives

Ask for options:
```
I want to add price alerts. Can you suggest 3 different approaches:
1. Browser notifications
2. Email alerts
3. SMS via Twilio

Explain pros/cons of each. Then implement the one you think
is best for a beginner.
```

### Ask for Code Review

Before major changes:
```
Before implementing this feature, can you:
1. Review my current code structure
2. Identify potential problems with my idea
3. Suggest the best approach
4. Estimate how difficult this will be

Then if it seems reasonable, go ahead and implement it.
```

### Reference Examples

Use this repository as reference:
```
I want to add a new scraper for Amazon. Can you follow the
same pattern used in app/scrapers/ebay.py? Keep the same
structure and error handling approach.
```

## Safety Tips

### 1. Backup Before Big Changes

```bash
# Backup database
cp data/metals_scanner.db data/backup_$(date +%Y%m%d).db

# Backup entire project
cd ..
tar -czf metals-scanner-backup.tar.gz metals-scanner/
```

### 2. Test in Isolation

When adding risky features:
```
Create this feature as a separate test script first
(test_notifications.py) so I can test it without affecting
the main application.
```

### 3. Understand Before Applying

```
Before making the changes, explain what each modification does
and why it's necessary. I want to understand what's changing.
```

### 4. Keep Versions

Use git to track changes:
```bash
# Before AI changes
git add .
git commit -m "Before adding platinum support"

# After AI changes and testing
git add .
git commit -m "Added platinum support - working"
```

### 5. API Key Security

Never share API keys with AI:
```
Add email configuration to .env, but use placeholder values
like "your_email_here". I'll fill in the real values myself.
```

## Example Conversation

Here's a complete example of customizing the scanner:

**You:**
```
I want to add support for Canadian gold maple leaf coins specifically.
I notice they often have good deals on eBay. Can you:

1. Add "gold maple leaf" as a search term
2. Create a special badge or highlight for maple leaf listings
3. Add a filter checkbox called "Maple Leaf Only"

Keep it simple - this is my first customization.
```

**Claude:**
```
I'll help you add Canadian gold maple leaf support. This is a
great first customization! Here's what I'll do:

1. Add search term to eBay scraper
2. Detect "maple leaf" in titles and add a flag
3. Add visual indicator (🍁 emoji) next to maple leaf listings
4. Add filter checkbox

This will modify 2 files:
- app/scrapers/ebay.py (add search term and detection)
- app/static/index.html (add UI elements)

Should I proceed?
```

**You:**
```
Yes, sounds perfect!
```

**Claude:**
```
Done! I've made the following changes:

📝 app/scrapers/ebay.py (lines 45-52)
   Added "gold maple leaf" to search terms
   Added detection logic to flag maple leaf listings

📝 app/static/index.html (lines 128-133, 295-298, 418-420)
   Added "Maple Leaf Only" checkbox
   Added 🍁 emoji to table rows for maple leaf coins
   Added filter logic

To use:
1. Restart: docker-compose restart
2. Click "Scan Now"
3. Look for 🍁 next to maple leaf listings
4. Try the "Maple Leaf Only" checkbox filter

Let me know if you want any adjustments!
```

**You:**
```
Perfect! It works. Can you also make the 🍁 emoji bigger and
add a golden glow effect around it?
```

**Claude:**
```
Sure! I'll increase the emoji size to 24px and add a subtle
golden glow using CSS text-shadow.

[Makes changes]

Done! Refresh your browser to see the larger, glowing maple leaf.
```

## Resources

### Learning More

- **Claude AI:** [claude.ai](https://claude.ai)
- **FastAPI Docs:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **Tailwind CSS:** [tailwindcss.com](https://tailwindcss.com/)
- **SQLite Tutorial:** [sqlitetutorial.net](https://sqlitetutorial.net/)

### Getting Help

1. **Documentation**
   - Read [README.md](README.md) for project overview
   - Check [CONTRIBUTING.md](CONTRIBUTING.md) for code structure

2. **AI Assistants**
   - **Claude Code:** Best for this project (it built this!)
   - **ChatGPT:** Good for general questions
   - **GitHub Copilot:** Good for inline code suggestions

3. **Community**
   - GitHub Issues for bugs
   - Discussions for feature ideas

## Conclusion

With AI assistance, you can customize this scanner without being a programmer. The key is:

1. **Be specific** about what you want
2. **Test incrementally** after each change
3. **Ask questions** when unsure
4. **Back up** before major changes
5. **Learn gradually** by asking AI to explain

Start with small changes (colors, filters) and work up to bigger features (new sources, notifications). You'll be surprised how much you can accomplish!

---

**Happy customizing! 🚀**
