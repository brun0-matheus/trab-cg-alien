# Importa a biblioteca glm para vetores e operações matemáticas
import glm

# Classe base para representar uma luz pontual (Point Light)
class Light:
    def __init__(
            self, 
            inside: bool,               # Define se a luz está dentro de um ambiente (ex: dentro da casa)
            position: glm.vec3,         # Posição da luz no mundo 3D
            diffuse: glm.vec3,          # Cor e intensidade da luz difusa
            specular: glm.vec3,         # Cor e intensidade da luz especular
            constant: float = 1.0,      # Fator de atenuação constante
            linear: float = 0.09,       # Fator de atenuação linear
            quadratic: float = 0.032    # Fator de atenuação quadrática
    ):
        self.inside = inside
        self.position = position
        self.diffuse = diffuse
        self.specular = specular
        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic

# Classe derivada que representa uma luz direcional em cone (Spotlight)
class SpotLight(Light):
    def __init__(self, *args, **kwargs):
        # Parâmetros específicos da Spotlight
        self.direction = kwargs.pop('direction', glm.vec3(0.0, 0.0, -1.0))                      # Direção para onde a luz aponta
        self.cutOff = kwargs.pop('cutOff', glm.cos(glm.radians(12.5)))                          # Ângulo interno do cone (corte)
        self.outerCutOff = kwargs.pop('outerCutOff', glm.cos(glm.radians(17.5)))                # Ângulo externo do cone (suavização)
        self.ambient = kwargs.pop('ambient', glm.vec3(0.05))                                    # Componente de luz ambiente (opcional)
        
        # Inicializa os atributos herdados da classe Light
        super().__init__(*args, **kwargs)
