"""Generates otan-idle/scene.rml: Otan the orangutan astronaut, idle loop."""
import itertools, math, sys

OUT = sys.argv[1]
_ids = itertools.count(100)
def nid():
    return f"0:{next(_ids)}"

NAVY, NAVY2, NAVY3 = "FF2B2862", "FF3B3890", "FF1F1C4A"
ORANGE, ORANGE_D = "FFF5822A", "FFD9661C"
FUR_T, FUR_B = "FFF2913F", "FFDD6526"
SKIN_T, SKIN_B = "FFFCD3A6", "FFF5B27B"
LAV, LAV_L = "FFDCDAF0", "FFE9E8F7"
WHITE, YELLOW, PINK = "FFFFFFFF", "FFF9B42D", "FFF4917A"

def solid(c):
    return f'<SolidColor colorValue="{c}" name="C"/>'

def fill(c=None, grad=None, feather=None, extra=""):
    paint = grad if grad else solid(c)
    rule = ' fillRule="clockwise"' if feather else ""
    fe = f'<Feather strength="{feather}" name="F"/>' if feather else ""
    return f'<Fill{rule} name="Fill">{paint}{fe}{extra}</Fill>'

def stroke(c, t, cap="round", grad=None):
    paint = grad if grad else solid(c)
    return f'<Stroke thickness="{t}" cap="{cap}" join="round" name="Stroke">{paint}</Stroke>'

def lin(x1, y1, x2, y2, *stops):
    s = "".join(f'<GradientStop colorValue="{c}" position="{p}"/>' for c, p in stops)
    return f'<LinearGradient startX="{x1}" startY="{y1}" endX="{x2}" endY="{y2}" name="G">{s}</LinearGradient>'

def rad(x1, y1, x2, y2, *stops):
    s = "".join(f'<GradientStop colorValue="{c}" position="{p}"/>' for c, p in stops)
    return f'<RadialGradient startX="{x1}" startY="{y1}" endX="{x2}" endY="{y2}" name="G">{s}</RadialGradient>'

def attrs(**kw):
    out = []
    for k, v in kw.items():
        if v is None:
            continue
        out.append(f'{k}="{v}"')
    return " ".join(out)

def shape(name, geo, *paints, id=None, **t):
    return f'<Shape {attrs(**t)} name="{name}"{f" id={chr(34)}{id}{chr(34)}" if id else ""}>{geo}{"".join(paints)}</Shape>'

def node(name, *children, id=None, **t):
    return f'<Node {attrs(**t)} name="{name}"{f" id={chr(34)}{id}{chr(34)}" if id else ""}>{"".join(children)}</Node>'

def ell(w, h, **t):
    return f'<Ellipse {attrs(width=w, height=h, **t)} name="P"/>'

def rect(w, h, r, **t):
    return f'<Rectangle {attrs(width=w, height=h, cornerRadiusTL=r, **t)} name="P"/>'

def path(verts, closed=True):
    return f'<PointsPath isClosed="{str(closed).lower()}" name="P">{"".join(verts)}</PointsPath>'

def sv(x, y, r=None):
    return f'<StraightVertex {attrs(x=x, y=y, radius=r)}/>'

def mv(x, y, rot, d):
    return f'<CubicMirroredVertex x="{x}" y="{y}" rotation="{rot}" distance="{d}"/>'

def dv(x, y, ir, idist, orot, odist):
    return (f'<CubicDetachedVertex x="{x}" y="{y}" inRotation="{ir}" inDistance="{idist}" '
            f'outRotation="{orot}" outDistance="{odist}"/>')

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


# Camera looks down at ~165 deg (almost overhead): we see the top of the helmet dome,
# the visor sits low and foreshortened at the front, the body is a disc around the head.
# Turning is an in-plane rotation of the whole character; hopping comes toward the camera.

