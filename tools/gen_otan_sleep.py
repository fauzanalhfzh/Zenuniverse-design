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


# Otan asleep, lying on his back, seen from the same near-overhead camera and with the
# same proportions as otan-idle. The body is drawn upright (head up, feet down) inside a
# "Lying" node that is rotated so the head rests at the right and the feet point lower-left.

PURPLE, PURPLE_D, PETAL, PETAL_D = "FFA77BF0", "FF7A4FD6", "FFF6A9CC", "FFE36FA6"
LIE = 1.25        # rotation of the whole body on the floor
T = 240           # 4s loop @60

ROOT, LYING, HEAD, TORSO, ARM_FOLD, MOUTH, BALL_GLOW, LIGHT, VISOR = (nid() for _ in range(9))
WING_L, WING_R, BUTTERFLY = (nid() for _ in range(3))
ZS = [nid() for _ in range(3)]
PETALS = [nid() for _ in range(4)]
FLOWERS = [nid() for _ in range(4)]

def tube(pts, w, c=WHITE, edge=LAV):
    """A rounded limb: an outline stroke under a fill stroke along a polyline."""
    return path([sv(x, y, 18) for x, y in pts], closed=False), stroke(edge, w + 5), stroke(c, w)

# ---------------------------------------------------------------- face (faces the camera: not foreshortened)
sleep_arc = lambda x: shape("Closed Eye", path([sv(-10, -2), mv(0, 5, 0, 7), sv(10, -2)], closed=False),
                            stroke(NAVY3, 4.5), x=x, y=-2)

face = node("Face",
    sleep_arc(-24), sleep_arc(24),
    shape("Brow L", rect(15, 5, 2.5), fill("FFC2551C"), x=-25, y=-24, rotation=-0.12),
    shape("Brow R", rect(15, 5, 2.5), fill("FFC2551C"), x=25, y=-24, rotation=0.12),
    shape("Nose", ell(5, 4, x=-4) + ell(5, 4, x=4), fill("FF9A5430"), y=12),
    shape("Smile", path([sv(-9, 0), mv(0, 6, 0, 6), sv(9, 0)], closed=False), stroke("FF3B1F3A", 3.5),
          id=MOUTH, y=24),
    shape("Blush L", ell(24, 14), fill(PINK, feather=4), x=-40, y=16, opacity=0.9),
    shape("Blush R", ell(24, 14), fill(PINK, feather=4), x=40, y=16, opacity=0.9),
    shape("Skin", ell(108, 88, y=14) + ell(56, 52, x=-23, y=-6) + ell(56, 52, x=23, y=-6),
          fill(grad=lin(0, -30, 0, 58, (SKIN_T, 0), (SKIN_B, 1)))),
    shape("Fur", ell(150, 132, y=-2), fill(grad=lin(0, -66, 0, 64, (FUR_T, 0), (FUR_B, 1)))),
    shape("Tuft", path([sv(-24, 10), dv(-8, -16, 2.3, 10, -0.5, 9), dv(4, -6, -2.2, 6, -1.0, 9),
                        dv(20, -15, -2.6, 8, 1.7, 11), sv(24, 10)]), fill(FUR_T), y=-62),
    shape("Ear L Inner", ell(15, 20), fill(SKIN_B), x=-72, y=8),
    shape("Ear L", ell(30, 38), fill(FUR_B), x=-72, y=8),
    shape("Ear R Inner", ell(15, 20), fill(SKIN_B), x=72, y=8),
    shape("Ear R", ell(30, 38), fill(FUR_B), x=72, y=8),
    f'<ClippingShape sourceId="{VISOR}" name="Clip"/>',
    y=6, scaleX=0.6, scaleY=0.6)

wing = lambda wid, side: node("Wing",
    shape("Spot", ell(9, 12), fill(YELLOW), x=10 * side, y=-6),
    shape("Upper", ell(22, 26), fill(grad=lin(0, -13, 0, 13, (PURPLE, 0), (PURPLE_D, 1))), stroke(NAVY, 1.5),
          x=11 * side, y=-6, rotation=0.35 * side),
    shape("Lower", ell(14, 16), fill(PURPLE_D), stroke(NAVY, 1.5), x=8 * side, y=9, rotation=-0.3 * side),
    id=wid)

