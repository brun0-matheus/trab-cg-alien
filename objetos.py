from objeto_textura import ObjetoTextura
import math
import glm
from OpenGL.GL import *
from loading_utils import load_texture_from_file
import numpy as np

def model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z):   
    # Gera a matriz model. Também é responsável por aplicar transformações globais
    angle = math.radians(angle)
    
    matrix_transform = glm.mat4(1.0) # instanciando uma matriz identidade
       
    # aplicando translacao (terceira operação a ser executada)
    matrix_transform = glm.translate(matrix_transform, glm.vec3(t_x, t_y, t_z))    
    
    # aplicando rotacao (segunda operação a ser executada)
    if angle!=0:
        matrix_transform = glm.rotate(matrix_transform, angle, glm.vec3(r_x, r_y, r_z))
    
    # aplicando escala (primeira operação a ser executada)
    matrix_transform = glm.scale(matrix_transform, glm.vec3(s_x, s_y, s_z))    
    return matrix_transform



"""
SERVIDOR
"""
class Servidor(ObjetoTextura):   
    def __init__(self, i: int):
        self.i = i
        return super().__init__('ServerV2+console.obj', glm.vec3(1), glm.vec3(1))

    def get_model(self):       
        s = 0.04
        return model(180, 0, 1, 0, 0.31, -0.445, -0.3 + 0.1 * self.i + (0.165 if self.i>=3 else 0), s, s, s)

"""
LOUSA
"""

class Lousa(ObjetoTextura):   
    def __init__(self):
        return super().__init__('footer.obj', glm.vec3(1), glm.vec3(1))

    def get_model(self):   
        s = 0.0003
        return model(90, 0, 1, 0, -0.765, -0.25, -0.1, s, s+0.00015, s)

"""
ALIEN
"""

class Alien(ObjetoTextura):   
    def __init__(self):
        return super().__init__('alien.obj', glm.vec3(1), glm.vec3(1))

    def get_model(self):   
        s = 0.02
        return model(90, 0, 1, 0, -0.75, -0.445, 0.5, s, s, s)

"""
ANTENA
"""

class Antena(ObjetoTextura):   
    def __init__(self):
        self.angle = 0
        return super().__init__('antena.obj', glm.vec3(1), glm.vec3(1), lambda xyz: xyz[1] > 2.1 or xyz[0] > 1)

    def get_model(self):   
        s = 0.025
        mat = model(0, 1, 0, 0, 0.3, -0.082, 0.35, s, s, s)

        # translada para aplicar a rotacao
        tx, ty, tz = -1.43128, 2.51128, -2.10823
        mat = glm.translate(mat, glm.vec3(tx, ty, tz))
        mat = glm.rotate(mat, math.radians(self.angle), glm.vec3(0.577263, 0.045363, -0.815298))
        mat = glm.translate(mat, glm.vec3(-tx, -ty, -tz))
        return mat
        #return glm.mat4(1.0)

"""
CARRO
"""

class Carro(ObjetoTextura):   
    def __init__(self):
        self.pos = 0
        return super().__init__('carro.obj', glm.vec3(1), glm.vec3(1))

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

        # O modelo original nao esta centrado no (0,0). Primeiro mandamos para la
        tx = 650
        ty = -80
        tz = 0

        mat = glm.translate(mat, glm.vec3(-tx, -ty, -tz))
        mat = glm.rotate(mat, math.radians(-19), glm.vec3(0, 0, 1))
        mat = glm.translate(mat, glm.vec3(tx, ty, tz))
        return mat

"""
CASA
"""

class Casa(ObjetoTextura):   
    def __init__(self):
        return super().__init__('casa.obj', glm.vec3(1), glm.vec3(1))

    def get_model(self):   
        s = 0.1
        return model(1, 0, 0, 1, 0.0, -0.5, 0, s, s, s)

"""
CHAO E FORRO
"""

class Chao:   
    def load(self):
        self.tex_chao = load_texture_from_file('grama.png')
        self.tex_piso = load_texture_from_file('concreto.jpg')
        self.tex_forro = load_texture_from_file('forro.jpg')

        lim = 60  # Limite do chão de grama
        y_grama = 0.001 - 0.5
        y_piso = 0.055 - 0.5
        y_forro = 0.38 - 0.5
        
        verts = [
            # Chao grama
            (-lim, y_grama, -lim),
            (lim, y_grama, -lim),
            (-lim, y_grama, lim),
            (lim, y_grama, lim),

            # Piso da casa
            (-0.761, y_piso, -0.367),
            (0.354, y_piso, -0.367),
            (-0.761, y_piso, 0.444),
            (0.354, y_piso, 0.444),
            # Segunda parte do piso
            (-0.761, y_piso, 0.444),
            (-0.456, y_piso, 0.444),
            (-0.761, y_piso, 0.67),
            (-0.456, y_piso, 0.67),

            # Forro da casa
            (-0.761, y_forro, -0.367),
            (0.354, y_forro, -0.367),
            (-0.761, y_forro, 0.444),
            (0.354, y_forro, 0.444),
        ]

        # A resolução controla quantas vezes a imagem da textura será repetida (em cada direção)
        resolucao_grama = 200
        resolucao_concreto = 1
        resolucao_forro = 10
        
        texture_coords = [
            (0, 0), (resolucao_grama, 0), (0, resolucao_grama), (resolucao_grama, resolucao_grama),
            (0, 0), (resolucao_concreto, 0), (0, resolucao_concreto), (resolucao_concreto, resolucao_concreto),
            (0, 0), (resolucao_concreto, 0), (0, resolucao_concreto), (resolucao_concreto, resolucao_concreto),
            (0, 0), (resolucao_forro, 0), (0, resolucao_forro), (resolucao_forro, resolucao_forro),
        ] 

        normals = [(1, 0, 0)] * len(verts)
        return verts, texture_coords, normals

    def desenha(self, ini_pos, shader):
        program = shader.ID

        shader.setVec3('materialDiffuse', glm.vec3(1))
        shader.setVec3('materialSpecular', glm.vec3(1))

        mat_model = glm.mat4(1.0)  # identidade
        loc_transformation = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_transformation, 1, GL_TRUE, np.array(mat_model))

        # Chão de grama
        glBindTexture(GL_TEXTURE_2D, self.tex_chao)
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)
        ini_pos+=4

        # Piso da casa
        glBindTexture(GL_TEXTURE_2D, self.tex_piso)
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)
        ini_pos+=4
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)
        ini_pos+=4

        # Forro
        glBindTexture(GL_TEXTURE_2D, self.tex_forro)
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)

