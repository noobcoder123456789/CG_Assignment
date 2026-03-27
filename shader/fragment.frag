#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec3 Color;
in vec2 TexCoord;

out vec4 FragColor;

uniform int u_RenderMode;
uniform vec3 u_FlatColor;
uniform sampler2D u_Texture;

#define MAX_LIGHTS 3
uniform vec3 lightPos[MAX_LIGHTS];
uniform vec3 lightColor[MAX_LIGHTS];
uniform int lightState[MAX_LIGHTS];

const vec3 viewPos = vec3(0.0, 0.0, 0.0);

uniform float near_plane = 0.1;
uniform float far_plane = 100.0;

float LinearizeDepth(float depth) {
    float z = depth * 2.0 - 1.0; // NDC 
    return (2.0 * near_plane * far_plane) / (far_plane + near_plane - z * (far_plane - near_plane));	
}

void main() {
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    
    vec3 result_lighting = vec3(0.0);
    
    for(int i = 0; i < MAX_LIGHTS; i++) {
        if(lightState[i] == 1) {
            vec3 lightDir = normalize(lightPos[i] - FragPos);
            
            float ambientStrength = 0.2;
            vec3 ambient = ambientStrength * lightColor[i];
            
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * lightColor[i];
            
            float specularStrength = 0.5;
            vec3 reflectDir = reflect(-lightDir, norm);  
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
            vec3 specular = specularStrength * spec * lightColor[i];
            
            result_lighting += (ambient + diffuse + specular);
        }
    }
    
    if (u_RenderMode == 0) {
        FragColor = vec4(u_FlatColor, 1.0);
    } else if (u_RenderMode == 1) {
        FragColor = vec4(Color, 1.0);
    } else if (u_RenderMode == 2) {
        FragColor = vec4(result_lighting * Color, 1.0);
    } else if (u_RenderMode == 3) {
        FragColor = texture(u_Texture, TexCoord);
    } else if (u_RenderMode == 4) {
        vec4 texColor = texture(u_Texture, TexCoord);
        FragColor = vec4(result_lighting, 1.0) * texColor;
    } else if (u_RenderMode == 5) {  
        float depth = LinearizeDepth(gl_FragCoord.z) / far_plane;
        FragColor = vec4(vec3(depth), 1.0);
    } else {
        FragColor = vec4(1.0, 0.0, 1.0, 1.0);
    }
}