"""Generates otan-happy/scene.rml: Otan the orangutan astronaut, front view, idle + happy wave.

Drawn in the reference image's own pixel space (2000x1500) inside a scaled "Scene" node,
so every coordinate below can be read straight off the reference.

usage: gen_otan_happy.py <out.rml> [--entry idle|happy|wave|toidle] [--is-happy]
  Debug aids, since the CLI cannot set inputs: --entry picks the layer's first state,
  --is-happy starts the isHappy input at true.
"""
import itertools, math, sys

OUT = sys.argv[1]
ENTRY = sys.argv[sys.argv.index("--entry") + 1] if "--entry" in sys.argv else "idle"
START_HAPPY = "--is-happy" in sys.argv
_ids = itertools.count(100)
def nid():
    return f"0:{next(_ids)}"

NAVY, NAVY2, NAVY3 = "FF262357", "FF2E2B6E", "FF1C1946"
ORANGE, ORANGE_L, ORANGE_D = "FFF27A2A", "FFF89A55", "FFDD6420"
FUR_T, FUR_B, BROW = "FFEE7A2C", "FFD9611D", "FFC4561A"
SKIN_T, SKIN_B = "FFFBC690", "FFF4A866"
WHITE, LAV, LAV_D = "FFFFFFFF", "FFE6E7F7", "FFC9CCEE"
BLUE, BLUE_D, SEAM = "FF7D9BE0", "FF4E6EC2", "FFA9B9EC"
PINK, PINK_D, BLUSH = "FFF392C0", "FFE2588F", "FFF7957E"
PURPLE, PURPLE_L, YELLOW = "FFA76BDB", "FFC395EC", "FFF8C23A"

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
    return " ".join(f'{k}="{round(v, 4) if isinstance(v, float) else v}"' for k, v in kw.items() if v is not None)

def _id(id):
    return f' id="{id}"' if id else ""

def shape(name, geo, *paints, id=None, **t):
    return f'<Shape {attrs(**t)} name="{name}"{_id(id)}>{geo}{"".join(paints)}</Shape>'

def node(name, *children, id=None, **t):
    return f'<Node {attrs(**t)} name="{name}"{_id(id)}>{"".join(children)}</Node>'

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

def smooth(pts, tension=1.0):
    """Closed Catmull-Rom curve through pts: every corner flows into the next."""
    n, out = len(pts), []
    for i, (x, y) in enumerate(pts):
        (px, py), (nx, ny) = pts[i - 1], pts[(i + 1) % n]
        out.append(mv(x, y, round(math.atan2(ny - py, nx - px), 5),
                      round(math.hypot(nx - px, ny - py) / 6 * tension, 2)))
    return path(out)

def line(x1, y1, x2, y2):
    return path([sv(x1, y1), sv(x2, y2)], closed=False)

def outlined(name, geo, paint, width=22, **t):
    """Two shapes over the same paths: a fat navy stroke under a fill, so overlapping
    sub-paths (petals, fingers) read as one silhouette with no inner seams."""
    return (shape(name, geo, paint, **t)
            + shape(f"{name} Outline", geo, stroke(NAVY, width), **t))

def at(p, pivot):
    return p[0] - pivot[0], p[1] - pivot[1]

# ---------------------------------------------------------------- keyframes
EASES = {
    "io": (0.42, 0, 0.58, 1),
    "soft": (0.37, 0, 0.63, 1),
    "out": (0.16, 1, 0.3, 1),
    "in": (0.55, 0, 0.9, 0.4),
    "back": (0.34, 1.5, 0.64, 1),
    "s": (0.65, 0, 0.35, 1),        # strong S-curve for the glove wrist
}

def kf(f, v, e):
    if e in ("hold", "linear"):
        return f'<KeyFrameDouble frame="{f}" value="{round(v, 4)}" interpolationType="{e}"/>'
    x1, y1, x2, y2 = EASES[e]
    return (f'<KeyFrameDouble frame="{f}" value="{round(v, 4)}" interpolationType="cubic">'
            f'<CubicEaseInterpolator x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/></KeyFrameDouble>')

class Anim:
    """Collects keys per (object, property); every main-layer clip keys the same set,
    so a cross-fade between any two of them never leaves a property stranded."""
    def __init__(self, name, duration, loop):
        self.name, self.duration, self.loop, self.id = name, duration, loop, nid()
        self.tracks = {}

    def key(self, obj, prop, keys):
        self.tracks.setdefault(obj, {})[prop] = keys
        return self

    def hold(self, obj, prop, v):
        return self.key(obj, prop, [(0, v, "hold"), (self.duration, v, "hold")])

    def xml(self):
        objs = "".join(
            f'<KeyedObject objectId="{o}">'
            + "".join(f'<KeyedProperty property="{p}">'
                      f'{"".join(kf(f, v + (ROT0.get(o, 0) if p == "rotation" else 0), e) for f, v, e in ks)}'
                      f'</KeyedProperty>' for p, ks in props.items())
            + '</KeyedObject>' for o, props in self.tracks.items())
        return (f'<LinearAnimation loopValue="{self.loop}" duration="{self.duration}" '
                f'name="{self.name}" id="{self.id}">{objs}</LinearAnimation>')

