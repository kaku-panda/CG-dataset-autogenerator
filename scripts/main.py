import sys
sys.path.append("/home/ymstkz/.local/lib/python3.10/site-packages/cv2/")

from email.mime import image
from operator import truediv
import os
from xml.etree.ElementTree import tostring
import bpy 
import random
import bpy_extras
from math import pi
from mathutils import Vector
import datetime
import cv2
import colorsys
import time
import mathutils

###################################
### set parameters 
###################################
target_model       = "doll"
model_number       = 1

if target_model == "doll":
    blender_file   = target_model + "_" + str(model_number)
else:
    blender_file   = target_model

num_of_photo       = 30000
dataset_offset     = 0


background_img_dir = "/media/slab/LAP_CHOL_DATA_2/contest_dataset/background/car/"
output_dir         = "/media/slab/LAP_CHOL_DATA_2/contest_dataset/ymstkz/"
dt                 = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
out_dir            = output_dir + target_model + "/" + dt + "/"
out_label_dir      = out_dir + "labels/"
out_image_dir      = out_dir + "images/"
out_debug_dir      = out_dir + "debugs/"
digit              = 10
use_gpu            = True
debug              = True
resolution_x       = 720
resolution_y       = 1280

clss = {
    'traffic_light_red'    : 0, 
    'traffic_light_yellow' : 1, 
    'traffic_light_green'  : 2,
    'doll'                 : 3,
    'arrow'                : 4,
    'barricade'            : 5,
    'bar'                  : 6,
    }

# save renderrig image
def render(i):
    bpy.ops.render.render()
    bpy.data.images['Render Result'].save_render(filepath= out_image_dir + str(i).zfill(digit) + ".jpg")
    return out_image_dir + str(i).zfill(10) + ".jpg"

def coodinates(scene, obj, i):
    bound_box = [list(), list()]
    
    for i in range(0, 8):
        temp = obj.matrix_world @ Vector(obj.bound_box[i])
        temp = bpy_extras.object_utils.world_to_camera_view(scene, bpy.data.objects["Camera"], temp)
        bound_box[0].append(temp[0])
        bound_box[1].append(temp[1])

    render_scale = scene.render.resolution_percentage / 100

    render_size = (
        int(scene.render.resolution_x * render_scale),
        int(scene.render.resolution_y * render_scale),  
    )

    right_bottom = [round(max(bound_box[0]) * render_size[0]), resolution_y -round(min(bound_box[1]) * render_size[1])]
    left_up      = [round(min(bound_box[0]) * render_size[0]), resolution_y - round(max(bound_box[1]) * render_size[1])]
    
    return [left_up, right_bottom]

def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh

    return (x,y,w,h)

