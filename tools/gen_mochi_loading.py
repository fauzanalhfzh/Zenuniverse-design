"""Generates mochi-loading/scene.rml: the peach mochi hopping to the right across the frame, loading loop."""
import itertools, sys

OUT = sys.argv[1]
_ids = itertools.count(100)
def nid():
    return f"0:{next(_ids)}"

WHITE = "FFFFFFFF"
MOCHI, MOCHI_TOP, MOCHI_SHADE = "FFFFD6A8", "FFFFE6C9", "FFFBC08A"   # soft apricot, not burnt orange
INK = "FF4B3530"
BLUSH = "FFFFA393"
TONGUE = "FFFF8A8A"
CONTACT_C, FLOOR = "FFDDDDDD", "FFEEEEEE"
DUST = "FFEADFD4"                       # warm puff, reads on white and on dark

def solid(c):
    return f'<SolidColor colorValue="{c}" name="C"/>'

def fill(c=None, grad=None, feather=None):
    paint = grad if grad else solid(c)
    rule = ' fillRule="clockwise"' if feather else ""
    fe = f'<Feather strength="{feather}" name="F"/>' if feather else ""
    return f'<Fill{rule} name="Fill">{paint}{fe}</Fill>'

def stroke(c, t, cap="round"):
    return f'<Stroke thickness="{t}" cap="{cap}" join="round" name="Stroke">{solid(c)}</Stroke>'

def lin(x1, y1, x2, y2, *stops):
    s = "".join(f'<GradientStop colorValue="{c}" position="{p}"/>' for c, p in stops)
    return f'<LinearGradient startX="{x1}" startY="{y1}" endX="{x2}" endY="{y2}" name="G">{s}</LinearGradient>'

def attrs(**kw):
    return " ".join(f'{k}="{v}"' for k, v in kw.items() if v is not None)

def shape(name, geo, *paints, id=None, **t):
    return f'<Shape {attrs(**t)} name="{name}"{f" id={chr(34)}{id}{chr(34)}" if id else ""}>{geo}{"".join(paints)}</Shape>'

def node(name, *children, id=None, **t):
    return f'<Node {attrs(**t)} name="{name}"{f" id={chr(34)}{id}{chr(34)}" if id else ""}>{"".join(children)}</Node>'

def ell(w, h, **t):
    return f'<Ellipse {attrs(width=w, height=h, **t)} name="P"/>'

def path(verts, closed=True):
    return f'<PointsPath isClosed="{str(closed).lower()}" name="P">{"".join(verts)}</PointsPath>'

def sv(x, y, r=None):
    return f'<StraightVertex {attrs(x=x, y=y, radius=r)}/>'

def mv(x, y, rot, d):
    return f'<CubicMirroredVertex x="{x}" y="{y}" rotation="{rot}" distance="{d}"/>'

# ---------------------------------------------------------------- keyframes
EASES = {
    "io": (0.42, 0, 0.58, 1),
    "out": (0.16, 1, 0.3, 1),
    "in": (0.55, 0, 0.9, 0.4),
    "soft": (0.37, 0, 0.63, 1),
    "back": (0.34, 1.4, 0.64, 1),
    "rise": (0.5, 1, 0.89, 1),       # ease-out quad: top of a parabola
    "fall": (0.11, 0, 0.5, 0),       # ease-in quad
}

def kfs(prop, keys):
    """keys: list of (frame, value, ease). ease shapes the segment leaving this key."""
    out = []
    for f, v, e in keys:
        if e in ("hold", "linear"):
            out.append(f'<KeyFrameDouble frame="{f}" value="{v}" interpolationType="{e}"/>')
        else:
            x1, y1, x2, y2 = EASES[e]
            out.append(f'<KeyFrameDouble frame="{f}" value="{v}" interpolationType="cubic">'
                       f'<CubicEaseInterpolator x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/></KeyFrameDouble>')
    return f'<KeyedProperty property="{prop}">{"".join(out)}</KeyedProperty>'

def keyed(obj, *props):
    return f'<KeyedObject objectId="{obj}">{"".join(props)}</KeyedObject>'

# ---------------------------------------------------------------- ids of animated parts
ROOT, SQUISH, FACE, BODY, CONTACT, DUST_L, DUST_R = (nid() for _ in range(7))
EYE_L, EYE_R, OPEN_EYES, HAPPY_EYES = (nid() for _ in range(4))
SMILE, OPEN_MOUTH, BLUSH_L, BLUSH_R, SHINE = (nid() for _ in range(5))

# ---------------------------------------------------------------- the mochi
# Camera sits a little above and in front (like a Duolingo character on its floor disc):
# the mochi faces us upright, a sliver of its top surface shows, and it stands on a flat
# floor strip. It hops to the right across the frame. Flat fills, no outline.
# Head-local origin is the bottom centre, so every squash keeps the mochi on the floor.
W, H = 192, 150
blob = path([
    mv(0, 0, 0, 64),                 # flat, heavy bottom
    mv(W / 2, -H * 0.36, -1.5708, 40),
    mv(0, -H, 3.1415927, 68),        # soft dome
    mv(-W / 2, -H * 0.36, 1.5708, 40),
])