# ---------------------------------------------------------------- ids of animated parts
OTAN, SPINE, HEAD, FACE, BACKPACK = (nid() for _ in range(5))
EYES_OPEN, EYES_HAPPY, EYE_L, EYE_R, MOUTH, MOUTH_SHAPE, CHEEKS, BROWS = (nid() for _ in range(8))
L_SHOULDER, L_ELBOW, L_HAND, R_ARM, VISOR = (nid() for _ in range(5))
BUTTERFLY, WING_L, WING_R = (nid() for _ in range(3))
FLOWERS = [nid() for _ in range(4)]
PETALS = [nid() for _ in range(3)]

# ---------------------------------------------------------------- pivots (reference px)
P_OTAN = (960, 1240)      # between the boots, on the floor
P_SPINE = (960, 1040)     # hips
P_HEAD = (960, 735)       # neck ring
P_FACE = (975, 520)
P_MOUTH = (1005, 578)
P_LSH = (1170, 790)       # waving shoulder (Otan's left, our right)
P_RSH = (735, 800)
P_PACK = (760, 760)

SCALE = 0.38
SCENE_X, SCENE_Y = round(250 - 1000 * SCALE, 2), round(262 - 712 * SCALE, 2)

L_UPPER = (115, -95)      # shoulder -> elbow
L_FORE = (88, -110)       # elbow -> wrist

# ---------------------------------------------------------------- face
def eye(name, eid, p):
    return node(name,
        shape("Glint Small", ell(9, 9), fill(WHITE), x=-9, y=14, opacity=0.8),
        shape("Glint", ell(18, 18), fill(WHITE), x=8, y=-14),
        shape("Iris", ell(50, 68), fill(grad=lin(0, -34, 0, 34, (NAVY2, 0), (NAVY3, 1)))),
        id=eid, x=p[0], y=p[1])

EYE_LP, EYE_RP = at((928, 500), P_FACE), at((1052, 482), P_FACE)

happy_eye = lambda p: shape("Happy", path([sv(-26, 10), mv(0, -16, 0, 17), sv(26, 10)], closed=False),
                            stroke(NAVY, 13), x=p[0], y=p[1])

brow = lambda name, p, rot: shape(name, path([sv(-24, 6), mv(0, -5, 0, 14), sv(24, 4)], closed=False),
                                  stroke(BROW, 11), x=p[0], y=p[1], rotation=rot)

mouth = node("Mouth",
    shape("Tongue", ell(64, 34, x=8, y=52), fill("FFF0657F"), f'<ClippingShape sourceId="{MOUTH_SHAPE}" name="Clip"/>'),
    shape("Mouth Shape", path([sv(-56, 0, 12), sv(56, 0, 12), mv(0, 64, 3.1415927, 42)]),
          fill("FF3A1E4A"), stroke(NAVY, 7), id=MOUTH_SHAPE),
    id=MOUTH, x=at(P_MOUTH, P_FACE)[0], y=at(P_MOUTH, P_FACE)[1], rotation=-0.05)

def tuft():
    pts = [at(p, P_FACE) for p in [(895, 350), (935, 288), (962, 322), (1004, 276), (1036, 346)]]
    return shape("Hair Tuft", path([sv(*pts[0]), sv(*pts[1], 18), sv(*pts[2], 10), sv(*pts[3], 18), sv(*pts[4])]),
                 fill(FUR_T))

def ear(name, p, w, h):
    x, y = at(p, P_FACE)
    return (shape(f"{name} Inner", ell(w * 0.5, h * 0.56), fill(SKIN_B), x=x + 4, y=y)
            + shape(name, ell(w, h), fill(FUR_B), x=x, y=y))

muzzle_geo = (ell(310, 215, x=at((992, 565), P_FACE)[0], y=at((992, 565), P_FACE)[1])
              + ell(160, 150, x=at((925, 480), P_FACE)[0], y=at((925, 480), P_FACE)[1])
              + ell(160, 150, x=at((1055, 462), P_FACE)[0], y=at((1055, 462), P_FACE)[1]))

