# How This Project Works (No Tech Background Needed)

This document explains the project in plain language — no code, no
jargon. If you can use a smartphone, you can follow this.

## The problem this solves

Everyone applying for tech internships checks the same handful of famous
companies — Google, Meta, Amazon, Microsoft. Those get thousands of
applicants per opening. But tons of other well-known companies you'd
never think of as "tech" — Target, John Deere, Garmin, Honeywell,
Lockheed Martin, Home Depot — also hire software/data/engineering
interns, with way less competition, because most students never think to
look.

This project is a personal assistant that watches those companies'
career pages for you, all day, every day, and texts you the moment a new
internship shows up that matches what you're looking for.

## The three pieces, in plain terms

**1. A list of companies to watch.** There's a spreadsheet-like file
listing 65 companies — the "hidden gems." For each one, it also notes
*how* to check that company's job listings (more on that below).

**2. A robot that checks the list.** On a schedule, a program visits
each company's career website, reads the job postings, and asks: "Is
this a new internship I haven't seen before? Does it match what the
user is interested in (software engineering, machine learning, embedded
systems, etc.)?" If yes to both, it saves the internship and flags it as
something to alert about.

**3. A text message.** When something new and relevant is found, the
program sends a text message straight to your phone with the company,
job title, location, and a link to apply. If several new ones show up
in the same check, you get one text listing all of them — not a flood
of separate messages.

## How it actually "reads" a company's job page

This is the trickiest part, and it works a few different ways depending
on the company:

- **Some companies have a clean, structured way to ask "what internships
  do you have right now?"** — like a librarian's catalog system instead
  of just a wall of books. For those (7 of the 65 companies so far,
  including Hudl, Garmin, Honeywell, and Lockheed Martin), the program
  asks directly and gets a precise, reliable answer.
- **Most companies don't have that**, so the program instead opens their
  website the way a person would (using a real, automated web browser
  running in the background), looks at the page, searches for the word
  "intern" in job titles, and ignores anything that's clearly not a real
  individual job posting (like a generic "Careers" link). This works for
  most of them, but not all — some companies' websites are built in ways
  that resist this kind of automated checking. It's expanding company by
  company as more get investigated.

## Does this run on my computer?

No — that's the important part. It runs automatically in the cloud
(specifically, on GitHub's servers, since this project's code lives on
GitHub), on a timer:

- Every **15 minutes**, it does a *quick* check of the companies with
  the clean, reliable system (piece 1 above).
- Every **2 hours**, it does a *full* check of all 65 companies,
  including the slower "read the page like a human" ones.

Your computer doesn't need to be on. Your phone doesn't need an app
open. It just happens, and a text arrives when something's found.

## What happens to duplicate postings?

Nothing — that's the point. Every internship the program has already
seen is remembered (in a small database file that lives alongside the
code). If the same posting shows up again on the next check, it's
recognized as "already seen" and gets silently skipped. You only get
texted about things that are genuinely new since the last time it
looked.

## What information does it use about me?

Just your declared interests (which categories of internship you care
about) and your phone number/email (so it knows where to send alerts).
It doesn't read your messages, browse on your behalf beyond checking
public job listing pages, or share anything with the companies it
checks.

## Is this "AI"?

Not in the way people usually mean that today. The day-to-day running
program doesn't use ChatGPT-style AI to "think" about each job posting —
it uses straightforward, predictable rules (word matching, simple
if/then logic) to decide what counts as a new internship and whether it
matches your interests. It's automation, not artificial intelligence,
once it's up and running.

(An AI assistant — Claude, from Anthropic — was used to *build* this
project: writing the code, investigating each company's website,
setting up the automatic schedule, and fixing bugs. But that's a
separate thing from the running program itself, which is just regular
software doing regular, repeatable tasks on a timer.)
