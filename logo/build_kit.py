"""Builds the Zeuniverse logo kit (direction A, Otan Tile) as fill-only SVG masters."""
import math, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "kit"
for d in ("master", "expressions"):
    os.makedirs(f"{OUT}/{d}", exist_ok=True)

ORANGE, ORANGE_D = "#F5822A", "#D9661C"
SKIN, NAVY = "#FCD3A6", "#2B2862"
MOUTH, TONGUE, BLUSH, NOSE, BROW = "#3B1F3A", "#E8637A", "#F4917A", "#9A5430", "#C2551C"
WHITE = "#FFFFFF"
TITLE = "Zeuniverse"


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def svg(body, vb="0 0 256 256", title=TITLE):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'
            f'<title>{title}</title>{body}</svg>\n')


def save(path, body, **kw):
    with open(f"{OUT}/{path}", "w", encoding="utf-8") as fh:
        fh.write(svg(body, **kw))


# ---------------------------------------------------------------- geometry helpers
def circle(cx, cy, r, fill):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"/>'


def ellipse(cx, cy, rx, ry, fill):
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}"/>'


def capsule(x1, y1, x2, y2, r):
    """Round-capped line as filled geometry (polygon + two end discs)."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * r, dx / L * r
    poly = (f'<path d="M{f(x1+nx)},{f(y1+ny)} L{f(x2+nx)},{f(y2+ny)} '
            f'L{f(x2-nx)},{f(y2-ny)} L{f(x1-nx)},{f(y1-ny)} Z"/>')
    return poly + f'<circle cx="{f(x1)}" cy="{f(y1)}" r="{f(r)}"/><circle cx="{f(x2)}" cy="{f(y2)}" r="{f(r)}"/>'


def arcband(cx, cy, R, a0, a1, r):
    """Round-capped circular arc from angle a0 to a1 (degrees, y-down, increasing = clockwise)."""
    def pt(rad, a):
        t = math.radians(a)
        return cx + rad * math.cos(t), cy + rad * math.sin(t)
    large = 1 if (a1 - a0) > 180 else 0
    o0, o1 = pt(R + r, a0), pt(R + r, a1)
    i0, i1 = pt(R - r, a0), pt(R - r, a1)
    band = (f'<path d="M{f(o0[0])},{f(o0[1])} A{f(R+r)},{f(R+r)} 0 {large} 1 {f(o1[0])},{f(o1[1])} '
            f'L{f(i1[0])},{f(i1[1])} A{f(R-r)},{f(R-r)} 0 {large} 0 {f(i0[0])},{f(i0[1])} Z"/>')
    e0, e1 = pt(R, a0), pt(R, a1)
    return band + f'<circle cx="{f(e0[0])}" cy="{f(e0[1])}" r="{f(r)}"/><circle cx="{f(e1[0])}" cy="{f(e1[1])}" r="{f(r)}"/>'


def mask_path(cx, cy, s):
    """Otan's skin mask as one outline: two eye lobes merged with a wide muzzle."""
    lx, ly, lr = 34 * s, cy - 14 * s, 46 * s
    ex, ey, erx, ery = cx, cy + 30 * s, 72 * s, 52 * s
    notch_y = ly - math.sqrt(lr**2 - lx**2)
    # walk the right lobe clockwise from the notch until it enters the muzzle ellipse
    a_notch = math.degrees(math.atan2(notch_y - ly, -lx))
    a = a_notch
    while True:
        a += 0.05
        px, py = cx + lx + lr * math.cos(math.radians(a)), ly + lr * math.sin(math.radians(a))
        if ((px - ex) / erx) ** 2 + ((py - ey) / ery) ** 2 <= 1:
            break
    large_lobe = 1 if (a - a_notch) > 180 else 0
    qx, qy = 2 * cx - px, py
    # ellipse arc from P round the bottom to its mirror: angle span via parametric angle
    t = math.degrees(math.atan2((py - ey) / ery, (px - ex) / erx))
    large_ell = 1 if (180 - 2 * t) > 180 else 0
    return (f'M{f(cx)},{f(notch_y)} A{f(lr)},{f(lr)} 0 {large_lobe} 1 {f(px)},{f(py)} '
            f'A{f(erx)},{f(ery)} 0 {large_ell} 1 {f(qx)},{f(qy)} '
            f'A{f(lr)},{f(lr)} 0 {large_lobe} 1 {f(cx)},{f(notch_y)} Z')


