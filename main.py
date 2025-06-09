# Bibliotecas e módulos
import glfw
from OpenGL.GL import *
import numpy as np
import glm
import math

# Módulos customizados
from shader_m import Shader
from objetos import *
from camera import Camera
from lights import Light, SpotLight

"""
INICIALIZAÇÃO DA JANELA
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
COMPILANDO SHADERS
"""
shader = Shader('shader.vs', 'shader.fs')
shader.use()
program = shader.ID

"""
ATIVAÇÕES OPENGL
"""
glEnable(GL_TEXTURE_2D)
glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_LINE_SMOOTH)

"""
INICIALIZA CÂMERA
"""
camera = Camera(position=glm.vec3(0.395353, -0.0869291, 2.15247), up=glm.vec3(0.0, 1.0, 0.0))

"""
CARREGAMENTO DE OBJETOS
"""
antena = Antena()
sinal = Sinal()
carro = Carro()
lampada = Lampada()

objetos = [Servidor(i) for i in range(6)] + [PainelSolar(), Alien(), Lousa(), TintaInvisivel(), Chao(), Skybox(), Casa()]
objetos += [antena, sinal, lampada]

# Dados de geometria
vertices_list, textures_coord_list, normals_list = [], [], []
pos_objetos = [0]*len(objetos)

for i, objeto in enumerate(objetos):
    pos_objetos[i] = len(vertices_list)
    vertices, texture, normal = objeto.load()
    vertices_list.extend(vertices)
    textures_coord_list.extend(texture)
    normals_list.extend(normal)

"""
ENVIANDO DADOS PARA GPU
"""
buffer_VBO = glGenBuffers(3)
verts_tudo = []

# Junta vértices, normais e texturas em um único array
assert len(vertices_list) == len(textures_coord_list) == len(normals_list)
for i in range(len(vertices_list)):
    verts_tudo.extend(vertices_list[i])
    verts_tudo.extend(normals_list[i])
    verts_tudo.extend(textures_coord_list[i])

vertices = glm.array(glm.float32, *map(float, verts_tudo))