face = node("Otan_Face",
    node("Happy Eyes", happy_eye(EYE_LP), happy_eye(EYE_RP), id=EYES_HAPPY, opacity=0),
    node("Eyes", eye("Eye L", EYE_L, EYE_LP), eye("Eye R", EYE_R, EYE_RP), id=EYES_OPEN),
    node("Brows", brow("Brow L", at((914, 440), P_FACE), -0.12), brow("Brow R", at((1050, 420), P_FACE), 0.06), id=BROWS),
    shape("Nose", ell(11, 8, x=3, y=15) + ell(11, 8, x=22, y=12), fill("FFB8582A")),
    mouth,
    node("Cheeks",
        shape("Blush L", ell(86, 56), fill(BLUSH, feather=10), x=-107, y=45, opacity=0.8),
        shape("Blush R", ell(76, 50), fill(BLUSH, feather=10), x=153, y=2, opacity=0.8),
        id=CHEEKS),
    shape("Muzzle", muzzle_geo, fill(grad=lin(0, -100, 0, 150, (SKIN_T, 0), (SKIN_B, 1)))),
    tuft(),
    shape("Fur", ell(430, 400, x=-3, y=-20), fill(grad=lin(0, -220, 0, 180, (FUR_T, 0), (FUR_B, 1)))),
    ear("Ear L", (775, 520), 82, 104), ear("Ear R", (1178, 485), 76, 98),
    f'<ClippingShape sourceId="{VISOR}" name="Clip"/>',
    id=FACE, x=at(P_FACE, P_HEAD)[0], y=at(P_FACE, P_HEAD)[1])

# ---------------------------------------------------------------- head
def headphone(name, p, w, h):
    x, y = at(p, P_HEAD)
    return node(name,
        shape("Highlight", ell(w * 0.32, h * 0.38), fill(ORANGE_L), x=-w * 0.14, y=-h * 0.16, opacity=0.9),
        shape("Cup", ell(w, h), fill(grad=lin(0, -h / 2, 0, h / 2, (ORANGE, 0), (ORANGE_D, 1))), stroke(NAVY, 12)),
        x=x, y=y)

band_pts = [at(p, P_HEAD) for p in [(712, 372), (960, 205), (1208, 362)]]
shine_pts = [at(p, P_HEAD) for p in [(778, 420), (810, 340), (880, 290)]]

head = node("Helmet_Outer",
    headphone("Antenna L", (668, 515), 118, 215),
    headphone("Antenna R", (1262, 440), 100, 195),
    shape("Visor Shine", path([sv(*shine_pts[0]), mv(*shine_pts[1], -1.05, 40), sv(*shine_pts[2])], closed=False),
          stroke(WHITE, 20), opacity=0.35),
    face,
    shape("Visor", ell(505, 455, x=8, y=-267), fill(grad=lin(0, -495, 0, -40, (NAVY2, 0), (NAVY3, 1))), id=VISOR),
    shape("Visor Rim", ell(530, 480, x=8, y=-267), fill(LAV)),
    shape("Band", path([sv(*band_pts[0]), mv(*band_pts[1], 0, 150), sv(*band_pts[2])], closed=False),
          stroke(ORANGE, 18)),
    shape("Helmet", ell(610, 595, x=-2, y=-290),
          fill(grad=lin(0, -590, 0, 0, (WHITE, 0), (WHITE, 0.55), (LAV, 1))), stroke(NAVY, 12)),
    id=HEAD, x=at(P_HEAD, P_SPINE)[0], y=at(P_HEAD, P_SPINE)[1])

# ---------------------------------------------------------------- arms
def band(name, dx, dy, t, length=64):
    a = math.atan2(dy, dx)
    return shape(name, rect(18, length, 4), fill(ORANGE), x=dx * t, y=dy * t, rotation=a)

GLOVE = fill(grad=lin(0, -80, 0, 40, (WHITE, 0), (LAV, 1)))

open_glove_geo = (ell(108, 100, y=-22)
                  + rect(34, 70, 17, x=-50, y=-10, rotation=-1.0)
                  + rect(34, 86, 17, x=-30, y=-74, rotation=-0.35)
                  + rect(34, 96, 17, x=2, y=-86, rotation=-0.05)
                  + rect(34, 88, 17, x=32, y=-76, rotation=0.25)
                  + rect(32, 70, 16, x=55, y=-52, rotation=0.6))

# The waving arm is a bone chain. One skinned sleeve path runs shoulder -> elbow -> wrist, so it
# bends as a single soft tube instead of two stiff segments meeting at a joint.
A_UP, A_FORE = math.atan2(L_UPPER[1], L_UPPER[0]), math.atan2(L_FORE[1], L_FORE[0])
LEN_UP, LEN_FORE = math.hypot(*L_UPPER), math.hypot(*L_FORE)
ROT0 = {L_SHOULDER: A_UP, L_ELBOW: A_FORE - A_UP, L_HAND: 0.0}   # bone rest rotations; clips key offsets

def world(p):
    """Reference px -> artboard px at rest (nothing above the arm is rotated at rest)."""
    return SCENE_X + SCALE * p[0], SCENE_Y + SCALE * p[1]

def bind(angle, p):
    wx, wy = world(p)
    c, s = SCALE * math.cos(angle), SCALE * math.sin(angle)
    return f'xx="{c:.6f}" xy="{s:.6f}" yx="{-s:.6f}" yy="{c:.6f}" tx="{wx:.4f}" ty="{wy:.4f}"'

