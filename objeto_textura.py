from loading_utils import load_obj_and_texture
from OpenGL.GL import *
import numpy as np

class ObjetoTextura:  
    # Classe genérica que lê um .obj e carrega sua textura
    def __init__(self, object_filename: str, filtro=None):
        self.object_filename = object_filename
        self.filtro = filtro or (lambda xyz: True)
    
    def get_model():   # Filhos tem que implementar
        return glm.mat4(1.0)
    
    def load(self):
        # Carrega do .obj
        self.verts_with_texture = load_obj_and_texture(self.object_filename, self.filtro)

        verts_coords, texture_coords, normals = [], [], []
        for verts, texture, normal, material in self.verts_with_texture:
            verts_coords.extend(verts)
            texture_coords.extend(texture)
            normals.extend(normal)

        return verts_coords, texture_coords, normals

    def desenha(self, ini_pos, program):     
        # Desenha o objeto
        
        mat_model = self.get_model() 
        loc_transformation = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_transformation, 1, GL_TRUE, np.array(mat_model))

        for verts, _, _, mat in self.verts_with_texture:
            inicio = ini_pos
            fim = len(verts) + inicio
            
            if mat.texture_id is not None:
                #print(f'Desenha de {inicio} ate {fim}, com textura {mat.texture_id} ({mat.texture_fname})')
                glBindTexture(GL_TEXTURE_2D, mat.texture_id)
            else:
                print(f'{inicio} ate {fim} sem textura, nao desenha')
                ini_pos = fim
                #continue
                raise Exception('Nao suporta renderizar sem textura')
            
            # desenha o modelo
            glDrawArrays(GL_TRIANGLES, inicio, fim - inicio) ## renderizando

            ini_pos = fim

