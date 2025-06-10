from enum import Enum
from OpenGL.GL import *
import glm

# Enumeração para os tipos de movimento da câmera
class Camera_Movement(Enum):
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4

# Constantes padrão da câmera
YAW         = -105.0      # Ângulo inicial no eixo Y (horizontal)
PITCH       = -6.0        # Ângulo inicial no eixo X (vertical)
SPEED       = 2.5         # Velocidade de movimento
SENSITIVITY = 0.1         # Sensibilidade do mouse
ZOOM        = 45.0        # Campo de visão (FOV)

# Classe de câmera com suporte a movimentação e rotação usando ângulos de Euler
class Camera:
    # Alias para facilitar chamadas
    FORWARD = Camera_Movement.FORWARD
    BACKWARD = Camera_Movement.BACKWARD
    LEFT = Camera_Movement.LEFT
    RIGHT = Camera_Movement.RIGHT

    def __init__(self, *args, **kwargs):
        # Caso a câmera seja inicializada com 8 parâmetros posicionais
        if (len(args) == 8 and len(kwargs) == 0):
            posX, posY, posZ, upX, upY, upZ, yaw, pitch = args
            self.Position = glm.vec3(posX, posY, posZ)     # Posição da câmera
            self.WorldUp = glm.vec3(upX, upY, upZ)          # Vetor Up global
            self.Yaw = yaw                                  # Rotação em Y
            self.Pitch = pitch                              # Rotação em X

        # Caso a câmera seja inicializada com argumentos nomeados ou menos parâmetros
        elif (len(args) + len(kwargs) <= 4):
            keyword_arguments = ("position", "up", "yaw", "pitch")
            keyword_arguments_defaults = {
                "position": glm.vec3(), 
                "up": glm.vec3(0,1,0), 
                "yaw": YAW, 
                "pitch": PITCH
            }

            # Mapeia argumentos posicionais para os nomes esperados
            for i in range(len(args)):
                kw = keyword_arguments[i]
                value = args[i]
                kwargs[kw] = value

            # Atualiza valores com defaults e overrides
            keyword_arguments_defaults.update(kwargs)

            self.Position = keyword_arguments_defaults["position"]
            self.WorldUp = keyword_arguments_defaults["up"]
            self.Yaw = keyword_arguments_defaults["yaw"]
            self.Pitch = keyword_arguments_defaults["pitch"]

        else:
            raise TypeError("Invalid argument count for Camera()")

        # Inicializa vetores de orientação
        self.Front = glm.vec3(0.0, 0.0, -1.0)
        self.Up = glm.vec3()
        self.Right = glm.vec3()

        # Parâmetros de controle
        self.MovementSpeed = SPEED
        self.MouseSensitivity = SENSITIVITY
        self.Zoom = ZOOM

        # Atualiza vetores de direção
        self.updateCameraVectors()

    # Retorna a matriz de visualização (view matrix)
    def GetViewMatrix(self) -> glm.mat4:
        return glm.lookAt(self.Position, self.Position + self.Front, self.Up)

    # Processa o movimento com base em uma direção e no tempo entre quadros
    def ProcessKeyboard(self, direction: Camera_Movement, deltaTime: float) -> None:
        velocity = self.MovementSpeed * deltaTime
        if (direction == Camera_Movement.FORWARD):
            self.Position += self.Front * velocity
        if (direction == Camera_Movement.BACKWARD):
            self.Position -= self.Front * velocity
        if (direction == Camera_Movement.LEFT):
            self.Position -= self.Right * velocity
        if (direction == Camera_Movement.RIGHT):
            self.Position += self.Right * velocity

    # Processa o movimento do mouse (rotação da câmera)
    def ProcessMouseMovement(self, xoffset: float, yoffset: float, constrainPitch: bool = True) -> None:
        # Aplica sensibilidade
        xoffset *= self.MouseSensitivity
        yoffset *= self.MouseSensitivity

        # Atualiza ângulos de Euler
        self.Yaw   += xoffset
        self.Pitch += yoffset

        # Limita o pitch para evitar efeito de flip
        if (constrainPitch):
            if (self.Pitch > 89.0):
                self.Pitch = 89.0
            if (self.Pitch < -89.0):
                self.Pitch = -89.0

        # Atualiza vetores com base nos novos ângulos
        self.updateCameraVectors()

    # Processa rolagem do mouse (zoom in/out)
    def ProcessMouseScroll(self, yoffset: float) -> None:
        self.Zoom -= yoffset
        self.Zoom = max(1.0, min(self.Zoom, 45.0))  # Limita o FOV entre 1 e 45

    # Atualiza os vetores de direção da câmera com base nos ângulos
    def updateCameraVectors(self) -> None:
        # Calcula o novo vetor "Front"
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.Yaw)) * glm.cos(glm.radians(self.Pitch))
        front.y = glm.sin(glm.radians(self.Pitch))
        front.z = glm.sin(glm.radians(self.Yaw)) * glm.cos(glm.radians(self.Pitch))
        self.Front = glm.normalize(front)

        # Recalcula os vetores "Right" e "Up"
        self.Right = glm.normalize(glm.cross(self.Front, self.WorldUp))  # Perpendicular à direção e ao Up global
        self.Up = glm.normalize(glm.cross(self.Right, self.Front))       # Perpendicular ao Right e à direção