def sleeve_l():
    ex, ey = L_UPPER
    wx, wy = ex + L_FORE[0], ey + L_FORE[1]
    split = 128 | (127 << 8)
    verts = (f'<StraightVertex x="-12" y="16"><Weight values="255" indices="1"/></StraightVertex>'
             f'<CubicDetachedVertex x="{ex}" y="{ey}" inRotation="{A_UP + math.pi:.5f}" inDistance="62" '
             f'outRotation="{A_FORE:.5f}" outDistance="62">'
             f'<CubicWeight values="{split}" indices="{1 | (2 << 8)}" inValues="255" inIndices="1" '
             f'outValues="255" outIndices="2"/></CubicDetachedVertex>'
             f'<StraightVertex x="{wx}" y="{wy}"><Weight values="255" indices="2"/></StraightVertex>')
    wxx, wyy = world(P_LSH)
    skin = (f'<Skin xx="{SCALE}" yy="{SCALE}" tx="{wxx:.4f}" ty="{wyy:.4f}" name="Skin">'
            f'<Tendon boneId="{L_SHOULDER}" {bind(A_UP, P_LSH)} name="Upper"/>'
            f'<Tendon boneId="{L_ELBOW}" {bind(A_FORE, (P_LSH[0] + ex, P_LSH[1] + ey))} name="Fore"/>'
            f'</Skin>')
    geo = f'<PointsPath isClosed="false" name="P">{verts}{skin}</PointsPath>'
    return shape("Sleeve", geo, stroke(NAVY, 84), stroke(WHITE, 62),
                 x=at(P_LSH, P_SPINE)[0], y=at(P_LSH, P_SPINE)[1])

def arm_band(name, length):
    return shape(name, rect(18, 64, 6), fill(ORANGE), x=length * 0.74)

glove_l = node("Glove",
    shape("Palm Crease", path([sv(-14, -30), mv(4, -12, 0.6, 12), sv(24, -4)], closed=False),
          stroke(LAV_D, 7)),
    outlined("Glove", open_glove_geo, GLOVE),
    shape("Cuff", ell(84, 40), fill(LAV), stroke(NAVY, 12), y=8, rotation=-0.2),
    rotation=round(-A_FORE, 5))

arm_l = node("Left Arm",
    f'<RootBone x="{at(P_LSH, P_SPINE)[0]}" y="{at(P_LSH, P_SPINE)[1]}" length="{LEN_UP:.3f}" '
    f'rotation="{A_UP:.5f}" name="L_Shoulder" id="{L_SHOULDER}">'
    f'<Bone length="{LEN_FORE:.3f}" rotation="{A_FORE - A_UP:.5f}" name="L_Elbow" id="{L_ELBOW}">'
    f'<Bone length="50" rotation="0" name="L_Hand" id="{L_HAND}">{glove_l}</Bone>'
    f'{arm_band("Cuff Band", LEN_FORE)}</Bone>'
    f'{arm_band("Elbow Band", LEN_UP)}</RootBone>',
    sleeve_l())

fist_geo = (ell(118, 92)
            + rect(32, 62, 16, x=46, y=-30, rotation=0.8)
            + ell(42, 36, x=-34, y=36) + ell(42, 36, x=0, y=44) + ell(42, 36, x=34, y=38))

arm_r = node("R_Arm",
    outlined("Glove", fist_geo, GLOVE, x=78, y=132),
    band("Arm Band", 55, 100, 0.42),
    shape("Sleeve", path([sv(0, 0), mv(16, 54, 1.2, 34), sv(58, 100)], closed=False),
          stroke(NAVY, 84), stroke(WHITE, 62)),
    id=R_ARM, x=at(P_RSH, P_SPINE)[0], y=at(P_RSH, P_SPINE)[1])

# ---------------------------------------------------------------- body
def S(p):
    return at(p, P_SPINE)

belt_box = node("Belt Box",
    shape("Button", ell(40, 40), fill("FF3F6CC7"), stroke(NAVY, 9), x=48, y=-2),
    shape("Latch", path([sv(-40, -46), sv(-26, -6), sv(-42, 46)], closed=False), stroke(NAVY, 9)),
    shape("Box", rect(200, 128, 26), fill(grad=lin(0, -64, 0, 64, (WHITE, 0), (LAV, 1))), stroke(NAVY, 12)),
    x=S((1020, 866))[0], y=S((1020, 866))[1], rotation=-0.06)

