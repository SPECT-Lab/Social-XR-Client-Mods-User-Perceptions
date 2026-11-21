# Labeling Guide

This guide is the decision tree applied to every Reddit post during manual codebook development and adapted into the per-label LLM prompts. It is written so a human coder (or an LLM) can walk top-to-bottom and produce the same set of labels as in the paper.

A post can carry **any subset** of the 13 codebook labels — including zero. Most labeled posts carry one or two; four or more is rare and usually indicates over-application. **When in doubt, do NOT apply a label.**

---

## Section A | Relevance Screening (Applies to All Items)

**1. Is the text primarily about VRChat, Rec Room, or Social VR modding / anti-cheat?**

Examples include discussions of modded clients, mod menus, Easy Anti-Cheat, Referee, anti-cheat updates, cheating, ripping, crashers, or bans resulting from anti-cheat measures.

- **Yes:** Continue to the next question.
- **No:** Label as `OUT_OF_SCOPE` and move to the next item.

**2. Is the text semantically meaningful (i.e., contains an interpretable claim, opinion, observation, or anecdote)?**

- **Yes:** Continue.
- **No:** Label as `NON_SUBSTANTIVE` and move to the next item.

**3. Does the text contain at least one claim or opinion about either (a) mods / modded clients or (b) anti-cheat?**

- **Yes:** Continue.
- **No:** Label as `OUT_OF_SCOPE` and move to the next item.

---

## Section B | RQ1: Harms attributed to client modifications

Apply each question independently. A post can receive multiple RQ1 labels, none of them, or be flagged in Section A above.

**4. Does the text describe modded clients used to disrupt, attack, grief, or cheat — including instance crashes, particle / shader / IK crashers, lobby-wide crashing, lag-inducing object spam, forced teleportation, portal hijacks, named gameplay cheats (aimbot, wallhack, ESP, speed hack, item spawning), DDoS originating from a modded client, or victim-side hardware damage caused by a malicious exploit?**

- **Yes:** Label `Disruption` and continue.
- **No:** Continue.

**5. Does the text describe avatar ripping, world ripping, model piracy, datamining, or extraction of user-created content from social XR — including ripping tools, force-cloning a private avatar, piracy distribution channels, or creators losing work to rippers?**

- **Yes:** Label `Asset Theft` and continue.
- **No:** Continue.

**6. Does the text describe privacy violations against *other users* enabled by a modded client — including IP grabbing, doxing, modded-client exposure of hidden information (friend lists, blocked status, world history), HWID logging of others, identity spoofing, or stalking via forced entry into private instances?**

- **Yes:** Label `Private Info Access` and continue.
- **No:** Continue.

**7. Does the text describe a *specific named mechanism* used to defeat account-level safety controls — including HWID spoofing, alt-account ban evasion, un-blockable / un-mutable clients, forced entry into invite-only instances, admin-command exploits, VPN use to evade IP bans, or hackers described as "un-kickable / un-bannable" because of an exploit?**

- **Yes:** Label `Safety Evasion` and continue.
- **No:** Continue.

Tie-breakers for Q7. Generic "hackers exist" or "they keep coming back" *without a specific named evasion mechanism* does **not** apply this label. Bypassing **anti-cheat software** (rather than platform-level moderation) belongs to `AC Ineffective` instead.

**8. Does the text warn about security or privacy risks to the user *who installed the mod* — including malware, RATs, keyloggers, token stealers, account hijacks via mod loaders, hardware/system damage from running cheat tools, AV detections of mod loaders, or shady distribution channels (piracy sites, unknown Discord repos)?**

- **Yes:** Label `Mod Side-Effects` and continue.
- **No:** Continue.

Tie-breakers for Q8. Hardware damage **caused by a crasher attacking the user** is `Disruption`, not `Mod Side-Effects`. Privacy or kernel-access concerns about the **anti-cheat itself** are `AC Privacy Concerns`, not `Mod Side-Effects`.

(Proceed to Section C regardless of which RQ1 labels were applied.)

---

## Section C | RQ2: Perceptions of anti-cheat

Apply each question independently. A post can receive multiple RQ2 labels, none of them, or be flagged in Section A above.

Anti-cheat timeline gating. Posts dated before deployment cannot describe AC in operation:
  - VRChat: Easy Anti-Cheat (kernel-level) deployed 2022-07-25.
  - Rec Room: Referee (in-house, hybrid) deployed 2024-12-19, replacing the previously adopted EAC by 2025-05-29.

Pre-deployment posts that *anticipate* a future AC may still receive `AC Effective` or `AC Ineffective` based on the prospective stance.

**9. Does the text frame anti-cheat as good, effective, working, beneficial, justified, or necessary — including concrete claims that crashers / hackers became rare after deployment, defenses of AC against critics, dismissals of anti-AC sentiment, counterfactual reasoning ("imagine if there were no AC"), or rational justification of AC's existence?**

