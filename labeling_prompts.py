LABELS = {
    "Disruption": "HARM_MOD_ABUSE",
    "Asset Theft": "HARM_ASSET_THEFT",
    "Safety Evasion": "HARM_SAFETY_EVASION",
    "Private Info Access": "HARM_PRIVACY",
    "Mod Side-Effects": "HARM_USER_SECURITY",
    "AC Effective": "AC_POSITIVE",
    "AC Ineffective": "AC_NEGATIVE",
    "Limited Platform Coverage": "AC_CONCERN_PLATFORM_GAPS",
    "Performance Overhead": "AC_CONCERN_PERFORMANCE",
    "Loss of Useful Mods": "AC_CONCERN_ACCESSIBILITY_QOL_LOSS",
    "AC Privacy Concerns": "AC_CONCERN_PRIVACY",
    "AC Financial Motives": "AC_CONCERN_FINANCIAL",
    "User Recommendations": "AC_RECOMMENDATION",
}

RULE = "=" * 64

PREAMBLE = """You are a qualitative coder for a research project on social VR mods and anti-cheat systems.
You will decide whether ONE specific label applies to this Reddit post.

Apply the label ONLY when the text contains a clear claim, observation, opinion, or anecdote matching the definition. Do NOT extrapolate; if you have to stretch, the answer is false.
Default stance: FALSE. Only answer TRUE if the text unambiguously satisfies the definition.
"""

TIMELINE = """ANTI-CHEAT TIMELINE (applies to all AC_* labels):
- VRChat: Easy Anti-Cheat (EAC, kernel-level) deployed 2022-07-25. Before that, VRChat had NO anti-cheat.
- Rec Room: "Referee" (hybrid, not kernel-level) deployed 2024-12-19. Before that, Rec Room had NO proprietary anti-cheat.
Posts before deployment cannot describe anti-cheat in operation."""

INPUT_TEMPLATE = """================================================================
POST TO CLASSIFY
================================================================
Subreddit: r/{subreddit}
Date posted: {post_date}

Post text:
\"\"\"{post_text}\"\"\"
"""

OUTPUT_FORMAT = """Respond ONLY with a valid JSON object of this exact form:
{"present": true}
or
{"present": false}
"""