# ---------------------------------------------------------------- ids of animated parts
ROOT, HEAD, ARM_L, ARM_R, BOOT_L, BOOT_R, SHADOW = (nid() for _ in range(7))
PUP_L, PUP_R, EYE_L, EYE_R, OPEN_EYES, HAPPY_EYES = (nid() for _ in range(6))
MOUTH, MOUTH_SHAPE, BROWS, ANTENNA, BALL_GLOW, LIGHT, VISOR = (nid() for _ in range(7))

# ---------------------------------------------------------------- face (drawn upright, then foreshortened)
def eye(name, eid, pid, x):
    pupil = node(f"{name} Pupil",
        shape("Glint", ell(8, 8), fill(WHITE), x=5, y=-7),
        shape("Glint Small", ell(4, 4), fill(WHITE), x=-4, y=6, opacity=0.8),
        shape("Iris", ell(23, 29), fill(grad=lin(0, -14, 0, 14, (NAVY2, 0), (NAVY3, 1)))),
        id=pid)
    return node(name, pupil, id=eid, x=x, y=-4)

happy_arc = lambda x: shape("Happy", path([sv(-10, 4), mv(0, -6, 0, 7), sv(10, 4)], closed=False),
                            stroke(NAVY3, 5), x=x, y=-4)

face = node("Face",
    node("Open Eyes", eye("Eye L", EYE_L, PUP_L, -24), eye("Eye R", EYE_R, PUP_R, 24), id=OPEN_EYES),
    node("Happy Eyes", happy_arc(-24), happy_arc(24), id=HAPPY_EYES, opacity=0),
    node("Brows",
        shape("Brow L", rect(16, 5, 2.5), fill("FFC2551C"), x=-25, y=-31, rotation=-0.28),
        shape("Brow R", rect(16, 5, 2.5), fill("FFC2551C"), x=25, y=-31, rotation=0.28),
        id=BROWS),
    shape("Nose", ell(5, 4, x=-4) + ell(5, 4, x=4), fill("FF9A5430"), y=13),
    node("Mouth",
        shape("Tongue", ell(20, 10, y=15), fill("FFE8637A"), f'<ClippingShape sourceId="{MOUTH_SHAPE}" name="Clip"/>'),
        shape("Mouth Shape", path([sv(-15, 0, 3), sv(15, 0, 3), mv(0, 19, 3.1415927, 10)]),
              fill("FF3B1F3A"), id=MOUTH_SHAPE),
        id=MOUTH, y=23),
    shape("Blush L", ell(22, 13), fill(PINK, feather=4), x=-41, y=20, opacity=0.85),
    shape("Blush R", ell(22, 13), fill(PINK, feather=4), x=41, y=20, opacity=0.85),
    shape("Skin", ell(108, 88, y=14) + ell(56, 52, x=-23, y=-6) + ell(56, 52, x=23, y=-6),
          fill(grad=lin(0, -30, 0, 58, (SKIN_T, 0), (SKIN_B, 1)))),
    shape("Fur", ell(150, 132, y=-2), fill(grad=lin(0, -66, 0, 64, (FUR_T, 0), (FUR_B, 1)))),
    shape("Ear L Inner", ell(15, 20), fill(SKIN_B), x=-72, y=8),
    shape("Ear L", ell(30, 38), fill(FUR_B), x=-72, y=8),
    shape("Ear R Inner", ell(15, 20), fill(SKIN_B), x=72, y=8),
    shape("Ear R", ell(30, 38), fill(FUR_B), x=72, y=8),
    f'<ClippingShape sourceId="{VISOR}" name="Clip"/>',
    y=5, scaleX=0.57, scaleY=0.42)

front = node("Front",
    shape("Shine", path([sv(-37, -8), mv(-27, -19, -0.6, 7), sv(-13, -25)], closed=False),
          stroke(WHITE, 4), opacity=0.45),
    face,
    shape("Visor", ell(100, 60), fill(grad=lin(0, -30, 0, 30, (NAVY2, 0), (NAVY3, 1))), id=VISOR),
    y=28)

headphone = lambda x: node("Headphone",
    shape("Pad", ell(8, 26), fill(ORANGE_D)),
    shape("Cup", ell(20, 42), fill(grad=lin(0, -21, 0, 21, ("FFFF9A45", 0), (ORANGE_D, 1)))),
    x=x, y=5)

