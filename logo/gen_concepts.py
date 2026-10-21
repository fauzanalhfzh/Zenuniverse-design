"""Generates Zeuniverse app-icon logo concepts built on Otan's face."""
import os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "concepts"
os.makedirs(OUT, exist_ok=True)

ORANGE, ORANGE_D, ORANGE_L = "#F5822A", "#D9661C", "#FF9A45"
SKIN, NAVY, NAVY_D = "#FCD3A6", "#2B2862", "#1F1C4A"
MOUTH, TONGUE, BLUSH, NOSE, BROW = "#3B1F3A", "#E8637A", "#F4917A", "#9A5430", "#C2551C"
WHITE = "#FFFFFF"

def svg(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">{body}</svg>\n'

def tile(color=ORANGE):
    return f'<rect width="256" height="256" rx="58" fill="{color}"/>'

def face(cx, cy, s=1.0, eyes="open"):
    """Otan's face: two-lobe skin mask, navy eyes with glints, nose dots, open smile."""
    def p(x, y): return f"{cx + x*s:.1f},{cy + y*s:.1f}"
    def r(v): return f"{v*s:.1f}"
    o = []
    # skin mask: two eye lobes + a wide muzzle, one fill so they merge
    o.append(f'<g fill="{SKIN}">'
             f'<circle cx="{cx-34*s:.1f}" cy="{cy-14*s:.1f}" r="{r(46)}"/>'
             f'<circle cx="{cx+34*s:.1f}" cy="{cy-14*s:.1f}" r="{r(46)}"/>'
             f'<ellipse cx="{cx:.1f}" cy="{cy+30*s:.1f}" rx="{r(72)}" ry="{r(52)}"/></g>')
    # blush
    for sx in (-1, 1):
        o.append(f'<ellipse cx="{cx+sx*56*s:.1f}" cy="{cy+30*s:.1f}" rx="{r(14)}" ry="{r(9)}" fill="{BLUSH}"/>')
    # eyes
    for sx in (-1, 1):
        ex, ey = cx + sx*34*s, cy - 10*s
        if eyes == "open":
            o.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{r(19)}" ry="{r(24)}" fill="{NAVY}"/>')
            o.append(f'<circle cx="{ex+7*s:.1f}" cy="{ey-9*s:.1f}" r="{r(7.5)}" fill="{WHITE}"/>')
            o.append(f'<circle cx="{ex-6*s:.1f}" cy="{ey+9*s:.1f}" r="{r(3.5)}" fill="{WHITE}"/>')
        else:  # happy closed arcs
            o.append(f'<path d="M{p(sx*34-16, -4)} Q{p(sx*34, -26)} {p(sx*34+16, -4)}" fill="none" '
                     f'stroke="{NAVY}" stroke-width="{r(9)}" stroke-linecap="round"/>')
    # nose
    for sx in (-1, 1):
        o.append(f'<ellipse cx="{cx+sx*7*s:.1f}" cy="{cy+20*s:.1f}" rx="{r(4.5)}" ry="{r(3.5)}" fill="{NOSE}"/>')
    # mouth: flat top, round bottom, tongue inside
    o.append(f'<path d="M{p(-24,32)} H{cx+24*s:.1f} Q{p(24,64)} {p(0,64)} Q{p(-24,64)} {p(-24,32)} Z" fill="{MOUTH}"/>')
    o.append(f'<path d="M{p(-13,57)} Q{p(0,44)} {p(13,57)} Q{p(8,64)} {p(0,64)} Q{p(-8,64)} {p(-13,57)} Z" fill="{TONGUE}"/>')
    return "".join(o)

def tuft(cx, top, s=1.0, color=ORANGE):
    """Three-spike hair tuft above the head."""
    def p(x, y): return f"{cx + x*s:.1f},{top + y*s:.1f}"
    return (f'<path d="M{p(-30,34)} Q{p(-26,8)} {p(-12,0)} Q{p(-14,14)} {p(-6,20)} '
            f'Q{p(-2,-6)} {p(16,-8)} Q{p(8,8)} {p(12,20)} Q{p(22,4)} {p(34,6)} '
            f'Q{p(30,24)} {p(30,34)} Z" fill="{color}"/>')

# A — Otan Tile: the tile *is* Otan's head (Duolingo-style full-bleed face)
a = (tile() +
     f'<rect x="0" y="196" width="256" height="60" rx="0" fill="none"/>' +
     tuft(128, 24, 1.5, ORANGE_D) +
     face(128, 132, 1.18))
open(f"{OUT}/a-otan-tile.svg", "w").write(svg(a))

# B — Helmet: Otan inside an astronaut visor on the orange tile (ties to the universe)
b = (tile() +
     f'<rect x="16" y="106" width="30" height="56" rx="15" fill="{ORANGE_D}"/><rect x="210" y="106" width="30" height="56" rx="15" fill="{ORANGE_D}"/>' +
     f'<circle cx="128" cy="134" r="98" fill="{WHITE}"/>' +
     f'<circle cx="128" cy="138" r="80" fill="{NAVY}"/>' +
     f'<circle cx="128" cy="150" r="64" fill="{ORANGE}"/>' +
     tuft(128, 76, 1.0) +
     face(128, 158, 0.74) +
     f'<path d="M74 104 Q86 80 112 72" fill="none" stroke="{WHITE}" stroke-width="7" stroke-linecap="round" opacity="0.55"/>')
open(f"{OUT}/b-helmet.svg", "w").write(svg(b))

# C — Z-Tuft: Otan's hair tuft drawn as a Z, the Zeuniverse initial
z = (f'<path d="M98 22 H158 Q166 22 161 29 L124 64 H156 Q164 64 164 72 V76 Q164 82 156 82 H98 '
     f'Q90 82 95 75 L132 40 H98 Q90 40 90 32 V30 Q90 22 98 22 Z" fill="{ORANGE_D}" transform="translate(0 22)"/>')
c = (tile() +
     f'<ellipse cx="22" cy="152" rx="26" ry="32" fill="{ORANGE_D}"/><ellipse cx="234" cy="152" rx="26" ry="32" fill="{ORANGE_D}"/>' +
     z +
     face(128, 150, 1.08))
open(f"{OUT}/c-z-tuft.svg", "w").write(svg(c))

# Expression set for A (Duolingo-style variety), happy-eyes variant
a2 = tile() + tuft(128, 24, 1.5, ORANGE_D) + face(128, 132, 1.18, eyes="happy")
open(f"{OUT}/a-otan-tile-happy.svg", "w").write(svg(a2))
print("ok")
