import glfw
from OpenGL.GL import *
import numpy as np
import glm
import math
from shader_m import Shader
from objetos import *
from camera import Camera
from lights import Light, SpotLight

"""
INICIALIZANDO JANELA
"""

glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
largura, altura = 700, 700
window = glfw.create_window(largura, altura, "WOW!", None, None)

if window is None:
    print("Failed to create GLFW window")
    glfwTerminate()
    
glfw.make_context_current(window)

"""
COMPILANDO E MANDANDO PRA GPU
"""

# Set shaders source
shader = Shader('shader.vs', 'shader.fs')
shader.use()
program = shader.ID

"""
LINKAGEM E ATIVANDO OPENGL PRA TEXTURA
"""

glEnable(GL_TEXTURE_2D)
glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glEnable( GL_BLEND )
glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
glEnable(GL_LINE_SMOOTH)

"""
CRIANDO CAMERA
"""
camera = Camera(position=glm.vec3(0.395353, -0.0869291, 2.15247), up=glm.vec3(0.0, 1.0, 0.0))


""" 
CRIANDO OBJETOS
"""

antena = Antena()
sinal = Sinal()
carro = Carro()
lampada = Lampada()
#farol = Farol()

objetos = [Servidor(i) for i in range(6)] + [PainelSolar(), Alien(), Lousa(), Chao(), Skybox()]
objetos += [antena, sinal, lampada]
#objetos.append(carro)

# Vetor que contém vértices de todos objetos
vertices_list = []
textures_coord_list = []
normals_list = []
# Vetor que armazena a posição que cada objeto começa no vetor global de vértices
pos_objetos = [0]*len(objetos)

for i, objeto in enumerate(objetos):
    pos_objetos[i] = len(vertices_list)
    vertices, texture, normal = objeto.load()
    vertices_list.extend(vertices)
    textures_coord_list.extend(texture)
    normals_list.extend(normal)

"""
MANDANDO PRA GPU
"""

buffer_VBO = glGenBuffers(3)

'''
# Manda vértices

vertices = np.zeros(len(vertices_list), [("position", np.float32, 3)])
vertices['position'] = vertices_list

glBindBuffer(GL_ARRAY_BUFFER, buffer_VBO[0])
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)
loc_vertices = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc_vertices)
glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)

# Manda coordenadas de textura

textures = np.zeros(len(textures_coord_list), [("position", np.float32, 2)]) # duas coordenadas
textures['position'] = textures_coord_list

glBindBuffer(GL_ARRAY_BUFFER, buffer_VBO[1])
glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
stride = textures.strides[0]
offset = ctypes.c_void_p(0)
loc_texture_coord = glGetAttribLocation(program, "texture_coord")
glEnableVertexAttribArray(loc_texture_coord)
glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)

# Manda normais

normals = np.zeros(len(normals_list), [("position", np.float32, 3)])
normals['position'] = normals_list


# Upload data
#glBindBuffer(GL_ARRAY_BUFFER, buffer_VBO[2])
#glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
#stride = normals.strides[0]
#offset = ctypes.c_void_p(0)
loc_normals = glGetAttribLocation(program, "vert_normal")
print(loc_normals)
glEnableVertexAttribArray(loc_normals)
#glVertexAttribPointer(loc_normals, 3, GL_FLOAT, False, stride, offset)
'''

verts_tudo = []  # agrupa coord de vertice, textura e normal
assert len(vertices_list) == len(textures_coord_list) and len(vertices_list) == len(normals_list)

for i in range(len(vertices_list)):
    verts_tudo.extend(vertices_list[i])
    verts_tudo.extend(normals_list[i])
    verts_tudo.extend(textures_coord_list[i])

vertices = glm.array(glm.float32, *map(float, verts_tudo))

VAO = glGenVertexArrays(1)
VBO = glGenBuffers(1)

glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW)

