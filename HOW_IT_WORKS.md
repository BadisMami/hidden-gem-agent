What this is

Most internship trackers on GitHub just list openings at the usual FAANG+ companies. This one is different: it's a curated list of 65 companies chosen around my interests (embedded systems, ML, software/aerospace engineering). Some are the expected defense/aerospace names — Honeywell, Garmin, Lockheed Martin. Others are companies you'd never guess run tech internship programs at all — Target, Chipotle, Alo, Progressive.

A bot checks all 65 automatically and texts me when something new and relevant posts - only SWE, ML, embedded, and robotics roles, and never PhD/Master's-only ones.

How it works

A scheduled program visits each company's career page and checks for new internship postings that match my interests. Some companies (7 so far, including Hudl, Garmin, Honeywell, Lockheed Martin) have a structured API-style feed, so those checks are precise. The rest get checked with an automated browser that scans listings for the word "intern" — works most of the time, still expanding coverage company by company.

It runs on GitHub's servers, not my computer:

Every 4 hours: full check of all 65
Texts only go out 8am-10pm Eastern; anything found overnight is sent with the first check after 8am

Already-seen postings are tracked in a small database, so I only get texted about genuinely new ones. If multiple show up at once, they're bundled into a single text with company, title, location, and a link.