spine = node("Spine",
    arm_r,
    belt_box,
    shape("Grip", rect(120, 34, 17), fill(BLUE_D), stroke(NAVY, 10), x=S((870, 905))[0], y=S((870, 905))[1], rotation=-0.06),
    shape("Belt", rect(390, 62, 26), fill(BLUE), stroke(NAVY, 12), x=S((1035, 900))[0], y=S((1035, 900))[1], rotation=-0.07),
    arm_l,      # above the head: the inward swing passes in front of the headphone
    head,
    shape("Collar", ell(420, 118), fill(LAV), stroke(NAVY, 36), stroke(ORANGE, 20), x=S((958, 742))[0], y=S((958, 742))[1]),
    shape("Seam", line(*S((962, 790)), *S((972, 1015))), stroke(SEAM, 9)),
    shape("Torso", smooth([S(p) for p in [(940, 718), (1105, 742), (1188, 830), (1200, 950), (1120, 1036),
                                          (940, 1058), (762, 1036), (676, 950), (690, 830), (772, 742)]]),
          fill(grad=lin(0, -320, 0, 20, (WHITE, 0), (WHITE, 0.45), (LAV, 1))), stroke(NAVY, 12)),
    node("Backpack",
        shape("Pack", smooth([(-60, -150), (8, -140), (40, 0), (12, 150), (-70, 150), (-96, 0)]), fill(grad=lin(0, -160, 0, 160, (BLUE, 0), (BLUE_D, 1))), stroke(NAVY, 12),
              x=-28, y=118),
        id=BACKPACK, x=S(P_PACK)[0], y=S(P_PACK)[1]),
    id=SPINE, x=at(P_SPINE, P_OTAN)[0], y=at(P_SPINE, P_OTAN)[1])

def O(p):
    return at(p, P_OTAN)

def leg(name, p):
    x, y = O(p)
    return (shape(f"{name} Band", rect(162, 24, 4), fill(ORANGE), x=x, y=y + 2)
            + shape(name, smooth([(-84, -92), (0, -100), (84, -92), (90, 0), (78, 96), (0, 102), (-78, 96), (-90, 0)],
                                 tension=0.9),
                    fill(grad=lin(0, -98, 0, 98, (WHITE, 0), (LAV, 1))), stroke(NAVY, 12), x=x, y=y))

def boot(name, p):
    x, y = O(p)
    return (shape(f"{name} Sole", rect(226, 40, 20), fill(BLUE_D), stroke(NAVY, 12), x=x, y=y + 36)
            + shape(name, rect(230, 106, 52), fill(grad=lin(0, -53, 0, 53, (WHITE, 0), (LAV, 1))), stroke(NAVY, 12),
                    x=x, y=y))

otan = node("Otan",
    spine,
    boot("Boot L", (868, 1205)), boot("Boot R", (1128, 1205)),
    leg("Leg L", (902, 1095)), leg("Leg R", (1092, 1095)),
    id=OTAN, x=P_OTAN[0], y=P_OTAN[1])

# ---------------------------------------------------------------- decor
def flower(name, fid, p, r):
    geo = "".join(ell(r, r, x=0.5 * r * math.cos(-math.pi / 2 + k * 2 * math.pi / 5),
                      y=0.5 * r * math.sin(-math.pi / 2 + k * 2 * math.pi / 5)) for k in range(5))
    return node(name,
        shape("Center", ell(r * 0.38, r * 0.38), fill(PINK_D)),
        outlined("Petals", geo, fill(PINK), width=20),
        id=fid, x=p[0], y=p[1])

def petal(name, pid, p, rot):
    return node(name,
        shape("Vein", line(-18, 0, 14, 0), stroke(PINK_D, 6), opacity=0.7),
        shape("Leaf", path([sv(-42, 0), mv(0, -22, 0, 26), sv(42, 0), mv(0, 22, 3.1415927, 26)]),
              fill(PINK), stroke(NAVY, 10)),
        id=pid, x=p[0], y=p[1], rotation=rot)

def wing(name, wid, side):
    s = side
    return node(name,
        shape("Inner Upper", ell(44, 78), fill(YELLOW), x=-58 * s, y=-58, rotation=0.5 * s),
        shape("Upper", ell(104, 150), fill(PURPLE), stroke(NAVY, 12), x=-62 * s, y=-56, rotation=0.45 * s),
        shape("Inner Lower", ell(34, 34), fill(YELLOW), x=-44 * s, y=40),
        shape("Lower", ell(84, 82), fill(PURPLE_L), stroke(NAVY, 12), x=-46 * s, y=38, rotation=-0.3 * s),
        id=wid)

butterfly = node("Butterfly",
    shape("Antennae", path([sv(-26, -90), mv(-10, -70, 1.2, 10), sv(-4, -46)], closed=False)
          + path([sv(24, -92), mv(10, -70, 1.9, 10), sv(4, -46)], closed=False), stroke(NAVY, 7)),
    shape("Body", rect(24, 110, 12), fill(YELLOW), stroke(NAVY, 10)),
    wing("Wing L", WING_L, 1), wing("Wing R", WING_R, -1),
    id=BUTTERFLY, x=1330, y=222, rotation=-0.62)

FLOWER_SPOTS = [((460, 690), 78), ((556, 1022), 56), ((1445, 890), 78), ((1560, 370), 54)]
PETAL_SPOTS = [((532, 378), -0.6), ((1578, 690), -0.95), ((1322, 1045), 1.05)]

decor = node("Flowers_Leaves",
    *(flower(f"Flower {i + 1}", FLOWERS[i], p, r) for i, (p, r) in enumerate(FLOWER_SPOTS)),
    *(petal(f"Petal {i + 1}", PETALS[i], p, rot) for i, (p, rot) in enumerate(PETAL_SPOTS)))

