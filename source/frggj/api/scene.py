# scene
from frggj.api.entity import GEntityType
import numpy as np
from frggj.api.utils import invert_matrix
from numba import njit, jit


class GScene(object):
    def __init__(self):
        self._content = {
            "enemies": {},
            "sceneries": {},
            "items": {},
            "platforms": {}
        }
    
    def update(self, elapsed_time):
        for entity_type in self._content.keys():
            for entity_name in self._content[entity_type]:
                self._content[entity_type][entity_name].update(elapsed_time)

    def add_entity(self, entity) -> None:
        if entity.get_type() == GEntityType.kEnemy:
            self._content["enemies"][entity.get_name()] = entity
        elif entity.get_type() == GEntityType.kScenery:
            self._content["sceneries"][entity.get_name()] = entity
        elif entity.get_type() == GEntityType.kItem:
            self._content["items"][entity.get_name()] = entity
        elif entity.get_type() == GEntityType.kPlatform:
            self._content["platforms"][entity.get_name()] = entity
    
    def get_entity(self, entity_type, entity_name):
        return self._content[entity_type][entity_name]
    
    def get_enemies(self):
        return list(self._content["enemies"].values())
    
    def get_sceneries(self):
        return self._content["sceneries"].values()
    
    def get_items(self):
        return self._content["items"].values()
    
    def get_platforms(self):
        return self._content["platforms"].values()

    def render(self, canvas, player, camera, time):
        player_transform = player.get_transform()
        camera_matrix = invert_matrix(camera.get_matrix())

        # set the player on the ground
        player_translation = player_transform.get_translation()
        # set_on_ground(player_translation, self._assets[1].get_mesh().get_points(), self._assets[1].get_mesh().get_triangles())
        # triangle_indices = np.asarray(range(len(self._assets[1].get_mesh().get_triangles())))
        player_transform.set_translation(player_translation)

        rendereables = [player] + self.get_enemies()

        for entity in rendereables:
            asset = entity.get_asset()
            asset_skeleton = asset.get_skeleton()
            if asset_skeleton:
                asset_bindpose = asset_skeleton.get_bindpose()
                asset_influences = asset_skeleton.get_influences()
            else:
                asset_bindpose = None
                asset_influences = None
            asset_animation = asset.get_animation(entity.get_active_animation())
            if asset_animation:
                frame = int(0.024 * time)%asset_animation.get_length()
                animation_frame = asset_animation.get_frame(frame)
            else:
                animation_frame = None
            project_points(asset.get_mesh().get_points(), entity.get_transform().get_matrix(), asset_bindpose, asset_influences, animation_frame, camera_matrix, canvas.size[0], canvas.size[1])
            draw_model(canvas.get_pixels(), asset.get_mesh().get_points(), asset.get_mesh().get_triangles(), asset.get_mesh().get_uvs(), asset.get_texture(), camera_matrix, canvas._z, canvas.size[0], canvas.size[1])


@njit()
def distance_cull(triangle_indices, points, triangles, camera, max_distance):
    square_max_distance = max_distance * max_distance
    counter = 0
    for triangle_index in range(len(triangles)):
        inv_index = len(triangles) - triangle_index - 1
        triangle = triangles[inv_index]
        p0 = np.asarray([points[triangle[0]][0], 0.0, points[triangle[0]][2]])
        p1 = np.asarray([points[triangle[1]][0], 0.0, points[triangle[1]][2]])
        p2 = np.asarray([points[triangle[2]][0], 0.0, points[triangle[2]][2]])
        camera_2d_pos = np.asarray([camera[0][3], 0.0, camera[2][3]])
        delta0 = p0 - camera_2d_pos
        delta1 = p1 - camera_2d_pos
        delta2 = p2 - camera_2d_pos
        dist0 = dot_3d(delta0, delta0)
        dist1 = dot_3d(delta1, delta1)
        dist2 = dot_3d(delta2, delta2)
        if min(dist0, dist1, dist2) < square_max_distance:
            triangle_indices.pop(inv_index)
    print(len(triangle_indices))


