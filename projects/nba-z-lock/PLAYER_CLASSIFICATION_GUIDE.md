# Player Classification Guide: Star vs Key vs Role Players

## Quick Reference

When using the manual injury input, you need to classify players into categories. Here's how to identify them:

---

## 🌟 **STAR PLAYER** (1 per team)

### Characteristics:
- **Franchise cornerstone** - Team's best player
- **All-Star caliber** - Current or recent All-Star
- **High usage** - Typically 25%+ usage rate
- **Team leader** - Often the team's leading scorer
- **MVP candidate** - Top 10-15 player in the league
- **Media attention** - Household name, frequent coverage

### Examples (2024-25 Season):
- **Lakers**: LeBron James
- **Warriors**: Stephen Curry
- **Nuggets**: Nikola Jokić
- **Bucks**: Giannis Antetokounmpo
- **Celtics**: Jayson Tatum
- **Mavericks**: Luka Dončić

### How to Identify:
1. Check team's leading scorer (usually 20+ PPG)
2. Look for All-Star selections (current or recent)
3. Check usage rate (top player on team)
4. Media coverage (most talked about player)
5. Team's "go-to" player in clutch situations

### In the UI:
- **Star Player Available**: Set to "No" if this player is OUT
- Only ONE star player per team

---

## 🔑 **KEY PLAYERS** (Top 2-3 after star)

### Characteristics:
- **Starter or 6th man** - Regular rotation player
- **Important role** - Significant impact on team success
- **15-20+ minutes per game** - Regular playing time
- **Starter** - Usually in starting lineup
- **Impact metrics** - High +/- or win shares
- **Team's 2nd/3rd best player** - After the star

### Examples (2024-25 Season):
- **Lakers**: Anthony Davis, D'Angelo Russell
- **Warriors**: Klay Thompson, Draymond Green
- **Nuggets**: Jamal Murray, Aaron Gordon
- **Bucks**: Damian Lillard, Khris Middleton
- **Celtics**: Jaylen Brown, Kristaps Porziņģis

### How to Identify:
1. **Starting lineup** - Usually 4 of 5 starters (excluding star)
2. **Minutes per game** - Top 5-6 players by minutes
3. **Scoring** - 2nd/3rd leading scorers
4. **Impact** - Players whose absence significantly hurts team
5. **Role importance** - Primary ball handler, rim protector, 3-point specialist

### In the UI:
- **Key Players Available**: Count how many of these are OUT
- Range: 0-3 (usually 2-3 key players per team)
- If 2 key players are out, set to "1" (3 total - 2 out = 1 available)

---

## 👥 **ROLE PLAYERS** (Not counted in injury system)

### Characteristics:
- **Bench players** - 7th-15th man
- **Limited minutes** - Under 15-20 MPG
- **Specialist** - One-dimensional role (3-point shooter, defender)
- **Replaceable** - Team has depth at their position
- **Low usage** - Under 15% usage rate

### Examples:
- Backup point guards
- 3-and-D specialists
- Reserve big men
- End-of-bench players

### In the UI:
- **Not counted** - These don't affect the injury inputs
- Only star + key players matter for predictions

---

## 📊 **Classification Methods**

### Method 1: Check NBA Stats (Recommended)

**Best Resources:**
- **NBA.com** - Official stats, team pages
- **ESPN.com** - Player stats, team rosters
- **Basketball-Reference.com** - Advanced stats, usage rates

**What to Look For:**
1. **Points Per Game (PPG)**
   - Star: 20+ PPG
   - Key: 12-20 PPG
   - Role: Under 12 PPG

2. **Minutes Per Game (MPG)**
   - Star: 30+ MPG
   - Key: 20-30 MPG
   - Role: Under 20 MPG

3. **Usage Rate**
   - Star: 25%+
   - Key: 18-25%
   - Role: Under 18%

4. **Starting Status**
   - Star: Always starter
   - Key: Usually starter or 6th man
   - Role: Bench player

### Method 2: Team Depth Chart

**Check Team's Official Depth Chart:**
1. **Starting 5** = Star (1) + Key Players (usually 2-3)
2. **6th Man** = Often a key player
3. **Bench** = Role players

