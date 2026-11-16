"""
Low-poly "reef turtle" reconstruction (Blender / bpy).

Run with Blender:   blender -b -P build_sea_turtle.py
or with the pip bpy module:  python build_sea_turtle.py

Produces:  sea_turtle_reef.blend  +  renders/front.png, renders/three_quarter.png, renders/back.png

Conventions: turtle faces -Y, up is +Z, +X is the turtle's LEFT side.
Shell width = 2.0 units (reference scale for every other measurement).
"""
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
RENDER_DIR = os.path.join(HERE, "renders")
os.makedirs(RENDER_DIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene
random.seed(11)


# ----------------------------------------------------------------------------- colours
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def C(h):
    h = h.lstrip("#")
    return tuple(_lin(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def jit(col, amt=0.07, rnd=random):
    f = 1.0 + rnd.uniform(-amt, amt)
    return tuple(max(0.0, min(1.0, c * f)) for c in col)


def pick(pal, rnd=random, amt=0.05):
    return jit(rnd.choice(pal), amt, rnd)


PAL = dict(
    head=[C("3CC3E6"), C("48CDEB"), C("33B8E0"), C("55D3EE")],
    head_light=[C("7ADFF1"), C("92E7F3"), C("6AD8EF")],
    head_back=[C("2AA2D8"), C("2E9BD4")],
    cream=[C("F0E9D2"), C("E6DEC4"), C("F6F0DD")],
    shell=[C("5262CC"), C("5B6BD3"), C("4D5BC4"), C("6070D6")],
    shell_lip=[C("4350B6"), C("3E4AAE"), C("4856BE")],
    rock_top=[C("7080DA"), C("7A89DE"), C("8593E2"), C("6B7BD6")],
    rock_side=[C("5565CC"), C("4A5AC2"), C("5E6ED2")],
    pink=[C("F06A8C"), C("F47C98"), C("EA5E82"), C("F78DA6")],
    purple=[C("A35BE6"), C("B06CEC"), C("9550DC"), C("BC7EF0")],
    orange=[C("F4B13C"), C("F7BE4F"), C("F0A632")],
    orange_top=[C("FAD072"), C("F8C95E")],
    orange_in=[C("C9781F"), C("B86A18")],
    kelp=[C("3CB043"), C("55C94F"), C("2E9E3E"), C("47BB48")],
    kelp_light=[C("7FDB5A"), C("6CCF4F")],
    moss=[C("9BD94A"), C("86CC3E"), C("B3E35C")],
    star=[C("F0705A"), C("F5826A"), C("E5604C")],
    eye_ring=[C("1F45AE"), C("2650C4"), C("2B58CC")],
    eye_ring_dark=[C("15338A"), C("1A3C9C")],
)
FLIP_BASE, FLIP_TIP, FLIP_UNDER = C("36C6D8"), C("C9EFB0"), C("6FD3DC")
SCUTE_BASE, SCUTE_TIP = C("2A9FE0"), C("4FC3E4")


# ----------------------------------------------------------------------------- materials
def _set(bsdf, names, val):
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = val
            return


def mat_lowpoly(name, rough=0.85):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    a = nt.nodes.new("ShaderNodeAttribute")
    a.attribute_name = "Col"
    a.location = (-300, 200)
    nt.links.new(a.outputs["Color"], bsdf.inputs["Base Color"])
    _set(bsdf, ["Roughness"], rough)
    _set(bsdf, ["Specular IOR Level", "Specular"], 0.25)
    return m


def mat_glow(name, strength=1.6):
    m = mat_lowpoly(name, 0.4)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    a = nt.nodes["Attribute"]
    for n in ("Emission Color", "Emission"):
        if n in bsdf.inputs:
            nt.links.new(a.outputs["Color"], bsdf.inputs[n])
            break
    _set(bsdf, ["Emission Strength"], strength)
    return m


def mat_bubble(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    _set(bsdf, ["Base Color"], (0.42, 0.68, 1.0, 1.0))
    _set(bsdf, ["Roughness"], 0.15)
    _set(bsdf, ["Alpha"], 0.45)
    for n in ("Emission Color", "Emission"):
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = (0.8, 0.9, 1.0, 1.0)
            break
    _set(bsdf, ["Emission Strength"], 0.0)
    m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    return m


MAT = dict(
    head=mat_lowpoly("M_Head_Turquoise"),
    cream=mat_lowpoly("M_Cream"),
    shell=mat_lowpoly("M_Shell_Indigo"),
    rock=mat_lowpoly("M_Rock_Periwinkle"),
    coral=mat_lowpoly("M_Coral"),
    sponge=mat_lowpoly("M_Sponge_Orange"),
    kelp=mat_lowpoly("M_Kelp_Green"),
    moss=mat_lowpoly("M_Moss_Lime"),
    star=mat_lowpoly("M_Starfish"),
    flipper=mat_lowpoly("M_Flipper_Teal"),
    scute=mat_lowpoly("M_Flipper_Scutes"),
    eye_ring=mat_lowpoly("M_Eye_Orbit", 0.5),
    eye_glow=mat_glow("M_Eye_Glow"),
    bubble=mat_bubble("M_Bubble"),
)


# ----------------------------------------------------------------------------- collections
ROOT = bpy.data.collections.new("SEA_TURTLE")
SC.collection.children.link(ROOT)
COLL = {}
for cname in ["HEAD", "EYES", "SHELL", "ROCKS", "FLIPPERS", "CORAL", "SPONGES",
              "KELP", "STARFISH", "MOSS", "BUBBLES"]:
    c = bpy.data.collections.new(cname)
    ROOT.children.link(c)
    COLL[cname] = c
COLL["CAMERAS_LIGHTS"] = bpy.data.collections.new("CAMERAS_LIGHTS")
SC.collection.children.link(COLL["CAMERAS_LIGHTS"])


# ----------------------------------------------------------------------------- mesh helpers
def build(name, V, F, FC, coll, mat, matrix=None, recalc=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in V], [], [list(f) for f in F])
    me.update()
    if recalc:
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
    attr = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    for p in me.polygons:
        c = FC[p.index]
        for li in p.loop_indices:
            attr.data[li].color = (c[0], c[1], c[2], 1.0)
        p.use_smooth = False
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if matrix is not None:
        ob.matrix_world = matrix
    return ob


def ico(sub, r=1.0):
    bm = bmesh.new()
    try:
        bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    except TypeError:
        bmesh.ops.create_icosphere(bm, subdivisions=sub, diameter=r)
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    V = [v.co.copy() for v in bm.verts]
    F = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    return V, F


def centroid(V, f):
    s = Vector((0, 0, 0))
    for i in f:
        s += V[i]
    return s / len(f)


def fnormal(V, f):
    a, b, c = V[f[0]], V[f[1]], V[f[2]]
    n = (b - a).cross(c - a)
    return n.normalized() if n.length > 1e-9 else Vector((0, 0, 1))


def axes_matrix(X, Y, Z, p):
    return Matrix(((X.x, Y.x, Z.x, p.x), (X.y, Y.y, Z.y, p.y), (X.z, Y.z, Z.z, p.z), (0, 0, 0, 1)))


def frame(d):
    d = d.normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u).normalized()
    return u, v


def add_prism(V, F, FC, p0, p1, r0, r1, col, n=6, rot=0.0, caps=True):
    u, v = frame(p1 - p0)
    b = len(V)
    for p, r in ((p0, r0), (p1, r1)):
        for k in range(n):
            a = rot + 2 * math.pi * k / n
            V.append(p + (u * math.cos(a) + v * math.sin(a)) * r)
    for k in range(n):
        k2 = (k + 1) % n
        F.append([b + k, b + k2, b + n + k2, b + n + k]); FC.append(col())
    if caps:
        F.append([b + k for k in range(n)][::-1]); FC.append(col())
        F.append([b + n + k for k in range(n)]); FC.append(col())


def add_ico(V, F, FC, c, r, col, sub=0, scale=(1, 1, 1), jitter=0.0, rnd=random):
    vs, fs = ico(sub, 1.0)
    b = len(V)
    for p in vs:
        q = Vector((p.x * scale[0], p.y * scale[1], p.z * scale[2])) * r
        if jitter:
            q += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * jitter * r
        V.append(c + q)
    for f in fs:
        F.append([b + i for i in f]); FC.append(col())


# ----------------------------------------------------------------------------- shell geometry
SH_A, SH_B, SH_ZR, SH_H = 1.0, 1.25, 0.32, 1.02   # half width, half length, rim height, dome height


def surf(x, y):
    r2 = min(0.97, (x / SH_A) ** 2 + (y / SH_B) ** 2)
    return SH_ZR + SH_H * (1 - r2) ** 0.42


def surf_normal(x, y):
    e = 0.01
    dx = (surf(x + e, y) - surf(x - e, y)) / (2 * e)
    dy = (surf(x, y + e) - surf(x, y - e)) / (2 * e)
    return Vector((-dx, -dy, 1)).normalized()


DRESS = 1.6


def place(x, y, yaw_deg=0.0, tilt=0.35, embed=0.04, scale=None, lift=0.0):
    scale = DRESS if scale is None else scale
    z = surf(x, y) + lift
    n = surf_normal(x, y)
    up = (Vector((0, 0, 1)) * (1 - tilt) + n * tilt).normalized()
    yaw = math.radians(yaw_deg)
    fwd = Vector((math.cos(yaw), math.sin(yaw), 0))
    X = (fwd - up * fwd.dot(up)).normalized()
    Y = up.cross(X)
    p = Vector((x, y, z)) - up * embed
    return axes_matrix(X * scale, Y * scale, up * scale, p)


def build_shell():
    rnd = random.Random(3)
    seg = 16
    rings = []  # (scale, z, kind)
    rings.append((0.90, SH_ZR - 0.13, "lip"))
    rings.append((1.05, SH_ZR - 0.05, "lip"))
    rings.append((1.00, SH_ZR + 0.02, "lip"))
    for phi in (16, 32, 48, 63, 77):
        p = math.radians(phi)
        rings.append((math.cos(p), SH_ZR + SH_H * math.sin(p) ** 0.84, "dome"))
    V, F, FC, ring_idx = [], [], [], []
    for k, (s, z, kind) in enumerate(rings):
        off = (k % 2) * 0.5
        idx = []
        for j in range(seg):
            th = 2 * math.pi * (j + off) / seg
            jr = 1 + (rnd.uniform(-0.03, 0.03) if kind == "dome" else rnd.uniform(-0.01, 0.01))
            V.append(Vector((SH_A * s * jr * math.cos(th), SH_B * s * jr * math.sin(th),
                             z + (rnd.uniform(-0.025, 0.025) if kind == "dome" else 0))))
            idx.append(len(V) - 1)
        ring_idx.append((idx, kind))
    for k in range(len(rings) - 1):
        a, ka = ring_idx[k]
        b, _ = ring_idx[k + 1]
        for j in range(seg):
            j2 = (j + 1) % seg
            for tri in ([a[j], a[j2], b[j2]], [a[j], b[j2], b[j]]):
                F.append(tri)
                FC.append(pick(PAL["shell_lip"] if ka == "lip" else PAL["shell"], rnd))
    top = len(V); V.append(Vector((0, 0, SH_ZR + SH_H)))
    last = ring_idx[-1][0]
    for j in range(seg):
        F.append([last[j], last[(j + 1) % seg], top]); FC.append(pick(PAL["shell"], rnd))
    bot = len(V); V.append(Vector((0, 0, SH_ZR - 0.13)))
    first = ring_idx[0][0]
    for j in range(seg):
        F.append([first[(j + 1) % seg], first[j], bot]); FC.append(pick(PAL["shell_lip"], rnd))
    build("Shell_Dome", V, F, FC, COLL["SHELL"], MAT["shell"])

    # plastron (cream belly plate)
    vs, fs = ico(2)
    rnd = random.Random(4)
    V = [Vector((p.x * 0.93, p.y * 1.17, p.z * 0.25)) + Vector((0, 0.02, 0.25)) for p in vs]
    FC = [pick(PAL["cream"], rnd) for _ in fs]
    build("Shell_Plastron", V, fs, FC, COLL["SHELL"], MAT["cream"])


def build_rocks():
    rocks = [(0.0, -0.15, 0.55), (-0.45, 0.25, 0.5), (0.45, 0.2, 0.5), (0.0, 0.55, 0.5),
             (-0.6, -0.45, 0.42), (0.6, -0.45, 0.42), (0.72, 0.6, 0.36), (-0.72, 0.6, 0.36),
             (0.0, 0.98, 0.36), (0.3, -0.78, 0.36), (-0.3, -0.78, 0.36), (0.86, 0.05, 0.3),
             (-0.86, 0.05, 0.3), (0.38, 1.0, 0.3), (-0.38, 1.0, 0.3), (0.0, -0.95, 0.3)]
    for i, (x, y, s) in enumerate(rocks):
        rnd = random.Random(100 + i)
        vs, fs = ico(1)
        V = []
        for p in vs:
            q = Vector((p.x * s * rnd.uniform(0.9, 1.1), p.y * s * rnd.uniform(0.85, 1.05), p.z))
            q += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * 0.06 * s
            z = min(q.z, 0.55) * 0.34 * (0.8 + s * 0.4)   # flattened plateau top
            V.append(Vector((q.x, q.y, z)))
        FC = []
        for f in fs:
            n = fnormal(V, f)
            FC.append(pick(PAL["rock_top"] if n.z > 0.6 else PAL["rock_side"], rnd))
        build(f"Shell_Rock_{i:02d}", V, fs, FC, COLL["ROCKS"], MAT["rock"],
              place(x, y, rnd.uniform(0, 360), tilt=0.85, embed=0.05, scale=1.0))


# ----------------------------------------------------------------------------- head
HEAD_POS = Vector((0.0, -1.74, 0.58))
HEAD_V = HEAD_F = None


def build_head():
    global HEAD_V, HEAD_F
    rnd = random.Random(21)
    vs, fs = ico(2)
    V = []
    for p in vs:
        x, y, z = p.x, p.y, p.z
        f = 1 - 0.20 * max(0.0, -y)            # snout narrows toward the front
        x *= f
        z *= 1 - 0.08 * max(0.0, -y)
        if z < -0.55:                           # flatter underside
            z = -0.55 + (z + 0.55) * 0.35
        if z > 0.2:                             # slightly domed forehead
            z += 0.05 * (1 - abs(x))
        q = Vector((x * 0.76, y * 0.80, z * 0.58))
        q += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.012
        V.append(q)
    FC = []
    for f in fs:
        c = centroid(V, f)
        n = fnormal(V, f)
        if c.y < 0.15:
            cream = c.z < (-0.05 + 0.14 * (abs(c.x) / 0.6) ** 2) - 0.15 * max(0.0, c.y + 0.1)
        else:
            cream = c.z < -0.32
        if cream:
            FC.append(pick(PAL["cream"], rnd))
        elif n.z > 0.35 and c.y < 0.2 and rnd.random() < 0.55:
            FC.append(pick(PAL["head_light"], rnd))
        elif c.y > 0.35:
            FC.append(pick(PAL["head_back"] + PAL["head"], rnd))
        else:
            FC.append(pick(PAL["head"], rnd))
    HEAD_V, HEAD_F = V, fs
    build("Head_Main", V, fs, FC, COLL["HEAD"], MAT["head"], Matrix.Translation(HEAD_POS))

    # neck: links head into the shell opening
    vs, fs = ico(1)
    rnd = random.Random(22)
    V = [Vector((p.x * 0.52, p.y * 0.5, p.z * 0.4)) for p in vs]
    FC = [pick(PAL["cream"] if centroid(V, f).z < -0.08 else PAL["head_back"] + PAL["head"], rnd) for f in fs]
    build("Head_Neck", V, fs, FC, COLL["HEAD"], MAT["head"], Matrix.Translation((0, -1.15, 0.52)))

    # moss tuft on top of the head
    build_moss_patch("Head_Moss", 0.16, Matrix.Translation(HEAD_POS + Vector((-0.15, 0.32, 0.55))) @
                     Matrix.Rotation(-0.25, 4, "X"), seed=23)


def build_eyes():
    """Eyes are RECESSED: a tapered hexagonal socket is boolean-cut into the head
    (socket walls = dark-blue orbit), the glowing cyan hexagon sits at the bottom."""
    head = bpy.data.objects["Head_Main"]
    tree = BVHTree.FromPolygons(HEAD_V, HEAD_F)
    n, rot = 6, math.radians(30)
    R_TOP, R_BOT, DEPTH = 0.235, 0.165, 0.095      # socket radius at surface / floor, depth
    cutters = []
    for side, sx in (("L", 1), ("R", -1)):
        d = Vector((0.58 * sx, -0.81, 0.05)).normalized()
        hit, nrm, _, _ = tree.ray_cast(Vector((0, 0, 0)), d)
        if nrm.dot(d) < 0:
            nrm = -nrm
        Z = (nrm + d).normalized()
        Xa = Vector((0, 0, 1)).cross(Z).normalized()
        Ya = Z.cross(Xa)
        rnd = random.Random(31 if sx > 0 else 32)
        # local eye frame: origin on the head surface, +Z out of the head
        M_local = axes_matrix(Xa, Ya, Z, hit)
        M = Matrix.Translation(HEAD_POS) @ M_local

        # --- socket cutter (tapered hex frustum), coloured as the orbit lining
        V, F, FC = [], [], []
        for (r, z) in ((R_BOT, -DEPTH), (R_TOP, 0.0), (R_TOP * 1.9, 0.35)):
            for k in range(n):
                a = rot + 2 * math.pi * k / n
                V.append(Vector((r * math.cos(a), r * math.sin(a), z)))
        for ring in range(2):
            for k in range(n):
                k2 = (k + 1) % n
                F.append([ring * n + k, ring * n + k2, (ring + 1) * n + k2, (ring + 1) * n + k])
                FC.append(pick(PAL["eye_ring"] if ring == 0 else PAL["eye_ring_dark"], rnd))
        F.append([k for k in range(n)][::-1]); FC.append(pick(PAL["eye_ring_dark"], rnd))
        F.append([2 * n + k for k in range(n)]); FC.append(pick(PAL["eye_ring_dark"], rnd))
        cut = build(f"_cut_{side}", V, F, FC, SC.collection, MAT["head"], M)
        cutters.append(cut)
        mod = head.modifiers.new(f"Socket_{side}", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cut
        if hasattr(mod, "solver"):
            mod.solver = "EXACT"

        # --- orbit: thin dark-blue bevel lip at the socket floor around the glow
        V, F, FC = [], [], []
        for (r, z) in ((R_BOT + 0.004, -DEPTH + 0.002), (R_BOT - 0.004, -DEPTH + 0.016), (0.142, -DEPTH + 0.010)):
            for k in range(n):
                a = rot + 2 * math.pi * k / n
                V.append(Vector((r * math.cos(a), r * math.sin(a), z)))
        for ring in range(2):
            for k in range(n):
                k2 = (k + 1) % n
                F.append([ring * n + k, ring * n + k2, (ring + 1) * n + k2, (ring + 1) * n + k])
                FC.append(pick(PAL["eye_ring_dark"], rnd))
        build(f"Eye_{side}_Orbit", V, F, FC, COLL["EYES"], MAT["eye_ring"], M, recalc=False)

        # --- glowing cyan centre, slightly domed, at the bottom of the socket
        z0 = -DEPTH + 0.006
        V, F, FC = [], [], []
        for k in range(n):
            a = rot + 2 * math.pi * k / n
            V.append(Vector((0.148 * math.cos(a), 0.148 * math.sin(a), z0)))
        for k in range(n):
            a = 2 * math.pi * k / n
            V.append(Vector((0.08 * math.cos(a), 0.08 * math.sin(a), z0 + 0.018)))
        V.append(Vector((0.0, 0.0, z0 + 0.022)))
        for k in range(n):
            k2 = (k + 1) % n
            F.append([k, k2, n + k2]); FC.append(jit(C("5EE6FF"), 0.06, rnd))
            F.append([k, n + k2, n + k]); FC.append(jit(C("74EEFF"), 0.06, rnd))
            F.append([n + k, n + k2, 2 * n]); FC.append(jit(C("B8FFFF"), 0.04, rnd))
        build(f"Eye_{side}_Glow", V, F, FC, COLL["EYES"], MAT["eye_glow"], M, recalc=False)

    # bake the sockets into the head mesh, then drop the cutters
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    new_me = bpy.data.meshes.new_from_object(head.evaluated_get(dg))
    old = head.data
    head.modifiers.clear()
    head.data = new_me
    new_me.name = "Head_Main"
    bpy.data.meshes.remove(old)
    for p in new_me.polygons:
        p.use_smooth = False
    for c in cutters:
        me = c.data
        bpy.data.objects.remove(c)
        bpy.data.meshes.remove(me)


# ----------------------------------------------------------------------------- flippers
def build_flipper(name, root, direction, normal_hint, L, W, T, seed, N=8, M=6):
    rnd = random.Random(seed)
    X = direction.normalized()
    Z = (normal_hint - X * normal_hint.dot(X)).normalized()
    Y = Z.cross(X)
    sweep = 1.0 if Y.dot(Vector((0, 1, 0))) > 0 else -1.0   # trailing-edge bulge goes backward
    Mx = axes_matrix(X, Y, Z, root)

    def hw(t):
        return W * (0.38 * (1 - t) + math.sin(math.pi * min(t, 1.0)) ** 0.85 * (1 - 0.25 * t))

    def yc(t):
        return sweep * W * 0.38 * math.sin(math.pi * t)

    def bend(t):
        return -0.10 * L * t * t

    sp = -0.3 * sweep   # thickest along the leading edge

    def ztop(t, s):
        q = (s - sp) / ((1 - sp) if s > sp else (1 + sp))
        return T * (0.2 + 0.8 * max(0.0, 1 - q * q) ** 0.55) * (1 - 0.38 * t)

    V, F, FC, top, bot = [], [], [], [], []
    for i in range(N):
        t = i / N
        row, brow = [], []
        for j in range(M + 1):
            s = -1 + 2 * j / M
            bump = rnd.uniform(-0.25, 0.25) * T * 0.35 if (0 < j < M and i > 0) else 0.0
            V.append(Vector((t * L, yc(t) + s * hw(t), ztop(t, s) + bend(t) + 0.004 + bump)))
            row.append(len(V) - 1)
        for j in range(M + 1):
            if j in (0, M):
                brow.append(row[j]); continue
            s = -1 + 2 * j / M
            V.append(Vector((t * L, yc(t) + s * hw(t), -0.75 * ztop(t, s) + bend(t))))
            brow.append(len(V) - 1)
        top.append(row); bot.append(brow)
    tip = len(V); V.append(Vector((L, yc(1.0), bend(1.0))))

    def tcol(f, under=False):
        t = centroid(V, f).x / L
        if under:
            return jit(lerp(FLIP_UNDER, FLIP_TIP, t ** 2.6 * 0.6), 0.08, rnd)
        return jit(lerp(FLIP_BASE, FLIP_TIP, t ** 2.6), 0.10, rnd)

    for grid, under in ((top, False), (bot, True)):
        for i in range(N - 1):
            for j in range(M):
                a, b, c, d = grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]
                tris = ([a, b, c], [a, c, d]) if (i + j) % 2 == 0 else ([a, b, d], [b, c, d])
                for tri in tris:
                    tri = tri[::-1] if under else tri
                    F.append(tri); FC.append(tcol(tri, under))
        for j in range(M):
            tri = [grid[N - 1][j], tip, grid[N - 1][j + 1]]
            tri = tri[::-1] if under else tri
            F.append(tri); FC.append(tcol(tri, under))
    cap = top[0][:] + bot[0][1:M][::-1]
    F.append(cap); FC.append(jit(FLIP_UNDER, 0.04, rnd))
    build(f"{name}", V, F, FC, COLL["FLIPPERS"], MAT["flipper"], Mx)

    # hexagonal scutes following the top surface
    rh = 0.13 * (L / 1.75)
    V, F, FC = [], [], []
    for r in range(-5, 6):
        yloc = r * 1.5 * rh
        for c in range(0, 30):
            x = c * math.sqrt(3) * rh + (r % 2) * math.sqrt(3) * rh / 2 + rh * 0.9
            t = x / L
            if not (0.10 < t < 0.86):
                continue
            if abs(yloc) > hw(t) - rh * 0.95 or abs(yloc) > hw(min(1, t + 0.05)) - rh * 0.6:
                continue

            def pt(px, py, lift):
                tt = px / L
                s = py / max(1e-4, hw(tt))
                return Vector((px, yc(tt) + py, ztop(tt, max(-1, min(1, s))) + bend(tt) + lift))

            b = len(V)
            for k in range(6):
                a = math.radians(30 + 60 * k)
                V.append(pt(x + 0.78 * rh * math.cos(a), yloc + 0.78 * rh * math.sin(a), 0.032))
            V.append(pt(x, yloc, 0.042))
            for k in range(6):
                tri = [b + k, b + (k + 1) % 6, b + 6]
                F.append(tri); FC.append(jit(lerp(SCUTE_BASE, SCUTE_TIP, t ** 1.4), 0.06, rnd))
    build(f"{name}_Scutes", V, F, FC, COLL["FLIPPERS"], MAT["scute"], Mx, recalc=False)


def build_flippers():
    for side, sx in (("L", 1), ("R", -1)):
        build_flipper(f"Flipper_Front_{side}", Vector((0.82 * sx, -0.80, 0.45)),
                      Vector((0.90 * sx, 0.45, -0.52)), Vector((0.38 * sx, -0.66, 0.66)),
                      L=1.75, W=0.37, T=0.28, seed=40 + sx)
        build_flipper(f"Flipper_Rear_{side}", Vector((0.70 * sx, 0.92, 0.32)),
                      Vector((0.85 * sx, 0.45, -0.38)), Vector((0.25 * sx, 0.60, 0.78)),
                      L=1.30, W=0.31, T=0.23, seed=50 + sx, N=7)


# ----------------------------------------------------------------------------- reef dressing
def make_coral(name, pal, H, r0, depth, seed, matrix, kids_p3=0.15, ang=(34, 58), bias=0.32):
    rnd = random.Random(seed)
    V, F, FC = [], [], []
    col = lambda: pick(pal, rnd)

    def grow(p, d, L, r, lvl):
        q = p + d * L
        add_prism(V, F, FC, p, q, r, r * 0.84, col, 6, rnd.random())
        add_ico(V, F, FC, q, r * 0.84 * 1.15, col, 0, rnd=rnd)
        if lvl == depth:
            return
        k = 3 if rnd.random() < kids_p3 else 2
        angs = [rnd.uniform(*ang), -rnd.uniform(*ang)] + ([rnd.uniform(-8, 8)] if k == 3 else [])
        for a in angs:
            nd = Matrix.Rotation(math.radians(a), 3, "Y") @ d
            nd = Matrix.Rotation(math.radians(rnd.uniform(-10, 10)), 3, "X") @ nd
            nd = (nd + Vector((0, 0, bias))).normalized()
            grow(q, nd, L * rnd.uniform(0.78, 0.95), r * 0.8, lvl + 1)

    grow(Vector((0, 0, -0.12)), Vector((rnd.uniform(-.1, .1), 0, 1)).normalized(), H * 0.30, r0, 0)
    return build(name, V, F, FC, COLL["CORAL"], MAT["coral"], matrix)


def build_sponges(name, tubes, matrix, seed):
    rnd = random.Random(seed)
    V, F, FC = [], [], []
    n = 6
    for (ox, oy, h, r, tx, ty) in tubes:
        h, r = h * 0.8, r * 1.45
        ox, oy = ox * 1.35, oy * 1.35
        d = Vector((tx, ty, 1)).normalized()
        u, v = frame(d)
        base = Vector((ox, oy, -0.08))
        topc = base + d * h
        rings = [(base, r * 1.05), (topc, r), (topc, r * 0.58), (topc - d * r * 1.3, r * 0.55)]
        b = len(V)
        rot = rnd.random()
        for (c, rr) in rings:
            for k in range(n):
                a = rot + 2 * math.pi * k / n
                V.append(c + (u * math.cos(a) + v * math.sin(a)) * rr)
        cols = [PAL["orange"], PAL["orange_top"], PAL["orange_in"]]
        for ring in range(3):
            for k in range(n):
                k2 = (k + 1) % n
                F.append([b + ring * n + k, b + ring * n + k2, b + (ring + 1) * n + k2, b + (ring + 1) * n + k])
                FC.append(pick(cols[ring], rnd))
        F.append([b + 3 * n + k for k in range(n)]); FC.append(pick(PAL["orange_in"], rnd))
        F.append([b + k for k in range(n)][::-1]); FC.append(pick(PAL["orange"], rnd))
    return build(name, V, F, FC, COLL["SPONGES"], MAT["sponge"], matrix, recalc=False)


def kelp_blade(V, F, FC, H, w, n, amp, fan_deg, yaw_deg, off, rnd):
    R = Matrix.Rotation(math.radians(yaw_deg), 3, "Z") @ Matrix.Rotation(math.radians(fan_deg), 3, "Y")
    th = 0.025
    rings = []
    for i in range(n):
        t = i / n
        cx = amp * (1 if i % 2 else -1) * (0.4 + t)
        ww = w * (1 - 0.45 * t) * (0.7 if i == 0 else 1.0)
        z = H * t - 0.08
        pts = [Vector((cx - ww / 2, 0, z)), Vector((cx, th, z + ww * 0.15)),
               Vector((cx + ww / 2, 0, z)), Vector((cx, -th, z + ww * 0.15))]
        idx = []
        for p in pts:
            V.append(R @ p + off); idx.append(len(V) - 1)
        rings.append(idx)
    tip = len(V); V.append(R @ Vector((amp * 0.5, 0, H)) + off)
    for i in range(n - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(4):
            k2 = (k + 1) % 4
            F.append([a[k], a[k2], b[k2], b[k]])
            FC.append(pick(PAL["kelp_light"] if k in (0, 3) and rnd.random() < 0.4 else PAL["kelp"], rnd))
    for k in range(4):
        F.append([rings[-1][k], rings[-1][(k + 1) % 4], tip]); FC.append(pick(PAL["kelp"], rnd))
    F.append(rings[0][::-1]); FC.append(pick(PAL["kelp"], rnd))


def build_kelp(name, H, blades, matrix, seed):
    rnd = random.Random(seed)
    V, F, FC = [], [], []
    for b in range(blades):
        fan = (b - (blades - 1) / 2) * 16 + rnd.uniform(-5, 5)
        hh = H * (1.0 if b == blades // 2 else rnd.uniform(0.7, 0.9))
        kelp_blade(V, F, FC, hh, 0.13 * (H / 0.8) ** 0.5 + 0.03, 7, 0.05, fan, b * 55 + rnd.uniform(-15, 15),
                   Vector(((b - (blades - 1) / 2) * 0.09, rnd.uniform(-0.03, 0.03), 0)), rnd)
    return build(name, V, F, FC, COLL["KELP"], MAT["kelp"], matrix)


def build_starfish(name, R, matrix, seed):
    rnd = random.Random(seed)
    h = R * 0.32
    V = [Vector((0, 0, h))]
    outer, inner, ridge = [], [], []
    for k in range(5):
        a = math.radians(90 + 72 * k)
        ai = a + math.radians(36)
        V.append(Vector((R * math.cos(a), R * math.sin(a), 0.03))); outer.append(len(V) - 1)
        V.append(Vector((R * 0.45 * math.cos(ai), R * 0.45 * math.sin(ai), 0.05))); inner.append(len(V) - 1)
        V.append(Vector((R * 0.55 * math.cos(a), R * 0.55 * math.sin(a), h * 0.6))); ridge.append(len(V) - 1)
    F, FC = [], []
    for k in range(5):
        ip = inner[k - 1]
        for tri in ([0, ip, ridge[k]], [0, ridge[k], inner[k]],
                    [ip, outer[k], ridge[k]], [ridge[k], outer[k], inner[k]]):
            F.append(tri); FC.append(pick(PAL["star"], rnd))
    outline = []
    for k in range(5):
        outline += [outer[k], inner[k]]
    b0 = len(V)
    for i in outline:
        V.append(Vector((V[i].x, V[i].y, 0.0)))
    for i in range(10):
        i2 = (i + 1) % 10
        F.append([outline[i], b0 + i, b0 + i2, outline[i2]]); FC.append(pick(PAL["star"], rnd))
    F.append([b0 + i for i in range(10)][::-1]); FC.append(pick(PAL["star"], rnd))
    return build(name, V, F, FC, COLL["STARFISH"], MAT["star"], matrix)


def build_moss_patch(name, r, matrix, seed):
    rnd = random.Random(seed)
    vs, fs = ico(1)
    V = [Vector((p.x * r * rnd.uniform(0.85, 1.15), p.y * r * rnd.uniform(0.7, 1.1), p.z * 0.045)) for p in vs]
    FC = [pick(PAL["moss"], rnd) for _ in fs]
    return build(name, V, fs, FC, COLL["MOSS"], MAT["moss"], matrix)


def build_reef():
    # big staghorn corals (pink) — plane of each coral faces mostly the front camera
    make_coral("Coral_Pink_Center", PAL["pink"], 1.15, 0.10, 2, 7, place(0.05, 0.15, 0, embed=0.02))
    make_coral("Coral_Pink_Front", PAL["pink"], 0.70, 0.075, 2, 12, place(-0.30, -0.40, 25, embed=0.02))
    make_coral("Coral_Pink_BackL", PAL["pink"], 0.55, 0.062, 2, 15, place(0.62, 0.62, 65, tilt=0.5))
    make_coral("Coral_Pink_BackTail", PAL["pink"], 0.40, 0.052, 2, 17, place(0.35, 0.98, 110, tilt=0.5))
    # purple branching corals
    make_coral("Coral_Purple_FrontR", PAL["purple"], 0.62, 0.052, 2, 21, place(-0.55, -0.45, -30, tilt=0.45),
               kids_p3=0.55, ang=(30, 50))
    make_coral("Coral_Purple_SideL", PAL["purple"], 0.50, 0.046, 2, 23, place(0.72, -0.30, 80, tilt=0.55),
               kids_p3=0.55, ang=(30, 50))
    make_coral("Coral_Purple_BackR", PAL["purple"], 0.50, 0.046, 2, 25, place(-0.60, 0.45, -60, tilt=0.5),
               kids_p3=0.55, ang=(30, 50))
    make_coral("Coral_Purple_RimR", PAL["purple"], 0.36, 0.04, 2, 27, place(-0.84, 0.80, -80, tilt=0.6),
               kids_p3=0.55, ang=(30, 50))
    # orange tube sponges
    build_sponges("Sponge_Main", [(0, 0, 0.55, 0.075, 0, 0), (0.15, 0.03, 0.42, 0.07, 0.15, 0),
                                  (-0.13, 0.05, 0.36, 0.065, -0.18, 0.05), (0.05, -0.13, 0.30, 0.06, 0.05, -0.2)],
                  place(0.42, 0.25, 0), 61)
    build_sponges("Sponge_BackL", [(0, 0, 0.30, 0.06, 0, 0), (0.11, 0.04, 0.24, 0.055, 0.2, 0.1),
                                   (-0.1, 0.06, 0.2, 0.05, -0.2, 0.1)], place(0.82, 0.86, 50, tilt=0.6), 62)
    build_sponges("Sponge_FrontR", [(0, 0, 0.22, 0.05, 0, 0), (0.09, 0.03, 0.16, 0.045, 0.25, 0)],
                  place(-0.84, -0.28, 0, tilt=0.6), 63)
    build_sponges("Sponge_BackR", [(0, 0, 0.25, 0.055, 0, 0), (0.1, 0.03, 0.18, 0.048, 0.25, 0)],
                  place(-0.82, 0.62, 0, tilt=0.6), 64)
    # kelp
    build_kelp("Kelp_BackTall", 0.85, 3, place(0.35, 0.80, 90, tilt=0.2), 71)
    build_kelp("Kelp_Center", 0.45, 3, place(-0.05, -0.12, 0, tilt=0.2), 72)
    build_kelp("Kelp_BackL", 0.35, 3, place(0.80, 1.00, 60, tilt=0.5), 73)
    build_kelp("Kelp_FrontR", 0.48, 3, place(-0.86, -0.40, -70, tilt=0.4), 74)
    build_kelp("Kelp_FrontL", 0.36, 3, place(0.86, -0.50, 70, tilt=0.4), 75)
    build_kelp("Kelp_BackR", 0.52, 3, place(-0.72, 0.60, -90, tilt=0.4), 76)
    build_kelp("Kelp_BackCenter", 0.24, 3, place(0.0, 0.78, 180, tilt=0.3), 77)
    # starfish
    build_starfish("Starfish_FrontL", 0.17, place(0.80, -0.72, 30, tilt=1.0, embed=0.0, scale=1.25), 81)
    build_starfish("Starfish_FrontR", 0.16, place(-0.80, -0.72, -30, tilt=1.0, embed=0.0, scale=1.25), 82)
    build_starfish("Starfish_Back", 0.21, place(0.05, 1.16, 180, tilt=1.0, embed=0.0, scale=2.2), 83)
    build_starfish("Starfish_SideL", 0.15, place(0.93, -0.12, 90, tilt=1.0, embed=0.0, scale=1.25), 84)
    # moss patches
    for i, (x, y, r) in enumerate([(0.55, -0.62, 0.16), (-0.3, 0.35, 0.14), (0.2, 0.85, 0.15), (-0.62, -0.1, 0.13),
                                   (0.86, 0.35, 0.14), (0.0, 1.10, 0.12), (-0.85, 0.72, 0.12), (0.45, -0.05, 0.12),
                                   (0.0, -1.02, 0.14), (-0.5, -0.8, 0.12)]):
        build_moss_patch(f"Moss_{i:02d}", r, place(x, y, i * 37, tilt=0.95, embed=-0.04, scale=1.3), 90 + i)


def build_bubbles():
    pts = [(-1.05, -0.3, 2.05, 0.10), (-1.38, 0.0, 1.70, 0.11), (-1.32, 0.2, 1.38, 0.065),
           (1.00, -0.3, 2.15, 0.10), (1.30, 0.1, 1.80, 0.115), (1.42, 0.3, 1.50, 0.075),
           (1.25, 0.5, 1.20, 0.06), (-1.18, 0.6, 1.10, 0.055)]
    for i, (x, y, z, r) in enumerate(pts):
        rnd = random.Random(200 + i)
        vs, fs = ico(1)
        V = [p * r for p in vs]
        FC = [(1, 1, 1) for _ in fs]
        build(f"Bubble_{i:02d}", V, fs, FC, COLL["BUBBLES"], MAT["bubble"],
              Matrix.Translation((x, y, z)) @ Matrix.Rotation(rnd.random() * 3, 4, "Z"))


# ----------------------------------------------------------------------------- world / lights / cameras
def setup_world():
    w = bpy.data.worlds.new("World_Ocean")
    SC.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*C("68C9F9"), 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (*C("2F6DE2"), 1)
    bg_cam = nt.nodes.new("ShaderNodeBackground")
    bg_amb = nt.nodes.new("ShaderNodeBackground")
    bg_amb.inputs["Color"].default_value = (0.86, 0.93, 1.0, 1)
    bg_amb.inputs["Strength"].default_value = 0.78
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg_cam.inputs["Color"])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    add.use_clamp = True
    nt.links.new(lp.outputs["Is Camera Ray"], add.inputs[0])
    nt.links.new(lp.outputs["Transparent Depth"], add.inputs[1])
    nt.links.new(add.outputs[0], mix.inputs["Fac"])
    nt.links.new(bg_amb.outputs[0], mix.inputs[1])
    nt.links.new(bg_cam.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def setup_lights_cameras():
    L = COLL["CAMERAS_LIGHTS"]
    sun = bpy.data.lights.new("Light_Key_Sun", "SUN")
    sun.energy = 1.5
    sun.angle = math.radians(25)
    so = bpy.data.objects.new("Light_Key_Sun", sun)
    L.objects.link(so)
    so.location = (-4, -8, 9)
    look_at(so, (0, 0, 0))
    fill = bpy.data.lights.new("Light_Fill_Sun", "SUN")
    fill.energy = 0.35
    fill.angle = math.radians(60)
    fo = bpy.data.objects.new("Light_Fill_Sun", fill)
    L.objects.link(fo)
    fo.location = (6, 4, 3)
    look_at(fo, (0, 0, 0))

    target = Vector((0.0, -0.15, 1.0))
    cams = {}
    for name, loc, scale in (("CAM_Front_Ortho", (0, -14, 1.0), 4.1),
                             ("CAM_Back_Ortho", (0, 14, 1.0), 4.1),
                             ("CAM_ThreeQuarter_Ortho", None, 4.6)):
        cd = bpy.data.cameras.new(name)
        cd.type = "ORTHO"
        cd.ortho_scale = scale
        cd.clip_end = 100
        co = bpy.data.objects.new(name, cd)
        L.objects.link(co)
        el = math.radians(6)
        if name == "CAM_Front_Ortho":
            loc = target + Vector((0, -math.cos(el), math.sin(el))) * 14
        elif name == "CAM_Back_Ortho":
            loc = target + Vector((0, math.cos(el), math.sin(el))) * 14
        else:
            loc = target + Vector((0.95, -0.30, 0.34)).normalized() * 14
        co.location = loc
        look_at(co, target if name != "CAM_ThreeQuarter_Ortho" else Vector((0, -0.45, 0.95)))
        cams[name] = co
    SC.camera = cams["CAM_Front_Ortho"]
    return cams


def setup_render():
    SC.render.engine = "CYCLES"
    SC.cycles.device = "CPU"
    SC.cycles.samples = int(os.environ.get("TURTLE_SAMPLES", "48"))
    try:
        SC.cycles.use_denoising = True
    except Exception:
        pass
    SC.render.resolution_x = SC.render.resolution_y = int(os.environ.get("TURTLE_RES", "1024"))
    SC.render.film_transparent = False
    SC.view_settings.view_transform = "Standard"
    SC.view_settings.look = "None"


# ----------------------------------------------------------------------------- main
build_shell()
build_rocks()
build_head()
build_eyes()
build_flippers()
build_reef()
build_bubbles()
setup_world()
cams = setup_lights_cameras()
setup_render()

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "sea_turtle_reef.blend"))

if os.environ.get("TURTLE_NO_RENDER") != "1":
    for key, fname in (("CAM_Front_Ortho", "front.png"), ("CAM_ThreeQuarter_Ortho", "three_quarter.png"),
                       ("CAM_Back_Ortho", "back.png")):
        SC.camera = cams[key]
        SC.render.filepath = os.path.join(RENDER_DIR, fname)
        bpy.ops.render.render(write_still=True)
    SC.camera = cams["CAM_Front_Ortho"]
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "sea_turtle_reef.blend"))
print("DONE")
