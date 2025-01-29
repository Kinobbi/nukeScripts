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
    int interpolationMode; // 0 for Linear, 1 for Smoothstep

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
    defineParam(interpolationMode, "Interpolation Mode", 0); // Default to Linear
  }

  // Initialization: Set up luminance coefficients based on Rec. 709 standard
  void init() {
    coefficients = float3(0.2126f, 0.7152f, 0.0722f);
  }

  float smoothStep(float edge0, float edge1, float x) {
    x = clamp((x - edge0) / (edge1 - edge0), 0.0f, 1.0f);
    return x * x * (3.0f - 2.0f * x);
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

    // Determine interpolation mode
    float factor1 = (interpolationMode == 0) ? ((normalizedLuminance - pos1) / (pos2 - pos1)) : smoothStep(pos1, pos2, normalizedLuminance);
    float factor2 = (interpolationMode == 0) ? ((normalizedLuminance - pos2) / (pos3 - pos2)) : smoothStep(pos2, pos3, normalizedLuminance);
    float factor3 = (interpolationMode == 0) ? ((normalizedLuminance - pos3) / (1.0f - pos3)) : smoothStep(pos3, 1.0f, normalizedLuminance);

    // Interpolation logic
    float4 remappedColor;
    if (normalizedLuminance <= pos1) {
        remappedColor = color1;
    } else if (normalizedLuminance <= pos2) {
        remappedColor = (1.0f - factor1) * color1 + factor1 * color2;
    } else if (normalizedLuminance <= pos3) {
        remappedColor = (1.0f - factor2) * color2 + factor2 * color3;
    } else {
        remappedColor = (1.0f - factor3) * color3 + factor3 * color4;
    }

    // Preserve the original alpha channel
    remappedColor.w = input.w * remappedColor.w;

    // Write the result to the output image
    dst() = remappedColor;
  }
};