shadow = shape("Shadow", ell(820, 110), fill("FFD9DAE6"), x=1000, y=1250)

scene = node("Scene", butterfly, otan, decor, shadow, x=SCENE_X, y=SCENE_Y, scaleX=SCALE, scaleY=SCALE)

# ---------------------------------------------------------------- motion
# Looping tracks are sampled sines, each with its own phase, so nothing stops dead on a key and
# every part trails the one driving it: shoulder -> elbow -> wrist, body -> head -> backpack.
TAU = 2 * math.pi
X0, Y0 = P_OTAN
HY = at(P_HEAD, P_SPINE)[1]
LSH_Y = at(P_LSH, P_SPINE)[1]

BASE = {
    (OTAN, "x"): X0, (OTAN, "y"): Y0, (OTAN, "scaleX"): 1, (OTAN, "scaleY"): 1,
    (SPINE, "rotation"): 0, (HEAD, "rotation"): 0, (HEAD, "y"): HY, (BACKPACK, "rotation"): 0,
    (EYES_OPEN, "opacity"): 1, (EYES_HAPPY, "opacity"): 0,
    (EYE_L, "scaleY"): 1, (EYE_R, "scaleY"): 1,
    (MOUTH, "scaleX"): 0.82, (MOUTH, "scaleY"): 0.72,
    (CHEEKS, "y"): 0, (CHEEKS, "scaleX"): 1, (CHEEKS, "scaleY"): 1,
    (BROWS, "y"): 0,
    (L_SHOULDER, "rotation"): 0, (L_SHOULDER, "y"): LSH_Y,
    (L_ELBOW, "rotation"): 0, (L_HAND, "rotation"): 0, (R_ARM, "rotation"): 0,
}
HAPPY_FACE = {
    (EYES_OPEN, "opacity"): 0, (EYES_HAPPY, "opacity"): 1,
    (MOUTH, "scaleX"): 1.22, (MOUTH, "scaleY"): 1.38,
    (CHEEKS, "y"): -15, (CHEEKS, "scaleX"): 1.12, (CHEEKS, "scaleY"): 1.12,
    (BROWS, "y"): -15,
}

def osc(p, phase):
    """-1 at `phase`, +1 half a cycle later."""
    return -math.cos(TAU * (p - phase))

def sampled(fn, duration, step=3):
    return [(f, fn(f), "linear") for f in list(range(0, duration, step)) + [duration]]

def smoothstep(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)

def finish(anim, pose):
    """Key every main-layer property the clip did not animate, holding `pose` (else BASE)."""
    for (o, p), v in BASE.items():
        if p not in anim.tracks.get(o, {}):
            anim.hold(o, p, pose.get((o, p), v))
    return anim

# ---------------------------------------------------------------- IDLE_GENTLE (2s loop): breathing
T_IDLE = 120
IDLE = {
    (OTAN, "y"): lambda p: Y0 - 5 - 5 * osc(p, 0),
    (OTAN, "scaleY"): lambda p: 1.006 + 0.006 * osc(p, 0),
    (OTAN, "scaleX"): lambda p: 0.998 - 0.002 * osc(p, 0),
    (SPINE, "rotation"): lambda p: 0.012 * math.sin(TAU * (p - 0.1)),
    (HEAD, "rotation"): lambda p: 0.03 * math.sin(TAU * (p - 0.2)),
    (HEAD, "y"): lambda p: HY + 3 * osc(p, 0.12),
    (BACKPACK, "rotation"): lambda p: 0.018 * math.sin(TAU * (p - 0.32)),
    (L_SHOULDER, "rotation"): lambda p: -0.035 - 0.035 * osc(p, 0.05),
    (L_ELBOW, "rotation"): lambda p: -0.05 * math.sin(TAU * (p - 0.15)),
    (L_HAND, "rotation"): lambda p: 0.08 * math.sin(TAU * (p - 0.28)),
    (R_ARM, "rotation"): lambda p: 0.03 * math.sin(TAU * (p - 0.12)),
    (MOUTH, "scaleY"): lambda p: 0.72 + 0.02 * osc(p, 0.1),
}
idle = Anim("IDLE_GENTLE", T_IDLE, "loop")
for (o, prop), fn in IDLE.items():
    idle.key(o, prop, sampled(lambda f, fn=fn: fn(f / T_IDLE), T_IDLE))
for e in (EYE_L, EYE_R):
    idle.key(e, "scaleY", [(0, 1, "hold"), (84, 1, "in"), (88, 0.08, "out"), (95, 1, "hold"), (120, 1, "hold")])
finish(idle, {})

