from setuptools import find_packages,setup
from typing import List

def get_requirements()->List[str]:
    """
    this function will return  list of requirements 
    
    
    """
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt','r') as file:
           #Read lines from file 
           lines=file.readlines()
           #process eachline 
           for line in lines:
               requirement=line.strip()
               ##ignore empty lines and -e.
               if requirement and requirement!='-e .':
                   requirement_lst.append(requirement)
    
    except FileNotFoundError:
        print("requirements.txt file not found")

    return requirement_lst

print(get_requirements())

setup(
    name="Network Security",
    version="0.0.1",
    author="Soham Nemade",
    author_email="nemadesoham21@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements() 
    )

                   
            