def random_setting(target):

    # environment lighting 
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = random.uniform(3, 5)
    
    # lighting
    if target_model == "traffic_light_red":
        scale = random.uniform(0.3, 0.4)
        location = [random.uniform(-0.4, 1.0), random.uniform(-0.5, 0.5)]
        rotate = [random.uniform(-0.6, 0.1), 0, random.uniform(-0.3, 0.3)]
        target.scale[0]            = scale
        target.scale[1]            = scale
        target.scale[2]            = scale
        target.location[0]         = location[0]
        target.location[2]         = location[1]
        target.rotation_euler[0]   = rotate[0]
        target.rotation_euler[1]   = rotate[1]
        target.rotation_euler[2]   = rotate[2]
        bpy.data.materials[target_model].node_tree.nodes["Principled BSDF"].inputs[20].default_value = random.uniform(0.5, 10)
        hue = random.uniform(0.95,1) if random.randint(0,1) else random.uniform(0,0.01)
        rgb = colorsys.hsv_to_rgb(hue, random.uniform(0,1), 1)
        bpy.data.materials[target_model].node_tree.nodes["カラーランプ"].color_ramp.elements[1].color = (rgb[0], rgb[1], rgb[2], 1)
        
        bpy.data.materials["traffic_light_body"].node_tree.nodes["Principled BSDF.001"].inputs[7].default_value = random.uniform(0, 0.2)
        rand = random.uniform(0.1, 0.9)
        bpy.data.materials["traffic_light_body"].node_tree.nodes["RGB.002"].outputs[0].default_value = (rand, rand, rand, 1)
        rand = random.uniform(0.2, 0.9)
        bpy.data.materials["traffic_light_body"].node_tree.nodes["Principled BSDF.001"].inputs[3].default_value = (rand, rand, rand, 1)
    
    if target_model == "traffic_light_yellow":
        scale = random.uniform(0.2, 1.0)
        location = [random.uniform(-1.0, 1.0), random.uniform(-0.4, 0.4)]
        rotate = [random.uniform(-0.6, 0.1), 0, random.uniform(-0.3, 0.3)]
        target.scale[0]            = scale
        target.scale[1]            = scale
        target.scale[2]            = scale
        target.location[0]         = location[0]
        target.location[2]         = location[1]
        target.rotation_euler[0]   = rotate[0]
        target.rotation_euler[1]   = rotate[1]
        target.rotation_euler[2]   = rotate[2]
        bpy.data.materials[target_model].node_tree.nodes["Principled BSDF"].inputs[20].default_value = random.uniform(1, 12)
        hue = random.uniform(0.025,0.10)
        saturation = random.uniform(0.95, 1)
        rgb = colorsys.hsv_to_rgb(hue, saturation, 1)
        bpy.data.materials[target_model].node_tree.nodes["カラーランプ"].color_ramp.elements[0].color = (rgb[0], rgb[1], rgb[2], 1)
        rgb = colorsys.hsv_to_rgb(hue, random.uniform(saturation-0.1,saturation), 1)
        bpy.data.materials[target_model].node_tree.nodes["カラーランプ"].color_ramp.elements[1].color = (rgb[0], rgb[1], rgb[2], 1)
        bpy.data.materials["traffic_light_body"].node_tree.nodes["Principled BSDF.001"].inputs[7].default_value = random.uniform(0, 0.2)
        rand = random.uniform(0.1, 0.9)
        bpy.data.materials["traffic_light_body"].node_tree.nodes["RGB.002"].outputs[0].default_value = (rand, rand, rand, 1)
        rand = random.uniform(0.2, 0.9)
        bpy.data.materials["traffic_light_body"].node_tree.nodes["Principled BSDF.001"].inputs[3].default_value = (rand, rand, rand, 1)

   
    if target_model == "traffic_light_green":
        scale = random.uniform(0.2, 1.0)
        location = [random.uniform(-1.0, 0.4), random.uniform(-0.4, 0.4)]
        rotate = [random.uniform(-0.6, 0.1), 0, random.uniform(-0.3, 0.3)]
        target.scale[0]            = scale
        target.scale[1]            = scale
        target.scale[2]            = scale
        target.location[0]         = location[0]
        target.location[2]         = location[1]
        target.rotation_euler[0]   = rotate[0]
        target.rotation_euler[1]   = rotate[1]
        target.rotation_euler[2]   = rotate[2]
        bpy.data.materials[target_model].node_tree.nodes["Principled BSDF"].inputs[20].default_value = random.uniform(1, 20)
        hue = random.uniform(0.4,0.57)
        saturation = 1
        rgb = colorsys.hsv_to_rgb(hue, saturation, 1)
        bpy.data.materials[target_model].node_tree.nodes["カラーランプ"].color_ramp.elements[0].color = (rgb[0], rgb[1], rgb[2], 1)
        rgb = colorsys.hsv_to_rgb(hue, random.uniform(saturation-0.01,saturation), 1)
        bpy.data.materials[target_model].node_tree.nodes["カラーランプ"].color_ramp.elements[1].color = (rgb[0], rgb[1], rgb[2], 1)
        bpy.data.materials["traffic_light_body"].node_tree.nodes["Principled BSDF.001"].inputs[7].default_value = random.uniform(0, 0.2)
        rand = random.uniform(0.1, 0.9)
        bpy.data.materials["traffic_light_body"].node_tree.nodes["RGB.002"].outputs[0].default_value = (rand, rand, rand, 1)
        rand = random.uniform(0.2, 0.9)
        bpy.data.materials["traffic_light_body"].node_tree.nodes["Principled BSDF.001"].inputs[3].default_value = (rand, rand, rand, 1)

    if target_model == "doll":
        body = bpy.context.scene.objects["doll_body"]
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.mode_set(mode='POSE')
        # reset positon and scale
        body.scale          = [1, 1, 1]
        body.location       = [0, 0, 0]
        body.rotation_euler = [0, 0, 0]

        if model_number == 0:
            # move arms
            body.pose.bones["arm_r_ik"].location     = (random.uniform(-1.4, 0.01), random.uniform(-0.7, 0.7), random.uniform(-0.65, 0.02))
            body.pose.bones["arm_l_ik"].location     = (random.uniform(-1.4, 0.01), random.uniform(-0.7, 0.7), random.uniform(-0.02, 0.65))
            body.pose.bones["hand_r"].rotation_mode  = 'XYZ'
            body.pose.bones["hand_r"].rotation_euler = mathutils.Euler((random.uniform(-40, 40), random.uniform(-90, 50),0), 'XYZ')
            body.pose.bones["hand_l"].rotation_mode  = 'XYZ'
            body.pose.bones["hand_l"].rotation_euler = mathutils.Euler((random.uniform(-40, 40), random.uniform(-90, 50),0), 'XYZ')
            # move f
            body.pose.bones["toes_r_ik"].location    = (random.uniform(-0.6, 0), random.uniform(-0.75, 0.75), random.uniform(-0.07, 0.07))
            body.pose.bones["toes_l_ik"].location    = (random.uniform(-0.6, 0), random.uniform(-0.75, 0.75), random.uniform(-0.07, 0.07))
            #
            body.pose.bones["head"].rotation_mode    = 'XYZ'
            body.pose.bones["head"].rotation_euler   = mathutils.Euler((random.uniform(-10, 10), random.uniform(-180, 180), random.uniform(-10, 10)), 'XYZ')
            body.pose.bones["chest"].rotation_mode   = 'XYZ'
            body.pose.bones["chest"].rotation_euler  = mathutils.Euler((random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)), 'XYZ')
        elif model_number == 1:
            # move
            body.pose.bones["arm_r_ik"].location     = (random.uniform(-0.55, 0.55), random.uniform(-0.55, 0.55), random.uniform(-0.0025, 0.47))
            body.pose.bones["arm_l_ik"].location     = (random.uniform(-0.55, 0.55), random.uniform(-0.55, 0.55), random.uniform(-0.47, 0.0025))
            body.pose.bones["hand_r"].rotation_mode  = 'XYZ'
            body.pose.bones["hand_r"].rotation_euler = mathutils.Euler((random.uniform(-40, 40), random.uniform(-90, 50),0), 'XYZ')
            body.pose.bones["hand_l"].rotation_mode  = 'XYZ'
            body.pose.bones["hand_l"].rotation_euler = mathutils.Euler((random.uniform(-40, 40), random.uniform(-90, 50),0), 'XYZ')
            # move f
            body.pose.bones["toes_r_ik"].location    = (random.uniform(-0.6, 0), random.uniform(-0.75, 0.75), random.uniform(-0.07, 0.07))
            body.pose.bones["toes_l_ik"].location    = (random.uniform(-0.6, 0), random.uniform(-0.75, 0.75), random.uniform(-0.07, 0.07))
            #
            body.pose.bones["head"].rotation_mode    = 'XYZ'
            body.pose.bones["head"].rotation_euler   = mathutils.Euler((random.uniform(-10, 10), random.uniform(-180, 180), random.uniform(-10, 10)), 'XYZ')
            body.pose.bones["chest"].rotation_mode   = 'XYZ'
            body.pose.bones["chest"].rotation_euler  = mathutils.Euler((random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)), 'XYZ')

        # random position and scale
        scale               = random.uniform(1.2, 1.4)
        body.scale          = [scale, scale, scale]
        body.location       = [random.uniform(-0.2, 0.2), 0, random.uniform(-0.7, -0.2)]
        rand_lot            = random.randint(0,3) 
        body.rotation_euler = [0, 0, 0 if rand_lot == 0 else 1.57 if rand_lot == 1 else -1.57 if rand_lot == 2 else 3.14]