# Configura VBO e VAO
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
VARIÁVEIS GLOBAIS
"""
firstMouse = True
lastX = largura / 2.0
lastY = altura / 2.0

deltaTime = 0.0
lastFrame = 0.0

is_inside = False

lanterna_ativa = True
lampada_ativa = True
farol_ativo = True
luz_ambiente_ativa = True

mult_ambient = 1
mult_diffuse = 1
mult_specular = 1

"""
EVENTOS DE TECLADO
"""
def key_event(window,key,scancode,action,mods):
    global is_inside, lanterna_ativa, lampada_ativa, farol_ativo
    global luz_ambiente_ativa, mult_ambient, mult_diffuse, mult_specular

    if action == glfw.RELEASE:
        return

    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
        return

    # Movimentação da câmera
    if key == glfw.KEY_W:
        camera.ProcessKeyboard(camera.FORWARD, deltaTime)
    elif key == glfw.KEY_S:
        camera.ProcessKeyboard(camera.BACKWARD, deltaTime)
    elif key == glfw.KEY_A:
        camera.ProcessKeyboard(camera.LEFT, deltaTime)
    elif key == glfw.KEY_D:
        camera.ProcessKeyboard(camera.RIGHT, deltaTime)

    # Ações nos objetos
    elif key == glfw.KEY_Q:
        antena.angle = max(antena.angle - 1, -40)
    elif key == glfw.KEY_X:
        sinal.escala = min(sinal.escala + 0.01, 5.3)
    elif key == glfw.KEY_Z:
        sinal.escala = max(sinal.escala - 0.01, 0.05)

    # Movimento do carro
    elif key == glfw.KEY_N:
        carro.pos += 0.01
        if carro.pos >= 5:
            carro.pos = -5
        for i in range(2):
            farol[i].position.x = carro.pos + 0.155
    elif key == glfw.KEY_B:
        carro.pos -= 0.01
        if carro.pos <= -5.10:
            carro.pos = 5
        for i in range(2):
            farol[i].position.x = carro.pos + 0.155

    # Intensidade da iluminação
    elif key in [glfw.KEY_O, glfw.KEY_L, glfw.KEY_I, glfw.KEY_K, glfw.KEY_U, glfw.KEY_J]:
        if key == glfw.KEY_O: mult_ambient += 0.1
        elif key == glfw.KEY_L: mult_ambient = max(mult_ambient - 0.1, 0)
        elif key == glfw.KEY_I: mult_diffuse += 0.1
        elif key == glfw.KEY_K: mult_diffuse = max(mult_diffuse - 0.1, 0)
        elif key == glfw.KEY_U: mult_specular += 0.1
        elif key == glfw.KEY_J: mult_specular = max(mult_specular - 0.1, 0)

    # Toggle de luzes
    elif key == glfw.KEY_1 and action == glfw.PRESS:
        lanterna_ativa = not lanterna_ativa
    elif key == glfw.KEY_2 and action == glfw.PRESS:
        lampada_ativa = not lampada_ativa
    elif key == glfw.KEY_3 and action == glfw.PRESS:
        farol_ativo = not farol_ativo
    elif key == glfw.KEY_4 and action == glfw.PRESS:
        luz_ambiente_ativa = not luz_ambiente_ativa
    elif key == glfw.KEY_P and action == glfw.PRESS:
        print(farol[0].position)
        print(farol[1].position)
        print('----')

    # Limites da câmera e verificação de entrada na casa
    vec_min = (-1.68604, -0.371484, -1.15517)
    vec_max = (1.40885, 1.01796, 2.45549)
    camera.Position.x = min(vec_max[0], max(vec_min[0], camera.Position.x))
    camera.Position.y = min(vec_max[1], max(vec_min[1], camera.Position.y))
    camera.Position.z = min(vec_max[2], max(vec_min[2], camera.Position.z))

    p1 = (-0.460817, -0.38, 0.679173)
    p2 = (-0.78, -0.101908, 0.373414)
    p3 = (0.325651, -0.38, -0.38)

    check_in = lambda a, b, c: min(a, b) <= c <= max(a, b)

    if all(check_in(p1[i], p2[i], camera.Position[i]) for i in range(3)):
        is_inside = True
    elif all(check_in(p2[i], p3[i], camera.Position[i]) for i in range(3)):
        is_inside = True
    else:
        is_inside = False

glfw.set_key_callback(window, key_event)

"""
CALLBACKS DE JANELA E MOUSE
"""
def framebuffer_size_callback(window, largura, altura):
    glViewport(0, 0, largura, altura)

def mouse_callback(window, xpos, ypos):
    global lastX, lastY, firstMouse
    if firstMouse:
        lastX = xpos
        lastY = ypos
        firstMouse = False
    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX = xpos
    lastY = ypos
    camera.ProcessMouseMovement(xoffset, yoffset)

def scroll_callback(window, xoffset, yoffset):
    camera.ProcessMouseScroll(yoffset)

glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
glfw.set_cursor_pos_callback(window, mouse_callback)
glfw.set_scroll_callback(window, scroll_callback)
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

"""
MATRIZES VIEW E PROJECTION
"""
def view():
    return np.array(glm.lookAt(camera.Position, camera.Position + camera.Front, camera.Up))

def projection():
    return np.array(glm.perspective(glm.radians(camera.Zoom), largura / altura, 0.1, 100.0))

"""
CONFIGURAÇÃO DE ILUMINAÇÃO
"""
lampada_luz = Light(inside=True, position=glm.vec3(-0.2, -0.19, 0), diffuse=glm.vec3(0.8), specular=glm.vec3(0.6),
                    constant=1, linear=0.136, quadratic=0.036)

lanterna = SpotLight(inside=True, position=camera.Position, direction=glm.normalize(camera.Front),
                     cutOff=glm.cos(glm.radians(10)), outerCutOff=glm.cos(glm.radians(15)),
                     diffuse=glm.vec3(1.0, 0.3, 1.0), specular=glm.vec3(0.6),
                     constant=1.0, linear=0.09, quadratic=0.09)

posicoes_farol = [glm.vec3(0.155, -0.445, 1.05), glm.vec3(0.155, -0.445, 0.96)]
farol = [SpotLight(inside=False, position=posicoes_farol[i], direction=glm.vec3(1, 0, 0),
                   cutOff=glm.cos(glm.radians(60)), outerCutOff=glm.cos(glm.radians(80)),
                   diffuse=glm.vec3(1), specular=glm.vec3(0.6),
                   constant=1.0, linear=0.09, quadratic=0.032) for i in range(2)]

"""
LOOP PRINCIPAL
"""
glfw.show_window(window)
glEnable(GL_DEPTH_TEST)

while not glfw.window_should_close(window):
    currentFrame = glfw.get_time()
    deltaTime = currentFrame - lastFrame
    lastFrame = currentFrame

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # Matrizes view e projection
    glUniformMatrix4fv(glGetUniformLocation(program, "view"), 1, GL_TRUE, view())
    glUniformMatrix4fv(glGetUniformLocation(program, "projection"), 1, GL_TRUE, projection())

    # Envia dados da câmera e iluminação para shader
    shader.setVec3('viewPos', camera.Position)
    shader.setFloat('shininess', 32.0)

    # Ativação das luzes
    point_lights = [lampada_luz] if lampada_ativa else []
    spot_lights = []
    if lanterna_ativa:
        lanterna.position = camera.Position
        lanterna.direction = glm.normalize(camera.Front)
        spot_lights.append(lanterna)
    if farol_ativo:
        spot_lights.extend(farol)

    # Luzes pontuais
    for i, light in enumerate(point_lights):
        shader.setVec3(f'pointLights[{i}].position', light.position)
        shader.setFloat(f'pointLights[{i}].constant', light.constant)
        shader.setFloat(f'pointLights[{i}].linear', light.linear)
        shader.setFloat(f'pointLights[{i}].quadratic', light.quadratic)
        if light.inside == is_inside:
            shader.setVec3(f'pointLights[{i}].diffuse', light.diffuse * mult_diffuse)
            shader.setVec3(f'pointLights[{i}].specular', light.specular * mult_specular)
        else:
            shader.setVec3(f'pointLights[{i}].diffuse', glm.vec3(0))
            shader.setVec3(f'pointLights[{i}].specular', glm.vec3(0))

    # Spotlights
    for i, light in enumerate(spot_lights):
        shader.setVec3(f'spotLights[{i}].position', light.position)
        shader.setVec3(f'spotLights[{i}].direction', light.direction)
        shader.setFloat(f'spotLights[{i}].cutOff', light.cutOff)
        shader.setFloat(f'spotLights[{i}].outerCutOff', light.outerCutOff)
        shader.setFloat(f'spotLights[{i}].constant', light.constant)
        shader.setFloat(f'spotLights[{i}].linear', light.linear)
        shader.setFloat(f'spotLights[{i}].quadratic', light.quadratic)
        if light.inside == is_inside:
            shader.setVec3(f'spotLights[{i}].diffuse', light.diffuse * mult_diffuse)
            shader.setVec3(f'spotLights[{i}].specular', light.specular * mult_specular)
        else:
            shader.setVec3(f'spotLights[{i}].diffuse', glm.vec3(0))
            shader.setVec3(f'spotLights[{i}].specular', glm.vec3(0))

    # Renderização dos objetos
    for objeto, pos in zip(objetos, pos_objetos):
        shader.setInt('numPointLights', len(point_lights))
        shader.setInt('numSpotLights', len(spot_lights))
        shader.setInt('invisible', 0)

        if luz_ambiente_ativa:
            if hasattr(objeto, 'own_light') and objeto.own_light:
                shader.setVec3('ambientLight', glm.vec3(1) * mult_ambient)
            else:
                branco = glm.vec3(0.1)
                roxo = glm.vec3(0.4, 0.1, 0.4) * sinal.escala * 0.5
                shader.setVec3('ambientLight', (branco + roxo) * mult_ambient)
        else:
            shader.setVec3('ambientLight', glm.vec3(0))

        if hasattr(objeto, 'invisible_paint') and objeto.invisible_paint:
            shader.setVec3('ambientLight', 0)
            shader.setInt('numPointLights', 0)
            shader.setInt('numSpotLights', 1)
            shader.setInt('invisible', 1)

        objeto.desenha(pos, shader)

    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.terminate()
