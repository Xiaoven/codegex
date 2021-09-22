import jpype
import jpype.imports

jpype.startJVM(classpath="dependencies/jars/*")
import spoon.Launcher as Launcher

if __name__ == '__main__':
    abs_path = '/Users/audrey/Documents/GitHub/xiaoven/codegex/tests/unit_tests/resources/FindBugs.java'

    print(jpype.java.lang.System.getProperty("java.class.path"))

    import spoon.Launcher as Launcher
    import spoon.reflect.cu.position.NoSourcePosition as NoSourcePosition

    with open(abs_path, 'r') as f:
        content = f.read()

    clazz = Launcher.parseClass(content)
    directChildren = clazz.getDirectChildren()
    for element in directChildren:
        sourcePosition = element.getPosition()
        if not isinstance(sourcePosition, NoSourcePosition):
            print(sourcePosition.getLine(), sourcePosition.getEndLine())

    jpype.shutdownJVM()
