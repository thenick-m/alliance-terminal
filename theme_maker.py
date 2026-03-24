def get_intermediate_colors(color1_rgb, color2_rgb, num_intermediate_colors):
    steps = num_intermediate_colors + 1 
    
    intermediate_colors = []
    for i in range(1, steps):
        t = i / steps
        

        r = int(color1_rgb[0] + t * (color2_rgb[0] - color1_rgb[0]))
        g = int(color1_rgb[1] + t * (color2_rgb[1] - color1_rgb[1]))
        b = int(color1_rgb[2] + t * (color2_rgb[2] - color1_rgb[2]))
        
        intermediate_colors.append((r, g, b))
        
    return intermediate_colors

start_color = tuple(int(color) for color in input("color1: ").split()) 
end_color = tuple(int(color) for color in input("color4: ").split())   

colors_between = get_intermediate_colors(start_color, end_color, 2)

print(f"color1: {start_color}")
print(f"color2: {colors_between[0]}")
print(f"color2: {colors_between[1]}")
print(f"color4: {end_color}")