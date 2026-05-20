#!/usr/bin/env python3
"""
Lokalnie generuje brakujące opisy produktów na podstawie szablonów.
Naprawia też opisy które zawierają nagłówek promptu.
"""
import json, os, random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "products_seed.json")

random.seed(42)

# --- szablony opisów garmentu wg typu produktu ---
GARMENT_TEMPLATES = {
    "Jersey": [
        "Crafted from moisture-wicking pro-mesh fabric with double-sewn tackle-twill numbers, this {edition} jersey captures every stitch of authenticity from the era. The breathable construction keeps you cool while the boldly embroidered {player} name across the back commands attention in any crowd.",
        "Premium polyester-blend fabric meets old-school tailoring in this stunning {edition} jersey. The sweat-resistant mesh panels, reinforced collar and authentic number font make this a must-have statement piece worthy of a championship display case.",
        "Built with the same lightweight performance fabric worn under the arena lights, this {edition} jersey features UV-resistant ink, satin-finished lettering and a relaxed athletic cut. Wear it courtside or frame it — either way, it turns heads.",
        "Woven from ultra-soft yet durable champion-grade fabrics, this {edition} jersey is a love letter to the golden age of basketball. The vibrant colorway mirrors the original uniform palette worn on the hardwood, down to the last pantone shade.",
        "Street-ready and arena-quality at once, this {edition} jersey blends throwback aesthetics with modern performance weaves. Reinforced stitching on the side seams ensures this piece outlasts every buzzer beater you watch in it.",
    ],
    "Shorts": [
        "These {edition} shorts feature an elastic waistband, deep side pockets and a satin-feel polyester lining that breathes as hard as a fourth-quarter sprint. The authentic team colorway and embroidered logo complete the retro-revival look.",
        "Cut wide in the old-school tradition, these {edition} shorts sit at the knee with a relaxed fit that echoes the silhouettes of the '90s golden era. Tag-free inner waistband and UV-stable team colors make them the definitive fan staple.",
        "Performance meets nostalgia in these {edition} shorts — engineered with quick-dry fabric and a drawstring inner panel so they move with you. The bold side stripe and embossed team crest are faithful recreations pulled from archival photographs.",
    ],
    "Hoodie": [
        "This heavyweight {edition} hoodie wraps you in 380gsm brushed fleece that feels like a championship bear hug. The kangaroo pocket, ribbed cuffs and embroidered chest logo carry the weight of a dynasty.",
        "Oversized and ultra-plush, this {edition} hoodie is woven from premium cotton-polyester fleece with a soft-wash finish. A tonal drawstring, dropped shoulders and heat-pressed vintage graphic give it that authentic collector energy.",
        "Cold-arena approved and street-legendary, this {edition} hoodie features a vaulted arch graphic on the back, satin-lined hood and chunky metal zipper pull. Limited fan-edition numbering on the interior label makes each one unique.",
    ],
    "T-Shirt": [
        "Ring-spun cotton at 200gsm keeps this {edition} tee whisper-soft yet built to last. The distressed screen-print graphic fades like a memory of a perfect game, which is exactly the point.",
        "This {edition} tee is cut in a boxy athletic silhouette with pre-shrunk jersey fabric and a vintage plastisol print that won't crack after a hundred washes. Simple. Iconic. Non-negotiable.",
        "Drop the jersey, grab this {edition} graphic tee for an off-duty fan flex. Reactive-dyed for a lived-in palette, the oversized photographic chest print captures the raw energy of peak-era basketball.",
    ],
    "Snapback": [
        "Six-panel structured crown, flat peak and a woven team patch — this {edition} snapback is the official off-court helmet. The moisture-wicking sweatband keeps it fresh through post-game celebrations.",
        "This {edition} snapback rocks a hard brim, embroidered front crest and an adjustable plastic snap closure for a perfect dial-in fit. The tonal under-brim coloring is the obsessive detail that separates real collectors from casual fans.",
        "Wool-blend body with a breathable mesh rear and a custom snap closure: this {edition} snapback is as functional as it is nostalgic. Vintage-wash treatment gives it that earned, been-there patina right out of the box.",
    ],
    "Jacket": [
        "Satin-shell exterior, quilted lining and embroidered twill patches — this {edition} jacket is straight from the locker-room rack. Ribbed collar, cuffs and hem lock in warmth while the full-zip front offers arena-to-street versatility.",
        "This {edition} bomber jacket channels pure championship swagger with a water-resistant nylon shell, team-coloured stripe across the chest and a hand-warmer pocket just deep enough for your championship ring.",
        "Heavyweight canvas shell meets a sherpa-lined interior in this {edition} jacket that transitions from tunnel walk to winter commute without missing a beat. YKK hardware and chain-stitched logos are the flourishes of a true collector's piece.",
    ],
    "Sweatpants": [
        "These {edition} sweatpants are cut from 300gsm French terry with tapered ankles, a dual-cord waistband and deep slash pockets. The embroidered leg logo says you know exactly who you root for.",
        "Relaxed taper, brushed interior and a pre-washed finish give these {edition} sweatpants that authentic warm-up room feel. The elastic ankle cuffs and team-coloured side tape are straight out of the pregame tunnel.",
    ],
    "Cap": [
        "Low-profile six-panel construction with a slightly curved brim and a soft buckram insert keeps this {edition} cap structured without the rigidity. The tonal embroidered logo sits centred and clean — understated flex at its finest.",
        "This {edition} dad cap is stonewashed for a faded vintage look, with a brass buckle closure and a miniature embroidered crest at the front. Exactly the kind of piece that looks better the more you wear it.",
    ],
    "Polo": [
        "Three-button placket, moisture-wicking piqué fabric and a subtle team-logo embroidery at the chest — this {edition} polo turns gameday into an all-day look. Tailored seams and a non-roll collar keep things sharp.",
        "Court-smart and boardroom-adjacent, this {edition} polo blends athletic piqué weave with a modern slim cut. The understated team crest on the left chest whispers fan devotion without shouting it.",
    ],
    "Tank Top": [
        "Cut from 160gsm performance jersey with open armholes and a dropped back hem, this {edition} tank top is built for summer bleacher heat. Bold number print on the front; nothing between you and the win.",
        "Racer-back silhouette, sweat-channelling mesh panels and a sublimated graphic across the chest: this {edition} tank top is the authentic pregame warm-up answer to brutally hot arenas.",
    ],
}