antenna = node("Antenna",
    shape("Glow", ell(26, 26), fill(YELLOW, feather=8), y=-18, opacity=0.55, id=BALL_GLOW),
    shape("Ball", ell(14, 14), fill(grad=rad(-3, -3, 8, 8, ("FFFFE08A", 0), (YELLOW, 1))), y=-18),
    shape("Stalk", path([sv(0, 0), sv(0, -14)], closed=False), stroke(NAVY, 4)),
    shape("Base", ell(12, 8), fill(NAVY)),
    id=ANTENNA, x=-24, y=-46, rotation=-0.3)

# head-local origin is the centre of the dome, so looking around turns about it
head = node("Head",
    antenna,
    shape("Dome Shine", ell(36, 13), fill(WHITE, feather=3), x=-24, y=-33, rotation=-0.5, opacity=0.9),
    front,
    shape("Band", path([sv(-46, -30), mv(0, -50, 0, 26), sv(46, -30)], closed=False), stroke(ORANGE, 7)),
    headphone(-66), headphone(66),
    shape("Helmet", ell(136, 128),
          fill(grad=rad(-30, -38, 96, 56, (WHITE, 0), (WHITE, 0.4), ("FFE3E1F4", 1))),
          stroke(LAV, 4)),
    id=HEAD, y=-30)

# ---------------------------------------------------------------- body
def arm(name, aid, side):
    s = side
    return node(name,
        shape("Glove", ell(26, 24), fill(grad=lin(0, -12, 0, 12, (WHITE, 0), (LAV_L, 1))), stroke(LAV, 3),
              x=-8 * s, y=34),
        shape("Cuff", rect(26, 8, 4), fill(ORANGE), x=-6 * s, y=23, rotation=0.25 * s),
        shape("Sleeve", path([sv(0, 0), sv(-7 * s, 24)], closed=False), stroke(LAV, 26), stroke(WHITE, 21)),
        id=aid, x=-70 * s, y=22, rotation=0.32 * s)

boot = lambda name, bid, x: node(name,
    shape("Toe Shine", ell(12, 5), fill(WHITE), y=2, opacity=0.25),
    shape("Boot", rect(34, 24, 11), fill(grad=lin(0, -12, 0, 12, (NAVY2, 0), (NAVY, 1)))),
    id=bid, x=x, y=88)

body = node("Body",
    node("Chest Panel",
        shape("Light", ell(5, 4), fill("FF6FD3A8"), x=9, id=LIGHT),
        shape("Light Y", ell(5, 4), fill(YELLOW)),
        shape("Light O", ell(5, 4), fill(ORANGE), x=-9),
        shape("Chest", rect(36, 12, 5), fill(NAVY)),
        y=64),
    shape("Collar", ell(108, 58, y=24), stroke(ORANGE, 7)),
    shape("Suit", ell(162, 114, y=30), fill(grad=lin(0, -26, 0, 86, (WHITE, 0), (LAV_L, 1))), stroke(LAV, 3)))

root = node("Otan", head, arm("Arm L", ARM_L, 1), arm("Arm R", ARM_R, -1), body,
            boot("Boot L", BOOT_L, -30), boot("Boot R", BOOT_R, 30),
            id=ROOT, x=160, y=150)

shadow = shape("Shadow", ell(214, 150), fill("FFE7E7EC"), id=SHADOW, x=160, y=184)

