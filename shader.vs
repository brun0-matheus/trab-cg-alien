#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 vert_normal;
layout (location = 2) in vec2 texture_coord;

varying vec3 FragPos;
varying vec3 Normal;
varying vec2 TexCoords;
		
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;            

void main(){
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * vert_normal;
	TexCoords = texture_coord;

	gl_Position = projection * view * model * vec4(position,1.0);
}
