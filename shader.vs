#version 330 core

// Entrada dos atributos do vértice
layout (location = 0) in vec3 aPos;        // Posição do vértice
layout (location = 1) in vec3 aNormal;     // Vetor normal do vértice
layout (location = 2) in vec2 aTexCoords;  // Coordenadas de textura

// Saídas para o fragment shader
out vec3 FragPos;       // Posição no espaço do mundo
out vec3 Normal;        // Vetor normal transformado
out vec2 TexCoords;     // Coordenadas de textura

// Uniforms de transformação
uniform mat4 model;     // Matriz de modelo (transformação local)
uniform mat4 view;      // Matriz de visão (câmera)
uniform mat4 projection;// Matriz de projeção (perspectiva)

void main()
{
    // Calcula a posição final do vértice na tela
    gl_Position = projection * view * model * vec4(aPos, 1.0);

    // Converte posição para espaço do mundo
    FragPos = vec3(model * vec4(aPos, 1.0));

    // Aplica a matriz de modelo à normal (transposta inversa para manter orientação)
    Normal = mat3(transpose(inverse(model))) * aNormal;

    // Repassa coordenadas de textura
    TexCoords = aTexCoords;
}