def eye(name, eid, x):
    return node(name,
        shape("Glint", ell(7, 7), fill(WHITE), x=3, y=-4.5),
        shape("Glint Small", ell(3, 3), fill(WHITE), x=-3, y=4.5, opacity=0.9),
        shape("Pupil", ell(17, 22), fill(INK)),
        id=eid, x=x)

happy_arc = lambda x: shape("Happy", path([sv(-9, 3), mv(0, -6, 0, 6), sv(9, 3)], closed=False),
                            stroke(INK, 4.6), x=x)

face = node("Face",
    node("Open Eyes", eye("Eye L", EYE_L, -34), eye("Eye R", EYE_R, 34), id=OPEN_EYES),
    node("Happy Eyes", happy_arc(-34), happy_arc(34), id=HAPPY_EYES, opacity=0),
    shape("Smile", path([sv(-11, -1), mv(-5.5, 4.5, 0, 3.5), sv(0, -0.5), mv(5.5, 4.5, 0, 3.5), sv(11, -1)],
                        closed=False), stroke(INK, 3.8), id=SMILE, y=17),
    node("Open Mouth",
        shape("Tongue", ell(10, 5), fill(TONGUE), y=3.5),
        shape("Mouth", path([sv(-9, -2, 3), sv(9, -2, 3), mv(0, 10, 3.1415927, 7)]), fill(INK)),
        id=OPEN_MOUTH, y=18, opacity=0),
    shape("Blush L", ell(30, 17), fill(BLUSH), x=-58, y=15, opacity=0.7, id=BLUSH_L),
    shape("Blush R", ell(30, 17), fill(BLUSH), x=58, y=15, opacity=0.7, id=BLUSH_R),
    id=FACE, x=10, y=-58)          # glancing the way it travels

# flat two-tone shading, clipped to the silhouette
shading = node("Shading",
    shape("Top", ell(150, 54), fill(MOCHI_TOP), y=-120),          # top surface seen from above
    shape("Shade", ell(W + 60, 76), fill(MOCHI_SHADE), x=14, y=14),  # underside in shadow
    f'<ClippingShape sourceId="{BODY}" name="Clip"/>')

squish = node("Squish",
    face,
    shape("Shine", ell(22, 12), fill(WHITE), x=-46, y=-116, rotation=-0.45, opacity=0.9, id=SHINE),
    shape("Shine Dot", ell(7, 6), fill(WHITE), x=-22, y=-128, opacity=0.9),
    node("Powder", *[shape("Dust", ell(d, d), fill(WHITE), x=x, y=y, opacity=o) for x, y, d, o in
        [(20, -126, 4, 0.8), (50, -114, 3, 0.7), (-4, -136, 3, 0.7), (70, -96, 3, 0.5), (-66, -92, 3, 0.5)]]),
    shading,
    shape("Body", blob, fill(MOCHI), id=BODY),
    id=SQUISH)

# ---------------------------------------------------------------- scene
AW, AH, G = 480, 220, 172
S = 0.6                                  # mochi drawn at idle size, shown smaller here
HOP_H = 62
STEP = 155
XS = [-70 + STEP * i for i in range(5)]   # -70 and 550 are both off-frame, so the wrap is invisible
HOP = 40                                  # frames per hop
T = HOP * (len(XS) - 1)

puff = lambda name, did, side: node(name,
    shape("Puff", ell(14, 14), fill(DUST), x=12 * side, y=-10),
    shape("Puff", ell(20, 20), fill(DUST)),
    shape("Puff", ell(11, 11), fill(DUST), x=-10 * side, y=-4),
    id=did, x=-112 * side, y=-6, opacity=0)

root = node("Mochi", puff("Dust L", DUST_L, 1), puff("Dust R", DUST_R, -1), squish,
            id=ROOT, x=XS[0], y=G, scaleX=S, scaleY=S)
contact = shape("Contact", ell(170 * S, 30 * S), fill(CONTACT_C), id=CONTACT, x=XS[0], y=G)
floor = shape("Floor", ell(AW - 30, 30), fill(FLOOR), x=AW / 2, y=G + 4)

# ---------------------------------------------------------------- loading loop: hop, hop, hop to the right
def track(per_hop, first=None, last=None):
    keys = [first] if first else []
    for i in range(len(XS) - 1):
        keys += per_hop(i * HOP, XS[i], XS[i + 1])
    if last:
        keys.append(last)
    return keys

root_x = track(lambda b, x0, x1: [(b + 10, x0, "linear"), (b + 30, x1, "hold")], (0, XS[0], "hold"))
root_y = track(lambda b, x0, x1: [(b + 10, G, "rise"), (b + 20, G - HOP_H, "fall"), (b + 30, G, "hold")],
               (0, G, "hold"), (T, G, "hold"))
# squash before take-off, stretch on the way up, round at the top, splat on landing, jiggle back
sx = track(lambda b, *_: [(b, 1, "soft"), (b + 6, 1.16, "out"), (b + 10, 0.86, "soft"), (b + 20, 1, "soft"),
                          (b + 28, 0.93, "linear"), (b + 31, 1.22, "out"), (b + 36, 0.95, "soft")], last=(T, 1, "linear"))
