/// Color Gradient Remap kernel: Remaps colors based on three gradient values with dynamic clamping.
/// Works only on RGBA images.
kernel GradientColorRemap : ImageComputationKernel<ePixelWise>
{
  Image<eRead, eAccessPoint, eEdgeClamped> src; // The input image
  Image<eWrite> dst; // The output image

  param:
    float4 color1;  // First gradient color (e.g., shadows)
    float4 color2;  // Second gradient color (e.g., midtones)
    float4 color3;  // Third gradient color (e.g., highlights)
    float clampMin; // Minimum luminance value for remapping
    float clampMax; // Maximum luminance value for remapping

  local:
    float3 coefficients; // Luminance calculation coefficients

  // Define parameter labels and default values
  void define() {
    defineParam(color1, "Gradient Color 1", float4(0.0f, 0.0f, 0.0f, 1.0f));  // Default black with full alpha
    defineParam(color2, "Gradient Color 2", float4(0.5f, 0.5f, 0.5f, 1.0f));  // Default gray with full alpha
    defineParam(color3, "Gradient Color 3", float4(1.0f, 1.0f, 1.0f, 1.0f));  // Default white with full alpha
    defineParam(clampMin, "Clamp Min", 0.0f);  // Default minimum luminance
    defineParam(clampMax, "Clamp Max", 1.0f);  // Default maximum luminance
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

    // Interpolation logic:
    //  - If luminance < 0.5, blend between color1 and color2
    //  - If luminance >= 0.5, blend between color2 and color3
    float4 remappedColor;
    if (normalizedLuminance < 0.5f) {
        float factor = normalizedLuminance * 2.0f;  // Scale 0-0.5 to 0-1 range
        remappedColor = (1.0f - factor) * color1 + factor * color2;
    } else {
        float factor = (normalizedLuminance - 0.5f) * 2.0f;  // Scale 0.5-1 to 0-1 range
        remappedColor = (1.0f - factor) * color2 + factor * color3;
    }

    // Preserve the original alpha channel by multiplying with remapped alpha
    remappedColor.w = input.w * remappedColor.w;

    // Write the result to the output image
    dst() = remappedColor;
  }
};