- **Yes:** Label `AC Effective` and continue.
- **No:** Continue.

**10. Does the text express *any* negative sentiment, complaint, criticism, or technical failure attributed to anti-cheat — including opposition to AC adoption, skepticism about AC necessity, claims that AC is bypassed / ineffective, false-positive bans, association bans, AC preventing the game from launching, AC causing tech-support issues (BSOD, AV conflicts, init errors), or sarcasm aimed at AC?**

- **Yes:** Label `AC Ineffective` and continue.
- **No:** Continue.

**11. Does the text raise privacy / surveillance / kernel-access concerns about the *anti-cheat software itself* — including kernel-level / ring-0 / rootkit characterizations, "spyware" comparisons, distrust of what the AC collects or sends back, privilege-escalation arguments, or discomfort with AC monitoring keystrokes / files / processes?**

- **Yes:** Label `AC Privacy Concerns` and continue.
- **No:** Continue.

Tie-breaker for Q11. Mods grabbing **other users'** info is `Private Info Access` (Q6), not `AC Privacy Concerns`. Malware from installing a mod is `Mod Side-Effects` (Q8).

**12. Does the text report a *specific named* performance regression or technical failure attributed to anti-cheat — including FPS drops / stutter / hitching tied to AC, CPU / memory / GPU overhead from the AC process, launch failures ("stuck on EAC loading screen"), specific BSOD or error codes attributed to AC, AV / firewall / driver conflicts with AC, or OS / hardware incompatibility with AC?**

- **Yes:** Label `Performance Overhead` and continue.
- **No:** Continue.

Tie-breaker for Q12. *Lost* performance mods (e.g., FSR, resolution optimizers banned by AC) belong to `Loss of Useful Mods` (Q13), not `Performance Overhead`. Generic "AC is bad / AC ruins the game" without a named technical symptom is `AC Ineffective` only.

**13. Does the text claim anti-cheat removed or restricts *legitimate / QoL / accessibility* mods — including specific named lost mods (face tracking, eye tracking, OSC, TTS, captions, colorblind filters, FSR / resolution scaling, anti-crasher mods, avatar search), claims that disabled players lost functionality, lists of mod features that should be built into the game officially, or arguments that "most mods were useful, not malicious"?**

- **Yes:** Label `Loss of Useful Mods` and continue.
- **No:** Continue.

**14. Does the text mention enforcement gaps across platforms — Linux / Proton / Steam Deck compatibility issues tied to AC, Quest vs. PC enforcement gaps, mobile / Android bypasses, VR vs. desktop differences, or any inconsistent AC enforcement across operating systems?**

- **Yes:** Label `Limited Platform Coverage` and continue.
- **No:** Continue.

**15. Does the text attribute the anti-cheat decision to corporate / business / financial motives — investor or shareholder appeasement, monetization rationale, paid-feature push, layoffs tied to the AC situation, PR / optics motive, or accusations the platform profits from hackers and therefore doesn't fix them?**

- **Yes:** Label `AC Financial Motives` and continue.
- **No:** Continue.

Tie-breaker for Q15. The financial framing must be tied to **AC or enforcement** specifically, not to generic platform pricing or paywall complaints.

**16. Does the text recommend a *concrete, specific* technical, architectural, or policy alternative for anti-cheat or modding — including server-side validation, integrity / hash checks at launch, signed or encrypted uploads, an official modding API, mod allowlist / store tab, sandboxed mod loader, named alternative AC products (BattlEye, etc.), age-gating, per-instance AC toggles, or other buildable mechanisms?**

- **Yes:** Label `User Recommendations` and continue.
- **No:** Continue.

Tie-breaker for Q16. Vague wishes ("fix it", "ban hackers", "do better"), tech-support tips to other users ("verify files", "reinstall"), and player-level workarounds (safety settings, instance level) do **not** apply this label — the recommendation must point at a buildable mechanism the *platform* could implement.

---

## Section D | Difficulty Flag (Quality Control)

**17. Was it difficult to answer any of the questions for this item due to ambiguity, sarcasm, lack of context, mixed meanings, or paraphrased quoting?**

- **Yes:** Label `HARD_TO_CLASSIFY` and move to the next item.
- **No:** Move to the next item.

`HARD_TO_CLASSIFY` is a quality-control flag, not a content label. It co-exists with whatever content labels were applied above and is used to triage borderline items for joint review.

---

## Coding Rules

- **Default stance is FALSE.** Every Yes / No question above has a strong default of *No*. Apply a label only when the text unambiguously satisfies the rule.
- **Code what the post says, not what the broader thread implies.** A crash incident in a parent comment does not transfer the `Disruption` label to a reply about EAC's performance.
- **Quotation does not count as endorsement.** A post that summarizes an anti-AC argument in order to disagree with it is `AC Effective`, not `AC Ineffective`.