# ---------------------------------------------------------------- the idle timeline (156f = 2.6s @60)
T = 156
TURN = 6.2831855
idle = [
    keyed(ROOT,
        # full spin in the floor plane, with a wind-up and a small overshoot
        kfs("rotation", [(0, 0, "hold"), (52, 0, "io"), (60, -0.2, "io"), (84, TURN + 0.08, "soft"),
                         (92, TURN, "hold"), (156, TURN, "hold")]),
        # breathe, crouch, hop toward the camera, land
        kfs("scaleX", [(0, 1, "soft"), (27, 1.015, "soft"), (54, 1, "io"), (60, 0.95, "io"), (72, 1.03, "io"),
                       (86, 1, "io"), (90, 0.93, "out"), (104, 1.2, "soft"), (112, 1.2, "in"), (122, 1.05, "back"),
                       (132, 0.99, "soft"), (144, 1, "linear"), (156, 1, "linear")]),
        kfs("scaleY", [(0, 1, "soft"), (27, 0.99, "soft"), (54, 1, "io"), (60, 0.94, "io"), (72, 1.03, "io"),
                       (86, 1, "io"), (90, 0.91, "out"), (104, 1.22, "soft"), (112, 1.22, "in"), (122, 0.95, "back"),
                       (132, 1.01, "soft"), (144, 1, "linear"), (156, 1, "linear")]),
        kfs("y", [(0, 150, "hold"), (90, 150, "out"), (104, 138, "soft"), (112, 138, "in"), (122, 150, "linear"),
                  (156, 150, "hold")])),
    # looking around = the head turns left, then right, on the body
    keyed(HEAD, kfs("rotation", [(0, 0, "soft"), (10, -0.3, "soft"), (24, -0.3, "soft"), (34, 0.3, "soft"),
                                 (48, 0.3, "soft"), (56, 0, "io"), (92, 0, "soft"), (102, 0.1, "soft"),
                                 (114, -0.1, "soft"), (126, 0, "linear"), (156, 0, "hold")])),
    keyed(PUP_L, kfs("x", [(0, 0, "soft"), (8, -6, "hold"), (26, -6, "soft"), (34, 6, "hold"), (48, 6, "soft"),
                           (56, 0, "linear"), (156, 0, "linear")])),
    keyed(PUP_R, kfs("x", [(0, 0, "soft"), (8, -6, "hold"), (26, -6, "soft"), (34, 6, "hold"), (48, 6, "soft"),
                           (56, 0, "linear"), (156, 0, "linear")])),
    keyed(EYE_L, kfs("scaleY", [(0, 1, "hold"), (142, 1, "io"), (146, 0.08, "io"), (151, 1, "hold"), (156, 1, "hold")])),
    keyed(EYE_R, kfs("scaleY", [(0, 1, "hold"), (142, 1, "io"), (146, 0.08, "io"), (151, 1, "hold"), (156, 1, "hold")])),
    keyed(OPEN_EYES, kfs("opacity", [(0, 1, "hold"), (88, 0, "hold"), (124, 1, "hold"), (156, 1, "hold")])),
    keyed(HAPPY_EYES, kfs("opacity", [(0, 0, "hold"), (88, 1, "hold"), (124, 0, "hold"), (156, 0, "hold")])),
    keyed(MOUTH,
        kfs("scaleX", [(0, 1, "hold"), (86, 1, "out"), (96, 1.2, "soft"), (120, 1.2, "soft"), (128, 1, "linear"), (156, 1, "hold")]),
        kfs("scaleY", [(0, 1, "hold"), (86, 1, "out"), (96, 1.35, "soft"), (120, 1.35, "soft"), (128, 1, "linear"), (156, 1, "hold")])),
    keyed(BROWS, kfs("y", [(0, 0, "hold"), (86, 0, "out"), (96, -4, "soft"), (120, -4, "soft"), (128, 0, "linear"), (156, 0, "hold")])),
    # arms: sway, flung out by the spin, flapping in the hop
    keyed(ARM_L, kfs("rotation", [(0, 0.32, "soft"), (27, 0.4, "soft"), (54, 0.32, "io"), (60, 0.15, "io"),
                                  (72, 0.8, "io"), (86, 0.4, "io"), (90, 0.3, "out"), (98, 1.3, "soft"),
                                  (104, 0.8, "soft"), (110, 1.4, "soft"), (116, 0.9, "soft"), (122, 0.5, "back"),
                                  (134, 0.28, "soft"), (146, 0.32, "linear"), (156, 0.32, "linear")])),
    keyed(ARM_R, kfs("rotation", [(0, -0.32, "soft"), (27, -0.4, "soft"), (54, -0.32, "io"), (60, -0.15, "io"),
                                  (72, -0.8, "io"), (86, -0.4, "io"), (90, -0.3, "out"), (98, -1.3, "soft"),
                                  (104, -0.8, "soft"), (110, -1.4, "soft"), (116, -0.9, "soft"), (122, -0.5, "back"),
                                  (134, -0.28, "soft"), (146, -0.32, "linear"), (156, -0.32, "linear")])),
    keyed(BOOT_R,
        kfs("y", [(0, 88, "hold"), (96, 88, "soft"), (104, 96, "soft"), (114, 88, "linear"), (156, 88, "hold")]),
        kfs("rotation", [(0, 0, "hold"), (96, 0, "soft"), (104, -0.45, "soft"), (114, 0, "linear"), (156, 0, "hold")])),
    keyed(BOOT_L,
        kfs("y", [(0, 88, "hold"), (98, 88, "soft"), (106, 92, "soft"), (116, 88, "linear"), (156, 88, "hold")]),
        kfs("rotation", [(0, 0, "hold"), (98, 0, "soft"), (106, 0.3, "soft"), (116, 0, "linear"), (156, 0, "hold")])),
    keyed(ANTENNA, kfs("rotation", [(0, -0.3, "soft"), (14, -0.15, "soft"), (30, -0.45, "soft"), (54, -0.3, "io"),
                                    (72, 0.5, "io"), (90, -0.5, "soft"), (100, -0.1, "soft"), (110, -0.55, "soft"),
                                    (122, 0.05, "back"), (132, -0.45, "soft"), (144, -0.25, "soft"), (156, -0.3, "linear")])),
    # floor disc: shrinks while Otan is in the air
    keyed(SHADOW,
        kfs("scaleX", [(0, 1, "soft"), (27, 1.01, "soft"), (54, 1, "hold"), (90, 1.03, "out"), (104, 0.88, "soft"),
                       (112, 0.88, "in"), (122, 1.04, "back"), (134, 1, "linear"), (156, 1, "linear")]),
        kfs("scaleY", [(0, 1, "soft"), (27, 1.01, "soft"), (54, 1, "hold"), (90, 1.03, "out"), (104, 0.88, "soft"),
                       (112, 0.88, "in"), (122, 1.04, "back"), (134, 1, "linear"), (156, 1, "linear")])),
]