# --- szablony sceny meczowej ---
GAME_SCENE_TEMPLATES = [
    "That night against {opponent} on {date}, {player} rewrote the definition of greatness. With {pts} points lighting up the scoreboard, the arena erupted into a noise that made the rafters shake — {reb} rebounds hauled down like personal possessions, {ast} assists threading passes that seemed to defy geometry. Owning this piece means carrying a sliver of that electric night wherever you go.",
    "The {opponent} thought they had a defensive answer, but {player} had other plans on {date}. A {pts}-point explosion silenced every doubter in the building; the {reb} boards and {ast} dimes were the fine print on a masterclass. The crowd was still on its feet after the final buzzer — this garment was born from that roar.",
    "Legends are measured by moments, and {date} against {opponent} was one for the history books. {player} dropped {pts} cold points, snatched {reb} rebounds and orchestrated {ast} assists while the city held its breath. Wearing this is a passport back to that unforgettable night.",
    "Picture it: {date}, the {opponent} across the court, and {player} in the zone that mere mortals don't reach. {pts} points, {reb} boards, {ast} assists — numbers that looked wrong on the stat sheet because they seemed too good to be real. The building erupted. This piece was made for that memory.",
    "On {date} the {opponent} had no answer. {player} singlehandedly dismantled their defence with {pts} points, pulled {reb} rebounds and distributed {ast} assists with the calm of a conductor leading an orchestra. The buzzer sounded; the legend grew. This garment carries the DNA of that performance.",
    "When {player} walked onto the court on {date}, the {opponent} coaching staff exchanged nervous glances — and for good reason. {pts} points, {reb} boards, {ast} assists and {stl} steals turned a regular-season game into a career highlight. That energy is stitched into every fibre of this piece.",
    "Forty-eight minutes of suffocating pressure: {player} against the {opponent} on {date}. {pts} points seemed inevitable once the first quarter ended; the {reb} rebounds and {ast} assists painted a complete portrait of dominance. The home faithful erupted at the final horn — this garment is your souvenir from that moment.",
    "It was the kind of performance that makes opponents trade jerseys mid-game. {player} poured in {pts} points against {opponent} on {date}, vacuumed up {reb} rebounds and delivered {ast} assists with surgical precision. Decades later, fans talk about that game with the same reverence. This piece keeps the conversation alive.",
]

def garment_type(name: str) -> str:
    for key in GARMENT_TEMPLATES:
        if key.lower() in name.lower():
            return key
    return "Jersey"

def edition(name: str) -> str:
    for ed in ["Retro", "Limited Edition", "Championship", "Signature", "Classic", "All-Star", "Playoff", "Legacy", "Hall of Fame", "Vintage"]:
        if ed in name:
            return ed
    return "Collector's Edition"

def make_description(p: dict) -> str:
    gtype = garment_type(p["name"])
    ed = edition(p["name"])
    templates = GARMENT_TEMPLATES.get(gtype, GARMENT_TEMPLATES["Jersey"])
    para1 = random.choice(templates).format(edition=ed, player=p["player"])
    para2 = random.choice(GAME_SCENE_TEMPLATES).format(
        player=p["player"],
        opponent=p["opponent"],
        date=p["game_date"],
        pts=p["points"],
        reb=p["rebounds"],
        ast=p["assists"],
        stl=p["steals"],
        blk=p["blocks"],
    )
    return f"{para1}\n\n{para2}"

def needs_fix(desc: str) -> bool:
    return (
        "Worn vs" in desc
        or len(desc) < 100
        or "| Player:" in desc
        or "| Game:" in desc
        or "| Stats:" in desc
    )

def clean_existing(desc: str) -> str:
    """Usuń wklejony nagłówek promptu z początku opisu."""
    lines = desc.split("\n")
    # Usuń linie które wyglądają jak prompt (zawierają | Player:, | Game:, | Stats:)
    cleaned = []
    for line in lines:
        if "| Player:" in line or "| Game:" in line or "| Stats:" in line:
            continue
        cleaned.append(line)
    result = "\n".join(cleaned).strip()
    return result

with open(INPUT_FILE) as f:
    products = json.load(f)

fixed = 0
generated = 0
for p in products:
    desc = p.get("description", "")
    if needs_fix(desc):
        p["description"] = make_description(p)
        generated += 1
    elif "| Player:" in desc or "| Game:" in desc:
        p["description"] = clean_existing(desc)
        fixed += 1

with open(INPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"Wygenerowano: {generated}, naprawiono nagłówek: {fixed}, razem: {len(products)}")

# podgląd
for p in products[:3]:
    print("\n---", p["name"])
    print(p["description"][:400])