butterfly = node("Butterfly",
    shape("Antennae", path([sv(-5, -20), sv(0, -9), sv(5, -20)], closed=False), stroke(NAVY, 1.5)),
    shape("Body", ell(6, 22), fill(NAVY)),
    wing(WING_L, -1), wing(WING_R, 1),
    id=BUTTERFLY, x=26, y=-60, rotation=0.3)

head = node("Head",
    butterfly,
    shape("Dome Shine", ell(34, 12), fill(WHITE, feather=3), x=-30, y=-38, rotation=-0.7, opacity=0.9),
    node("Front",
        shape("Shine", path([sv(-38, -12), mv(-28, -30, -0.8, 9), sv(-10, -40)], closed=False),
              stroke(WHITE, 4), opacity=0.45),
        face,
        shape("Visor", ell(100, 92), fill(grad=lin(0, -46, 0, 46, (NAVY2, 0), (NAVY3, 1))), id=VISOR),
        y=4),
    shape("Band", path([sv(-56, -18), mv(0, -56, 0, 34), sv(56, -18)], closed=False), stroke(ORANGE, 6)),
    node("Headphone L",
        shape("Pad", ell(8, 26), fill(ORANGE_D)),
        shape("Cup", ell(20, 42), fill(grad=lin(0, -21, 0, 21, ("FFFF9A45", 0), (ORANGE_D, 1)))), x=-66, y=4),
    node("Headphone R",
        shape("Pad", ell(8, 26), fill(ORANGE_D)),
        shape("Cup", ell(20, 42), fill(grad=lin(0, -21, 0, 21, ("FFFF9A45", 0), (ORANGE_D, 1)))), x=66, y=4),
    shape("Helmet", ell(136, 128), fill(grad=rad(-30, -38, 96, 56, (WHITE, 0), (WHITE, 0.4), ("FFE3E1F4", 1))),
          stroke(LAV, 4)),
    node("Antenna",
        shape("Glow", ell(24, 24), fill(YELLOW, feather=8), y=-18, opacity=0.4, id=BALL_GLOW),
        shape("Ball", ell(13, 13), fill(grad=rad(-3, -3, 8, 8, ("FFFFE08A", 0), (YELLOW, 1))), y=-18),
        shape("Stalk", path([sv(0, 0), sv(0, -14)], closed=False), stroke(NAVY, 4)),
        x=-34, y=-54, rotation=-0.5),
    # head is turned on the pillow so the face reads nearly upright on screen
    id=HEAD, y=-96, rotation=-1.0)

glove = lambda x, y, r=0: (
    shape("Glove", ell(28, 25), fill(grad=lin(0, -12, 0, 12, (WHITE, 0), (LAV_L, 1))), stroke(LAV, 3),
          x=x, y=y, rotation=r))

torso = node("Torso",
    node("Folded Arm",
        glove(-6, 16, 0.4),
        shape("Cuff", rect(9, 26, 4.5), fill(ORANGE), x=-20, y=15, rotation=-0.15),
        shape("Sleeve", *tube([(-46, -30), (-56, 6), (-22, 15)], 24)),
        id=ARM_FOLD),
    node("Chest Panel",
        shape("Light", ell(5, 5), fill("FF6FD3A8"), x=9, id=LIGHT),
        shape("Light Y", ell(5, 5), fill(YELLOW)),
        shape("Light O", ell(5, 5), fill(ORANGE), x=-9),
        shape("Chest", rect(36, 16, 6), fill(NAVY)),
        x=18, y=-10),
    shape("Collar", ell(96, 30), stroke(ORANGE, 7), y=-40),
    shape("Belt", rect(118, 10, 5), fill(ORANGE), y=56),
    shape("Suit", rect(122, 126, 52, y=12), fill(grad=lin(-60, 0, 60, 0, (WHITE, 0), (LAV_L, 1))), stroke(LAV, 3)),
    id=TORSO)