def tuft(cx, top, s, color):
    def p(x, y): return f"{f(cx + x*s)},{f(top + y*s)}"
    return (f'<path d="M{p(-30,34)} Q{p(-26,8)} {p(-12,0)} Q{p(-14,14)} {p(-6,20)} '
            f'Q{p(-2,-6)} {p(16,-8)} Q{p(8,8)} {p(12,20)} Q{p(22,4)} {p(34,6)} '
            f'Q{p(30,24)} {p(30,34)} Z" fill="{color}"/>')


# ---------------------------------------------------------------- face
def eye_open(ex, ey, s, small=False):
    o = ellipse(ex, ey, 19 * s, 24 * s, NAVY)
    if small:
        return o + circle(ex + 6 * s, ey - 8 * s, 8.5 * s, WHITE)
    return o + circle(ex + 7 * s, ey - 9 * s, 7.5 * s, WHITE) + circle(ex - 6 * s, ey + 9 * s, 3.5 * s, WHITE)


def eye_arc(ex, ey, s):
    # happy closed eye: a round-capped arc over the top
    return f'<g fill="{NAVY}">{arcband(ex, ey + 10*s, 17*s, 205, 335, 5*s)}</g>'


def mouth_open(cx, cy, s, tongue=True):
    def p(x, y): return f"{f(cx + x*s)},{f(cy + y*s)}"
    o = (f'<path d="M{p(-24,32)} H{f(cx+24*s)} Q{p(24,64)} {p(0,64)} Q{p(-24,64)} {p(-24,32)} Z" '
         f'fill="{MOUTH}"/>')
    if tongue:
        o += (f'<path d="M{p(-13,57)} Q{p(0,44)} {p(13,57)} Q{p(8,64)} {p(0,64)} Q{p(-8,64)} {p(-13,57)} Z" '
              f'fill="{TONGUE}"/>')
    return o


def mouth_o(cx, cy, s):
    return ellipse(cx, cy + 46 * s, 13 * s, 16 * s, MOUTH) + ellipse(cx, cy + 54 * s, 8 * s, 6 * s, TONGUE)


def face(cx, cy, s, left="open", right="open", mouth="open", brows=False, small=False):
    o = [f'<path d="{mask_path(cx, cy, s)}" fill="{SKIN}"/>']
    if not small:
        for sx in (-1, 1):
            o.append(ellipse(cx + sx * 56 * s, cy + 30 * s, 14 * s, 9 * s, BLUSH))
    for sx, kind in ((-1, left), (1, right)):
        ex, ey = cx + sx * 34 * s, cy - 10 * s
        o.append(eye_open(ex, ey, s, small) if kind == "open" else eye_arc(ex, ey, s))
    if brows:
        o.append(f'<g fill="{BROW}">{capsule(cx-44*s, cy-46*s, cx-26*s, cy-50*s, 3.5*s)}'
                 f'{capsule(cx+26*s, cy-50*s, cx+44*s, cy-46*s, 3.5*s)}</g>')
    if not small:
        for sx in (-1, 1):
            o.append(ellipse(cx + sx * 7 * s, cy + 20 * s, 4.5 * s, 3.5 * s, NOSE))
    o.append(mouth_o(cx, cy, s) if mouth == "o" else mouth_open(cx, cy, s, tongue=not small))
    return "".join(o)


def tile(color=ORANGE):
    return f'<rect width="256" height="256" rx="58" fill="{color}"/>'


FACE_C, FACE_S = (128, 132), 1.18


def icon(**kw):
    return tile() + tuft(128, 24, 1.5, ORANGE_D) + face(*FACE_C, FACE_S, **kw)


# ---------------------------------------------------------------- masters
save("master/zeuniverse-icon.svg", icon())

