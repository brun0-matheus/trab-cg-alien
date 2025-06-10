from objeto_textura import ObjetoTextura
import math
import glm
from OpenGL.GL import *
from loading_utils import load_texture_from_file
import numpy as np

# Função utilitária que gera uma matriz de transformação 3D completa (model)
def model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z):
    angle = math.radians(angle)
    matrix_transform = glm.mat4(1.0)

    # Aplica translação
    matrix_transform = glm.translate(matrix_transform, glm.vec3(t_x, t_y, t_z))
    # Aplica rotação se necessário
    if angle != 0:
        matrix_transform = glm.rotate(matrix_transform, angle, glm.vec3(r_x, r_y, r_z))
    # Aplica escala
    matrix_transform = glm.scale(matrix_transform, glm.vec3(s_x, s_y, s_z))

    return matrix_transform


"""
SERVIDOR
"""
class Servidor(ObjetoTextura):
    def __init__(self, i: int):
        self.i = i
        return super().__init__('ServerV2+console.obj', glm.vec3(1), glm.vec3(1.5))

    def get_model(self):
        s = 0.04
        z_offset = -0.3 + 0.1 * self.i + (0.165 if self.i >= 3 else 0)
        return model(180, 0, 1, 0, 0.31, -0.445, z_offset, s, s, s)

"""
LOUSA E TINTA INVISÍVEL
"""
class Lousa(ObjetoTextura):
    def __init__(self):
        return super().__init__('footer.obj', glm.vec3(1), glm.vec3(1))

    def get_model(self):
        s = 0.0003
        return model(90, 0, 1, 0, -0.765, -0.25, -0.1, s, s+0.00015, s)

class TintaInvisivel(ObjetoTextura):
    def __init__(self):
        self.invisible_paint = True
        return super().__init__('tinta_invisivel.obj', glm.vec3(1), glm.vec3(1))

    def get_model(self):
        s = 0.0003
        return model(90, 0, 1, 0, -0.764, -0.25, -0.1, s, s+0.00015, s)

"""
ALIEN
"""
class Alien(ObjetoTextura):
    def __init__(self):
        return super().__init__('alien.obj', glm.vec3(1), glm.vec3(2))

    def get_model(self):
        s = 0.02
        return model(90, 0, 1, 0, -0.75, -0.445, 0.5, s, s, s)

"""
ANTENA
"""
class Antena(ObjetoTextura):
    def __init__(self):
        self.angle = 0
        return super().__init__('antena.obj', glm.vec3(1), glm.vec3(3), lambda xyz: xyz[1] > 2.1 or xyz[0] > 1)

    def get_model(self):
        s = 0.025
        mat = model(0, 1, 0, 0, 0.3, -0.082, 0.35, s, s, s)

        # Translação para rotação local
        tx, ty, tz = -1.43128, 2.51128, -2.10823
        mat = glm.translate(mat, glm.vec3(tx, ty, tz))
        mat = glm.rotate(mat, math.radians(self.angle), glm.vec3(0.577263, 0.045363, -0.815298))
        mat = glm.translate(mat, glm.vec3(-tx, -ty, -tz))
        return mat

"""
CARRO
"""
class Carro(ObjetoTextura):
    def __init__(self):
        self.pos = 0
        return super().__init__('carro.obj', glm.vec3(1), glm.vec3(3))

    def get_model(self):
        s = 0.002
        return model(90, 0, 1, 0, self.pos, -0.5, 1, s, s, s)

"""
PAINEL SOLAR
"""
class PainelSolar(ObjetoTextura):
    def __init__(self):
        return super().__init__('painel_solar.obj', glm.vec3(1), glm.vec3(1))

    def get_model(self):
        s = 0.001
        mat = model(90, 0, 1, 0, -0.2, -0.06, -0.4, s, s, s)

        # Recentrar modelo e inclinar
        tx, ty, tz = 650, -80, 0
        mat = glm.translate(mat, glm.vec3(-tx, -ty, -tz))
        mat = glm.rotate(mat, math.radians(-19), glm.vec3(0, 0, 1))
        mat = glm.translate(mat, glm.vec3(tx, ty, tz))
        return mat

"""
CASA
"""
class Casa(ObjetoTextura):
    def __init__(self):
        return super().__init__('casa.obj', glm.vec3(1), glm.vec3(0.1))

    def get_model(self):
        s = 0.1
        return model(1, 0, 0, 1, 0.0, -0.5, 0, s, s, s)

