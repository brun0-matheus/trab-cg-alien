#version 330 core

struct PointLight {
    vec3 position;
    
    float constant;
    float linear;
    float quadratic;
	
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct SpotLight {
    vec3 position;
    vec3 direction;
    float cutOff;
    float outerCutOff;
  
    float constant;
    float linear;
    float quadratic;
  
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;       
};

#define MAX_POINT_LIGHTS 4
#define MAX_SPOT_LIGHTS 4

varying vec3 FragPos;
varying vec3 Normal;
varying vec2 TexCoords;

uniform vec3 viewPos;
uniform PointLight pointLights[MAX_POINT_LIGHTS];
uniform SpotLight spotLights[MAX_SPOT_LIGHTS];
uniform float shininess;
uniform vec3 materialSpecular;
uniform vec3 materialDiffuse;

uniform int numPointLights;
uniform int numSpotLights;
uniform int invisible;

uniform vec3 ambientLight;

uniform sampler2D imagem;

// function prototypes
vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir);
vec3 CalcSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir);

void main()
{    
	vec4 texture = texture2D(imagem, TexCoords);
    if(texture.a < 0.1)
        discard;

    // properties
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    
    vec3 result = ambientLight;
    // phase 2: point lights
    for(int i = 0; i < numPointLights; i++)
        result += CalcPointLight(pointLights[i], norm, FragPos, viewDir);    
    // phase 3: spot light
    for(int i = 0; i < numSpotLights; i++)
        result += CalcSpotLight(spotLights[i], norm, FragPos, viewDir);    

    float alpha = 1.0;
    if(invisible == 1) {
        alpha = result.x - 0.3;
        alpha = max(alpha, 0);
        alpha = min(alpha, 1);
    }
    
    vec3 noAlpha = vec3(texture); 
    gl_FragColor = vec4(result * noAlpha, alpha);
}

// calculates the color when using a point light.
vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);
    // diffuse shading
    // inverter normal se luz estiver vindo do lado oposto
    float diff = abs(dot(normal, lightDir));

    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    // attenuation
    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));    
    // combine results
    vec3 diffuse = light.diffuse * diff * materialDiffuse;
    vec3 specular = light.specular * spec * materialSpecular;

    diffuse *= attenuation;
    specular *= attenuation;
    return diffuse + specular;
}

// calculates the color when using a spot light.
vec3 CalcSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(fragPos - light.position);

    // Diffuse shading
    // inverter normal se luz estiver vindo do lado oposto
    float diff = abs(dot(normal, lightDir));
    // Specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);

    // Attenuation
    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));

    // Spotlight intensity
    float theta = dot(lightDir, normalize(light.direction));
    float epsilon = light.cutOff - light.outerCutOff;
    float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);

    // combine results
    vec3 diffuse = light.diffuse * diff * materialDiffuse;
    vec3 specular = light.specular * spec * materialSpecular;
    diffuse *= attenuation * intensity;
    specular *= attenuation * intensity;
    return diffuse + specular;
}