# small-size cut (<= 32 px): no tuft, nose, blush, tongue; one big glint per eye
save("master/zeuniverse-icon-small.svg", tile() + face(128, 128, 1.24, small=True))

# head without tile, for use on light/dark backgrounds that aren't orange
head = (ellipse(30, 146, 22, 28, ORANGE_D) + ellipse(226, 146, 22, 28, ORANGE_D) +
        tuft(128, 24, 1.5, ORANGE) + circle(128, 140, 102, ORANGE) +
        face(128, 140, 1.0))
save("master/zeuniverse-head.svg", head)

# one-colour: tile with the mask cut out, features as ink, glints as holes
s = FACE_S
cx, cy = FACE_C
ink = [f'<path fill-rule="evenodd" d="M58,0 H198 A58,58 0 0 1 256,58 V198 A58,58 0 0 1 198,256 H58 '
       f'A58,58 0 0 1 0,198 V58 A58,58 0 0 1 58,0 Z {mask_path(cx, cy, s)}"/>']
for sx in (-1, 1):
    ex, ey = cx + sx * 34 * s, cy - 10 * s
    rx, ry = 19 * s, 24 * s
    def ring(x, y, r):
        return f'M{f(x-r)},{f(y)} A{f(r)},{f(r)} 0 1 0 {f(x+r)},{f(y)} A{f(r)},{f(r)} 0 1 0 {f(x-r)},{f(y)} Z'
    ink.append(f'<path fill-rule="evenodd" d="M{f(ex-rx)},{f(ey)} A{f(rx)},{f(ry)} 0 1 0 {f(ex+rx)},{f(ey)} '
               f'A{f(rx)},{f(ry)} 0 1 0 {f(ex-rx)},{f(ey)} Z {ring(ex+7*s, ey-9*s, 7.5*s)} {ring(ex-6*s, ey+9*s, 3.5*s)}"/>')
    ink.append(f'<ellipse cx="{f(cx+sx*7*s)}" cy="{f(cy+20*s)}" rx="{f(4.5*s)}" ry="{f(3.5*s)}"/>')
def p(x, y): return f"{f(cx + x*s)},{f(cy + y*s)}"
ink.append(f'<path d="M{p(-24,32)} H{f(cx+24*s)} Q{p(24,64)} {p(0,64)} Q{p(-24,64)} {p(-24,32)} Z"/>')
MONO = "".join(ink)
save("master/zeuniverse-icon-mono.svg", f'<g fill="{ORANGE}">{MONO}</g>')

# ---------------------------------------------------------------- wordmark "zeuniverse"
# monoline rounded lowercase, stroke 22 on a 100-unit x-height; centrelines y 111..189, bowls r 39 at y 150
R_ST, BOWL = 11, 39


def ellband(cx, cy, a, b, t0, t1, r):
    """Round-capped elliptical arc (parametric angles, degrees); band approximated by +-r on both radii."""
    def pt(ra, rb, t):
        t = math.radians(t)
        return cx + ra * math.cos(t), cy + rb * math.sin(t)
    large = 1 if (t1 - t0) > 180 else 0
    o0, o1 = pt(a + r, b + r, t0), pt(a + r, b + r, t1)
    i0, i1 = pt(a - r, b - r, t0), pt(a - r, b - r, t1)
    band = (f'<path d="M{f(o0[0])},{f(o0[1])} A{f(a+r)},{f(b+r)} 0 {large} 1 {f(o1[0])},{f(o1[1])} '
            f'L{f(i1[0])},{f(i1[1])} A{f(a-r)},{f(b-r)} 0 {large} 0 {f(i0[0])},{f(i0[1])} Z"/>')
    e0, e1 = pt(a, b, t0), pt(a, b, t1)
    return band + f'<circle cx="{f(e0[0])}" cy="{f(e0[1])}" r="{f(r)}"/><circle cx="{f(e1[0])}" cy="{f(e1[1])}" r="{f(r)}"/>'


