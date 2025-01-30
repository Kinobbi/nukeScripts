kernel GradientColorRemap : ImageComputationKernel<ePixelWise>
{
  Image<eRead, eAccessPoint, eEdgeClamped> src;
  Image<eWrite> dst;

  param:
    float4 color1, color2, color3, color4;
    float pos1, pos2, pos3;
    float clampMin, clampMax;
    int interpolationMode;

  local:
    float3 coefficients;

  void define() {
    defineParam(color1, "Gradient Color 1", float4(0.0f, 0.0f, 0.0f, 1.0f));
    defineParam(color2, "Gradient Color 2", float4(0.33f, 0.33f, 0.33f, 1.0f));
    defineParam(color3, "Gradient Color 3", float4(0.66f, 0.66f, 0.66f, 1.0f));
    defineParam(color4, "Gradient Color 4", float4(1.0f, 1.0f, 1.0f, 1.0f));
    defineParam(pos1, "Position 1", 0.0f);
    defineParam(pos2, "Position 2", 0.33f);
    defineParam(pos3, "Position 3", 0.66f);
    defineParam(clampMin, "Clamp Min", 0.0f);
    defineParam(clampMax, "Clamp Max", 1.0f);
    defineParam(interpolationMode, "Interpolation Mode", 0);
  }

  void init() {
    coefficients = float3(0.2126f, 0.7152f, 0.0722f); // Rec. 709 Luminance Coefficients
  }

  float smoothStep(float edge0, float edge1, float x) {
    x = clamp((x - edge0) / (edge1 - edge0), 0.0f, 1.0f);
    return x * x * (3.0f - 2.0f * x);
  }

  void process() {
    // Read input pixel
    SampleType(src) input = src();
    
    // Extract RGB values
    float3 srcPixel = float3(input[0], input[1], input[2]);

    // Compute original luminance (brightness before remapping)
    float originalLuminance = dot(srcPixel, coefficients);
    
    // Clamp luminance for valid range
    float clampedLuminance = clamp(originalLuminance, clampMin, clampMax);
    
    // **Scale position knobs dynamically within the clamp range**
    float adjustedPos1 = clampMin + pos1 * (clampMax - clampMin);
    float adjustedPos2 = clampMin + pos2 * (clampMax - clampMin);
    float adjustedPos3 = clampMin + pos3 * (clampMax - clampMin);

    // Normalize clamped luminance for interpolation
    float normalizedLuminance = (clampedLuminance - clampMin) / (clampMax - clampMin);

    // Compute interpolation factors
    float factor1 = (interpolationMode == 0) ? ((clampedLuminance - adjustedPos1) / (adjustedPos2 - adjustedPos1)) : smoothStep(adjustedPos1, adjustedPos2, clampedLuminance);
    float factor2 = (interpolationMode == 0) ? ((clampedLuminance - adjustedPos2) / (adjustedPos3 - adjustedPos2)) : smoothStep(adjustedPos2, adjustedPos3, clampedLuminance);
    float factor3 = (interpolationMode == 0) ? ((clampedLuminance - adjustedPos3) / (clampMax - adjustedPos3)) : smoothStep(adjustedPos3, clampMax, clampedLuminance);

    // Perform gradient color interpolation
    float4 remappedColor;
    if (clampedLuminance <= adjustedPos1) {
        remappedColor = color1;
    } else if (clampedLuminance <= adjustedPos2) {
        remappedColor = (1.0f - factor1) * color1 + factor1 * color2;
    } else if (clampedLuminance <= adjustedPos3) {
        remappedColor = (1.0f - factor2) * color2 + factor2 * color3;
    } else {
        remappedColor = (1.0f - factor3) * color3 + factor3 * color4;
    }

    // Compute luminance of remapped color
    float remappedLuminance = dot(float3(remappedColor[0], remappedColor[1], remappedColor[2]), coefficients);

    // **Ensure the output retains the original brightness**  
    float3 finalColor = remappedColor.xyz;

    // Adjust the brightness to match the original input luminance
    if (remappedLuminance > 0.0) {
        finalColor = (finalColor / remappedLuminance) * originalLuminance;
    } else {
        finalColor = float3(0.0, 0.0, 0.0);
    }

    // Preserve original alpha channel
    remappedColor.xyz = finalColor;
    remappedColor.w = input[3];

    // Write to output
    dst() = remappedColor;
  }
};
