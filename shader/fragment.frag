#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec3 Color;
in vec2 TexCoord;

out vec4 FragColor;

uniform int u_RenderMode;
uniform vec3 u_FlatColor;
uniform sampler2D u_Texture;

const vec3 lightPos = vec3(10.0, 10.0, 10.0);
const vec3 lightColor = vec3(1.0, 1.0, 1.0);
const vec3 viewPos = vec3(0.0, 0.0, 0.0);

void main() {
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    
    float ambientStrength = 0.2;
    vec3 ambient = ambientStrength * lightColor;
    
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);  
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightColor;
    
    vec3 phongLighting = ambient + diffuse + specular;
    
    if (u_RenderMode == 0) {
        FragColor = vec4(u_FlatColor, 1.0);
    } 
    else if (u_RenderMode == 1) {
        FragColor = vec4(Color, 1.0);
    } 
    else if (u_RenderMode == 2) {
        FragColor = vec4(phongLighting * Color, 1.0); 
    } 
    else if (u_RenderMode == 3) {
        FragColor = texture(u_Texture, TexCoord);
    } 
    else if (u_RenderMode == 4) {
        vec4 texColor = texture(u_Texture, TexCoord);
        FragColor = vec4(phongLighting * Color, 1.0) * texColor;
    } 
    else {
        FragColor = vec4(1.0, 0.0, 1.0, 1.0);
    }
}