GLYPHS = {
    "z": (80, lambda x: capsule(x+11, 111, x+69, 111, R_ST) + capsule(x+69, 111, x+11, 189, R_ST)
                        + capsule(x+11, 189, x+69, 189, R_ST)),
    "e": (100, lambda x: capsule(x+11, 150, x+89, 150, R_ST) + arcband(x+50, 150, BOWL, 40, 360, R_ST)),
    "u": (100, lambda x: capsule(x+11, 111, x+11, 150, R_ST) + arcband(x+50, 150, BOWL, 0, 180, R_ST)
                         + capsule(x+89, 111, x+89, 189, R_ST)),
    "n": (100, lambda x: capsule(x+11, 111, x+11, 189, R_ST) + arcband(x+50, 150, BOWL, 180, 360, R_ST)
                         + capsule(x+89, 150, x+89, 189, R_ST)),
    "i": (22, lambda x: capsule(x+11, 111, x+11, 189, R_ST)),
    "v": (92, lambda x: capsule(x+11, 111, x+46, 189, R_ST) + capsule(x+46, 189, x+81, 111, R_ST)),
    "r": (76, lambda x: capsule(x+11, 111, x+11, 189, R_ST) + arcband(x+50, 150, BOWL, 180, 292, R_ST)),
    "s": (82, lambda x: ellband(x+41, 130.5, 30, 19.5, 90, 330, R_ST) + ellband(x+41, 169.5, 30, 19.5, -90, 150, R_ST)),
}
# optical spacing: round sides sit tighter than straight stems
KERN = {"ze": 12, "eu": 12, "un": 16, "ni": 16, "iv": 10, "ve": 8, "er": 12, "rs": 8, "se": 10}


def wordmark(ink, dot):
    x, parts, idot = 0, [], None
    word = "zeuniverse"
    for i, ch in enumerate(word):
        w, draw = GLYPHS[ch]
        parts.append(draw(x))
        if ch == "i":
            idot = (x + 11, 80)
        if i < len(word) - 1:
            x += w + KERN[word[i:i+2]]
    width = x + GLYPHS[word[-1]][0]
    body = f'<g fill="{ink}">{"".join(parts)}</g>' + circle(idot[0], idot[1], 14, dot)
    return body, width


WM_TOP, WM_BOTTOM = 64, 200  # i-dot top .. baseline
for name, ink, dot in (("wordmark", NAVY, ORANGE), ("wordmark-white", WHITE, ORANGE),
                       ("wordmark-black", "#000000", "#000000")):
    body, W = wordmark(ink, dot)
    save(f"master/zeuniverse-{name}.svg", body, vb=f"0 {WM_TOP} {f(W)} {WM_BOTTOM-WM_TOP}")


def lockup_h(ink, dot, mark=None):
    mark = mark or icon()
    body, W = wordmark(ink, dot)
    k = 1.15  # wordmark x-height = 45 % of icon height
    gap = 52
    xh_mid = 150 * k  # optical centre of the x-height aligns with the icon centre
    ty = 128 - xh_mid
    total = 256 + gap + W * k
    return (mark + f'<g transform="translate({f(256+gap)} {f(ty)}) scale({k})">{body}</g>', total)


def lockup_v(ink, dot, mark=None):
    mark = mark or icon()
    body, W = wordmark(ink, dot)
    k = 0.62
    total_w = max(256, W * k)
    ix = (total_w - 256) / 2
    ty = 256 + 48 - WM_TOP * k
    wx = (total_w - W * k) / 2
    h = 256 + 48 + (WM_BOTTOM - WM_TOP) * k
    return (f'<g transform="translate({f(ix)} 0)">{mark}</g>'
            f'<g transform="translate({f(wx)} {f(ty)}) scale({k})">{body}</g>', total_w, h)


for name, ink in (("", NAVY), ("-white", WHITE)):
    b, w = lockup_h(ink, ORANGE)
    save(f"master/zeuniverse-horizontal{name}.svg", b, vb=f"0 0 {f(w)} 256")
    b, w, h = lockup_v(ink, ORANGE)
    save(f"master/zeuniverse-stacked{name}.svg", b, vb=f"0 0 {f(w)} {f(h)}")