"""
CHÃO E FORRO
"""
class Chao:
    def load(self):
        # Carrega texturas
        self.tex_chao = load_texture_from_file('grama.png')
        self.tex_piso = load_texture_from_file('concreto.jpg')
        self.tex_forro = load_texture_from_file('forro.jpg')

        lim = 60
        y_grama = 0.001 - 0.5
        y_piso = 0.055 - 0.5
        y_forro = 0.38 - 0.5

        # Define os vértices para chão, piso e forro
        verts = [
            (-lim, y_grama, -lim), (-lim, y_grama, lim), (lim, y_grama, -lim), (lim, y_grama, lim),
            (-0.761, y_piso, -0.367), (0.354, y_piso, -0.367), (-0.761, y_piso, 0.444), (0.354, y_piso, 0.444),
            (-0.761, y_piso, 0.444), (-0.456, y_piso, 0.444), (-0.761, y_piso, 0.67), (-0.456, y_piso, 0.67),
            (-0.761, y_forro, -0.367), (0.354, y_forro, -0.367), (-0.761, y_forro, 0.444), (0.354, y_forro, 0.444)
        ]

        # Coordenadas de textura com diferentes resoluções
        texture_coords = [
            (0, 0), (200, 0), (0, 200), (200, 200),
            (0, 0), (1, 0), (0, 1), (1, 1),
            (0, 0), (1, 0), (0, 1), (1, 1),
            (0, 0), (10, 0), (0, 10), (10, 10)
        ]

        normals = [(0, 1, 0)] * len(verts)
        return verts, texture_coords, normals

    def desenha(self, ini_pos, shader):
        program = shader.ID
        shader.setVec3('materialDiffuse', glm.vec3(1))
        shader.setVec3('materialSpecular', glm.vec3(0.1))
        loc_transformation = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_transformation, 1, GL_TRUE, np.array(glm.mat4(1.0)))

        # Chão de grama
        glBindTexture(GL_TEXTURE_2D, self.tex_chao)
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)
        ini_pos += 4

        # Piso
        glBindTexture(GL_TEXTURE_2D, self.tex_piso)
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)
        ini_pos += 4
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)
        ini_pos += 4

        # Forro
        glBindTexture(GL_TEXTURE_2D, self.tex_forro)
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)

"""
SINAL (PLACA COM OLHO)
"""
class Sinal:
    def __init__(self):
        self.own_light = True

    def load(self):
        self.texture = load_texture_from_file('eye.png')
        self.escala = 0.1
        return [(-1, 0, -1), (-1, 0, 1), (1, 0, -1), (1, 0, 1)], [(0, 0), (0, 1), (1, 0), (1, 1)], [(0, 1, 0)] * 4

    def desenha(self, ini_pos, shader):
        program = shader.ID
        shader.setVec3('materialDiffuse', glm.vec3(0))
        shader.setVec3('materialSpecular', glm.vec3(0))

        s = self.escala
        mat_model = model(0, 0, 0, 1, 2, 7, 3, s, s, s)
        loc_transformation = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_transformation, 1, GL_TRUE, np.array(mat_model))

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)

"""
SKYBOX (CÉU)
"""
class Skybox:
    def __init__(self):
        self.own_light = True

    def load(self):
        self.tex_up = load_texture_from_file('sky_up.jpg')
        self.tex_side = load_texture_from_file('sky_side.jpg')

        lim = 60
        y_grama = 0.001 - 0.5
        y_ceu = 10

        verts = [
            (-lim, y_ceu, -lim), (lim, y_ceu, -lim), (-lim, y_ceu, lim), (lim, y_ceu, lim),
            (-lim, y_grama, -lim), (lim, y_grama, -lim), (-lim, y_ceu, -lim), (lim, y_ceu, -lim),
            (-lim, y_grama, lim), (lim, y_grama, lim), (-lim, y_ceu, lim), (lim, y_ceu, lim),
            (-lim, y_grama, lim), (-lim, y_grama, -lim), (-lim, y_ceu, lim), (-lim, y_ceu, -lim),
            (lim, y_grama, lim), (lim, y_grama, -lim), (lim, y_ceu, lim), (lim, y_ceu, -lim)
        ]

        tex_coords = [
            (0, 0), (30, 0), (0, 30), (30, 30),
            (0, 0), (10, 0), (0, 10), (10, 10),
            (0, 0), (10, 0), (0, 10), (10, 10),
            (0, 0), (10, 0), (0, 10), (10, 10),
            (0, 0), (10, 0), (0, 10), (10, 10)
        ]

        normals = [(1, 0, 0)] * len(verts)
        return verts, tex_coords, normals

    def desenha(self, ini_pos, shader):
        program = shader.ID
        shader.setVec3('materialDiffuse', glm.vec3(0))
        shader.setVec3('materialSpecular', glm.vec3(0))
        mat_model = glm.mat4(1.0)
        loc_transformation = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_transformation, 1, GL_TRUE, np.array(mat_model))

        glBindTexture(GL_TEXTURE_2D, self.tex_up)
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)
        ini_pos += 4

        glBindTexture(GL_TEXTURE_2D, self.tex_side)
        for _ in range(4):
            glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)
            ini_pos += 4

"""
LÂMPADA
"""
class Lampada(ObjetoTextura):
    pos = (-0.2, -0.13, 0)

    def __init__(self):
        return super().__init__('LightBulb.obj', glm.vec3(1), glm.vec3(1))

    def get_model(self):
        s = 0.015
        return model(180, 0, 0, 1, -0.2, -0.13, 0, s, s, s)