glow = [keyed(BALL_GLOW, kfs("opacity", [(0, 0.25, "soft"), (40, 0.75, "soft"), (80, 0.25, "linear")])),
        keyed(LIGHT, kfs("opacity", [(0, 1, "hold"), (30, 0.2, "hold"), (40, 1, "hold"), (80, 1, "hold")]))]

def layer(name, lid, sid, aid):
    return (f'<StateMachineLayer name="{name}" id="{lid}"><AnyState x="200" y="-120"/><ExitState x="400" y="-120"/>'
            f'<EntryState><StateTransition stateToId="{sid}"/></EntryState>'
            f'<AnimationState x="200" animationId="{aid}" id="{sid}"/></StateMachineLayer>')

A_IDLE, A_GLOW = nid(), nid()
sm = ('<StateMachine name="State Machine 1" id="0:7">'
      + layer("Idle", nid(), nid(), A_IDLE) + layer("Glow", nid(), nid(), A_GLOW) + '</StateMachine>')

anims = (f'<LinearAnimation loopValue="loop" duration="{T}" name="Idle" id="{A_IDLE}">{"".join(idle)}</LinearAnimation>'
         f'<LinearAnimation loopValue="loop" duration="80" name="Glow" id="{A_GLOW}">{"".join(glow)}</LinearAnimation>')

doc = (f'<Rive version="1" kind="fragment">\n'
       f'<Artboard defaultStateMachineId="0:7" styleId="0:5" width="320" height="290" name="Otan Idle" id="0:2">'
       f'<LayoutComponentStyle name="Artboard Style" id="0:5"/>'
       f'{root}{shadow}{sm}{anims}</Artboard>\n</Rive>\n')

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(doc)
print("wrote", OUT, len(doc))
