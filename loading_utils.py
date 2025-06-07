from OpenGL.GL import *
from PIL import Image

# Essa classe mantém informações sobre o material: cor base, nome do arquivo da textura, id da textura carregada
class Material:
    def __init__(self, r=0, g=0, b=0, texture_fname=''):
        self.r = r 
        self.g = g
        self.b = b
        self.texture_fname = texture_fname
        self.texture_id = None        

# Mantém um dicionário de quais arquivos de textura já foram mapeados.
# Chave: nome do arquivo. Valor: id da textura na gpu
mapped_textures = {}

def load_materials_from_file(filename):
    # Processa os materiais de um arquivo .mtl 
    # Não carrega as texturas, armazena só o nome do arquivo
    filename = 'models/' + filename
    material_name = None
    materials = {}
    
    for line in open(filename, 'r'):
        if line.startswith('#'):
            continue ## ignora comentarios
        values = line.split() # quebra a linha por espaço
        if not values:
            continue

        if values[0] == 'newmtl':  # le o nome do material
            material_name = values[1]
            materials[material_name] = Material()
        elif values[0] in ('map_Ka', 'map_Kd'):
            materials[material_name].texture_fname = values[1]
        elif values[0] in ('Ka', 'Kd'):
            r,g,b = map(float, values[1:])
            materials[material_name].r = r
            materials[material_name].g = g
            materials[material_name].b = b

    return materials

def load_model_from_file(filename, filtro):
    # Carrega a geometria de um arquivo .obj 
    # filtro é uma função que recebe uma tupla de 3 valores (x,y,z), e retorna um booleano
    # o filtro serve para aceitar vértices ou não: faces são renderizadas apenas se todos os seus
    # vértices passarem no filtro. Isso serve para cortar fora certas partes dos modelos.
    
    filename = 'models/' + filename
    vertices = []
    texture_coords = []
    normals = []
    faces = []

    material = None
    mtl_file = None

    # abre o arquivo obj para leitura
    for line in open(filename, "r"): ## para cada linha do arquivo .obj
        if line.startswith('#'):
            continue ## ignora comentarios
        values = line.split() # quebra a linha por espaço
        if not values:
            continue

        ### recuperando vertices
        if values[0] == 'v':
            vertices.append(values[1:4])

        ### recuperando coordenadas de textura
        elif values[0] == 'vt':
            texture_coords.append(values[1:3])

        ### recuperando coordenadas de normais
        elif values[0] == 'vn':
            normals.append(values[1:4])

        ### recuperando faces 
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'f':
            face = []
            face_texture = []
            face_normal = []

            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 3 and len(w[2]) > 0:
                    face_normal.append(int(w[2]))
                else:
                    face_normal.append(0)

                if len(w) >= 2 and len(w[1]) > 0:
                    face_texture.append(int(w[1]))
                else:
                    face_texture.append(0)

            if all(map(filtro, [[float(x) for x in vertices[i-1]] for i in face])):
                faces.append((face, face_texture, face_normal, material))
        elif values[0] == 'mtllib':
            assert mtl_file is None
            mtl_file = values[1]

    model = {}
    model['vertices'] = vertices
    model['texture'] = texture_coords
    model['normal'] = normals
    model['faces'] = faces
    model['materials'] = {}

    if mtl_file is not None:
        model['materials'] = load_materials_from_file(mtl_file)

    return model


def load_texture_from_file(img_textura):
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
    img = img.convert('RGBA')  # Usamos RGBA para habilitar transparência
    img_width = img.size[0]
    img_height = img.size[1]
    image_data = img.tobytes("raw", "RGBA", 0, -1)
    #image_data = np.array(list(img.getdata()), np.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    return texture_id

def get_textura_cor(r, g, b):
    # Cria uma textura monocromática
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
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1, 1, 0, GL_RGB, GL_UNSIGNED_BYTE, bytes([r, g, b]))

    return texture_id

def process_nagons(arr):
    # Alguns modelos tem mais de 3 vértices. O código antigo da disciplina funcionava com 4, mas para 
    # objetos com 5 ou mais dava errado.
    # Funciona tipo o GL_TRIANGLE_FAN
    
    if len(arr) == 3:
        return arr
    result = []
    for i in range(len(arr)-1):
        result.append(arr[0])
        result.extend(arr[i:i+2])
    return result


def load_obj_and_texture(objFile, filtro):
    modelo = load_model_from_file(objFile, filtro)

    # Carrega os materiais
    for mat in modelo['materials'].values():
        if mat.texture_fname:
            mat.texture_id = load_texture_from_file(mat.texture_fname)

    # Mantém os vértices (de geometria, de textura e normais) ordenados por nome do arquivo de textura
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