lying = node("Lying",
    head,
    torso,
    node("Side Arm", glove(64, 50, -0.2),
         shape("Cuff", rect(26, 8, 4), fill(ORANGE), x=63, y=37, rotation=-0.12),
         shape("Sleeve", *tube([(46, -26), (60, 8), (63, 36)], 24))),
    node("Boot L", shape("Shine", ell(22, 10), fill("FF5A57B8"), y=-6),
         shape("Boot", ell(42, 36), fill(grad=lin(0, -18, 0, 18, (NAVY2, 0), (NAVY, 1)))), x=-31, y=138, rotation=0.1),
    node("Boot R", shape("Shine", ell(22, 10), fill("FF5A57B8"), y=-6),
         shape("Boot", ell(42, 36), fill(grad=lin(0, -18, 0, 18, (NAVY2, 0), (NAVY, 1)))), x=29, y=138, rotation=-0.3),
    shape("Knee Band L", rect(40, 8, 4), fill(ORANGE), x=-28, y=102, rotation=0.09),
    shape("Knee Band R", rect(40, 8, 4), fill(ORANGE), x=39, y=112, rotation=0.47),
    shape("Leg L", *tube([(-24, 62), (-30, 126)], 36)),
    shape("Leg R", *tube([(24, 62), (46, 96), (30, 126)], 36)),
    id=LYING, x=210, y=168, rotation=LIE)

shadow = shape("Shadow", ell(336, 132), fill("FFE7E7EC"), x=206, y=196, rotation=-0.28)

def flower(fid, x, y, size, rot):
    petals = "".join(shape("Petal", ell(size * 0.5, size * 0.5), fill(PETAL), stroke(PETAL_D, 1.5),
                           x=round(size * 0.27 * math.sin(i * 1.2566), 2),
                           y=round(-size * 0.27 * math.cos(i * 1.2566), 2)) for i in range(5))
    return node("Flower", shape("Center", ell(size * 0.28, size * 0.28), fill(PETAL_D)), petals,
                id=fid, x=x, y=y, rotation=rot)

flowers = [flower(FLOWERS[0], 58, 118, 40, 0.2), flower(FLOWERS[1], 398, 140, 32, -0.3),
           flower(FLOWERS[2], 250, 296, 36, 0.5), flower(FLOWERS[3], 372, 262, 26, 0.1)]

petal = lambda pid: shape("Falling Petal", ell(16, 9), fill(PETAL), stroke(PETAL_D, 1.2), id=pid, opacity=0)

def z_letter(zid, size):
    h = size / 2
    return shape("Z", path([sv(-h, -h), sv(h, -h), sv(-h, h), sv(h, h)], closed=False),
                 stroke(NAVY2, 3.5), id=zid, opacity=0)

zs = [z_letter(ZS[0], 14), z_letter(ZS[1], 18), z_letter(ZS[2], 22)]

# ---------------------------------------------------------------- motion helpers
def sampled(prop, fn, step=8, digits=3):
    frames = list(range(0, T, step)) + [T]
    return kfs(prop, [(f, round(fn(f), digits), "linear") for f in frames])

def breath(f, lo, hi):
    """Slow sine breathing, one breath every 2s (two per loop)."""
    return lo + (hi - lo) * (0.5 - 0.5 * math.cos(f / T * 4 * math.pi))

def zz(i):
    """Z i floats up from the helmet, growing and swaying, then fades."""
    off = i * 80
    def phase(f):
        return ((f - off) % T) / T
    def life(f):
        p = phase(f)
        return min(p / 0.6, 1.0)
    sx, sy = 352, 96
    def x(f):
        q = life(f)
        return sx + 30 * q + 8 * math.sin(q * 2 * math.pi)
    def y(f):
        return sy - 68 * life(f)
    def sc(f):
        return 0.5 + 0.6 * life(f)
    def op(f):
        p = phase(f)
        if p > 0.6:
            return 0
        q = p / 0.6
        return min(1, q / 0.15) * min(1, (1 - q) / 0.3)
    return keyed(ZS[i], sampled("x", x), sampled("y", y), sampled("scaleX", sc), sampled("scaleY", sc),
                 sampled("opacity", op), sampled("rotation", lambda f: -0.2 + 0.25 * life(f)))

def drift(i, start, end):
    """A petal glides across the floor in a lazy zigzag, tumbling as it goes."""
    off = i * 60
    (x0, y0), (x1, y1) = start, end
    def p(f):
        return ((f - off) % T) / T
    def op(f):
        q = p(f)
        return 0.9 * min(1, q / 0.12) * min(1, (1 - q) / 0.12)
    return keyed(PETALS[i],
                 sampled("x", lambda f: x0 + (x1 - x0) * p(f) + 14 * math.sin(p(f) * 6 * math.pi)),
                 sampled("y", lambda f: y0 + (y1 - y0) * p(f)),
                 sampled("rotation", lambda f: 0.8 + p(f) * 9.0),
                 sampled("scaleY", lambda f: 0.4 + 0.6 * abs(math.cos(p(f) * 5 * math.pi))),
                 sampled("opacity", op))

