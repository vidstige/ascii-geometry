 #version 330
//in vec4 position;
in vec4 color;
//out float f_color;

out vec4 f_color;
void main() {
    //float lum = clamp(dot(normalize(Light - v_vert), normalize(v_norm)), 0.0, 1.0) * 0.8 + 0.2;
    //f_color = vec4(texture(Texture, v_text).rgb * lum, 1.0);
    //f_color = 1.0f;
    //f_color = vec4(0.3, 0.5, 1.0, 1.0);
    //f_color = vec4(1.0, 1.0, 1.0, 1.0);
    
    f_color = color;
}
