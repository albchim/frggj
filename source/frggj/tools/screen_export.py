import maya.cmds as cmds
import maya.OpenMaya as om
import os
import shutil
import json


def get_triangle_colors(mesh_name):
    shapes = cmds.listRelatives(mesh_name, shapes=True, fullPath=True)
    shape = shapes[0]
    
    num_faces = cmds.polyEvaluate(shape, face=True)
    colors = [(0.5, 0.5, 0.5)] * num_faces
    face_to_shader = [None] * num_faces
    
    sgs = cmds.listConnections(shape, type="shadingEngine")
    sgs = list(dict.fromkeys(sgs))
    
    for sg in sgs:
        shaders = cmds.listConnections(f"{sg}.surfaceShader", s=True, d=False) or []
        shader = shaders[0] if shaders else None
        members = cmds.sets(sg, q=True) or []
        if members:
            rgb = [
                int(cmds.getAttr("{0}.colorR".format(shader)) * 255),
                int(cmds.getAttr("{0}.colorG".format(shader)) * 255),
                int(cmds.getAttr("{0}.colorB".format(shader)) * 255)]
    
            members = cmds.sets(sg, q=True) or []
            # members may include: shape, shape.f[1], shape.f[2:10], and also other objects
            for m in members:
                if not m.startswith(mesh_name):
                    continue
    
                # Whole-object assignment: "shape"
                if m == shape:
                    for fi in range(num_faces):
                        colors[fi] = rgb
                        face_to_shader[fi] = shader
                    continue
    
                # Face ranges: "shape.f[3]" or "shape.f[2:9]"
                if ".f[" in m:
                    inside = m.split(".f[", 1)[1].rstrip("]")
                    if ":" in inside:
                        a, b = inside.split(":", 1)
                        start = int(a)
                        end = int(b)
                        for fi in range(start, end + 1):
                            if 0 <= fi < num_faces:
                                colors[fi] = rgb
                                face_to_shader[fi] = shader
                    else:
                        fi = int(inside)
                        if 0 <= fi < num_faces:
                            colors[fi] = rgb
                            face_to_shader[fi] = shader
    return colors


