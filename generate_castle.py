import math

class WavefrontObjBuilder:
    def __init__(self, obj_name="Slott_10Etasjer", mtl_filename="slott_10etasjer.mtl"):
        self.obj_name = obj_name
        self.mtl_filename = mtl_filename
        self.vertices = []
        self.uvs = [
            (0.0, 0.0),  # vt 1
            (1.0, 0.0),  # vt 2
            (1.0, 1.0),  # vt 3
            (0.0, 1.0),  # vt 4
            (0.5, 1.0),  # vt 5 (spiss på tak)
        ]
        # Pre-allokerte aksejusterte normaler (vn 1..6)
        self.normals = [
            ( 0.0,  0.0, -1.0),  # vn 1: Bunn (-Z)
            ( 0.0,  0.0,  1.0),  # vn 2: Topp (+Z)
            ( 0.0, -1.0,  0.0),  # vn 3: Sør (-Y)
            ( 0.0,  1.0,  0.0),  # vn 4: Nord (+Y)
            (-1.0,  0.0,  0.0),  # vn 5: Vest (-X)
            ( 1.0,  0.0,  0.0),  # vn 6: Øst (+X)
        ]
        # Lagrer flater gruppert etter (group_name, material_name)
        self.groups = {}
        self.current_group = "Default"
        self.current_material = "SteinMur"

    def set_context(self, group_name, material_name):
        self.current_group = group_name
        self.current_material = material_name
        key = (group_name, material_name)
        if key not in self.groups:
            self.groups[key] = []

    def add_vertex(self, x, y, z):
        self.vertices.append((x, y, z))
        return len(self.vertices)

    def add_normal(self, nx, ny, nz):
        length = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
        self.normals.append((nx / length, ny / length, nz / length))
        return len(self.normals)

    def add_face(self, verts_uv_norm):
        """verts_uv_norm: liste med tupler (v_idx, vt_idx, vn_idx)"""
        key = (self.current_group, self.current_material)
        if key not in self.groups:
            self.groups[key] = []
        self.groups[key].append(verts_uv_norm)

    def add_box(self, x, y, z, dx, dy, dz):
        idx = len(self.vertices)
        self.vertices.extend([
            (x,      y,      z),       # +1
            (x + dx, y,      z),       # +2
            (x + dx, y + dy, z),       # +3
            (x,      y + dy, z),       # +4
            (x,      y,      z + dz),  # +5
            (x + dx, y,      z + dz),  # +6
            (x + dx, y + dy, z + dz),  # +7
            (x,      y + dy, z + dz),  # +8
        ])
        # Bunn (vn 1)
        self.add_face([(idx+1, 1, 1), (idx+4, 2, 1), (idx+3, 3, 1), (idx+2, 4, 1)])
        # Topp (vn 2)
        self.add_face([(idx+5, 1, 2), (idx+6, 2, 2), (idx+7, 3, 2), (idx+8, 4, 2)])
        # Front -Y (vn 3)
        self.add_face([(idx+1, 1, 3), (idx+2, 2, 3), (idx+6, 3, 3), (idx+5, 4, 3)])
        # Bak +Y (vn 4)
        self.add_face([(idx+3, 1, 4), (idx+4, 2, 4), (idx+8, 3, 4), (idx+7, 4, 4)])
        # Venstre -X (vn 5)
        self.add_face([(idx+4, 1, 5), (idx+1, 2, 5), (idx+5, 3, 5), (idx+8, 4, 5)])
        # Høyre +X (vn 6)
        self.add_face([(idx+2, 1, 6), (idx+3, 2, 6), (idx+7, 3, 6), (idx+6, 4, 6)])

    def add_cylinder(self, cx, cy, z_base, radius, height, segments=20, cone_height=0, roof_mat="TakSkifer"):
        wall_group = self.current_group
        wall_mat = self.current_material

        base_v = []
        top_v = []
        radial_vn = []

        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            ca, sa = math.cos(angle), math.sin(angle)
            vx, vy = cx + radius * ca, cy + radius * sa
            base_v.append(self.add_vertex(vx, vy, z_base))
            top_v.append(self.add_vertex(vx, vy, z_base + height))
            radial_vn.append(self.add_normal(ca, sa, 0.0))

        # Sylindervegger
        self.set_context(wall_group, wall_mat)
        for i in range(segments):
            ni = (i + 1) % segments
            vn_idx = radial_vn[i]
            self.add_face([
                (base_v[i], 1, vn_idx),
                (base_v[ni], 2, vn_idx),
                (top_v[ni], 3, vn_idx),
                (top_v[i], 4, vn_idx)
            ])

        # Konisk tak
        if cone_height > 0:
            self.set_context(wall_group + "_Tak", roof_mat)
            apex = self.add_vertex(cx, cy, z_base + height + cone_height)
            for i in range(segments):
                ni = (i + 1) % segments
                mid_angle = 2.0 * math.pi * (i + 0.5) / segments
                n_idx = self.add_normal(math.cos(mid_angle), math.sin(mid_angle), radius / cone_height)
                self.add_face([
                    (top_v[i], 1, n_idx),
                    (top_v[ni], 2, n_idx),
                    (apex, 5, n_idx)
                ])

    def export(self, obj_filename="slott_10etasjer.obj"):
        # 1. Skriv tilhørende .mtl-fil med materialmetadata
        with open(self.mtl_filename, "w", encoding="ascii", newline="\n") as mf:
            mf.write("# Wavefront MTL Material File\n")
            mf.write("# Generated for Blender Import\n\n")
            
            mf.write("newmtl SteinMur\n")
            mf.write("Ns 50.0000\nKa 0.2000 0.2000 0.2000\nKd 0.5500 0.5300 0.5000\nKs 0.1000 0.1000 0.1000\nd 1.0\nillum 2\n\n")
            
            mf.write("newmtl GulvDekke\n")
            mf.write("Ns 30.0000\nKa 0.1500 0.1200 0.1000\nKd 0.4200 0.3200 0.2200\nKs 0.0800 0.0800 0.0800\nd 1.0\nillum 2\n\n")
            
            mf.write("newmtl TakSkifer\n")
            mf.write("Ns 80.0000\nKa 0.1000 0.1000 0.1500\nKd 0.2200 0.2600 0.3200\nKs 0.2500 0.2500 0.2500\nd 1.0\nillum 2\n")

        # 2. Skriv .obj-fil med standard Wavefront-header og metadata
        total_faces = sum(len(flist) for flist in self.groups.values())
        with open(obj_filename, "w", encoding="ascii", newline="\n") as f:
            f.write("# Blender 4.0.0 - Wavefront OBJ File\n")
            f.write("# www.blender.org\n")
            f.write(f"# Vertices: {len(self.vertices)} | Faces: {total_faces}\n")
            f.write(f"mtllib {self.mtl_filename}\n")
            f.write(f"o {self.obj_name}\n\n")

            # Vertekser (v)
            for vx, vy, vz in self.vertices:
                f.write(f"v {vx:.4f} {vy:.4f} {vz:.4f}\n")
            f.write("\n")

            # Teksturkoordinater (vt)
            for u, v in self.uvs:
                f.write(f"vt {u:.4f} {v:.4f}\n")
            f.write("\n")

            # Verteksnormaler (vn)
            for nx, ny, nz in self.normals:
                f.write(f"vn {nx:.4f} {ny:.4f} {nz:.4f}\n")
            f.write("\n")

            # Geometri gruppert per etasje og materiale
            for (group_name, mat_name), faces in self.groups.items():
                f.write(f"g {group_name}\n")
                f.write(f"usemtl {mat_name}\n")
                f.write("s off\n")
                for face in faces:
                    face_str = " ".join(f"{v}/{vt}/{vn}" for v, vt, vn in face)
                    f.write(f"f {face_str}\n")
                f.write("\n")

        print(f"Ferdig! Genererte '{obj_filename}' og '{self.mtl_filename}' ({len(self.vertices)} v, {total_faces} f).")