sy = track(lambda b, *_: [(b, 1, "soft"), (b + 6, 0.8, "out"), (b + 10, 1.16, "soft"), (b + 20, 1, "soft"),
                          (b + 28, 1.07, "linear"), (b + 31, 0.78, "out"), (b + 36, 1.05, "soft")], last=(T, 1, "linear"))
# leans back to wind up, tips forward into the hop, overshoots a little on landing
lean = track(lambda b, *_: [(b, 0, "soft"), (b + 6, -0.07, "soft"), (b + 13, 0.16, "soft"), (b + 26, 0.06, "soft"),
                            (b + 31, 0.12, "out"), (b + 36, -0.04, "soft")], last=(T, 0, "linear"))
face_y = track(lambda b, *_: [(b, -58, "soft"), (b + 6, -52, "out"), (b + 12, -64, "soft"), (b + 22, -58, "soft"),
                              (b + 31, -52, "out"), (b + 37, -60, "soft")], last=(T, -58, "linear"))
air = lambda on, off: track(lambda b, *_: [(b, off, "hold"), (b + 8, on, "hold"), (b + 32, off, "hold")],
                            last=(T, off, "hold"))
mouth = lambda on, off: track(lambda b, *_: [(b, off, "hold"), (b + 10, on, "hold"), (b + 31, off, "hold")],
                              last=(T, off, "hold"))
shadow_s = track(lambda b, *_: [(b, 1, "soft"), (b + 6, 1.12, "soft"), (b + 20, 0.55, "soft"), (b + 30, 0.95, "linear"),
                                (b + 31, 1.2, "out"), (b + 36, 1, "soft")], last=(T, 1, "linear"))
shadow_o = track(lambda b, *_: [(b + 10, 1, "soft"), (b + 20, 0.45, "soft"), (b + 30, 1, "hold")],
                 (0, 1, "hold"), (T, 1, "hold"))
dust_o = track(lambda b, *_: [(b + 30, 0, "hold"), (b + 31, 0.95, "soft"), (b + 39, 0, "hold")], (0, 0, "hold"))
dust_s = track(lambda b, *_: [(b + 30, 0.3, "hold"), (b + 31, 0.4, "out"), (b + 39, 1.2, "hold")], (0, 0.3, "hold"))
dust_x = lambda side: track(lambda b, *_: [(b + 30, -112 * side, "hold"), (b + 31, -112 * side, "out"),
                                           (b + 39, -150 * side, "hold")], (0, -112 * side, "hold"))
dust_y = track(lambda b, *_: [(b + 30, -6, "hold"), (b + 31, -6, "out"), (b + 39, -20, "hold")], (0, -6, "hold"))

hop = [
    keyed(ROOT, kfs("x", root_x), kfs("y", root_y)),
    keyed(SQUISH, kfs("scaleX", sx), kfs("scaleY", sy), kfs("rotation", lean)),
    keyed(FACE, kfs("y", face_y)),
    keyed(OPEN_EYES, kfs("opacity", air(0, 1))),
    keyed(HAPPY_EYES, kfs("opacity", air(1, 0))),
    keyed(SMILE, kfs("opacity", mouth(0, 1))),
    keyed(OPEN_MOUTH, kfs("opacity", mouth(1, 0))),
    keyed(CONTACT, kfs("x", root_x), kfs("scaleX", shadow_s), kfs("scaleY", shadow_s), kfs("opacity", shadow_o)),
    keyed(DUST_L, kfs("opacity", dust_o), kfs("scaleX", dust_s), kfs("scaleY", dust_s), kfs("x", dust_x(1)), kfs("y", dust_y)),
    keyed(DUST_R, kfs("opacity", dust_o), kfs("scaleX", dust_s), kfs("scaleY", dust_s), kfs("x", dust_x(-1)), kfs("y", dust_y)),
]

def layer(name, lid, sid, aid):
    return (f'<StateMachineLayer name="{name}" id="{lid}"><AnyState x="200" y="-120"/><ExitState x="400" y="-120"/>'
            f'<EntryState><StateTransition stateToId="{sid}"/></EntryState>'
            f'<AnimationState x="200" animationId="{aid}" id="{sid}"/></StateMachineLayer>')

A_HOP = nid()
sm = '<StateMachine name="State Machine 1" id="0:7">' + layer("Loading", nid(), nid(), A_HOP) + '</StateMachine>'
anims = f'<LinearAnimation loopValue="loop" duration="{T}" name="Loading" id="{A_HOP}">{"".join(hop)}</LinearAnimation>'

doc = (f'<Rive version="1" kind="fragment">\n'
       f'<Artboard defaultStateMachineId="0:7" styleId="0:5" width="{AW}" height="{AH}" name="Mochi Loading" id="0:2">'
       f'<LayoutComponentStyle name="Artboard Style" id="0:5"/>'
       f'{root}{contact}{floor}{sm}{anims}</Artboard>\n</Rive>\n')

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(doc)
print("wrote", OUT, len(doc))