**Example Depth Chart:**
```
Lakers (2024-25):
PG: D'Angelo Russell (Key)
SG: Austin Reaves (Key)
SF: LeBron James (STAR) ⭐
PF: Rui Hachimura (Key)
C:  Anthony Davis (Key)
6th: Gabe Vincent (Role)
```

### Method 3: Injury Impact Assessment

**Ask yourself:**
- "If this player is out, does it significantly hurt the team?"
- **Star**: Team struggles to win without them
- **Key**: Noticeable drop in team performance
- **Role**: Minimal impact, team has depth

### Method 4: Media & Expert Analysis

**Sources:**
- **Team beat reporters** - Know team's hierarchy
- **NBA analysts** - Identify key contributors
- **Fantasy basketball rankings** - Reflects player importance
- **Team Twitter/announcements** - Official injury reports

---

## 🎯 **Practical Examples**

### Example 1: Lakers vs Warriors

**Lakers:**
- **Star**: LeBron James
- **Key Players**: Anthony Davis, D'Angelo Russell, Austin Reaves
- **Injury Status**: LeBron OUT, AD OUT, Russell OUT
  - Star Player Available: **No**
  - Key Players Available: **1** (Reaves still available)

**Warriors:**
- **Star**: Stephen Curry
- **Key Players**: Klay Thompson, Draymond Green, Andrew Wiggins
- **Injury Status**: All healthy
  - Star Player Available: **Yes**
  - Key Players Available: **3**

### Example 2: Nuggets vs Celtics

**Nuggets:**
- **Star**: Nikola Jokić
- **Key Players**: Jamal Murray, Aaron Gordon, Michael Porter Jr.
- **Injury Status**: Jokić OUT, Murray OUT
  - Star Player Available: **No**
  - Key Players Available: **2** (Gordon + Porter available)

**Celtics:**
- **Star**: Jayson Tatum
- **Key Players**: Jaylen Brown, Kristaps Porziņģis, Derrick White
- **Injury Status**: All healthy
  - Star Player Available: **Yes**
  - Key Players Available: **3**

---

## ⚠️ **Common Mistakes to Avoid**

1. **Counting too many key players**
   - Only count top 2-3 after the star
   - Not every starter is a "key player"

2. **Confusing star with key**
   - Star = 1 player (the best)
   - Key = 2-3 players (next most important)

3. **Including role players**
   - Bench players don't count
   - Only star + key players matter

4. **Not updating regularly**
   - Player importance changes with trades/injuries
   - Check current season, not last season

---

## 🔍 **Quick Identification Checklist**

Before setting injuries, ask:

1. **Who is the team's best player?** → Star Player
2. **Who are the 2-3 most important players after the star?** → Key Players
3. **Are any of these players injured?**
   - Star out? → Set "Star Player Available" to "No"
   - Key players out? → Count how many key players remain (0-3)

---

## 📱 **Helpful Resources**

### Official NBA Sources:
- **NBA.com/teams** - Team rosters and stats
- **NBA.com/injury-report** - Official injury reports
- **Team websites** - Official depth charts

### Stats & Analysis:
- **Basketball-Reference.com** - Comprehensive stats
- **ESPN.com/nba** - Player stats and analysis
- **NBA.com/stats** - Advanced metrics

### Injury Reports:
- **ESPN Injury Report** - Daily updates
- **Rotowire.com** - Fantasy injury updates
- **Team Twitter accounts** - Official announcements

---

## 💡 **Pro Tips**

1. **Start with the star** - Always identify the star player first
2. **Check recent games** - See who's actually playing
3. **Use depth charts** - Official team depth charts are most accurate
4. **Consider context** - A "key player" on a bad team might be a "role player" on a good team
5. **Update daily** - Injury status changes frequently

---

## 🎮 **Using in the Tool**

1. **Before prediction**: Check injury reports for both teams
2. **Identify star players**: One per team
3. **Count key players**: Top 2-3 after star
4. **Set injuries**: Adjust UI inputs accordingly
5. **Get prediction**: Tool uses your injury data for more accurate predictions

---

**Remember**: The more accurate your injury classification, the better your predictions will be!