def build_10_storey_castle():
    builder = WavefrontObjBuilder()

    num_floors = 10
    rooms_per_side = 16  # 16 Nord + 16 Sør = 32 rom per etasje (320 rom totalt)
    room_w, room_d = 6.0, 10.0
    corridor_d = 4.0
    floor_h, slab_th = 4.5, 0.5
    wall_th, ext_wall_th = 0.4, 0.8
    door_w, door_h = 1.6, 2.8
    win_w, win_h, win_sill = 1.8, 2.2, 1.1

    total_w = rooms_per_side * room_w
    total_d = (2 * room_d) + corridor_d
    half_w, half_d = total_w / 2.0, total_d / 2.0

    # Fundament
    builder.set_context("Fundament", "SteinMur")
    builder.add_box(-half_w - 6, -half_d - 6, 0, total_w + 12, total_d + 12, 2.0)

    # 10 Etasjer med 32 rom hver
    for fl in range(num_floors):
        floor_label = f"Etasje_{fl+1:02d}"
        z_floor = 2.0 + fl * (floor_h + slab_th)
        z_wall = z_floor + slab_th

        # Etasjeskiller / Gulv
        builder.set_context(f"{floor_label}_Gulv", "GulvDekke")
        builder.add_box(-half_w, -half_d, z_floor, total_w, total_d, slab_th)

        # Vegger og rom i etasjen
        builder.set_context(f"{floor_label}_Vegger", "SteinMur")
        builder.add_box(-half_w, -half_d, z_wall, ext_wall_th, total_d, floor_h)
        builder.add_box(half_w - ext_wall_th, -half_d, z_wall, ext_wall_th, total_d, floor_h)

        # Trappesjakter
        builder.add_box(-half_w + ext_wall_th, -corridor_d/2, z_wall, 4.0, corridor_d, floor_h)
        builder.add_box(half_w - ext_wall_th - 4.0, -corridor_d/2, z_wall, 4.0, corridor_d, floor_h)

        for r in range(rooms_per_side):
            rx = -half_w + r * room_w

            # Skillevegger mellom rom
            if r > 0:
                builder.add_box(rx, -half_d, z_wall, wall_th, room_d, floor_h)
                builder.add_box(rx, corridor_d/2, z_wall, wall_th, room_d, floor_h)

            # Sør-fløy: Korridorvegg med dør + Fasadevegg med vindu
            builder.add_box(rx, -corridor_d/2 - wall_th, z_wall, (room_w - door_w)/2, wall_th, floor_h)
            builder.add_box(rx + (room_w + door_w)/2, -corridor_d/2 - wall_th, z_wall, (room_w - door_w)/2, wall_th, floor_h)
            builder.add_box(rx + (room_w - door_w)/2, -corridor_d/2 - wall_th, z_wall + door_h, door_w, wall_th, floor_h - door_h)

            builder.add_box(rx, -half_d, z_wall, (room_w - win_w)/2, ext_wall_th, floor_h)
            builder.add_box(rx + (room_w + win_w)/2, -half_d, z_wall, (room_w - win_w)/2, ext_wall_th, floor_h)
            builder.add_box(rx + (room_w - win_w)/2, -half_d, z_wall, win_w, ext_wall_th, win_sill)
            builder.add_box(rx + (room_w - win_w)/2, -half_d, z_wall + win_sill + win_h, win_w, ext_wall_th, floor_h - (win_sill + win_h))

            # Nord-fløy: Korridorvegg med dør + Fasadevegg med vindu
            builder.add_box(rx, corridor_d/2, z_wall, (room_w - door_w)/2, wall_th, floor_h)
            builder.add_box(rx + (room_w + door_w)/2, corridor_d/2, z_wall, (room_w - door_w)/2, wall_th, floor_h)
            builder.add_box(rx + (room_w - door_w)/2, corridor_d/2, z_wall + door_h, door_w, wall_th, floor_h - door_h)

            builder.add_box(rx, half_d - ext_wall_th, z_wall, (room_w - win_w)/2, ext_wall_th, floor_h)
            builder.add_box(rx + (room_w + win_w)/2, half_d - ext_wall_th, z_wall, (room_w - win_w)/2, ext_wall_th, floor_h)
            builder.add_box(rx + (room_w - win_w)/2, half_d - ext_wall_th, z_wall, win_w, ext_wall_th, win_sill)
            builder.add_box(rx + (room_w - win_w)/2, half_d - ext_wall_th, z_wall + win_sill + win_h, win_w, ext_wall_th, floor_h - (win_sill + win_h))

    # Tak og kreneleringer
    top_z = 2.0 + num_floors * (floor_h + slab_th)
    builder.set_context("Tak_Krenelering", "SteinMur")
    builder.add_box(-half_w, -half_d, top_z, total_w, total_d, slab_th * 2)

    for step_x in range(int(-half_w), int(half_w), 3):
        builder.add_box(step_x, -half_d, top_z + slab_th * 2, 1.8, 0.8, 1.8)
        builder.add_box(step_x, half_d - 0.8, top_z + slab_th * 2, 1.8, 0.8, 1.8)

    # 4 Hjørnetårn
    corners = [(-half_w, -half_d), (half_w, -half_d), (half_w, half_d), (-half_w, half_d)]
    for idx_t, (tx, ty) in enumerate(corners, 1):
        builder.set_context(f"Hjornetarn_{idx_t}", "SteinMur")
        builder.add_cylinder(tx, ty, 0, radius=7.0, height=top_z + 8.0, segments=24, cone_height=14.0)

    return builder

if __name__ == "__main__":
    castle = build_10_storey_castle()
    castle.export("slott_10etasjer.obj")
