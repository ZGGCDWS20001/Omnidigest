# OmniDigest Python Commenting Standard

This document outlines the standard for writing comments and docstrings in the OmniDigest Python codebase. The goal is to ensure consistency, clarity, and accessibility for both English-speaking and Chinese-speaking developers.

## 1. Bilingual Requirement
All major comments, including module-level docstrings, class docstrings, function/method docstrings, and significant inline comments, **must be bilingual**.
- **English First:** The primary description should be in English.
- **Chinese Translation:** A direct, accurate Chinese translation should follow immediately beneath the English text or in the respective sections.

## 2. Docstring Style
We strictly adhre to the **Google Python Docstring Style** convention, extended to support bilingual text.

### 2.1 Module Docstrings
Every `.py` file must start with a module-level docstring explaining its purpose.
```python
"""
Brief description of the module in English.
模块的简短中文描述。

Detailed explanation of what the module does, its main components, 
and any other relevant information.
详细解释模块的功能、主要组件以及任何其他相关信息。
"""
```

### 2.2 Function and Method Docstrings
Functions and methods must describe their purpose, arguments, return values, and exceptions raised.

```python
def example_function(param1: int, param2: str) -> bool:
    """
    Brief description of the function in English.
    函数的简短中文描述。
    
    Args:
        param1 (int): Description of param1 in English. / param1 的中文描述。
        param2 (str): Description of param2 in English. / param2 的中文描述。
        
    Returns:
        bool: Description of the return value in English.
        布尔值: 返回值的中文描述。
        
    Raises:
        ValueError: When param1 is invalid. / 当 param1 无效时引发。
    """
    pass
```

### 2.3 Class Docstrings
Classes should describe their purpose and any important attributes.

```python
class ExampleClass:
    """
    Brief description of the class in English.
    类的简短中文描述。
    
    Attributes:
        attr1 (int): Description of attr1 in English. / attr1 的中文描述。
        attr2 (str): Description of attr2 in English. / attr2 的中文描述。
    """
```

## 3. Inline Comments
Use inline comments sparingly. When complex logic requires explanation, use the following format:

```python
# Calculate the final score based on the weighted sum of inputs and decay factor.
# 根据输入的加权和衰减因子计算最终得分。
final_score = (base_score * weight) - decay
```

## 4. Type Hinting
Type hinting is **mandatory** for all function and method signatures. This reduces the need for extensive parameter type descriptions in the docstrings.
