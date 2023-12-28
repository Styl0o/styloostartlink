bl_info = {
    "name": "Styloolinkstart",
    "blender": (4, 0, 0),
    "category": "Object",
}

import bpy
import os

class OBJECT_PT_linkmat(bpy.types.Panel):
    bl_label = "StylooLlinkmat"
    bl_idname = "PT_linkmat"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        
        
        layout.prop(context.scene, "main_folder", text="Dossier principal")
        
     
        # Ajouter un bouton pour lancer la fonction
        layout.operator("object.linkmat", text="linkmat")

class OBJECT_OT_linkmat(bpy.types.Operator):
    bl_idname = "object.linkmat"
    bl_label = "linkmat"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        import bpy
        import os

        # Set the main folder path
        main_folder = context.scene.main_folder
        main_folder = bpy.path.abspath(main_folder)


        print(f"Exécution de l'opérateur avec le dossier principal : {main_folder}")

        # Check if a main folder is provided
        if main_folder:
            # Iterate through all objects in the scene
            selected_objects = bpy.context.selected_objects
            for obj in selected_objects:
                # Check if the object is a mesh
                if obj.type == 'MESH':
                    # Get the object name
                    object_name = obj.name

                    # Construct the path to the object-specific texture folder
                    object_texture_folder = os.path.join(main_folder, object_name)

                    # Check if the texture folder exists
                    if os.path.exists(object_texture_folder):
                        # Create a new material or use an existing one
                        obj.data.materials.clear()
                        material_name = f"{object_name}_Material"
                        material = bpy.data.materials.get(material_name)
                        
                        if len(obj.data.materials) == 0: obj.data.materials.append(material)
                        
                        if material is None:
                            obj.data.materials.clear()
                            material = bpy.data.materials.new(name=material_name)
                            obj.data.materials.append(material)
                
                
                    

                            #print(f"Material created for {object_name}")

                        # Ensure "Use Nodes" is set to true
                        material.use_nodes = True
                        tree = material.node_tree

                        # Clear existing nodes
                        for node in tree.nodes:
                            tree.nodes.remove(node)

                        # Create shader nodes
                        principled_node = tree.nodes.new(type='ShaderNodeBsdfPrincipled')
                        output_node = tree.nodes.new(type='ShaderNodeOutputMaterial')

                        # Iterate through all files in the folder
                        for filename in os.listdir(object_texture_folder):
                            # Check if the file is a PNG image
                            if filename.lower().endswith('.png'):
                                # Construct the full path to the texture
                                texture_path = os.path.join(object_texture_folder, filename)

                                # Load the texture
                                bpy.data.images.load(texture_path)

                                # Create a texture node
                                texture_node = tree.nodes.new(type='ShaderNodeTexImage')
                                texture_node.image = bpy.data.images[filename]

                                # Check for keywords in the filename and connect to Principled BSDF accordingly
                                if 'color' in filename.lower():
                                    tree.links.new(texture_node.outputs["Color"], principled_node.inputs["Base Color"])
                                    texture_node.location.x =-500
                                    texture_node.location.y = 600
                                elif 'metallic' in filename.lower():
                                    tree.links.new(texture_node.outputs["Color"], principled_node.inputs["Metallic"])
                                    # Set color space to Non-Color for metallic texture                      
                                    texture_node.image.colorspace_settings.name = 'Non-Color'
                                    texture_node.location.x =-500
                                    texture_node.location.y = 300
                            
                                elif 'roughness' in filename.lower():
                                    tree.links.new(texture_node.outputs["Color"], principled_node.inputs["Roughness"])
                                    # Set color space to Non-Color for roughness texture
                                    texture_node.image.colorspace_settings.name = 'Non-Color'
                                    texture_node.location.x =-500
                                    texture_node.location.y = 0
                                elif 'normal' in filename.lower():
                                    normal_map_node = tree.nodes.new(type='ShaderNodeNormalMap')
                                    tree.links.new(texture_node.outputs["Color"], normal_map_node.inputs["Color"])
                                    tree.links.new(normal_map_node.outputs["Normal"], principled_node.inputs["Normal"])
                                    # Set color space to Non-Color for normal map texture
                                    texture_node.image.colorspace_settings.name = 'Non-Color'
                                    texture_node.location.x =-500
                                    texture_node.location.y = -300
                                    normal_map_node.location.x =-200
                                    normal_map_node.location.y = -300

                                elif 'alpha' in filename.lower():
                                    tree.links.new(texture_node.outputs["Alpha"], principled_node.inputs["Alpha"])
                                    # Set color space to Non-Color for alpha texture
                                    texture_node.image.colorspace_settings.name = 'Non-Color'
                                    texture_node.location.x =-500
                                    texture_node.location.y = -600
                
                

                        # Link principled shader to the output
                        tree.links.new(principled_node.outputs["BSDF"], output_node.inputs["Surface"])
                        principled_node.location.x = 0
                        principled_node.location.y = 0
                        output_node.location.x = 500
                        output_node.location.y = 0

            
                        if obj.children and len(obj.data.materials) > 0 :
                            parent_material = obj.data.materials[0]  # Assuming the object has only one material
                            for child in obj.children:
                                child.data.materials.clear()
                                child.data.materials.append(parent_material)
                
                        print(f"Material setup completed for {object_name}")
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_linkmat.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_PT_linkmat)
    bpy.utils.register_class(OBJECT_OT_linkmat)
    #bpy.types.TOPBAR_MT_editor_menus.append(menu_func)  # Change this line
    bpy.types.Scene.main_folder = bpy.props.StringProperty(name="Dossier principal", default="", subtype='DIR_PATH')


def unregister():
    bpy.utils.unregister_class(OBJECT_PT_linkmat)
    bpy.utils.unregister_class(OBJECT_OT_linkmat)
    bpy.types.TOPBAR_MT_editor_menus.remove(menu_func)  # Change this line
    del bpy.types.Scene.main_folder

if __name__ == "__main__":
    register()