def main():
    if not os.path.exists(background_img_dir):
        print("couldn't find '" + background_img_dir + "' directiory.")
        exit()
    else:
        print("find " + background_img_dir + " !")
    
    if not os.path.exists(output_dir):
        print("couldn't find '" + output_dir + "' directiory.")
        exit()
    else:
        print("find " + output_dir + " !")


    if not os.path.exists(output_dir + target_model):
        os.mkdir(output_dir + target_model)
        
    os.mkdir(out_dir)   
    os.mkdir(out_label_dir)
    os.mkdir(out_image_dir)
    if debug:
        os.mkdir(out_debug_dir)
    
    # create project
    bpy.data.objects.remove(bpy.data.objects["Cube"])
    bpy.data.objects.remove(bpy.data.objects["Light"])
    scene = bpy.context.scene

    # add camera
    camera = bpy.data.objects["Camera"]
    camera.location = (0, -4, 0)
    camera.rotation_euler = (((pi * 90 / 180),0,0))
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    
    # add target model
    bpy.ops.wm.append(filepath="../models/" + blender_file + ".blend", directory="../models/" + blender_file + ".blend" + "/Collection/", filename=target_model)

    # check render engine
    if use_gpu:
        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'GPU'
        scene.render.film_transparent = True
        scene.cycles.samples = 128

    
    scene.use_nodes = True
    node_tree = scene.node_tree
    nodes = node_tree.nodes
    for n in nodes:
        nodes.remove(n)

    # create node tree for icluding background image to render image.
    links = node_tree.links
    back_image_node = nodes.new(type='CompositorNodeImage')
    scale_node = nodes.new(type="CompositorNodeScale")
    scale_node.space = "RENDER_SIZE"
    scale_node.frame_method = "CROP"
    alphao_node = nodes.new('CompositorNodeAlphaOver') 
    renderl_node = nodes.new('CompositorNodeRLayers')   
    comp_node = nodes.new('CompositorNodeComposite')   
    links.new(back_image_node.outputs[0], scale_node.inputs[0])  
    links.new(scale_node.outputs[0], alphao_node.inputs[1])
    links.new(renderl_node.outputs[0], alphao_node.inputs[2])
    links.new(alphao_node.outputs[0], comp_node.inputs[0])

    # scene background enviroment light
    node_tree = scene.world.node_tree
    nodes = node_tree.nodes
    links = node_tree.links

    env_node = nodes.new('ShaderNodeTexEnvironment')
    links.new(env_node.outputs["Color"], nodes[1].inputs["Color"])
    links.new(nodes[1].outputs["Background"], nodes[0].inputs["Surface"])
    
    back_image_node.image = bpy.data.images.load(background_img_dir  + str(0).zfill(digit) + ".jpg", check_existing=False)
    env_node.image = bpy.data.images.load(background_img_dir + str(0).zfill(digit) + ".jpg", check_existing=False)
    
    target = bpy.data.objects[target_model]

    # start create dataset
    start = time.time()
    i = 0
    while 1:
        
        if i >= num_of_photo:
            break
        print(f"\r [debug_log] progress {i} / {num_of_photo}")

        back_image_node.image = bpy.data.images.load(background_img_dir  + str(i + dataset_offset).zfill(digit) + ".jpg", check_existing=False)
        env_node.image = bpy.data.images.load(background_img_dir + str(i + dataset_offset).zfill(digit) + ".jpg", check_existing=False)
        
        random_setting(target)
        img_path = render(int(i + dataset_offset))
        coods = coodinates(scene, target, int(i))
        if target_model == "doll":
            if coods[0][0] > resolution_x:
                coods[0][0] = resolution_x - 1
            if coods[0][0] < 0: 
                coods[0][0] = 0
            if coods[1][0] > resolution_x:
                coods[1][0] = resolution_x - 1
            if coods[1][0] < 0:
                coods[1][0] = 0
            if coods[0][1] > resolution_y:
                coods[0][1] = resolution_y - 1
            if coods[0][1] < 0:
                coods[0][1] = 0
            if coods[1][1] > resolution_y:
                coods[1][1] = resolution_y - 1
            if coods[1][1] < 0:
                coods[1][1] = 0
        else:    
            if coods[0][0] > resolution_x or coods[0][0] < 0: 
                continue
            if coods[1][0] > resolution_x or coods[1][0] < 0:
                continue 
            if coods[0][1] > resolution_y or coods[0][1] < 0:
                continue
            if coods[1][1] > resolution_y or coods[1][1] < 0: 
                continue

        result = convert([resolution_x, resolution_y], (coods[0][0], coods[1][0], coods[0][1], coods[1][1]))

        if debug:
            img = cv2.imread(img_path)
            img = cv2.rectangle(img, (int((result[0]-result[2]/2)*resolution_x), int((result[1]-result[3]/2)*resolution_y)), (int((result[0]+result[2]/2)*resolution_x), int((result[1]+result[3]/2)*resolution_y)), (255, 0, 0), thickness=1, lineType=cv2.LINE_4)
            img = cv2.circle(img, (int(result[0] * resolution_x), int(result[1] * resolution_y)), 10, (0, 0, 255))
            cv2.imwrite(filename= out_debug_dir + str(i + dataset_offset).zfill(digit) + ".jpg", img=img)
            cv2.imwrite(filename="out.jpg", img=img)
        
        flabel = open(out_label_dir + str(i + dataset_offset).zfill(10) + ".txt", 'w', encoding='UTF-8')
        flabel.write(f'{clss[target_model]} {result[0]} {result[1]} {result[2]} {result[3]}')
        i+=1

    end = time.time()
    flabel.close()

    print(f"[debug_log] elapsed time : {end - start} s")

if __name__  == "__main__":
    main()