def export_mesh(mesh_name, asset_path):
    selection = om.MSelectionList()
    selection.add(mesh_name)
    mesh_dag = om.MDagPath()
    selection.getDagPath(0, mesh_dag)

    mesh_fn = om.MFnMesh(mesh_dag)
    mesh_points = om.MPointArray()
    mesh_fn.getPoints(mesh_points)
    num_points = mesh_fn.numVertices()
    points = []
    for point_index in range(num_points):
        point = mesh_points[point_index]
        points.append([
            point.x,
            point.y,
            point.z])

    triangles = []
    triangle_counts = om.MIntArray()
    triangle_vertices = om.MIntArray()
    mesh_fn.getTriangles(triangle_counts, triangle_vertices)
    num_triangles = triangle_counts.length()
    for triangle_index in range(num_triangles):
        triangles.append([
            triangle_vertices[triangle_index * 3],
            triangle_vertices[triangle_index * 3 + 1],
            triangle_vertices[triangle_index * 3 + 2]])
            
    uvs = []
    u_array = om.MFloatArray()
    v_array = om.MFloatArray()
    mesh_fn.getUVs(u_array, v_array)
    util = om.MScriptUtil()
    util.createFromInt(-1)
    indexPtr = util.asIntPtr()
    max_index = -1
    for triangle_index in range(num_triangles):
        triangle_uvs = []
        mesh_fn.getPolygonUVid(triangle_index, 0, indexPtr)
        index = util.getInt(indexPtr)
        triangle_uvs += [u_array[index]%1.0, v_array[index]%1.0]
        mesh_fn.getPolygonUVid(triangle_index, 1, indexPtr)
        index = util.getInt(indexPtr)
        triangle_uvs += [u_array[index]%1.0, v_array[index]%1.0]
        mesh_fn.getPolygonUVid(triangle_index, 2, indexPtr)
        index = util.getInt(indexPtr)
        triangle_uvs += [u_array[index]%1.0, v_array[index]%1.0]
        uvs.append(triangle_uvs)
    data = {
        "name": mesh_name,
        "points": points,
        "triangles": triangles,
        "uvs": uvs}

    export_filepath = os.path.join(asset_path, "geo.json")
    with open(export_filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return "geo.json"


def export_texture(mesh_name, asset_path):
    shapes = cmds.listRelatives(mesh_name, shapes=True, fullPath=True)
    shape = shapes[0]
    sgs = cmds.listConnections(shape, type="shadingEngine")
    if sgs:
        sgs = list(set(sgs))
    if len(sgs) == 1:
        shaders = cmds.listConnections("{0}.surfaceShader".format(sgs[0]), s=True, d=False) or []
        shader = shaders[0] if shaders else None
        if shader:
            color_file_node = cmds.listConnections("{0}.outColor".format(shader))[1]
            color_filepath = cmds.getAttr("{0}.fileTextureName".format(color_file_node))
            export_filepath = os.path.join(asset_path, "color.png")
            shutil.copyfile(color_filepath, export_filepath)
    return "color.png"


def export_skeleton(mesh_name, asset_filepath):
    cmds.currentTime(1)
    influences = []
    bind_matrices = []
    shapes = cmds.listRelatives(mesh_name, shapes=True, fullPath=True)
    shape = shapes[0]
    history = cmds.listHistory(shape, pruneDagObjects=True) or []
    skinclusters = []
    for node in history:
        if cmds.nodeType(node) == "skinCluster":
            skinclusters.append(cmds.ls(node, long=True)[0])
    skinclusters = list(set(skinclusters))
    if len(skinclusters) == 1:
        joints = cmds.skinCluster(skinclusters[0], query=True, influence=True) or []
        for joint_name in joints:
            joint_matrix = cmds.xform(joint_name, query=True, matrix=True, worldSpace=True)
            bind_matrices.append([
                [joint_matrix[0], joint_matrix[4], joint_matrix[8], joint_matrix[12]],
                [joint_matrix[1], joint_matrix[5], joint_matrix[9], joint_matrix[13]],
                [joint_matrix[2], joint_matrix[6], joint_matrix[10], joint_matrix[14]],
                [joint_matrix[3], joint_matrix[7], joint_matrix[11], joint_matrix[15]]
            ])
        # for joint_index in joints:
        for vertex_index in range(cmds.polyEvaluate(mesh_name, vertex=True)):
            vertex_name = "{0}.vtx[{1}]".format(mesh_name, vertex_index)
            weights = cmds.skinPercent(skinclusters[0], vertex_name, q=True, value=True) or []
            influences.append(weights.index(1.0))
    data = {
        "binding_matrices": bind_matrices,
        "binding_indices": influences}
    
    export_filepath = os.path.join(asset_filepath, "skeleton.json")
    with open(export_filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return "skeleton.json"


def export_manifest(mesh_filepath, texture_filepath, asset_path):
    manifest = {
        "mesh": mesh_filepath,
        "texture": texture_filepath,
        "skeleton": None,
        "animation": None,
        "animation_map": None}
    export_filepath = os.path.join(asset_path, "asset.json")
    with open(export_filepath, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=4)
    return export_filepath


def export_content(mesh_name, export_folder, skeleton=False, anim=False):
    asset_path = export_folder + mesh_name
    if not os.path.isdir(asset_path):
        os.mkdir(asset_path)
    mesh_filepath = export_mesh(mesh_name, asset_path)
    texture_filepath = export_texture(mesh_name, asset_path)
    x = export_manifest(mesh_filepath, texture_filepath, asset_path)
    print("Asset {0} exported to file {1}".format(mesh_name, x))


assets_export_folder = "C:/dev/gitrepos/frggj/assets/"
scene_export_folder = "C:/dev/gitrepos/frggj/levels/level1/screen1"

set_group = cmds.ls("|set")
platforms_group = cmds.ls("|platforms")
background_group = cmds.ls("|background")

exported_assets = []
scene_layout = {"set": {}, "platforms": {}, "background": {}}
if set_group:
    assets = cmds.listRelatives(set_group)
    for asset_transform in assets:
        shapes = cmds.listRelatives(asset_transform, shapes=True, fullPath=True, noIntermediate=True) or []
        if len(shapes) == 1 and shapes[0][-5:]=="Shape":
            filtered_shape_name = shapes[0][:-5].rpartition("|")[2]
            if filtered_shape_name not in exported_assets:
                export_content(filtered_shape_name, assets_export_folder)
                exported_assets.append(filtered_shape_name)
            instance_translation = cmds.xform(asset_transform, query=True, translation=True, worldSpace=True)
            instance_rotation = cmds.xform(asset_transform, query=True, rotation=True, worldSpace=True)
            instance_data = {
                "asset": filtered_shape_name,
                "translate": instance_translation,
                "rotation": instance_rotation}
            scene_layout["set"][asset_transform] = instance_data
if platforms_group:
    assets = cmds.listRelatives(platforms_group)
    for asset_transform in assets:
        shapes = cmds.listRelatives(asset_transform, shapes=True, fullPath=True, noIntermediate=True) or []
        if len(shapes) == 1 and shapes[0][-5:]=="Shape":
            filtered_shape_name = shapes[0][:-5].rpartition("|")[2]
            if filtered_shape_name not in exported_assets:
                export_content(filtered_shape_name, assets_export_folder)
                exported_assets.append(filtered_shape_name)
            instance_translation = cmds.xform(asset_transform, query=True, translation=True, worldSpace=True)
            instance_rotation = cmds.xform(asset_transform, query=True, rotation=True, worldSpace=True)
            instance_data = {
                "asset": filtered_shape_name,
                "translate": instance_translation,
                "rotation": instance_rotation}
            scene_layout["platforms"][asset_transform] = instance_data
if background_group:
    assets = cmds.listRelatives(background_group)
    for asset_transform in assets:
        shapes = cmds.listRelatives(asset_transform, shapes=True, fullPath=True, noIntermediate=True) or []
        if len(shapes) == 1 and shapes[0][-5:]=="Shape":
            filtered_shape_name = shapes[0][:-5].rpartition("|")[2]
            if filtered_shape_name not in exported_assets:
                export_content(filtered_shape_name, assets_export_folder)
                exported_assets.append(filtered_shape_name)
            instance_translation = cmds.xform(asset_transform, query=True, translation=True, worldSpace=True)
            instance_rotation = cmds.xform(asset_transform, query=True, rotation=True, worldSpace=True)
            instance_data = {
                "asset": filtered_shape_name,
                "translate": instance_translation,
                "rotation": instance_rotation}
            scene_layout["background"][asset_transform] = instance_data

export_filepath = os.path.join(scene_export_folder, "description.json")
with open(export_filepath, 'w', encoding='utf-8') as f:
    json.dump(scene_layout, f, ensure_ascii=False, indent=4)