sleep = [
    # chest rises and falls; the folded arm rides on it; head rocks gently on the pillow
    keyed(TORSO, sampled("scaleX", lambda f: breath(f, 1, 1.035))),
    keyed(ARM_FOLD, sampled("x", lambda f: breath(f, 0, -2.5))),
    keyed(HEAD, sampled("rotation", lambda f: -1.0 + breath(f, 0, 0.045)),
                sampled("y", lambda f: -96 + breath(f, 0, -1.5))),
    keyed(MOUTH, sampled("scaleY", lambda f: breath(f, 0.75, 1.15))),
    # the butterfly rests, flutters twice, rests again
    keyed(WING_L, kfs("scaleX", [(0, 1, "hold"), (40, 1, "soft"), (46, 0.2, "soft"), (52, 1, "soft"), (58, 0.2, "soft"),
                                 (64, 1, "hold"), (160, 1, "soft"), (166, 0.25, "soft"), (172, 1, "hold"), (240, 1, "hold")])),
    keyed(WING_R, kfs("scaleX", [(0, 1, "hold"), (40, 1, "soft"), (46, 0.2, "soft"), (52, 1, "soft"), (58, 0.2, "soft"),
                                 (64, 1, "hold"), (160, 1, "soft"), (166, 0.25, "soft"), (172, 1, "hold"), (240, 1, "hold")])),
    keyed(BUTTERFLY, kfs("rotation", [(0, 0.3, "soft"), (40, 0.3, "soft"), (58, 0.12, "soft"), (90, 0.3, "soft"),
                                      (240, 0.3, "linear")]),
                     kfs("y", [(0, -60, "hold"), (40, -60, "soft"), (50, -66, "soft"), (64, -60, "hold"), (240, -60, "hold")])),
    keyed(BALL_GLOW, sampled("opacity", lambda f: breath(f, 0.15, 0.6))),
    keyed(LIGHT, kfs("opacity", [(0, 1, "hold"), (60, 0.25, "hold"), (75, 1, "hold"), (180, 0.25, "hold"), (195, 1, "hold"),
                                 (240, 1, "hold")])),
    # flowers sway in the breeze
    *[keyed(fid, sampled("rotation", lambda f, r=r, k=k: r + 0.12 * math.sin(f / T * 2 * math.pi + k)))
      for k, (fid, r) in enumerate(zip(FLOWERS, [0.2, -0.3, 0.5, 0.1]))],
    *[zz(i) for i in range(3)],
    drift(0, (30, 60), (170, 120)), drift(1, (130, 20), (300, 70)),
    drift(2, (20, 250), (190, 300)), drift(3, (300, 260), (410, 300)),
]

def layer(name, lid, sid, aid):
    return (f'<StateMachineLayer name="{name}" id="{lid}"><AnyState x="200" y="-120"/><ExitState x="400" y="-120"/>'
            f'<EntryState><StateTransition stateToId="{sid}"/></EntryState>'
            f'<AnimationState x="200" animationId="{aid}" id="{sid}"/></StateMachineLayer>')

A_SLEEP = nid()
sm = '<StateMachine name="State Machine 1" id="0:7">' + layer("Sleep", nid(), nid(), A_SLEEP) + '</StateMachine>'
anims = f'<LinearAnimation loopValue="loop" duration="{T}" name="Sleep" id="{A_SLEEP}">{"".join(sleep)}</LinearAnimation>'

doc = (f'<Rive version="1" kind="fragment">\n'
       f'<Artboard defaultStateMachineId="0:7" styleId="0:5" width="420" height="320" name="Otan Sleep" id="0:2">'
       f'<LayoutComponentStyle name="Artboard Style" id="0:5"/>'
       f'{"".join(zs)}{"".join(petal(p) for p in PETALS)}{lying}{"".join(flowers)}{shadow}{sm}{anims}'
       f'</Artboard>\n</Rive>\n')

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(doc)
print("wrote", OUT, len(doc))
