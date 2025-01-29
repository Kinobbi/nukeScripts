/// Extended Color Gradient Remap kernel: Remaps colors based on four gradient values with custom positions.
/// Works only on RGBA images.
kernel GradientColorRemap : ImageComputationKernel<ePixelWise>
{
  Image<eRead, eAccessPoint, eEdgeClamped> src; // The input image
  Image<eWrite> dst; // The output image

  param:
    float4 color1;  // First gradient color (e.g., shadows)
    float4 color2;  // Second gradient color (e.g., midtones 1)
    float4 color3;  // Third gradient color (e.g., midtones 2)
    float4 color4;  // Fourth gradient color (e.g., highlights)
    float pos1;     // Position of color1 along the remap scale (0-1)
    float pos2;     // Position of color2 along the remap scale (0-1)
    float pos3;     // Position of color3 along the remap scale (0-1)
    float clampMin; // Minimum luminance value for remapping
    float clampMax; // Maximum luminance value for remapping

  local:
    float3 coefficients; // Luminance calculation coefficients

  // Define parameter labels and default values
  void define() {
    defineParam(color1, "Gradient Color 1", float4(0.0f, 0.0f, 0.0f, 1.0f));  // Default black
    defineParam(color2, "Gradient Color 2", float4(0.33f, 0.33f, 0.33f, 1.0f));  // Default dark gray
    defineParam(color3, "Gradient Color 3", float4(0.66f, 0.66f, 0.66f, 1.0f));  // Default light gray
    defineParam(color4, "Gradient Color 4", float4(1.0f, 1.0f, 1.0f, 1.0f));  // Default white
    defineParam(pos1, "Position 1", 0.0f); // Default position for color1
    defineParam(pos2, "Position 2", 0.33f); // Default position for color2
    defineParam(pos3, "Position 3", 0.66f); // Default position for color3
    defineParam(clampMin, "Clamp Min", 0.0f); // Default min luminance
    defineParam(clampMax, "Clamp Max", 1.0f); // Default max luminance
  }

  // Initialization: Set up luminance coefficients based on Rec. 709 standard
  void init() {
    coefficients = float3(0.2126f, 0.7152f, 0.0722f);
  }

  void process() {
    // Read the input pixel
    SampleType(src) input = src();
    
    // Extract RGB values from the input and calculate luminance
    float3 srcPixel = float3(input.x, input.y, input.z);
    float luminance = dot(srcPixel, coefficients);

    // Clamp luminance dynamically using user-defined parameters
    luminance = clamp(luminance, clampMin, clampMax);

    // Normalize the clamped luminance to the range [0, 1]
    float normalizedLuminance = (luminance - clampMin) / (clampMax - clampMin);

    // Interpolation logic based on user-defined positions
    float4 remappedColor;
    if (normalizedLuminance <= pos1) {
        remappedColor = color1;
    } else if (normalizedLuminance <= pos2) {
        float factor = (normalizedLuminance - pos1) / (pos2 - pos1);
        remappedColor = (1.0f - factor) * color1 + factor * color2;
    } else if (normalizedLuminance <= pos3) {
        float factor = (normalizedLuminance - pos2) / (pos3 - pos2);
        remappedColor = (1.0f - factor) * color2 + factor * color3;
    } else {
        float factor = (normalizedLuminance - pos3) / (1.0f - pos3);
        remappedColor = (1.0f - factor) * color3 + factor * color4;
    }

    // Preserve the original alpha channel
    remappedColor.w = input.w * remappedColor.w;

    // Write the result to the output image
    dst() = remappedColor;
  }
};