# one-colour lockups: mono icon + wordmark in the same ink
os.makedirs(f"{OUT}/variants", exist_ok=True)
for name, ink in (("black", "#000000"), ("white", WHITE), ("navy", NAVY)):
    b, w = lockup_h(ink, ink, mark=f'<g fill="{ink}">{MONO}</g>')
    save(f"variants/zeuniverse-horizontal-{name}.svg", b, vb=f"0 0 {f(w)} 256")
    b, w, h = lockup_v(ink, ink, mark=f'<g fill="{ink}">{MONO}</g>')
    save(f"variants/zeuniverse-stacked-{name}.svg", b, vb=f"0 0 {f(w)} {f(h)}")

# ---------------------------------------------------------------- expressions (Duolingo-style set)
EXPR = {
    "default": dict(),
    "happy": dict(left="arc", right="arc"),
    "wink": dict(left="open", right="arc"),
    "wow": dict(mouth="o", brows=True),
}
for name, kw in EXPR.items():
    save(f"expressions/otan-{name}.svg", icon(**kw))

# astronaut edition: Otan in a visor, for space-themed moments
astro = (tile() +
         f'<rect x="16" y="106" width="30" height="56" rx="15" fill="{ORANGE_D}"/>'
         f'<rect x="210" y="106" width="30" height="56" rx="15" fill="{ORANGE_D}"/>' +
         circle(128, 134, 98, WHITE) + circle(128, 138, 80, NAVY) + circle(128, 150, 64, ORANGE) +
         tuft(128, 76, 1.0, ORANGE) + face(128, 158, 0.74) +
         f'<g fill="{WHITE}" opacity="0.55">{arcband(128, 138, 64, 205, 245, 3.5)}</g>')
save("expressions/otan-astronaut.svg", astro)
print("kit masters written")

# full-bleed square for platforms that apply their own mask (iOS, Android adaptive, PWA)
FEATURES = tuft(128, 24, 1.5, ORANGE_D) + face(*FACE_C, FACE_S)
save("master/zeuniverse-icon-fullbleed.svg", f'<rect width="256" height="256" fill="{ORANGE}"/>' + FEATURES)
save("master/zeuniverse-icon-maskable.svg", f'<rect width="256" height="256" fill="{ORANGE}"/>'
     f'<g transform="translate(128 132) scale(0.8) translate(-128 -132)">{FEATURES}</g>')
print("platform icons written")
# features only, for placing on any orange surface (mockups, merch, platform tiles)
save("master/zeuniverse-face.svg", FEATURES)


# ---------------------------------------------------------------- one-colour glyphs for system-tinted surfaces
def disc(x, y, rx, ry=None):
    ry = rx if ry is None else ry
    return f'M{f(x-rx)},{f(y)} A{f(rx)},{f(ry)} 0 1 0 {f(x+rx)},{f(y)} A{f(rx)},{f(ry)} 0 1 0 {f(x-rx)},{f(y)} Z'


def mouth_d(cx, cy, s):
    def p(x, y): return f"{f(cx + x*s)},{f(cy + y*s)}"
    return f'M{p(-24,32)} H{f(cx+24*s)} Q{p(24,64)} {p(0,64)} Q{p(-24,64)} {p(-24,32)} Z'


# one-colour glyph (notification, Android themed icon): head silhouette, mask cut out, eyes and mouth solid (no glints/nose at 24 dp)
hs = 1.0
save("master/zeuniverse-glyph.svg",
     f'<g fill="{WHITE}">{tuft(128, 24, 1.5, WHITE)}'
     f'<ellipse cx="26" cy="146" rx="22" ry="28"/><ellipse cx="230" cy="146" rx="22" ry="28"/>'
     f'<path fill-rule="evenodd" d="{disc(128, 140, 102)} {mask_path(128, 140, hs)} '
     + "".join(disc(128 + sx*34*hs, 130, 21, 26) for sx in (-1, 1)) +
     f' {mouth_d(128, 140, hs)}"/></g>')
print("mono glyphs written")