@njit()
def set_on_ground(point, ground_points, ground_triangles):
    height = 0.0
    flat_point = np.asarray([point[0], 0.0, point[2]])
    for triangle in ground_triangles:
        p0 = ground_points[triangle[0]]
        p1 = ground_points[triangle[1]]
        p2 = ground_points[triangle[2]]

        flat_point0 = np.asarray([p0[0], 0.0, p0[2]])
        flat_point1 = np.asarray([p1[0], 0.0, p1[2]])
        flat_point2 = np.asarray([p2[0], 0.0, p2[2]])

        den = (flat_point1[2] - flat_point2[2])*(flat_point0[0] - flat_point2[0]) + (flat_point2[0] - flat_point1[0])*(flat_point0[2] - flat_point2[2])

        u = ((flat_point1[2] - flat_point2[2])*(flat_point[0] - flat_point2[0]) + (flat_point2[0] - flat_point1[0])*(flat_point[2] - flat_point2[2])) / den
        v = ((flat_point2[2] - flat_point0[2])*(flat_point[0] - flat_point2[0]) + (flat_point0[0] - flat_point2[0])*(flat_point[2] - flat_point2[2])) / den
        w = 1.0 - u - v

        eps = 0.00001
        if (u >= -eps) and (v >= -eps) and (w >= -eps):
            proj_point = u*p0[:3] + v*p1[:3] + w*p2[:3]
            height = proj_point[1]
            break
    point[1] = height


@njit()
def project_points(points, transform, bindpose, influences, pose, camera, width, height):
    FOV_V = np.pi/4 # 45 degrees vertical fov
    FOV_H = FOV_V*width/height

    hor_fov_adjust = 0.5*width/ np.tan(FOV_H * 0.5) 
    ver_fov_adjust = 0.5*height/ np.tan(FOV_V * 0.5)
    
    point_index = 0
    for point in points:
        # animate point
        transformed = point[:3]
        if not bindpose == None:
            transformed = mult_3d(bindpose[influences[point_index]], transformed)
            transformed = mult_3d(pose[influences[point_index]], transformed)

        # transform point
        transformed = mult_3d(transform, transformed)

        # translate to have camera as origin
        transformed = mult_3d(camera, transformed)

        transformed[2] = max(transformed[2], 0.001)
        
        if transformed[2] <  0.001 and transformed[2] >  - 0.001: # jump over 0 to avoid zero division ¯\_(ツ)_/¯
            transformed[2] = - 0.001

        point[3] = int(-hor_fov_adjust*transformed[0]/transformed[2] + 0.5 * width)
        point[4] = int(-ver_fov_adjust*transformed[1]/transformed[2] + 0.5 * height)
        point[5] = transformed[2] # np.sqrt(translate[0]*translate[0] + translate[1]*translate[1] + translate[2]*translate[2])
        point_index += 1


@njit()
def dot_3d(arr1, arr2):
    return arr1[0]*arr2[0] + arr1[1]*arr2[1] + arr1[2]*arr2[2]


@njit()
def mult_3d(matrix, vector):
    return np.asarray([
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1] + matrix[0][2] * vector[2] + matrix[0][3],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1] + matrix[1][2] * vector[2] + matrix[1][3],
        matrix[2][0] * vector[0] + matrix[2][1] * vector[1] + matrix[2][2] * vector[2] + matrix[2][3]])