glBindVertexArray(VAO)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), None)
glEnableVertexAttribArray(0)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
glEnableVertexAttribArray(1)
glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), ctypes.c_void_p(6 * glm.sizeof(glm.float32)))
glEnableVertexAttribArray(2)


"""
GLOBAIS PARA TRANSFORMACOES
"""

# camera

firstMouse = True
lastX =  largura / 2.0
lastY =  altura / 2.0

# timing
deltaTime = 0.0	# time between current frame and last frame
lastFrame = 0.0

# transformações
mostra_malha = False

# Luzes
lanterna_ativa = True
lampada_ativa = True

"""
EVENTOS DE TECLADO
"""

def key_event(window,key,scancode,action,mods):
    global mostra_malha

    global lanterna_ativa, lampada_ativa

    # Quando solta a tecla não é pra fazer nada
    if action == glfw.RELEASE:
        return

    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
        return
    
    if key == glfw.KEY_W:
        camera.ProcessKeyboard(camera.FORWARD, deltaTime)
    elif key == glfw.KEY_S:
        camera.ProcessKeyboard(camera.BACKWARD, deltaTime)
    elif key == glfw.KEY_A:
        camera.ProcessKeyboard(camera.LEFT, deltaTime)
    elif key == glfw.KEY_D:
        camera.ProcessKeyboard(camera.RIGHT, deltaTime)
    elif key == glfw.KEY_Q:
        antena.angle -= 1
        antena.angle = max(antena.angle, -40)
    elif key == glfw.KEY_X:
        sinal.escala += 0.01
        sinal.escala = min(sinal.escala, 5.3)
    elif key == glfw.KEY_Z:
        sinal.escala -= 0.01
        sinal.escala = max(sinal.escala, 0.05)
    elif key == glfw.KEY_I:
        carro.pos += 0.01 
        if carro.pos >= 5:
            carro.pos = -5
    elif key == glfw.KEY_K:
        carro.pos -= 0.01
        if carro.pos <= -5.10:
            carro.pos = 5
                      # (só ativa quando aperta pela primeira vez)
    # Tecla L para alternar a lanterna
    elif key == glfw.KEY_P and action == glfw.PRESS:
        lanterna_ativa = not lanterna_ativa
    # Tecla T para alternar a lâmpada
    elif key == glfw.KEY_O and action == glfw.PRESS:
        lampada_ativa = not lampada_ativa
    elif key == 80 and action == glfw.PRESS: # p -> mostra (ou não) a malha poligonal 
        mostra_malha = not mostra_malha     
   
    # aplica limites na câmera
    vec_min = (-1.68604, -0.371484, -1.15517)
    vec_max = (1.40885, 1.01796, 2.45549)

    camera.Position.x = min(vec_max[0], max(vec_min[0], camera.Position.x))
    camera.Position.y = min(vec_max[1], max(vec_min[1], camera.Position.y))
    camera.Position.z = min(vec_max[2], max(vec_min[2], camera.Position.z))

        
glfw.set_key_callback(window,key_event)

"""
MOUSE E JANELA
"""

def framebuffer_size_callback(window, largura, altura):
    # make sure the viewport matches the new window dimensions note that width and 
    # height will be significantly larger than specified on retina displays.
    glViewport(0, 0, largura, altura)

# glfw: whenever the mouse moves, this callback is called
# -------------------------------------------------------
def mouse_callback(window, xpos, ypos):
    global lastX, lastY, firstMouse 
   
    if firstMouse:
        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos # reversed since y-coordinates go from bottom to top
    lastX = xpos
    lastY = ypos

    camera.ProcessMouseMovement(xoffset, yoffset)


# glfw: whenever the mouse scroll wheel scrolls, this callback is called
# ----------------------------------------------------------------------
def scroll_callback(window, xoffset, yoffset):
    camera.ProcessMouseScroll(yoffset)
    
glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
glfw.set_cursor_pos_callback(window, mouse_callback)
glfw.set_scroll_callback(window, scroll_callback)

# tell GLFW to capture our mouse
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)


