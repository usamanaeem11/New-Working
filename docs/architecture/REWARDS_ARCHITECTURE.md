# Reward System Architecture

## Overview

The reward system has TWO modes that coexist:

1. **MANUAL MODE**: Managers/admins manually award rewards
2. **AI MODE**: AI automatically suggests and optionally auto-awards rewards

## System Design

```
┌─────────────────────────────────────────────────────────┐
│              REWARD & GAMIFICATION ENGINE                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐        ┌──────────────────┐      │
│  │  MANUAL REWARDS  │        │   AI REWARDS     │      │
│  │                  │        │                  │      │
│  │ - Manager awards │        │ - Auto-detect    │      │
│  │ - Admin awards   │        │ - Auto-suggest   │      │
│  │ - Manual bonus   │        │ - Auto-award     │      │
│  │ - Custom badges  │        │ - ML predictions │      │
│  └──────────────────┘        └──────────────────┘      │
│           │                           │                 │
│           └───────────┬───────────────┘                 │
│                       ↓                                 │
│            ┌─────────────────────┐                      │
│            │  REWARD PROCESSOR   │                      │
│            │  - Validate         │                      │
│            │  - Calculate points │                      │
│            │  - Update balance   │                      │
│            │  - Notify user      │                      │
│            └─────────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

## Reward Types

1. **Badges** (Achievement-based)
   - First Timer, Team Player, Top Performer
   - Perfect Attendance, Early Bird, Night Owl
   - AI-suggested: Burnout Avoider, Focus Master

2. **Points** (Accumulated)
   - Task completion: +10-100 points
   - Goal achievement: +50-500 points
   - Milestone reached: +100-1000 points

3. **Bonuses** (Monetary)
   - Performance bonus: $100-$10,000
   - Project completion: $500-$5,000
   - AI-suggested: Efficiency bonus, Quality bonus

4. **Achievements**
   - Streaks (7-day, 30-day, 90-day)
   - Milestones (100 tasks, 1000 hours)
   - Special events (hackathon, launch)

## Integration Points

Every module has reward opportunities:
- ✅ Time Tracking → Punctuality rewards
- ✅ Task Completion → Achievement rewards
- ✅ Team Collaboration → Team player rewards
- ✅ Cognitive Health → Wellness rewards
- ✅ Performance Metrics → Excellence rewards

