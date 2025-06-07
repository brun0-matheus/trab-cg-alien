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

def SpotLight(Light):
    def __init__(*args, **kwargs):
        self.cutoff = kwargs.pop('cutoff', glm.cos(glm.radians(12.5)))
        self.outer_cutoff = kwargs.pop('outer_cutoff', glm.cose(glm.radians(15)))

        super().__init__(*args, **kwargs)