# ---------------------------------------------------------------- HAPPY_WAVE: 3 waves x 0.8s, loop
# (center, amplitude, phase in cycles) per track; arm amplitudes grow down the chain for the whip.
WAVE = {
    (L_SHOULDER, "rotation"): (0.01, 0.17, 0.0),
    (L_SHOULDER, "y"): (LSH_Y - 5, -5, 0.0),          # shoulder lifts with the outward swing
    (L_ELBOW, "rotation"): (0.02, 0.22, 0.08),
    (L_HAND, "rotation"): (0.12, 0.44, 0.17),         # glove trails furthest: flexible wrist
    (HEAD, "rotation"): (0.085, 0.025, 0.22),         # tilted toward the wave, nodding along
    (HEAD, "y"): (HY + 1, 3, 0.3),
    (SPINE, "rotation"): (0.02, 0.012, 0.12),
    (BACKPACK, "rotation"): (0.0, 0.03, 0.32),        # follow-through
    (R_ARM, "rotation"): (0.02, 0.03, 0.2),
    (OTAN, "y"): (Y0 - 5, -5, 0.05),
    (OTAN, "x"): (X0 + 2, 2, 0.05),
    (OTAN, "scaleY"): (1.006, 0.006, 0.05),
    (OTAN, "scaleX"): (0.997, -0.003, 0.05),
    (MOUTH, "scaleY"): (1.38, 0.07, 0.1),             # laughing along with each wave
    (MOUTH, "scaleX"): (1.22, -0.03, 0.1),
    (CHEEKS, "y"): (-15, -2, 0.1),
    (BROWS, "y"): (-15, -2.5, 0.05),
}
L_WAVE = 48
happy = Anim("HAPPY_WAVE", 3 * L_WAVE, "loop")
for (o, prop), (c, a, ph) in WAVE.items():
    happy.key(o, prop, sampled(lambda f, c=c, a=a, ph=ph: c + a * osc(f / L_WAVE, ph), 3 * L_WAVE))
finish(happy, HAPPY_FACE)

def happy_at0(k):
    if k in WAVE:
        c, a, ph = WAVE[k]
        return c + a * osc(0, ph)
    return HAPPY_FACE.get(k, BASE[k])

def idle_at0(k):
    return IDLE[k](0) if k in IDLE else BASE[k]

# ---------------------------------------------------------------- WAVE_QUICK (triggerWave): faster, wider
L_QUICK, T_QUICK = 30, 90
quick = Anim("WAVE_QUICK", T_QUICK, "oneShot")
env = lambda f: smoothstep(f / 14) * smoothstep((T_QUICK - f) / 22)
for (o, prop), (c, a, ph) in WAVE.items():
    boost = 1.35 if o in (L_SHOULDER, L_ELBOW, L_HAND) else 1.0
    quick.key(o, prop, sampled(
        lambda f, c=c, a=a, ph=ph, b=boost, h0=happy_at0((o, prop)): h0 * (1 - env(f))
        + (c + b * a * osc(f / L_QUICK, ph)) * env(f), T_QUICK, step=2))
finish(quick, HAPPY_FACE)

# ---------------------------------------------------------------- TRANSITION_TO_IDLE (1s)
# Everything eases home with a small overshoot; the squinted eyes pop back open.
back = Anim("TRANSITION_TO_IDLE", 60, "oneShot")
for k in BASE:
    o, prop = k
    s, e = happy_at0(k), idle_at0(k)
    if prop == "opacity":
        back.key(o, prop, [(0, s, "hold"), (24, e, "hold"), (60, e, "hold")])
    elif o in (EYE_L, EYE_R):
        back.key(o, prop, [(0, 1, "hold"), (22, 1, "in"), (25, 0.3, "out"), (36, 1, "hold"), (60, 1, "hold")])
    else:
        lag = {L_ELBOW: 4, L_HAND: 8, HEAD: 6, BACKPACK: 10}.get(o, 0)
        back.key(o, prop, [(0, s, "soft"), (lag, s, "soft"), (32 + lag, e + 0.2 * (e - s), "soft"),
                           (min(60, 50 + lag), e, "linear"), (60, e, "linear")] if lag else
                          [(0, s, "soft"), (32, e + 0.2 * (e - s), "soft"), (50, e, "linear"), (60, e, "linear")])

# ---------------------------------------------------------------- AMBIENT (3s loop): butterfly + floating decor
amb = Anim("AMBIENT", 180, "loop")
flaps = [(0, 1, "io"), (5, 0.22, "io"), (10, 1, "io"), (15, 0.22, "io"), (20, 1, "io"), (25, 0.22, "io"),
         (32, 1, "soft"), (62, 0.7, "soft"), (84, 1, "io"),                     # glide
         (89, 0.22, "io"), (94, 1, "io"), (99, 0.22, "io"), (104, 1, "io"),
         (120, 0.75, "soft"), (134, 1, "io"), (139, 0.22, "io"), (144, 1, "io"), (149, 0.22, "io"),
         (154, 1, "io"), (159, 0.22, "io"), (166, 1, "soft"), (180, 1, "linear")]
