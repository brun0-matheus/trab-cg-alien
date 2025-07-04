from OpenGL.GL import *
import glm

# Classe Shader: encapsula a criação, compilação e uso de shaders em OpenGL
class Shader:
    def __init__(self, vertexPath: str, fragmentPath: str):
        # 1. Carrega o código-fonte dos arquivos de shader
        try:
            # Abre os arquivos
            vShaderFile = open(vertexPath)
            fShaderFile = open(fragmentPath)

            # Lê o conteúdo dos arquivos
            vertexCode = vShaderFile.read()
            fragmentCode = fShaderFile.read()

            # Fecha os arquivos após leitura
            vShaderFile.close()
            fShaderFile.close()

            # 2. Compila os shaders

            # Compila o Vertex Shader
            vertex = glCreateShader(GL_VERTEX_SHADER)
            glShaderSource(vertex, vertexCode)
            glCompileShader(vertex)
            self.checkCompileErrors(vertex, "VERTEX")

            # Compila o Fragment Shader
            fragment = glCreateShader(GL_FRAGMENT_SHADER)
            glShaderSource(fragment, fragmentCode)
            glCompileShader(fragment)
            self.checkCompileErrors(fragment, "FRAGMENT")

            # Cria o programa e anexa os shaders compilados
            self.ID = glCreateProgram()
            glAttachShader(self.ID, vertex)
            glAttachShader(self.ID, fragment)
            glLinkProgram(self.ID)
            self.checkCompileErrors(self.ID, "PROGRAM")

            # Após linkar, os shaders podem ser deletados
            glDeleteShader(vertex)
            glDeleteShader(fragment)

        except IOError:
            print("ERROR::SHADER::FILE_NOT_SUCCESFULLY_READ")

    # Ativa o shader atual no OpenGL
    def use(self) -> None:
        glUseProgram(self.ID)

    # Métodos utilitários para definir variáveis uniform no shader
    def setBool(self, name: str, value: bool) -> None:
        glUniform1i(glGetUniformLocation(self.ID, name), int(value))

    def setInt(self, name: str, value: int) -> None:
        glUniform1i(glGetUniformLocation(self.ID, name), value)

    def setFloat(self, name: str, value: float) -> None:
        glUniform1f(glGetUniformLocation(self.ID, name), value)

    def setVec2(self, name: str, *args) -> None:
        if (len(args) == 1 and type(args[0]) == glm.vec2):
            glUniform2fv(glGetUniformLocation(self.ID, name), 1, glm.value_ptr(args[0]))
        elif (len(args) == 2 and all(map(lambda x: type(x) == float, args))):
            glUniform2f(glGetUniformLocation(self.ID, name), *args)

    def setVec3(self, name: str, *args) -> None:
        if (len(args) == 1 and type(args[0]) == glm.vec3):
            glUniform3fv(glGetUniformLocation(self.ID, name), 1, glm.value_ptr(args[0]))
        elif (len(args) == 3 and all(map(lambda x: type(x) == float, args))):
            glUniform3f(glGetUniformLocation(self.ID, name), *args)

    def setVec4(self, name: str, *args) -> None:
        if (len(args) == 1 and type(args[0]) == glm.vec4):
            glUniform4fv(glGetUniformLocation(self.ID, name), 1, glm.value_ptr(args[0]))
        elif (len(args) == 3 and all(map(lambda x: type(x) == float, args))):
            glUniform4f(glGetUniformLocation(self.ID, name), *args)

    def setMat2(self, name: str, mat: glm.mat2) -> None:
        glUniformMatrix2fv(glGetUniformLocation(self.ID, name), 1, GL_FALSE, glm.value_ptr(mat))

    def setMat3(self, name: str, mat: glm.mat3) -> None:
        glUniformMatrix3fv(glGetUniformLocation(self.ID, name), 1, GL_FALSE, glm.value_ptr(mat))

    def setMat4(self, name: str, mat: glm.mat4) -> None:
        glUniformMatrix4fv(glGetUniformLocation(self.ID, name), 1, GL_FALSE, glm.value_ptr(mat))

    # Método utilitário para verificar erros de compilação e linkagem dos shaders
    def checkCompileErrors(self, shader: int, type: str) -> None:
        if (type != "PROGRAM"):
            success = glGetShaderiv(shader, GL_COMPILE_STATUS)
            if (not success):
                infoLog = glGetShaderInfoLog(shader)
                print("ERROR::SHADER_COMPILATION_ERROR of type: " + type + "\n" + infoLog.decode() + "\n -- --------------------------------------------------- -- ")
        else:
            success = glGetProgramiv(shader, GL_LINK_STATUS)
            if (not success):
                infoLog = glGetProgramInfoLog(shader)
                print("ERROR::PROGRAM_LINKING_ERROR of type: " + type + "\n" + infoLog.decode() + "\n -- --------------------------------------------------- -- ")
