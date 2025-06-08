import glm

class Light:
    def __init__(
            self, 
            position: glm.vec3, 
            diffuse: glm.vec3,
            specular: glm.vec3,
            constant: float = 1.0, 
            linear: float = 0.09, 
            quadratic: float = 0.032
    ):
        self.position = position
        self.diffuse = diffuse
        self.specular = specular
        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic

class SpotLight(Light):
    def __init__(self, *args, **kwargs):
        self.direction = kwargs.pop('direction', glm.vec3(0.0, 0.0, -1.0))
        self.cutOff = kwargs.pop('cutOff', glm.cos(glm.radians(12.5)))
        self.outerCutOff = kwargs.pop('outerCutOff', glm.cos(glm.radians(17.5)))
        self.ambient = kwargs.pop('ambient', glm.vec3(0.05))
        super().__init__(*args, **kwargs)





