#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec3 Color;
in vec2 TexCoord;
out vec4 FragColor;

uniform int u_RenderMode;
uniform vec3 u_FlatColor;
uniform sampler2D u_Texture;

uniform vec3 u_SunPos;
uniform int u_HasSun;

const vec3 viewPos = vec3(0.0, 0.0, 0.0);
uniform float near_plane = 0.1;
uniform float far_plane = 100.0;

void main() {
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    
    vec3 result_base = vec3(0.0);
    vec3 result_specular = vec3(0.0);
    
    if(u_HasSun == 1) {
        float distance = length(u_SunPos - FragPos);
        float attenuation = 1.0 / (1.0 + 0.045 * distance + 0.0075 * (distance * distance));
        
        vec3 lightDir = normalize(u_SunPos - FragPos);
        
        float ambientStrength = 0.1;
        vec3 ambient = ambientStrength * vec3(1.0);
        
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = diff * vec3(1.0);
        
        float specularStrength = 1.2;
        vec3 reflectDir = reflect(-lightDir, norm);  
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 64);
        vec3 specular = specularStrength * spec * vec3(1.0);
        
        ambient *= attenuation;
        diffuse *= (attenuation * 10.0); 
        specular *= (attenuation * 10.0);
        
        result_base = ambient + diffuse;
        result_specular = specular;
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
        float z = gl_FragCoord.z * 2.0 - 1.0;
        float depth = (2.0 * near_plane * far_plane) / (far_plane + near_plane - z * (far_plane - near_plane));
        FragColor = vec4(vec3(depth / far_plane), 1.0);
    } else {
        FragColor = vec4(1.0, 0.0, 1.0, 1.0);
    }
}