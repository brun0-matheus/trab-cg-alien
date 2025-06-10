from loading_utils import load_obj_and_texture

from OpenGL.GL import *
import glm
import numpy as np

# Classe base genérica para objetos com textura carregada de arquivos .obj
class ObjetoTextura:  
    def __init__(self, object_filename: str, diffuse: glm.vec3, specular: glm.vec3, filtro=None):
        self.object_filename = object_filename      # Nome do arquivo .obj
        self.diffuse = diffuse                      # Cor difusa do material (reflete luz difusa)
        self.specular = specular                    # Cor especular do material (reflete brilho)
        self.filtro = filtro or (lambda xyz: True)  # Função para filtrar vértices (default: aceita todos)

    def get_model():  # Deve ser implementado pelas subclasses para retornar a matriz de transformação
        return glm.mat4(1.0)

    def load(self):
        """
        Carrega a geometria e materiais do objeto a partir do .obj
        Retorna listas planas de vértices, coordenadas de textura e normais
        """
        self.verts_with_texture = load_obj_and_texture(self.object_filename, self.filtro)

        verts_coords, texture_coords, normals = [], [], []
        for verts, texture, normal, material in self.verts_with_texture:
            verts_coords.extend(verts)
            texture_coords.extend(texture)
            normals.extend(normal)

        return verts_coords, texture_coords, normals

    def desenha(self, ini_pos, shader):     
        """
        Realiza o desenho (renderização) do objeto.
        Aplica a textura e envia a matriz de transformação para o shader.
        """
        program = shader.ID

        # Define as propriedades do material no shader
        shader.setVec3('materialDiffuse', self.diffuse)
        shader.setVec3('materialSpecular', self.specular)
        
        # Matriz modelo
        mat_model = self.get_model() 
        loc_transformation = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_transformation, 1, GL_TRUE, np.array(mat_model))

        # Itera sobre cada conjunto de vértices associado a um material
        for verts, _, _, mat in self.verts_with_texture:
            inicio = ini_pos
            fim = len(verts) + inicio

            if mat.texture_id is not None:
                # Ativa a textura correspondente no OpenGL
                # print(f'Desenha de {inicio} ate {fim}, com textura {mat.texture_id} ({mat.texture_fname})')
                glBindTexture(GL_TEXTURE_2D, mat.texture_id)
            else:
                # Não é suportado desenhar sem textura no momento
                print(f'{inicio} ate {fim} sem textura, nao desenha')
                ini_pos = fim
                raise Exception('Nao suporta renderizar sem textura')

            # Realiza o desenho com base nos vértices carregados
            glDrawArrays(GL_TRIANGLES, inicio, fim - inicio)  # Renderização da geometria com OpenGL

            # Atualiza o índice de início para o próximo lote
            ini_pos = fim
