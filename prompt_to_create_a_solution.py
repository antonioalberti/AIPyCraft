def get_prompt(solution_name, solution_description):
    prompt = f"""Solution: {solution_name} \n\nDescription: {solution_description}\n\nPlease provide a detailed description of how to code a complete program for this solution. 

How to work:

The Solutions are composed by Components. 
Each Component is a piece of code that solves a specific problem. 
Make the Solution with the minimum number of Components possible. 
Make instructions to yourselve, since you are going to code this solution in the future.
Do not send the code now. This will be done in further interactions.
The last Component will always be a main.py program. 
Therefore, always put a if __name__ == "__main__": at the end of the main.py program, inializing and running the all the solution.
The previous Components are classes to be initiatized in the main.py program. Therefeore, the main.py program must be able to import all the required classes.

Expected answer:

Add a blank line and describe the Components required to implement this Solution. After every Component, put the file associatated with the Component using the label File. 
All the Components should be numbered and separated by a new line. This will make the Solution modular and each Component is self-contained. 
All files need to have different names obrigatory.
For the response parser to be possible, each Component description must be on a single line, starting with the word "Component N:", where N is the number of the Component.

The following is an example:

Description: Plot Mandelbrot fractal with resolution 1000x1000 and color mapping.

Component 1: Create a class MandelbrotFractal that will handle the calculations and generation of the Mandelbrot fractal. 
Include methods to determine the escape time for each point in the fractal, based on the Mandelbrot set formula. 
This class will be in a file named mandelbrot.py.

File 1: mandelbrot.py

Component 2: Create a class FractalPlotter that will handle the plotting of the Mandelbrot fractal. 
Include methods to generate the plot with customizable resolution and color mapping. 
This class will be in a file named fractal_plotter.py.

File 2: fractal_plotter.py

Component 3: Implement a main program in a file named main.py that will instantiate the MandelbrotFractal class and the FractalPlotter class. 
Use these classes to calculate the escape times and plot the Mandelbrot fractal. 
Allow the user to specify the resolution of the plot and the color mapping. 
Include a if __name__ == "__main__": at the end of the main.py program, inializing and running the all the Solution.

File 3: main.py
"""
    return prompt