"""
SINAL
"""

class Sinal:
    def load(self):
        self.texture = load_texture_from_file('eye.png')
        self.escala = 0.1

        # Quadrado
        return [(-1, 0, -1), (-1, 0, 1), (1, 0, -1), (1, 0, 1)], [(0, 0), (0, 1), (1, 0), (1, 1)], [(1, 0, 0)] * 4

    def desenha(self, ini_pos, shader):
        program = shader.ID

        shader.setVec3('materialDiffuse', glm.vec3(1))
        shader.setVec3('materialSpecular', glm.vec3(1))

        s = self.escala
        
        mat_model = model(0, 0, 0, 1, 2, 7, 3, s, s, s)
        loc_transformation = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_transformation, 1, GL_TRUE, np.array(mat_model))

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)

"""
SKYBOX
"""

class Skybox:
    def load(self):
        self.tex_up = load_texture_from_file('sky_up.jpg')
        self.tex_side = load_texture_from_file('sky_side.jpg')

        lim = 60 
        y_grama = 0.001 - 0.5
        y_ceu = 10

        verts = [
            # Cima
            (-lim, y_ceu, -lim), (lim, y_ceu, -lim), (-lim, y_ceu, lim), (lim, y_ceu, lim),
            # Lados
            (-lim, y_grama, -lim), (lim, y_grama, -lim), (-lim, y_ceu, -lim), (lim, y_ceu, -lim),
            (-lim, y_grama, lim), (lim, y_grama, lim), (-lim, y_ceu, lim), (lim, y_ceu, lim),
            (-lim, y_grama, lim), (-lim, y_grama, -lim), (-lim, y_ceu, lim), (-lim, y_ceu, -lim),
            (lim, y_grama, lim), (lim, y_grama, -lim), (lim, y_ceu, lim), (lim, y_ceu, -lim),
        ]

        # A resolução controla quantas vezes a imagem da textura será repetida (em cada direção)
        resolucao_up = 30
        resolucao_side = 1

        tex_coords = [
            # Cima
            (0, 0), (resolucao_up, 0), (0, resolucao_up), (resolucao_up, resolucao_up),
            # Lados
            (0, 0), (resolucao_side, 0), (0, resolucao_side), (resolucao_side, resolucao_side),
            (0, 0), (resolucao_side, 0), (0, resolucao_side), (resolucao_side, resolucao_side),
            (0, 0), (resolucao_side, 0), (0, resolucao_side), (resolucao_side, resolucao_side),
            (0, 0), (resolucao_side, 0), (0, resolucao_side), (resolucao_side, resolucao_side),
        ]

        normals = [(1, 0, 0)] * len(verts)
        return verts, tex_coords, normals

    def desenha(self, ini_pos, shader):
        program = shader.ID

        shader.setVec3('materialDiffuse', glm.vec3(1))
        shader.setVec3('materialSpecular', glm.vec3(1))

        mat_model = glm.mat4(1.0)
        loc_transformation = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_transformation, 1, GL_TRUE, np.array(mat_model))

        # Cima
        glBindTexture(GL_TEXTURE_2D, self.tex_up)
        glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)
        ini_pos+=4

        # Outros lados
        glBindTexture(GL_TEXTURE_2D, self.tex_side)
        for _ in range(4):
            glDrawArrays(GL_TRIANGLE_STRIP, ini_pos, 4)
            ini_pos+=4

"""
Lâmpada
"""

class Lampada(ObjetoTextura):   
    pos = (-0.2, -0.13, 0)

    def __init__(self):
        return super().__init__('LightBulb.obj', glm.vec3(1), glm.vec3(1))

    def get_model(self):   
        s = 0.015
        return model(180, 0, 0, 1, -0.2, -0.13, 0, s, s, s)

"""
Farol
"""

class Farol(ObjetoTextura):   
    def __init__(self):
        self.pos = 0
        return super().__init__('Farol.obj')

    def get_model(self):   
        s = 0.002
        return model(90, 0, 1, 0, self.pos, -0.5, 1, s, s, s)

"""
Lanterna
"""

