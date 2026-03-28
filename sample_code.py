# sample_code.py — Test file for CodeSentinel demo
# Contains intentional code issues for the scanner to find.

import os
import pickle

# SECURITY: Hardcoded credentials
DATABASE_PASSWORD = "super_secret_123"
API_KEY = "sk-abc123def456"

def process_user_input(user_data):
    """Process raw user input — has multiple issues."""
    # SECURITY: eval() on user input = remote code execution
    result = eval(user_data)
    
    # SECURITY: os.system with string concat = command injection
    os.system("echo " + user_data)
    
    # SECURITY: pickle.loads on untrusted data = arbitrary code execution
    obj = pickle.loads(user_data.encode())
    
    return result

def deeply_nested(a, b, c, d, e, f, g):
    """Too many parameters and deeply nested logic."""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
    return 0

class MassiveController:
    """God class with too many methods."""
    def action_1(self): pass
    def action_2(self): pass
    def action_3(self): pass
    def action_4(self): pass
    def action_5(self): pass
    def action_6(self): pass
    def action_7(self): pass
    def action_8(self): pass
    def action_9(self): pass
    def action_10(self): pass
    def action_11(self): pass
    def action_12(self): pass
    def action_13(self): pass
    def action_14(self): pass
    def action_15(self): pass
    def action_16(self): pass
    def action_17(self): pass
    def action_18(self): pass
    def action_19(self): pass
    def action_20(self): pass
    def action_21(self): pass

def buggy_error_handling():
    """Bare except catches everything including Ctrl+C."""
    try:
        x = 1 / 0
    except:
        pass  # Silently swallowing ALL exceptions

def another_buggy():
    try:
        open("missing_file.txt")
    except:
        pass
