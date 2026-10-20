"""Generates mochi-idle/scene.rml: a peach mochi head, high front camera on a floor disc, hopping idle loop."""
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
ROOT, SQUISH, FACE, BODY, CONTACT = (nid() for _ in range(5))
EYE_L, EYE_R, OPEN_EYES, HAPPY_EYES = (nid() for _ in range(4))
SMILE, OPEN_MOUTH, BLUSH_L, BLUSH_R, SHINE = (nid() for _ in range(5))

# ---------------------------------------------------------------- the mochi
# Camera sits a little above and in front (like a Duolingo character on its floor disc):
# the mochi faces us upright, a sliver of its top surface shows, and it stands on a flat
# floor ellipse. Hops go up the screen. Flat fills, no outline.
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
    id=FACE, y=-58)

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

CX, GROUND = 170, 244
root = node("Mochi", squish, id=ROOT, x=CX, y=GROUND)
contact = shape("Contact", ell(170, 30), fill(CONTACT_C), id=CONTACT, x=CX, y=GROUND)
floor = shape("Floor", ell(244, 96), fill(FLOOR), x=CX, y=GROUND + 6)

# ---------------------------------------------------------------- idle timeline (132f = 2.2s @60)
T = 132
UP = GROUND - 76
idle = [
    # hop height lives on the root; squash and stretch on the inner node, anchored at the bottom
    keyed(ROOT, kfs("y", [(0, GROUND, "hold"), (30, GROUND, "out"), (52, UP, "soft"), (58, UP, "in"),
                          (76, GROUND, "hold"), (T, GROUND, "hold")])),
    keyed(SQUISH,
        kfs("scaleX", [(0, 1, "soft"), (12, 1.03, "soft"), (20, 1, "io"),
                       (30, 1.18, "out"),                     # anticipation squash
                       (38, 0.86, "soft"), (52, 1.0, "soft"),  # launch stretch, settle at apex
                       (62, 0.96, "in"), (76, 0.92, "linear"),
                       (78, 1.24, "out"),                     # land splat
                       (88, 0.92, "soft"), (97, 1.06, "soft"), (106, 0.98, "soft"), (114, 1, "soft"),
                       (124, 1.02, "soft"), (T, 1, "linear")]),
        kfs("scaleY", [(0, 1, "soft"), (12, 0.97, "soft"), (20, 1, "io"),
                       (30, 0.8, "out"),
                       (38, 1.18, "soft"), (52, 1.0, "soft"),
                       (62, 1.04, "in"), (76, 1.1, "linear"),
                       (78, 0.74, "out"),
                       (88, 1.1, "soft"), (97, 0.95, "soft"), (106, 1.02, "soft"), (114, 1, "soft"),
                       (124, 0.98, "soft"), (T, 1, "linear")])),
    # the face lags a touch behind the body: dips on the squash, lifts on the stretch
    keyed(FACE, kfs("y", [(0, -58, "soft"), (12, -56, "soft"), (20, -58, "io"), (30, -52, "out"),
                          (38, -62, "soft"), (52, -58, "soft"), (76, -60, "linear"), (78, -52, "out"),
                          (90, -61, "soft"), (102, -57, "soft"), (114, -58, "linear"), (T, -58, "hold")])),
    keyed(OPEN_EYES, kfs("opacity", [(0, 1, "hold"), (28, 0, "hold"), (82, 1, "hold"), (T, 1, "hold")])),
    keyed(HAPPY_EYES, kfs("opacity", [(0, 0, "hold"), (28, 1, "hold"), (82, 0, "hold"), (T, 0, "hold")])),
    keyed(SMILE, kfs("opacity", [(0, 1, "hold"), (34, 0, "hold"), (78, 1, "hold"), (T, 1, "hold")])),
    keyed(OPEN_MOUTH,
        kfs("opacity", [(0, 0, "hold"), (34, 1, "hold"), (78, 0, "hold"), (T, 0, "hold")]),
        kfs("scaleY", [(0, 0.6, "hold"), (34, 0.6, "back"), (44, 1.15, "soft"), (60, 0.9, "soft"), (76, 0.6, "hold"),
                       (T, 0.6, "hold")])),
    keyed(EYE_L, kfs("scaleY", [(0, 1, "hold"), (112, 1, "io"), (116, 0.1, "io"), (121, 1, "hold"), (T, 1, "hold")])),
    keyed(EYE_R, kfs("scaleY", [(0, 1, "hold"), (112, 1, "io"), (116, 0.1, "io"), (121, 1, "hold"), (T, 1, "hold")])),
    keyed(BLUSH_L, kfs("opacity", [(0, 0.7, "soft"), (40, 1, "soft"), (96, 0.7, "linear"), (T, 0.7, "hold")])),
    keyed(BLUSH_R, kfs("opacity", [(0, 0.7, "soft"), (40, 1, "soft"), (96, 0.7, "linear"), (T, 0.7, "hold")])),
    # contact shadow on the floor disc shrinks and fades while the mochi is up
    keyed(CONTACT,
        kfs("scaleX", [(0, 1, "soft"), (12, 1.03, "soft"), (20, 1, "io"), (30, 1.14, "out"), (52, 0.6, "soft"),
                       (58, 0.6, "in"), (76, 1, "linear"), (78, 1.22, "out"), (92, 1, "soft"), (T, 1, "linear")]),
        kfs("scaleY", [(0, 1, "soft"), (12, 1.03, "soft"), (20, 1, "io"), (30, 1.14, "out"), (52, 0.6, "soft"),
                       (58, 0.6, "in"), (76, 1, "linear"), (78, 1.22, "out"), (92, 1, "soft"), (T, 1, "linear")]),
        kfs("opacity", [(0, 1, "hold"), (30, 1, "out"), (52, 0.5, "soft"), (58, 0.5, "in"), (76, 1, "hold"),
                        (T, 1, "hold")])),
]

sparkle = [keyed(SHINE, kfs("opacity", [(0, 0.9, "soft"), (45, 0.55, "soft"), (90, 0.9, "linear")]))]

def layer(name, lid, sid, aid):
    return (f'<StateMachineLayer name="{name}" id="{lid}"><AnyState x="200" y="-120"/><ExitState x="400" y="-120"/>'
            f'<EntryState><StateTransition stateToId="{sid}"/></EntryState>'
            f'<AnimationState x="200" animationId="{aid}" id="{sid}"/></StateMachineLayer>')

A_IDLE, A_SHINE = nid(), nid()
sm = ('<StateMachine name="State Machine 1" id="0:7">'
      + layer("Idle", nid(), nid(), A_IDLE) + layer("Shine", nid(), nid(), A_SHINE) + '</StateMachine>')

anims = (f'<LinearAnimation loopValue="loop" duration="{T}" name="Idle" id="{A_IDLE}">{"".join(idle)}</LinearAnimation>'
         f'<LinearAnimation loopValue="loop" duration="90" name="Shine" id="{A_SHINE}">{"".join(sparkle)}</LinearAnimation>')

doc = (f'<Rive version="1" kind="fragment">\n'
       f'<Artboard defaultStateMachineId="0:7" styleId="0:5" width="340" height="330" name="Mochi Idle" id="0:2">'
       f'<LayoutComponentStyle name="Artboard Style" id="0:5"/>'
       f'{root}{contact}{floor}{sm}{anims}</Artboard>\n</Rive>\n')

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(doc)
print("wrote", OUT, len(doc))