"""
SLA
"""


def view():
    mat_view = glm.lookAt(camera.Position, camera.Position + camera.Front, camera.Up)
    mat_view = np.array(mat_view)
    return mat_view

def projection():
    global altura, largura
    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(camera.Zoom), largura/altura, 0.1, 100.0)
    
    mat_projection = np.array(mat_projection)    
    return mat_projection


"""
ILUMINAÇÃO
"""

# Lampada
lampada_luz = Light(position=glm.vec3(-0.2, -0.19, 0),
                    diffuse=glm.vec3(1.0, 1.0, 0.8),
                    specular=glm.vec3(1.0, 1.0, 0.8),
                    constant=1,
                    linear=0.136,
                    quadratic=0.036)

# SpotLight da câmera
lanterna = SpotLight(
    position=camera.Position,
    direction=glm.normalize(camera.Front),
    cutOff=glm.cos(glm.radians(10)),
    outerCutOff=glm.cos(glm.radians(15)),
    ambient=glm.vec3(0),
    diffuse=glm.vec3(1.0),
    specular=glm.vec3(0.6),
    constant=1.0,
    linear=0.09,
    quadratic=0.032,
)


"""
LOOP PRINCIPAL
"""

glfw.show_window(window)

glEnable(GL_DEPTH_TEST) ### importante para 3D

while not glfw.window_should_close(window):
    currentFrame = glfw.get_time()
    deltaTime = currentFrame - lastFrame
    lastFrame = currentFrame
    
    # mostra ou não a malha
    if mostra_malha:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)    
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # envia as matrizes view e projection
    mat_view = view()
    loc_view = glGetUniformLocation(program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_TRUE, mat_view)

    mat_projection = projection()
    loc_projection = glGetUniformLocation(program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_TRUE, mat_projection)    

    # passa parametros do shader
    shader.setVec3('viewPos', camera.Position)
    shader.setFloat('shininess', 32.0)
    shader.setVec3('ambientLight', glm.vec3(1, 1, 1) * 0.01)

    # Define quais luzes estão ativas
    point_lights = []
    if lampada_ativa:
        point_lights.append(lampada_luz)

    spot_lights = []
    if lanterna_ativa:
        spot_lights.append(lanterna)
        spot_lights[0].direction = glm.normalize(camera.Front)
        spot_lights[0].position = camera.Position

    shader.setInt('numPointLights', len(point_lights))
    shader.setInt('numSpotLights', len(spot_lights))

    # posiciona luzes
    for i in range(len(point_lights)):
        light = point_lights[i]
        shader.setVec3(f'pointLights[{i}].position', light.position)
        shader.setVec3(f'pointLights[{i}].diffuse', light.diffuse)
        shader.setVec3(f'pointLights[{i}].specular', light.specular)
        shader.setFloat(f'pointLights[{i}].constant', light.constant)
        shader.setFloat(f'pointLights[{i}].linear', light.linear)
        shader.setFloat(f'pointLights[{i}].quadratic', light.quadratic)

    for i, light in enumerate(spot_lights):
        shader.setVec3(f'spotLights[{i}].position', light.position)
        shader.setVec3(f'spotLights[{i}].direction', light.direction)
        shader.setVec3(f'spotLights[{i}].diffuse', light.diffuse)
        shader.setVec3(f'spotLights[{i}].specular', light.specular)
        shader.setVec3(f'spotLights[{i}].ambient', light.ambient)
        shader.setFloat(f'spotLights[{i}].cutOff', light.cutOff)
        shader.setFloat(f'spotLights[{i}].outerCutOff', light.outerCutOff)
        shader.setFloat(f'spotLights[{i}].constant', light.constant)
        shader.setFloat(f'spotLights[{i}].linear', light.linear)
        shader.setFloat(f'spotLights[{i}].quadratic', light.quadratic)

    # desenha objetos
    for objeto, pos in zip(objetos, pos_objetos):
        objeto.desenha(pos, program)
    
    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.terminate()

