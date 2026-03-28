#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec3 Color;
in vec2 TexCoord;
out vec4 FragColor;

uniform int u_RenderMode;
uniform vec3 u_FlatColor;
uniform sampler2D u_Texture;

#define MAX_LIGHTS 10
uniform vec3 lightPos[MAX_LIGHTS];
uniform vec3 lightColor[MAX_LIGHTS];
uniform int lightState[MAX_LIGHTS];
uniform float lightIntensity[MAX_LIGHTS];

const vec3 viewPos = vec3(0.0, 0.0, 0.0);
uniform float near_plane = 0.1;
uniform float far_plane = 100.0;

void main() {
    vec3 norm = normalize(Normal);

    if (!gl_FrontFacing) {
        norm = -norm;
    }

    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 result_base = vec3(0.0);
    vec3 result_specular = vec3(0.0);
    
    for(int i = 0; i < MAX_LIGHTS; i++) {
        if(lightState[i] == 1) {
            float distance = length(lightPos[i] - FragPos);
            float attenuation = 1.0 / (1.0 + 0.045 * distance + 0.0075 * (distance * distance));
            
            vec3 lightDir = normalize(lightPos[i] - FragPos);
            
            float ambientStrength = 0.1;
            vec3 ambient = ambientStrength * lightColor[i];
            
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * lightColor[i];
            
            float specularStrength = 1.2;
            vec3 reflectDir = reflect(-lightDir, norm);  
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), 64);
            vec3 specular = specularStrength * spec * lightColor[i];
            
            ambient *= attenuation;
            diffuse *= (attenuation * lightIntensity[i]); 
            specular *= (attenuation * lightIntensity[i]);
            
            result_base += (ambient + diffuse);
            result_specular += specular;
        }
    }
    
    if (u_RenderMode == 0) {
        FragColor = vec4(u_FlatColor, 1.0);
    } else if (u_RenderMode == 1) {
        FragColor = vec4(Color, 1.0);
    } else if (u_RenderMode == 2) {
        FragColor = vec4(result_base * u_FlatColor + result_specular, 1.0);
    } else if (u_RenderMode == 3) {
        FragColor = texture(u_Texture, TexCoord);
    } else if (u_RenderMode == 4) {
        vec4 texColor = texture(u_Texture, TexCoord);
        vec3 baseColor = texColor.rgb * Color; 
        FragColor = vec4(result_base * baseColor + result_specular, texColor.a);
    } else if (u_RenderMode == 5) {  
        float real_depth = abs(FragPos.z);
        float depthValue = clamp(real_depth / 15.0, 0.0, 1.0); 
        FragColor = vec4(vec3(depthValue), 1.0);
    } else {
        FragColor = vec4(1.0, 0.0, 1.0, 1.0);
    }
}