@njit()
def draw_model(frame, points, triangles, texture_uv, texture, camera, z_buffer, width, height):
    text_size = [len(texture)-1, len(texture[0])-1]
    color_scale = 230/np.max(np.abs(points[:,:3]))
    for index in range(len(triangles)):
        
        triangle = triangles[index]

        # Use Cross-Product to get surface normal
        vet1 = points[triangle[1]][:3]  - points[triangle[0]][:3]
        vet2 = points[triangle[2]][:3] - points[triangle[0]][:3]

        # backface culling with dot product between normal and camera ray
        normal = np.cross(vet1, vet2)
        normal = normal/np.sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2])
        CameraRay = points[triangle[0]][:3] - camera[3][:3]
        CameraRay = CameraRay/np.sqrt(CameraRay[0]*CameraRay[0] + CameraRay[1]*CameraRay[1] + CameraRay[2]*CameraRay[2])

        # get projected 2d points for crude filtering of offscreen triangles
        xxs = [points[triangle[0]][3],  points[triangle[1]][3],  points[triangle[2]][3]]
        yys = [points[triangle[0]][4],  points[triangle[1]][4],  points[triangle[2]][4]]
        z_min = min([points[triangle[0]][5],  points[triangle[1]][5],  points[triangle[2]][5]])
        z_max = max([points[triangle[0]][5],  points[triangle[1]][5],  points[triangle[2]][5]])
        if z_min <= 0.001 and z_max <= 0.001:
            continue
        
        # check valid values
        if filter_triangles(z_min, normal, CameraRay, xxs, yys, width, height):

            # shade = 0.5*dot_3d(light_dir, normal) + 0.5 #  directional lighting
            shade = 1.0

            proj_points = points[triangle][:,3:] #

            sorted_y = proj_points[:,1].argsort()

            start = proj_points[sorted_y[0]]
            middle = proj_points[sorted_y[1]]
            stop = proj_points[sorted_y[2]]

            x_slopes = get_slopes(start[0], middle[0], stop[0], start[1], middle[1], stop[1])

            # invert z for interpolation
            start[2], middle[2], stop[2] = 1/start[2], 1/middle[2], 1/stop[2]
            z_slopes = get_slopes(start[2], middle[2], stop[2], start[1], middle[1], stop[1])

            # uv coordinates multiplied by inverted z to account for perspective
            textured = True
            if not textured:
                color = shade*np.abs(points[triangles[index][0]][:3])*color_scale + 25
                draw_flat_triangle(frame, z_buffer, color, start, middle, stop, x_slopes, z_slopes, width, height)
            else:
                uv_points = texture_uv[index]
                uv_start = uv_points[sorted_y[0]]*start[2]
                uv_middle = uv_points[sorted_y[1]]*middle[2]
                uv_stop = uv_points[sorted_y[2]]*stop[2]
                u_slopes = get_slopes(uv_start[0], uv_middle[0], uv_stop[0], start[1], middle[1], stop[1])
                v_slopes = get_slopes(uv_start[1], uv_middle[1], uv_stop[1], start[1], middle[1], stop[1])
                draw_text_triangle(frame, z_buffer, texture, text_size, shade, start, middle, stop, x_slopes,
                       z_slopes, uv_start, uv_middle, u_slopes, v_slopes, width, height)


