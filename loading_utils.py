from OpenGL.GL import *
from PIL import Image

# Classe que representa um material (cor + textura)
class Material:
    def __init__(self, r=0, g=0, b=0, texture_fname=''):
        self.r = r                       # componente vermelha da cor base
        self.g = g                       # componente verde da cor base
        self.b = b                       # componente azul da cor base
        self.texture_fname = texture_fname  # nome do arquivo da textura
        self.texture_id = None           # id da textura carregada na GPU

# Dicionário global que evita carregar texturas duplicadas
# Chave = nome do arquivo | Valor = id da textura na GPU
mapped_textures = {}

def load_materials_from_file(filename):
    """
    Carrega os materiais de um arquivo .mtl (material)
    Retorna um dicionário com nome do material como chave e Material como valor
    """
    filename = 'models/' + filename
    material_name = None
    materials = {}

    for line in open(filename, 'r'):
        if line.startswith('#'):
            continue
        values = line.split()
        if not values:
            continue

        if values[0] == 'newmtl':  # novo material
            material_name = values[1]
            materials[material_name] = Material()
        elif values[0] in ('map_Ka', 'map_Kd'):  # textura
            materials[material_name].texture_fname = values[1]
        elif values[0] in ('Ka', 'Kd'):  # cor base
            r, g, b = map(float, values[1:])
            materials[material_name].r = r
            materials[material_name].g = g
            materials[material_name].b = b

    return materials

def load_model_from_file(filename, filtro):
    """
    Lê um arquivo .obj com geometria 3D e filtra os vértices.
    Retorna dicionário com: vértices, coordenadas de textura, normais, faces e materiais.
    """
    filename = 'models/' + filename
    vertices = []
    texture_coords = []
    normals = []
    faces = []

    material = None
    mtl_file = None

    for line in open(filename, "r"):
        if line.startswith('#'):
            continue
        values = line.split()
        if not values:
            continue

        if values[0] == 'v':  # vértice
            vertices.append(values[1:4])
        elif values[0] == 'vt':  # textura
            texture_coords.append(values[1:3])
        elif values[0] == 'vn':  # normal
            normals.append(values[1:4])
        elif values[0] in ('usemtl', 'usemat'):  # uso de material
            material = values[1]
        elif values[0] == 'f':  # face
            face = []
            face_texture = []
            face_normal = []

            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                face_normal.append(int(w[2]) if len(w) >= 3 and w[2] else 0)
                face_texture.append(int(w[1]) if len(w) >= 2 and w[1] else 0)

            # Aplica filtro aos vértices da face
            if all(map(filtro, [[float(x) for x in vertices[i-1]] for i in face])):
                faces.append((face, face_texture, face_normal, material))
        elif values[0] == 'mtllib':  # arquivo de material
            assert mtl_file is None
            mtl_file = values[1]

    model = {
        'vertices': vertices,
        'texture': texture_coords,
        'normal': normals,
        'faces': faces,
        'materials': {}
    }

    if mtl_file is not None:
        model['materials'] = load_materials_from_file(mtl_file)

    return model

def load_texture_from_file(img_textura):
    """
    Carrega uma textura da pasta texture/ se ainda não estiver carregada.
    Retorna o ID da textura na GPU.
    """
    if img_textura not in mapped_textures:
        texture_id = len(mapped_textures)
        mapped_textures[img_textura] = texture_id
    else:
        return mapped_textures[img_textura]

    img_textura = 'texture/' + img_textura
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    img = Image.open(img_textura)
    img = img.convert('RGBA')  # Com transparência
    img_width, img_height = img.size
    image_data = img.tobytes("raw", "RGBA", 0, -1)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    return texture_id

def get_textura_cor(r, g, b):
    """
    Cria e retorna uma textura de cor sólida (1x1).
    Ideal para objetos sem textura de imagem.
    """
    nome = f'__COR_{r}_{g}_{b}'
    if nome not in mapped_textures:
        texture_id = len(mapped_textures)
        mapped_textures[nome] = texture_id
    else:
        return mapped_textures[nome]

    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    # Define a cor RGB como textura 1x1
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1, 1, 0, GL_RGB, GL_UNSIGNED_BYTE, bytes([r, g, b]))
    return texture_id

def process_nagons(arr):
    """
    Converte polígonos com N lados (N-gons) em triângulos usando o padrão GL_TRIANGLE_FAN.
    Retorna uma lista "triangulada" de índices.
    """
    if len(arr) == 3:
        return arr
    result = []
    for i in range(len(arr) - 1):
        result.append(arr[0])
        result.extend(arr[i:i+2])
    return result

def load_obj_and_texture(objFile, filtro):
    """
    Carrega um arquivo .obj e suas texturas, agrupando os dados por material.
    Retorna: lista de tuplas (vértices, coordenadas de textura, normais, material)
    """
    modelo = load_model_from_file(objFile, filtro)

    # Carrega texturas dos materiais
    for mat in modelo['materials'].values():
        if mat.texture_fname:
            mat.texture_id = load_texture_from_file(mat.texture_fname)

    # Organiza dados por nome de material/textura
    by_texture = {name: ([], [], [], mat) for name, mat in modelo['materials'].items()}

    for face in modelo['faces']:
        mat_name = face[3]
        for vertice_id in process_nagons(face[0]):
            by_texture[mat_name][0].append(modelo['vertices'][vertice_id - 1])
        for texture_id in process_nagons(face[1]):
            by_texture[mat_name][1].append(modelo['texture'][texture_id - 1])
        for normal_id in process_nagons(face[2]):
            by_texture[mat_name][2].append(modelo['normal'][normal_id - 1])

    return by_texture.values()