amb.key(WING_L, "scaleX", flaps).key(WING_R, "scaleX", flaps)
amb.key(BUTTERFLY, "y", [(0, 222, "soft"), (60, 196, "soft"), (120, 236, "soft"), (180, 222, "linear")])
amb.key(BUTTERFLY, "x", [(0, 1330, "soft"), (90, 1352, "soft"), (180, 1330, "linear")])
amb.key(BUTTERFLY, "rotation", [(0, -0.62, "soft"), (70, -0.5, "soft"), (130, -0.72, "soft"), (180, -0.62, "linear")])
for i, (fid, ((x, y), r)) in enumerate(zip(FLOWERS, FLOWER_SPOTS)):
    d, s = 10 if r > 60 else 7, 1 if i % 2 else -1
    amb.key(fid, "y", [(0, y, "soft"), (90, y - d * s, "soft"), (180, y, "linear")])
    amb.key(fid, "rotation", [(0, 0, "soft"), (90, 0.12 * s, "soft"), (180, 0, "linear")])
for i, (pid, ((x, y), rot)) in enumerate(zip(PETALS, PETAL_SPOTS)):
    s = 1 if i % 2 else -1
    amb.key(pid, "y", [(0, y, "soft"), (60, y - 14 * s, "soft"), (120, y + 6 * s, "soft"), (180, y, "linear")])
    amb.key(pid, "rotation", [(0, rot, "soft"), (90, rot + 0.3 * s, "soft"), (180, rot, "linear")])

# ---------------------------------------------------------------- state machine
IS_HAPPY, TRIGGER = nid(), nid()
S_IDLE, S_HAPPY, S_QUICK, S_BACK, S_AMB = (nid() for _ in range(5))

def tr(to, ms, *conds, exit_pct=None):
    ex = (f' enableExitTime="true" exitTimeIsPercetange="true" exitTime="{exit_pct}"'
          if exit_pct is not None else "")
    # cross-fades ease in and out rather than mixing at a constant rate
    return (f'<StateTransition stateToId="{to}" duration="{ms}" interpolationType="cubic"{ex}>'
            f'<CubicEaseInterpolator x1="0.42" y1="0" x2="0.58" y2="1"/>{"".join(conds)}</StateTransition>')

happy_on = f'<TransitionBoolCondition inputId="{IS_HAPPY}" opValue="equal"/>'
happy_off = f'<TransitionBoolCondition inputId="{IS_HAPPY}" opValue="notEqual"/>'
wave_fired = f'<TransitionTriggerCondition inputId="{TRIGGER}"/>'

def state(sid, anim, x, y, *transitions, reset=False):
    r = ' reset="true"' if reset else ""
    return f'<AnimationState x="{x}" y="{y}" animationId="{anim.id}"{r} id="{sid}">{"".join(transitions)}</AnimationState>'

first = {"idle": S_IDLE, "happy": S_HAPPY, "wave": S_QUICK, "toidle": S_BACK}[ENTRY]

main_layer = (
    f'<StateMachineLayer name="Otan" id="{nid()}">'
    f'<AnyState x="0" y="-150"/><ExitState x="700" y="-150"/>'
    f'<EntryState x="0" y="0"><StateTransition stateToId="{first}"/></EntryState>'
    # isHappy blends IDLE into HAPPY_WAVE (a 400ms cross-fade of the two clips)
    + state(S_IDLE, idle, 200, 0, tr(S_QUICK, 180, wave_fired), tr(S_HAPPY, 500, happy_on))
    + state(S_HAPPY, happy, 500, 0, tr(S_QUICK, 180, wave_fired), tr(S_BACK, 300, happy_off))
    + state(S_QUICK, quick, 350, 200,
            tr(S_HAPPY, 150, happy_on, exit_pct=100), tr(S_BACK, 150, happy_off, exit_pct=100), reset=True)
    + state(S_BACK, back, 350, -150,
            tr(S_QUICK, 180, wave_fired), tr(S_HAPPY, 350, happy_on), tr(S_IDLE, 120, exit_pct=100), reset=True)
    + '</StateMachineLayer>')

ambient_layer = (
    f'<StateMachineLayer name="Ambient" id="{nid()}">'
    f'<AnyState x="0" y="-150"/><ExitState x="400" y="-150"/>'
    f'<EntryState x="0" y="0"><StateTransition stateToId="{S_AMB}"/></EntryState>'
    + state(S_AMB, amb, 200, 0) + '</StateMachineLayer>')

sm = (f'<StateMachine name="State Machine 1" id="0:7">'
      f'<StateMachineBool name="isHappy"{' value="true"' if START_HAPPY else ""} id="{IS_HAPPY}"/>'
      f'<StateMachineTrigger name="triggerWave" id="{TRIGGER}"/>'
      + main_layer + ambient_layer + '</StateMachine>')

anims = "".join(a.xml() for a in (idle, happy, quick, back, amb))

doc = (f'<Rive version="1" kind="fragment">\n'
       f'<Artboard defaultStateMachineId="0:7" styleId="0:5" width="500" height="500" name="Otan Happy" id="0:2">'
       f'<LayoutComponentStyle name="Artboard Style" id="0:5"/>'
       f'{scene}{sm}{anims}</Artboard>\n</Rive>\n')

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(doc)
print("wrote", OUT, len(doc), "entry:", ENTRY)