@njit()
def draw_text_triangle(frame, z_buffer, texture, text_size, shade, start, middle, stop, x_slopes,
                       z_slopes, uv_start, uv_middle, u_slopes, v_slopes, width, height):
    for y in range(max(0, int(start[1])), min(height, int(stop[1]+1))):
        delta_y = y - start[1]
        x1 = start[0] + int(delta_y*x_slopes[0])
        z1 = start[2] + delta_y*z_slopes[0]
        u1 = uv_start[0] + delta_y*u_slopes[0]
        v1 = uv_start[1] + delta_y*v_slopes[0]

        if y < middle[1]:
            x2 = start[0] + int(delta_y*x_slopes[1])
            z2 = start[2] + delta_y*z_slopes[1]
            u2 = uv_start[0] + delta_y*u_slopes[1]
            v2 = uv_start[1] + delta_y*v_slopes[1]

        else:
            delta_y = y - middle[1]
            x2 = middle[0] + int(delta_y*x_slopes[2])
            z2 = middle[2] + delta_y*z_slopes[2]
            u2 = uv_middle[0] + delta_y*u_slopes[2]
            v2 = uv_middle[1] + delta_y*v_slopes[2]
        
        if x1 > x2: # lower x should be on the left
            x1, x2 = x2, x1
            z1, z2 = z2, z1
            u1, u2 = u2, u1
            v1, v2 = v2, v1

        xx1, xx2 = max(0, min(width, int(x1))), max(0, min(width, int(x2+1)))
        if xx1 != xx2:
            z_slope = (z2 - z1)/(x2 - x1 + 1e-32)
            u_slope = (u2 - u1)/(x2 - x1 + 1e-32)
            v_slope = (v2 - v1)/(x2 - x1 + 1e-32)

            for x in range(xx1, xx2):
                delta_x = x - x1
                z = 1/(z1 + delta_x*z_slope + 1e-32) # retrive z
                if z < z_buffer[x][y]: # check z buffer
                    u = (u1 + delta_x*u_slope)*z # multiply by z to go back to uv space
                    v = (v1 + delta_x*v_slope)*z # multiply by z to go back to uv space
                    if min(u, v) >= 0 and max(u, v) <= 1: # don't render out of bounds
                        z_buffer[x][y] = z
                        fog = 1.0 - min(z, 500.0) / 500.0
                        frame[x, y] = shade*fog*texture[int(u*text_size[0])][int(v*text_size[1])]


@njit()
def draw_flat_triangle(frame, z_buffer, color, start, middle, stop, x_slopes, z_slopes, width, height):

    for y in range(max(0, int(start[1])), min(height, int(stop[1]+1))):
        delta_y = y - start[1]
        x1 = start[0] + int(delta_y*x_slopes[0])
        z1 = start[2] + delta_y*z_slopes[0]

        if y < middle[1]:
            x2 = start[0] + int(delta_y*x_slopes[1])
            z2 = start[2] + delta_y*z_slopes[1]

        else:
            delta_y = y - middle[1]
            x2 = middle[0] + int(delta_y*x_slopes[2])
            z2 = middle[2] + delta_y*z_slopes[2]
        
        if x1 > x2: # lower x should be on the left
            x1, x2 = x2, x1
            z1, z2 = z2, z1

        xx1, xx2 = max(0, min(width, int(x1))), max(0, min(width, int(x2+1)))
        if xx1 != xx2:
            z_slope = (z2 - z1)/(x2 - x1 + 1e-32)
            if min(z_buffer[xx1:xx2, y]) == 1e32: # check z buffer, fresh pixels
                z_buffer[xx1:xx2, y] = 1/((np.arange(xx1, xx2)-x1)*z_slope + z1)
                frame[xx1:xx2, y] = color

            else:
                for x in range(xx1, xx2):
                    z = 1/(z1 + (x - x1)*z_slope + 1e-32) # retrive z
                    if z < z_buffer[x][y]: # check z buffer
                        z_buffer[x][y] = z
                        frame[x, y] = color


@njit()
def get_slopes(num_start, num_middle, num_stop, den_start, den_middle, den_stop):
    slope_1 = (num_stop - num_start)/(den_stop - den_start + 1e-32) # + 1e-32 avoid zero division ¯\_(ツ)_/¯
    slope_2 = (num_middle - num_start)/(den_middle - den_start + 1e-32)
    slope_3 = (num_stop - num_middle)/(den_stop - den_middle + 1e-32)
    return np.asarray([slope_1, slope_2, slope_3])


@njit()
def filter_triangles(z_min, normal, CameraRay, xxs, yys, width, height): #TODO replace filtering with proper clipping
    if z_min > 0.0 and max(xxs) >= 0.0 and min(xxs) < width and max(yys) >= 0.0 and min(yys) < height:
        return True
    else:
        return False

