from ctypes import windll, c_int, byref, sizeof, Structure, POINTER, c_void_p
from ctypes.wintypes import DWORD, HWND, ULONG

class ACCENT_POLICY(Structure):
    _fields_ = [
        ("AccentState", DWORD),
        ("AccentFlags", DWORD),
        ("GradientColor", DWORD),
        ("AnimationId", DWORD),
    ]

class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ("Attribute", DWORD),
        ("Data", POINTER(ACCENT_POLICY)),
        ("SizeOfData", ULONG),
    ]

# Accent States
ACCENT_DISABLED = 0
ACCENT_ENABLE_GRADIENT = 1
ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
ACCENT_INVALID_STATE = 5

# Window Composition Attributes
WCA_ACCENT_POLICY = 19

def apply_acrylic(hwnd):
    """
    Applies the Windows 10/11 Acrylic effect to a window given its HWND.
    """
    # Create Accent Policy
    # GradientColor: AABBGGRR (Alpha, Blue, Green, Red) - hex
    # For full transparency but keeping blur, we use a low alpha or specific color
    # 0x01000000 is often used for dark acrylic
    accent = ACCENT_POLICY()
    accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
    accent.GradientColor = 0x01050505  # Very dark, almost black
    accent.AccentFlags = 2 # COMPOSITE_ON_SURFACE (usually needed for Acrylic)
    accent.AnimationId = 0
    
    # Create Window Composition Attribute Data
    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = WCA_ACCENT_POLICY
    data.Data = byref(accent)
    data.SizeOfData = sizeof(accent)
    
    # helper for SetWindowCompositionAttribute
    SetWindowCompositionAttribute = windll.user32.SetWindowCompositionAttribute
    SetWindowCompositionAttribute.argtypes = [HWND, POINTER(WINDOWCOMPOSITIONATTRIBDATA)]
    SetWindowCompositionAttribute.restype = c_int
    
    SetWindowCompositionAttribute(hwnd, byref(data))

def cleanup_acrylic(hwnd):
    """
    Disables the effect (resets to default).
    """
    accent = ACCENT_POLICY()
    accent.AccentState = ACCENT_DISABLED
    
    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = WCA_ACCENT_POLICY
    data.Data = byref(accent)
    data.SizeOfData = sizeof(accent)
    
    SetWindowCompositionAttribute = windll.user32.SetWindowCompositionAttribute
    SetWindowCompositionAttribute(hwnd, byref(data))