DEFINITIONS = {
    "HARM_MOD_ABUSE": {
        "summary": "Mods, modded clients, cheat tools, or exploits being used to DISRUPT, ATTACK, GRIEF, or CHEAT in social VR. Covers both disruption (crashing/griefing) and unfair gameplay (aimbot/speed hack/etc).",
        "apply": [
            "Named crash mechanisms — crasher avatars, particle bombs, shader crashes, audio/codec crashes, IK killers, RAM-drop, RPC/Udon-hook exploits, force teleports, portal hijacks, grief tools, lobby-wide crashing.",
            "First- or third-person crash stories — being crashed, witnessing someone crash a lobby, crasher groups active in public instances.",
            "Named gameplay cheats — aimbot, wallhack, flight, speed hack, noclip, invisibility, invincibility, item/currency spawning, rank/score manipulation, auto-fire, ESP, teleport cheats.",
            "Cheating in named PvP / combat contexts — paintball, dodgeball, laser tag, combat worlds, competitive events.",
            "Bypassing safety settings specifically to crash or grief.",
            "Item / object / currency spawners used to disrupt or cheat.",
            "Generic statements that hackers / cheaters / crashers are ruining the game or are active in the community.",
            "Modded clients enabling harassment or griefing against targeted users.",
            "DDoS / server attacks originating from modded clients.",
            "Victim-side hardware damage from a malicious exploit (GPU overheating, BSOD, bricked hardware caused by a crasher attack targeting the victim).",
            "Safety-settings discussions motivated by defending against crashers or cheaters.",
            "Acknowledgments that crashers / cheaters exist as an ongoing problem on the platform.",
        ],
        "do_not": [
            "The poster's own game crashing from bugs with no malicious actor.",
            "Bare 'hackers exist' with zero disruption or cheating context (no mechanism, no incident).",
            "Performance issues attributed to anti-cheat itself (AC_CONCERN_PERFORMANCE).",
            "'Hacker' meaning avatar ripper (HARM_ASSET_THEFT) or IP grabber / doxer (HARM_PRIVACY).",
            "Accessibility / QoL mods with no competitive edge or harm.",
            "Casual or joking misuse of 'hacker' (e.g. accusing children of hacking, using as a compliment).",
            "Complaining about OTHER PEOPLE falsely accusing users of being crashers / cheaters.",
        ],
    },
    "HARM_ASSET_THEFT": {
        "summary": "Avatar ripping, asset theft, model piracy, datamining, or content extraction from social VR.",
        "apply": [
            "Descriptions of ripping / force-cloning / extracting content, including general discussion of ripping as an activity.",
            "Datamining or extracting assets (models, textures, videos, sounds) from game files or memory.",
            "Named ripping tools or methods, even when mentioned in the context of another game.",
            "Piracy sites / Discord servers / channels that share ripped or stolen content.",
            "Creators losing work to rippers, including defensive behaviors (watermarking, hiding avatars, private uploads).",
            "Modded clients that clone, force-wear, or swap to someone else's private avatar.",
            "Discussion of whether anti-cheat does or doesn't stop ripping (either way).",
            "Incidental mentions — listing ripping as one of several ban reasons, or mentioning it in passing in a broader modding discussion.",
            "Blame or accusations calling someone a \"ripper\".",
        ],
        "do_not": [
            "Anti-cheat scanning the user's own files (that's AC behavior, not mod-enabled theft).",
            "Making your own ORIGINAL avatar with no ripping mention.",
            "General copyright / IP philosophy with no ripping or mod-theft angle.",
            "Reposting public or free avatars with the creator's permission.",
            "IP-grabbing, doxing, or stalking (that's HARM_PRIVACY).",
        ],
    },
    "HARM_PRIVACY": {
        "summary": "Privacy violations against OTHER users enabled by mods, modded clients, or cheating tools.",
        "apply": [
            "IP grabbing / IP logging of other users, or discussing the existence of IP-grabber tools.",
            "Doxing / stalking — publishing or threatening to publish other users' personal information.",
            "Modded clients that expose information users have hidden (friends list, world history, blocked status, private settings).",
            "Clients that impersonate or spoof another user's identity.",
            "Mods that bypass a target user's block or mute for privacy-violating purposes.",
            "HWID / user-ID reporting via a mod or SDK, collecting other users' device identifiers.",
            "Discussion of IP-ban or HWID-ban bypass mechanisms framed around other users' info.",
            "Force-kick or DDoS clients that abuse network-layer info about other users.",
        ],
        "do_not": [
            "Avatar ripping / asset theft (that's HARM_ASSET_THEFT).",
            "Privacy concerns about anti-cheat SOFTWARE itself (that's AC_CONCERN_PRIVACY).",
            "Generic non-mod harassment (e.g. roommate-was-rude complaints).",
            "Random mentions of 'privacy' unrelated to mods or clients.",
            "Account-hacking threats against the poster — that's HARM_USER_SECURITY.",
        ],
    },
    "HARM_SAFETY_EVASION": {
        "summary": "A SPECIFIC NAMED mechanism used to defeat the platform's account-level safety / moderation system (bans, blocks, mutes, kicks, invite-only rooms, vote-kicks, identity verification). Requires the mechanism to be explicitly described — not merely implied.",
        "apply": [
            "HWID / hardware-ID spoofing to defeat hardware bans (must mention HWID, hardware ID, or hardware spoof).",
            "Alt-account ban evasion — explicit mention of cycling through alt / burner / new accounts to defeat a ban.",
            "Clients that explicitly bypass blocks, mutes, or kicks (e.g. 'my mute doesn't work on them', 'they keep speaking even when muted', 'un-blockable client').",
            "Forced entry into private / invite-only rooms described as a bypass mechanism (not merely being uninvited).",
            "Admin-command exploits — unauthorized use of dev/admin permissions by non-admins to kick/ban/teleport.",
            "VPN use SPECIFICALLY to evade IP bans.",
            "Identity manipulation via exploit — name spoofing, impersonation through a client.",
            "Bots used for ban evasion — each bot account explicitly replacing a banned account.",
            "Explicit persistent re-entry — 'they keep coming back despite being kicked', 'kicked and instantly rejoined'.",
            "Report-system abuse — explicit mass-report or votekick-manipulation mechanism.",
            "Hackers described as 'un-kickable / un-bannable' due to elevated permissions or exploit immunity.",
        ],
        "do_not": [
            "General mic/chat spamming bots with no evasion mechanism (simple bot flooding → HARM_MOD_ABUSE).",
            "Bypassing ANTI-CHEAT SOFTWARE (that's AC_NEGATIVE).",
            "Modded clients used to crash/grief without any moderation-evasion mechanism (HARM_MOD_ABUSE alone).",
            "False-positive bans or association bans ('I got banned but I didn't cheat') — that's AC_NEGATIVE.",
            "Generic 'there are hackers / crashers / trolls' without a specific evasion mechanism.",
            "Statements that bad actors exist in every lobby without describing how they defeat moderation.",
            "Passing mentions of 'ban evaders' without describing HOW evasion works.",
            "Being permanently banned — being banned is not evasion; evasion is defeating a ban.",
            "Requests for help with hackers ('how do I prevent hackers?') without describing an evasion mechanism.",
        ],
    },
    "HARM_USER_SECURITY": {
        "summary": "Security risks to the user who INSTALLED a mod / modded client / cheat tool / unofficial content. Harm must be on the INSTALLER'S side.",
        "apply": [
            "Malware in mods / cheat tools / unofficial clients — trojans, RATs, keyloggers, botnets, coin-miners, malicious DLLs, token stealers, hidden payloads.",
            "Account or credential theft through installed mods.",
            "Hardware / system damage from running a cheat or modded client on your own machine (overheating, bricked GPU, corrupted Windows from a lag-switch or mod loader).",
            "Account-hacking threats tied to the poster's OWN mod/cheat tooling.",
            "AV detections of shady mod loaders, cheat tools, or unofficial game downloads.",
            "Shady distribution channels — piracy sites, unknown Discord repos, unofficial sources known to put users at risk.",
        ],
        "do_not": [
            "Generic 'malicious mods exist' framings with no installer-side harm specified.",
            "Mods harming OTHER users (→ HARM_ASSET_THEFT / HARM_PRIVACY / HARM_MOD_ABUSE).",
            "Having EAC prevents malicious mods from continuing — that's about AC, not installer-side.",
            "'Security of players' framing with no specific installer-side risk.",
            "Victim-side harm from crashers (broken GPU, BSOD caused by a crasher TARGETING the user) — that's HARM_MOD_ABUSE.",
            "Denials ('the viruses claim is not a fact').",
            "Anti-cheat kernel / privacy concerns about the AC itself (AC_CONCERN_PRIVACY).",
            "AV flagging the OFFICIAL game or EAC as a false positive — route to AC_NEGATIVE.",
        ],
    },
    "AC_POSITIVE": {
        "summary": "Anti-cheat is GOOD, EFFECTIVE, WORKING, BENEFICIAL, WELCOME, JUSTIFIED, or NECESSARY. Combines concrete effectiveness claims AND any supportive/defending stance toward AC.",
        "apply": [
            "Concrete effectiveness claims — crashers / hackers have become rare, bypasses patched quickly, AC catches tampered content.",
            "Active enforcement working — AC-driven bans of modders or cheaters as a positive outcome.",
            "Platform-side protections that work — server-side or API-level checks successfully rejecting tampered content.",
            "Counterfactual reasoning — worry or fear about what would happen if AC were removed.",
            "Comparative improvement — the platform is better than before AC, fewer disruption events.",
            "General approval / acceptance — 'this was needed', 'direction is right', 'it had to happen'.",
            "Pragmatic acceptance — acknowledging a rough rollout while affirming the underlying direction.",
            "Defense of AC against critics — rebutting anti-AC arguments, crediting the dev team.",
            "Rational justification of AC — 'AC is necessary because…', 'AC is the only way to…', 'better to have AC than not'.",
            "Posts that SUMMARIZE anti-AC complaints but then DISAGREE or provide counter-arguments — the disagreement part triggers AC_POSITIVE. Distinguishing rule: look at the poster's OWN stance, not the views they are describing. Quoting critics to argue against them qualifies.",
            "Posts that dismiss anti-AC sentiment (e.g., 'the outrage is overblown', 'the complaints are cynical', 'most reasonable people accept this') — the dismissal of criticism IS a defense of AC.",
            "Mentions that the no-EAC period was worse, that mods were being abused, or that something-had-to-be-done — these framings support AC's necessity.",
            "Acknowledgments that AC reduced a specific harm (fewer crashers, fewer rippers) counted even when followed by caveats.",
            "Neutral/balanced reasoning that explains AC's rationale WITHOUT expressing opposition — if there is no critical framing, and the post explains why AC makes sense, apply AC_POSITIVE.",
        ],
        "do_not": [
            "Posts whose entire stance is anti-AC.",
            "Sarcastic 'thanks EAC' that is actually complaining.",
            "Resigned blaming framings where AC happened because of external pressure (that's AC_NEGATIVE).",
            "Improvements attributed to safety settings / particle limiters / user toggles rather than AC.",
            "Mere mention of AC's existence without a positive stance.",
            "Polarity rule: if the post is ONLY negative about AC, answer FALSE. Mixed posts with any genuine positive stance (defense, justification, acknowledgment of improvement, dismissal of critics) qualify.",
        ],
    },
    "AC_NEGATIVE": {
        "summary": "ANY negative sentiment, complaint, criticism, or problem with anti-cheat. BROAD label covering: general opposition, limited effectiveness, usability problems (won't launch, BSOD, init errors, AV conflicts), and false positives.",
        "apply": [
            "General hostility or opposition — 'shouldn't have been added', 'reverse it', 'shouldn't need AC on a social platform'.",
            "Skepticism about AC necessity — questioning why the game needs AC.",
            "Sarcasm or snark aimed at AC.",
            "Resigned / blame-framed framings that AC happened because of external pressure (Epic, contracts, investors).",
            "AC is failing / ineffective — cheaters still everywhere, bypasses widely available, catches only casual modders.",
            "Ongoing harms despite AC — crashers still around, rippers still succeeding, malicious clients still exist.",
            "AC not addressing the real problem — crashing originates elsewhere, ripping doesn't require a client.",
            "Game won't function due to AC — crashes on launch, BSOD, stuck on loading, AV blocks AC, init errors, specific error codes.",
            "Tech-support issues caused by AC — firewall blocking EAC, AV conflicts, needing to clean/reinstall AC folders.",
            "False positives / wrongful punishment — banned without cheating, legitimate tools flagged, association bans.",
            "Explicit disappointment / abandonment — negative reviews, unsubscribing, quitting because of AC.",
            "Stacked complaints — post combines multiple AC problems.",
            "LEAN YES: any critical, frustrated, resigned, skeptical, disappointed, or sarcastic tone about anti-cheat qualifies.",
        ],
        "do_not": [
            "Purely factual / neutral AC discussion with no negative framing.",
            "Explicitly and wholly pro-AC posts.",
            "Posts about other topics that mention AC only in passing with no negative tone.",
            "Platform gaps alone (that's AC_CONCERN_PLATFORM_GAPS — but AC_NEGATIVE can CO-OCCUR with it).",
        ],
    },
    "AC_CONCERN_PLATFORM_GAPS": {
        "summary": "Discrepancies in AC enforcement or game availability across platforms.",
        "apply": [
            "Linux / Proton / Steam Deck compatibility issues tied to AC.",
            "Quest vs PC enforcement gaps — Quest users not subject to AC.",
            "Mobile / Android bypasses — different enforcement rules.",
            "VR vs Desktop mode differences in enforcement.",
            "Any inconsistent AC enforcement across platforms / OS.",
            "Can CO-OCCUR with AC_NEGATIVE when post also expresses general frustration.",
        ],
        "do_not": [
            "General AC complaints without platform comparison.",
            "Performance complaints on a specific OS without framing as a platform gap.",
        ],
    },
    "AC_CONCERN_PERFORMANCE": {
        "summary": "Performance degradation OR complete technical failure ATTRIBUTED TO anti-cheat, with a SPECIFIC named symptom. AC as a resource hog, OR AC preventing the game from launching/running. Requires evidence of a concrete technical problem, not mere dislike.",
        "apply": [
            "SPECIFIC FPS drops, stutter, lag, hitching attributed to AC — e.g., 'EAC cut my FPS in half', 'since EAC the game stutters', 'EAC causes lag spikes'.",
            "SPECIFIC CPU / memory / GPU overhead attributed to AC process.",
            "SPECIFIC launch failures — 'EAC won't start the game', 'stuck on EAC loading screen', 'game crashes 5 seconds after launch, suspect EAC'.",
            "SPECIFIC error codes / BSODs attributed to AC — 'EasyAntiCheat error code X', 'BSOD whenever EAC initializes', 'EAC.sys crash'.",
            "SPECIFIC AV / firewall / driver conflict with AC — 'my AV blocks EasyAntiCheat', 'firewall has to be disabled for EAC to run'.",
            "SPECIFIC OS / hardware incompatibility — 'EAC incompatible with my PC/Mac/Linux', 'AC doesn't work on my rig', 'EAC kicks me off consistently'.",
            "SPECIFIC post-AC regression tied to hardware — 'my CPU/GPU temps rose after EAC', 'stutter started after AC update'.",
            "Post references AC directly (EAC, Referee, 'anti-cheat', 'anticheat') AND names a specific technical symptom (crash / launch failure / performance hit / error / incompatibility).",
        ],
        "do_not": [
            "Lost performance MODS (FSR, resolution optimizers removed by AC) — that's AC_CONCERN_ACCESSIBILITY_QOL_LOSS.",
            "General 'AC is bad / AC ruins the game / I hate AC' without a named technical symptom — that's AC_NEGATIVE only.",
            "Tech-support replies to someone else's issue that explain how EAC works, without the poster themselves having the issue.",
            "Posts about game bugs that do NOT mention AC as the cause.",
            "Performance issues attributed to hardware, bugs, or content rather than AC.",
            "Cosmetic / UI changes related to the AC loading screen (that's not a technical impact).",
            "Generic 'AC has overhead / AC takes resources' with no specific symptom reported.",
        ],
    },
    "AC_CONCERN_ACCESSIBILITY_QOL_LOSS": {
        "summary": "Anti-cheat removed or restricts LEGITIMATE / QoL / ACCESSIBILITY mods.",
        "apply": [
            "Naming specific lost QoL / accessibility mods — resolution scaling, face tracking, eye tracking, haptics, OSC, TTS, captions, colorblind filters, avatar search, performance optimizers, anti-crasher mods.",
            "Arguing 'most mods were QoL / accessibility, not malicious' — defending the modding community's contributions.",
            "Claims that disabled players / accessibility users lost functionality.",
            "'The only thing AC affected are the useful / wholesome mods' framings.",
            "Lists of mod features that should be built into the game officially as replacements.",
            "Laments about specific lost convenience or features tied to mods.",
            "Post-deployment posts that defend modding's community value in the context of AC removing it.",
        ],
        "do_not": [
            "Generic 'AC is bad' without tying the harm to lost good mods.",
            "Performance complaints about AC itself (AC_CONCERN_PERFORMANCE).",
            "Pre-deployment posts discussing mods abstractly without an AC-loss framing.",
            "Posts that DISMISS the QoL defense as exaggerated (usually AC_POSITIVE).",
            "Wish-list suggestions for replacement features without a defense of modding or a claim of loss.",
        ],
    },
    "AC_CONCERN_PRIVACY": {
        "summary": "Privacy / surveillance / kernel-access concerns about the ANTI-CHEAT SOFTWARE itself.",
        "apply": [
            "Kernel-level / ring-0 / rootkit characterization of the AC.",
            "Discomfort with AC watching, recording, or transmitting user data (keystrokes, screen captures, file reads, process monitoring).",
            "'Spyware' comparisons aimed at the AC.",
            "Privilege-escalation / security-risk arguments — a kernel program could be exploited to harm the user.",
            "Distrust of what the AC collects or sends back.",
        ],
        "do_not": [
            "Malware from installing a MOD (HARM_USER_SECURITY).",
            "Mods grabbing OTHER users' info (HARM_PRIVACY).",
            "Mentions of AC existence without a privacy/surveillance framing.",
            "Generic platform-privacy concerns unconnected to anti-cheat software.",
            "'Rootkit protection' referring to an antivirus feature (that's a positive protection, not an AC concern).",
            "Broad 'any program could damage your PC' speculation.",
        ],
    },
    "AC_CONCERN_FINANCIAL": {
        "summary": "Anti-cheat decision attributed to MONEY / CORPORATE / BUSINESS motives. The financial framing must be connected to AC or enforcement — not generic platform pricing complaints.",
        "apply": [
            "Investor / shareholder appeasement — AC adopted to please funders, parent company, or external business pressure.",
            "Platform-monetization rationale explaining AC — revenue, paid features, or platform strategy as the reason AC exists or persists.",
            "Layoffs / firings tied to the AC situation — cost-cutting, reduced staff.",
            "Cash-grab or paywall framing tied specifically to AC or enforcement — removing mods to push paid subscriptions.",
            "Disrespecting user spending — users who invested in hardware / cosmetics being dismissed by AC decisions.",
            "PR / optics motive for AC — AC as marketing rather than security.",
            "Platform profiting from hackers — accusations the platform benefits from hackers (engagement, attention) and therefore doesn't fix them.",
        ],
        "do_not": [
            "Generic platform pricing / paywall complaints unconnected to AC or enforcement.",
            "Mentions of 'financial crisis' or 'layoffs' without tying them to AC motivation.",
            "Generic cash-grab complaints that don't involve AC.",
            "Standard PR / communication commentary about how to announce changes.",
            "Technical-debt or framework-refactor discussion without a financial motive stated.",
            "Neutral / curious questions about AC economics with no accusation or skeptical framing.",
        ],
    },
    "AC_RECOMMENDATION": {
        "summary": "A CONCRETE, SPECIFIC technical, architectural, or policy fix for anti-cheat or modding. Must point at a specific buildable / enactable mechanism — not a vague wish.",
        "apply": [
            "Named alternative anti-cheat products or systems proposed as replacements.",
            "Architectural mechanisms — server-side validation, netcode sanity checks, hash/integrity checks at launch, signed/encrypted uploads, an official modding API, mod allowlist / store tab, sandboxed mod loader, rate-limits, behavioral detection.",
            "Specific policy changes — age-gating the platform, making AC optional per private room / per lobby, whitelisting moderated avatars, launch-flag patterns borrowed from other games to toggle AC off.",
            "Specific design patches — server-side reject private avatars not uploaded by the wearer, build captions / colorblind filters / performance scaling as official in-game features, encrypt uploaded avatars, expose an AC API for world devs.",
            "Named workarounds proposed AS recommendations to the platform (not as individual player workarounds).",
            "Applies even when stated as a wish ('they should just X') if the mechanism is SPECIFIC and buildable.",
        ],
        "do_not": [
            "Vague wishes — 'fix it', 'do better', 'ban hackers', 'patch this', 'revert', 'rework moderation' without specifics.",
            "Tech-support instructions to other users ('verify files', 'reinstall', 'run as admin').",
            "Info pointers — 'join X discord for info'.",
            "References to the platform's existing roadmap without the poster proposing anything new.",
            "Pure complaints with no mechanism named.",
            "Player-level workarounds or tips — circuits to kick hackers, setting room level, safety settings, moving spawned items.",
            "Vague hypotheticals — 'they would need a mod framework' without a concrete proposal from the poster.",
            "Sarcastic rhetorical questions framed as complaints.",
            "'Make AC optional' on its own without more specifics.",
            "Informational statements about someone else's system without the poster recommending it to devs.",
        ],
    },
}


def build_prompt(label_id, subreddit, post_date, post_text, examples=""):
    """Exact deployed prompt for one (post, label) pair."""
    d = DEFINITIONS[label_id]
    block = [f"## {label_id}", d["summary"], "APPLY when:"]
    block += [f"  - {b}" for b in d["apply"]]
    block += ["DO NOT APPLY for:"]
    block += [f"  - {b}" for b in d["do_not"]]

    parts = [PREAMBLE]
    if label_id.startswith("AC_"):
        parts += [RULE, "ANTI-CHEAT TIMELINE", RULE, TIMELINE, ""]
    parts += [RULE, f"LABEL: {label_id}", RULE, "\n".join(block), "", examples]
    parts += [INPUT_TEMPLATE
              .replace("{subreddit}", str(subreddit))
              .replace("{post_date}", str(post_date))
              .replace("{post_text}", str(post_text)),
              OUTPUT_FORMAT]
    return "\n".join(parts)
