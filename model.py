import open3d as o3d
import numpy as np
import sys
from PIL import Image

def read_obj_file(file_path):
    # Read vertices, faces, and texture coordinates from an OBJ file
    vertices = []
    faces = []
    uvs = []
    
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('v '):
                vertices.append(list(map(float, line.strip().split()[1:])))
            elif line.startswith('vt '):
                uvs.append(list(map(float, line.strip().split()[1:])))
            elif line.startswith('f '):
                face = [int(idx.split('/')[0]) - 1 for idx in line.strip().split()[1:]]
                faces.append(face)
    
    return np.array(vertices), np.array(faces), np.array(uvs)

def convert_quads_to_triangles(faces):
    # Convert quads to triangles
    triangles = []
    for face in faces:
        if len(face) == 3:
            triangles.append(face)  # Already a triangle
        elif len(face) == 4:
            triangles.append([face[0], face[1], face[2]])
            triangles.append([face[0], face[2], face[3]])
        else:
            raise ValueError(f"Unsupported face with {len(face)} vertices.")
    
    return np.array(triangles)

def create_mesh(vertices, faces, uvs):
    # Create an Open3D TriangleMesh from vertices, faces, and texture coordinates
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    
    # Convert faces to triangles
    triangles = convert_quads_to_triangles(faces)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    
    if uvs.size == 0:
        print("No UVs found. Skipping UV assignment.")
    
    return mesh

def simplify_mesh(mesh, decimation_factor):
    # Simplify the 3D mesh using Quadric Edge Collapse Decimation
    num_triangles = len(mesh.triangles)
    target_num_triangles = int(num_triangles * decimation_factor)
    
    if target_num_triangles < 1:
        raise ValueError("Decimation factor too low; target number of triangles must be at least 1.")
    
    mesh_simplified = mesh.simplify_quadric_decimation(target_number_of_triangles=target_num_triangles)
    
    return mesh_simplified

def compress_image(texture_path, output_texture_path, quality=40, max_size=(1024, 1024)):
    """
    Compress the texture image by reducing its quality and resizing.
    
    Parameters:
    texture_path: str : Path to the original texture file.
    output_texture_path: str : Path to save the compressed texture file.
    quality: int : Compression quality (1-100, lower reduces file size but also image quality).
    max_size: tuple : Maximum dimensions (width, height) to resize the image.
    
    Returns:
    None
    """
    with Image.open(texture_path) as img:
        # Resize image to a maximum size, keeping aspect ratio
        img.thumbnail(max_size)
        
        # Save with compression
        img.save(output_texture_path, optimize=True, quality=quality)
        print(f"Compressed texture saved as '{output_texture_path}' with quality={quality}.")

def save_mesh(mesh, output_path, texture_path=None):
    # Save the mesh and optionally handle the texture file
    o3d.io.write_triangle_mesh(output_path, mesh)
    
    if texture_path:
        print(f"Mesh saved as '{output_path}' with original texture.")

def process_3d_model(input_path, texture_path=None, output_path=None, decimation_factor=0.5, compress_image_path=None, quality=40, max_size=(1024, 1024)):
    """
    Process the 3D model by reading, simplifying, and saving. Also, compress the texture image if provided.
    
    Parameters:
    input_path: str : Path to the input OBJ file.
    texture_path: str : Path to the texture file (optional).
    output_path: str : Path to save the simplified OBJ file (optional).
    decimation_factor: float : Factor to simplify the mesh.
    compress_image_path: str : Path to save the compressed texture file (optional).
    quality: int : Compression quality for texture (1-100).
    max_size: tuple : Maximum dimensions (width, height) to resize the texture image.
    
    Returns:
    None
    """
    # Read OBJ file
    vertices, faces, uvs = read_obj_file(input_path)
    
    # Create mesh
    mesh = create_mesh(vertices, faces, uvs)
    
    # Simplify mesh
    simplified_mesh = simplify_mesh(mesh, decimation_factor)
    
    # Save simplified mesh
    if output_path:
        save_mesh(simplified_mesh, output_path, texture_path)
    
    # Compress and save texture image if provided
    if texture_path and compress_image_path:
        compress_image(texture_path, compress_image_path, quality=quality, max_size=max_size)
        print(f"Compressed texture saved as '{compress_image_path}'.")

if __name__ == "__main__":
    try:
        input_obj_path = sys.argv[1]  # Example: "input.obj"
        texture_path = sys.argv[2] if len(sys.argv) > 2 else None  # Example: "texture.png"
        output_path = sys.argv[3] if len(sys.argv) > 3 else None  # Example: "output.obj"
        
        # Path for the compressed texture image (optional)
        compress_image_path = sys.argv[4] if len(sys.argv) > 4 else None
        
        process_3d_model(input_obj_path, texture_path, output_path, compress_image_path=compress_image_path)
    except Exception as e:
        print(f"An error occurred: {e}")

